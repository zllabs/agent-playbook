import json
import re
import sqlite3
from pathlib import Path
from typing import Optional

from sources import playbook_skill_path

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "data" / "catalog.json"
CUSTOM_SKILLS_PATH = ROOT / "data" / "custom_skills.json"
CUSTOM_SKILLS_EXAMPLE = ROOT / "data" / "custom_skills.example.json"
SKILLS_DIR = ROOT / "skills"
DB_PATH = ROOT / "data" / "playbook.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> int:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    catalog = json.loads(CATALOG_PATH.read_text())
    local = discover_local_skills()
    custom = _load_custom_skills_file()
    conn = get_conn()
    try:
        conn.executescript("""
            DROP TABLE IF EXISTS skills_fts;
            DROP TABLE IF EXISTS edges;
            DROP TABLE IF EXISTS skills;

            CREATE TABLE skills (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                tags TEXT NOT NULL,
                ecosystem TEXT NOT NULL,
                repo_url TEXT NOT NULL,
                source_url TEXT NOT NULL,
                author TEXT NOT NULL,
                license TEXT,
                version TEXT,
                custom INTEGER NOT NULL DEFAULT 0,
                local INTEGER NOT NULL DEFAULT 0
            );

            CREATE VIRTUAL TABLE skills_fts USING fts5(
                id UNINDEXED,
                title,
                description,
                tags,
                content='skills',
                content_rowid='rowid'
            );

            CREATE TABLE edges (
                from_id TEXT NOT NULL,
                to_id TEXT NOT NULL,
                type TEXT NOT NULL
            );
        """)

        for skill in catalog["skills"]:
            _insert_skill_row(conn, skill)

        for skill in local:
            _insert_skill_row(conn, skill, local=True)

        known_ids = {s["id"] for s in catalog["skills"]} | {s["id"] for s in local}
        for skill in custom:
            if skill["id"] in known_ids:
                continue
            _insert_skill_row(conn, skill, custom=True)

        conn.execute("INSERT INTO skills_fts(id, title, description, tags) SELECT id, title, description, tags FROM skills")

        for edge in catalog.get("edges", []):
            conn.execute(
                "INSERT INTO edges (from_id, to_id, type) VALUES (?, ?, ?)",
                (edge["from_id"], edge["to_id"], edge["type"]),
            )

        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
        return count
    finally:
        conn.close()


def discover_local_skills() -> list[dict]:
    """Load skill packages from skills/*/skill.json."""
    skills: list[dict] = []
    if not SKILLS_DIR.is_dir():
        return skills
    for pkg_dir in sorted(SKILLS_DIR.iterdir()):
        if not pkg_dir.is_dir() or pkg_dir.name.startswith("."):
            continue
        manifest = pkg_dir / "skill.json"
        if not manifest.exists():
            continue
        data = json.loads(manifest.read_text())
        data.setdefault("id", pkg_dir.name)
        data.setdefault("ecosystem", "cursor")
        data.setdefault("author", "Agent Playbook")
        data.setdefault("license", "MIT")
        data.setdefault("repo_url", playbook_skill_path(data["id"]).rsplit("/tree/", 1)[0])
        if not str(data.get("source_url", "")).startswith("http"):
            data["source_url"] = playbook_skill_path(data["id"])
        data["tags"] = [t.lower() for t in data.get("tags", [])]
        skills.append(data)
    return skills


def _load_custom_skills_file() -> list[dict]:
    if not CUSTOM_SKILLS_PATH.exists():
        if CUSTOM_SKILLS_EXAMPLE.exists():
            CUSTOM_SKILLS_PATH.write_text(CUSTOM_SKILLS_EXAMPLE.read_text())
        else:
            CUSTOM_SKILLS_PATH.write_text('{"skills": []}\n')
        return []
    return json.loads(CUSTOM_SKILLS_PATH.read_text()).get("skills", [])


def _save_custom_skills_file(skills: list[dict]) -> None:
    CUSTOM_SKILLS_PATH.write_text(json.dumps({"skills": skills}, indent=2) + "\n")


def _insert_skill_row(
    conn: sqlite3.Connection,
    skill: dict,
    *,
    custom: bool = False,
    local: bool = False,
) -> None:
    tags_str = " ".join(skill["tags"])
    conn.execute(
        """INSERT INTO skills
           (id, title, description, tags, ecosystem, repo_url, source_url, author, license, version, custom, local)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            skill["id"],
            skill["title"],
            skill["description"],
            tags_str,
            skill["ecosystem"],
            skill["repo_url"],
            skill["source_url"],
            skill["author"],
            skill["license"],
            skill.get("version"),
            1 if custom else 0,
            1 if local else 0,
        ),
    )


def _sync_fts_insert(conn: sqlite3.Connection, skill_id: str) -> None:
    conn.execute(
        """INSERT INTO skills_fts(rowid, id, title, description, tags)
           SELECT rowid, id, title, description, tags FROM skills WHERE id = ?""",
        (skill_id,),
    )


def _sync_fts_delete(conn: sqlite3.Connection, skill_id: str) -> None:
    row = conn.execute("SELECT rowid FROM skills WHERE id = ?", (skill_id,)).fetchone()
    if row:
        conn.execute("INSERT INTO skills_fts(skills_fts, rank) VALUES('delete', ?)", (row[0],))


def list_local_skills() -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM skills WHERE local = 1 ORDER BY title").fetchall()
        return [_row_to_skill(r) for r in rows]
    finally:
        conn.close()


def list_custom_skills() -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM skills WHERE custom = 1 ORDER BY title").fetchall()
        return [_row_to_skill(r) for r in rows]
    finally:
        conn.close()


def add_custom_skill(skill: dict) -> dict:
    validate_skill_id(skill["id"])
    if get_skill(skill["id"]):
        raise ValueError(f"Skill id already exists: {skill['id']}")

    custom = _load_custom_skills_file()
    custom.append(skill)
    _save_custom_skills_file(custom)

    conn = get_conn()
    try:
        _insert_skill_row(conn, skill, custom=True)
        _sync_fts_insert(conn, skill["id"])
        conn.commit()
    finally:
        conn.close()

    return {**skill, "custom": True, "local": False}


def delete_custom_skill(skill_id: str) -> bool:
    conn = get_conn()
    try:
        row = conn.execute("SELECT custom FROM skills WHERE id = ?", (skill_id,)).fetchone()
        if not row or not row["custom"]:
            return False
    finally:
        conn.close()

    custom = [s for s in _load_custom_skills_file() if s["id"] != skill_id]
    _save_custom_skills_file(custom)

    conn = get_conn()
    try:
        _sync_fts_delete(conn, skill_id)
        conn.execute("DELETE FROM skills WHERE id = ?", (skill_id,))
        conn.commit()
    finally:
        conn.close()

    return True


def get_skill_count() -> int:
    conn = get_conn()
    try:
        return conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
    finally:
        conn.close()


def get_skill(skill_id: str) -> Optional[dict]:
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM skills WHERE id = ?", (skill_id,)).fetchone()
        return _row_to_skill(row) if row else None
    finally:
        conn.close()


def list_skills(q: str = "", custom: Optional[bool] = None) -> list[dict]:
    conn = get_conn()
    try:
        if q.strip():
            tokens = _tokenize(q)
            if not tokens:
                rows = []
            else:
                fts_query = " OR ".join(tokens)
                try:
                    rows = conn.execute(
                        """SELECT s.* FROM skills s
                           JOIN skills_fts f ON s.id = f.id
                           WHERE skills_fts MATCH ?
                           ORDER BY rank LIMIT 50""",
                        (fts_query,),
                    ).fetchall()
                except sqlite3.OperationalError:
                    rows = []
        else:
            rows = conn.execute("SELECT * FROM skills ORDER BY title").fetchall()

        skills = [_row_to_skill(r) for r in rows]
        if custom is True:
            skills = [s for s in skills if s["custom"]]
        elif custom is False:
            skills = [s for s in skills if not s["custom"]]
        return skills
    finally:
        conn.close()


GENERIC_TAGS = frozenset({
    "cursor", "workflow", "planning", "skills", "rules", "documentation",
    "quality", "backend", "frontend", "api", "testing", "devops", "ui",
})


def search_skills(task: str) -> list[tuple[dict, float, list[str]]]:
    """Return (skill, score, matched_tags) ranked by relevance."""
    tokens = _tokenize(task)
    if not tokens:
        return []

    conn = get_conn()
    try:
        all_skills = conn.execute("SELECT * FROM skills").fetchall()
        results: list[tuple[dict, float, list[str]]] = []

        for row in all_skills:
            skill = _row_to_skill(row)
            tag_set = {t.lower() for t in skill["tags"]}
            title_lower = skill["title"].lower()
            desc_lower = skill["description"].lower()

            score = 0.0
            matched_tags: list[str] = []

            for token in tokens:
                if token in tag_set:
                    if token in GENERIC_TAGS:
                        score += 2.0
                    else:
                        score += 10.0
                        matched_tags.append(token)
                elif token in title_lower:
                    score += 5.0
                elif token in desc_lower:
                    score += 2.0

            if score <= 0:
                continue

            title_hit = any(token in title_lower for token in tokens)
            if not matched_tags and not title_hit:
                continue

            fts_query = " OR ".join(tokens)
            fts_row = conn.execute(
                """SELECT rank FROM skills_fts WHERE skills_fts MATCH ? AND id = ?""",
                (fts_query, skill["id"]),
            ).fetchone()
            if fts_row:
                score += abs(fts_row[0]) * 3.0

            results.append((skill, score, matched_tags))

        results.sort(key=lambda x: x[1], reverse=True)
        return results
    finally:
        conn.close()


def get_edges_for_skills(skill_ids: set[str]) -> list[dict]:
    if not skill_ids:
        return []
    conn = get_conn()
    try:
        placeholders = ",".join("?" * len(skill_ids))
        rows = conn.execute(
            f"""SELECT from_id, to_id, type FROM edges
                WHERE from_id IN ({placeholders}) AND to_id IN ({placeholders})""",
            list(skill_ids) + list(skill_ids),
        ).fetchall()
        return [{"from_id": r[0], "to_id": r[1], "type": r[2]} for r in rows]
    finally:
        conn.close()


def is_valid_skill_id(skill_id: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9-]+", skill_id)) and ".." not in skill_id


def local_skill_readme_path(skill_id: str) -> Optional[Path]:
    if not is_valid_skill_id(skill_id):
        return None
    readme = (SKILLS_DIR / skill_id / "README.md").resolve()
    skills_root = SKILLS_DIR.resolve()
    if skills_root not in readme.parents:
        return None
    return readme if readme.is_file() else None


def _row_to_skill(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "tags": row["tags"].split(),
        "ecosystem": row["ecosystem"],
        "repo_url": row["repo_url"],
        "source_url": row["source_url"],
        "author": row["author"],
        "license": row["license"],
        "version": row["version"],
        "custom": bool(row["custom"]),
        "local": bool(row["local"]),
    }


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    stop = {"a", "an", "the", "and", "or", "for", "to", "in", "on", "with", "using", "build", "make", "add", "create", "implement", "write", "set", "up"}
    return [w for w in words if w not in stop and len(w) > 1]


def slugify_id(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:64]


def validate_skill_id(skill_id: str) -> None:
    if not is_valid_skill_id(skill_id):
        raise ValueError("Skill id must use lowercase letters, numbers, and hyphens only")
