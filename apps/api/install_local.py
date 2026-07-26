"""Install playbook resources into Cursor or Claude Code dirs (local API host only)."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Literal
from urllib.parse import urlparse

import httpx

from sources import PLAYBOOK_REPO

ROOT = Path(__file__).resolve().parents[2]

GITHUB_BLOB = re.compile(
    r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/blob/(?P<branch>[^/]+)/(?P<path>.+)$"
)
GITHUB_TREE = re.compile(
    r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/tree/(?P<branch>[^/]+)/(?P<path>.*)$"
)

CURSOR_KIT_RAW = "https://raw.githubusercontent.com/duongductrong/cursor-kit/master"
CURSOR_KIT_REPO = "https://github.com/duongductrong/cursor-kit.git"

Scope = Literal["project", "user"]
Ide = Literal["cursor", "claude"]


def github_blob_to_raw(url: str) -> str | None:
    m = GITHUB_BLOB.match(url.strip())
    if not m:
        return None
    return (
        f"https://raw.githubusercontent.com/{m.group('owner')}/{m.group('repo')}/"
        f"{m.group('branch')}/{m.group('path')}"
    )


def parse_github_tree(url: str) -> tuple[str, str, str] | None:
    m = GITHUB_TREE.match(url.strip())
    if not m:
        return None
    repo = f"https://github.com/{m.group('owner')}/{m.group('repo')}.git"
    return repo, m.group("branch"), m.group("path").rstrip("/")


def _cursor_kit_parts(skill_id: str) -> tuple[str, str] | None:
    if skill_id.startswith("cursor-kit-cmd-"):
        return "command", skill_id.removeprefix("cursor-kit-cmd-") + ".md"
    if skill_id.startswith("cursor-kit-rule-"):
        return "rule", skill_id.removeprefix("cursor-kit-rule-") + ".md"
    if skill_id.startswith("cursor-kit-"):
        return "skill", skill_id.removeprefix("cursor-kit-")
    return None


def resolve_target(scope: Scope, target_dir: str = ".") -> Path:
    if scope == "user":
        return Path.home()
    path = Path(target_dir.strip() or ".").expanduser()
    if not path.is_absolute():
        # Relative to repo root — API cwd is apps/api under ./dev.sh
        path = (ROOT / path).resolve()
    else:
        path = path.resolve()
    return path


def install_root(target: Path, ide: Ide) -> Path:
    return target / (".cursor" if ide == "cursor" else ".claude")


def skill_matches_ide(skill: dict[str, Any], ide: Ide) -> bool:
    """Only install resources that belong to the selected IDE."""
    skill_id = skill.get("id") or ""
    if skill.get("local"):
        pkg = ROOT / "skills" / skill_id
        if ide == "cursor":
            return (pkg / "cursor").is_dir() or (pkg / "cursor" / "rule.mdc").is_file()
        return (pkg / "claude").is_dir() or (pkg / "claude" / "SKILL.md").is_file()
    if _cursor_kit_parts(skill_id):
        return ide == "cursor"
    eco = (skill.get("ecosystem") or "cursor").lower()
    if ide == "cursor":
        return eco == "cursor"
    return eco == "claude"


def _write_bytes(dest: Path, data: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)


def _write_text(dest: Path, text: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")


def _fetch(url: str) -> bytes:
    with httpx.Client(follow_redirects=True, timeout=60.0) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.content


def _cursor_kit_templates_dir(prefer_global_cli: bool) -> Path | None:
    if not prefer_global_cli:
        return None
    try:
        root = subprocess.check_output(
            ["npm", "root", "-g"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        tpl = Path(root) / "cursor-kit-cli" / "templates"
        if tpl.is_dir():
            return tpl
    except (OSError, subprocess.CalledProcessError):
        pass
    return None


def _sparse_copy(repo: str, branch: str, path: str, dest: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        repo_dir = Path(tmp) / "repo"
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                branch,
                "--filter=blob:none",
                "--sparse",
                repo,
                str(repo_dir),
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "sparse-checkout", "set", path],
            cwd=repo_dir,
            check=True,
            capture_output=True,
        )
        src = repo_dir / path
        if not src.exists():
            raise FileNotFoundError(f"sparse path missing: {path}")
        if dest.exists():
            shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)


def _install_cursor_kit(
    kind: str,
    name: str,
    target: Path,
    prefer_global_cli: bool,
) -> str:
    cursor = target / ".cursor"
    tpl = _cursor_kit_templates_dir(prefer_global_cli)

    if kind == "command":
        dest = cursor / "commands" / name
        if tpl and (tpl / "commands" / name).is_file():
            _write_bytes(dest, (tpl / "commands" / name).read_bytes())
        else:
            _write_bytes(dest, _fetch(f"{CURSOR_KIT_RAW}/.cursor/commands/{name}"))
        return str(dest)

    if kind == "rule":
        base = name.removesuffix(".md")
        dest = cursor / "rules" / f"{base}.mdc"
        if tpl and (tpl / "rules" / name).is_file():
            _write_text(dest, (tpl / "rules" / name).read_text(encoding="utf-8"))
        else:
            _write_bytes(dest, _fetch(f"{CURSOR_KIT_RAW}/.cursor/rules/{base}.mdc"))
        return str(dest)

    dest = cursor / "skills" / name
    if name == "swiftui-design":
        _sparse_copy(CURSOR_KIT_REPO, "master", "templates/skills/swiftui-design", dest)
        return str(dest)
    if tpl and (tpl / "skills" / name).is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(tpl / "skills" / name, dest)
        skill_md = dest / "SKILL.md"
        skill_mdc = dest / "SKILL.mdc"
        if skill_md.is_file() and not skill_mdc.exists():
            skill_md.rename(skill_mdc)
        return str(dest)
    _sparse_copy(CURSOR_KIT_REPO, "master", f".cursor/skills/{name}", dest)
    return str(dest)


def _install_local(skill: dict[str, Any], target: Path, ide: Ide) -> str:
    skill_id = skill["id"]
    pkg = ROOT / "skills" / skill_id
    if ide == "cursor":
        src = pkg / "cursor" / "rule.mdc"
        dest = target / ".cursor" / "rules" / f"{skill_id}.mdc"
        if src.is_file():
            _write_text(dest, src.read_text(encoding="utf-8"))
        else:
            raw = (
                f"{PLAYBOOK_REPO.replace('github.com', 'raw.githubusercontent.com')}/main/"
                f"skills/{skill_id}/cursor/rule.mdc"
            )
            _write_bytes(dest, _fetch(raw))
        return str(dest)

    src = pkg / "claude" / "SKILL.md"
    dest = target / ".claude" / "skills" / skill_id / "SKILL.md"
    if src.is_file():
        _write_text(dest, src.read_text(encoding="utf-8"))
    else:
        raw = (
            f"{PLAYBOOK_REPO.replace('github.com', 'raw.githubusercontent.com')}/main/"
            f"skills/{skill_id}/claude/SKILL.md"
        )
        _write_bytes(dest, _fetch(raw))
    return str(dest)


def _dest_for_blob(skill: dict[str, Any], raw_url: str, target: Path, ide: Ide) -> Path:
    skill_id = skill["id"]
    name = PurePosixPath(urlparse(raw_url).path).name
    if ide == "claude":
        if name.upper() == "SKILL.MD" or name.upper().startswith("SKILL"):
            return target / ".claude" / "skills" / skill_id / "SKILL.md"
        return target / ".claude" / "skills" / skill_id / name
    if name.endswith(".mdc") or "/rules-mdc/" in raw_url:
        return target / ".cursor" / "rules" / name
    if name.endswith(".md"):
        return target / ".cursor" / "commands" / name
    return target / ".cursor" / "rules" / f"{skill_id}-{name}"


def install_one(
    skill: dict[str, Any],
    target: Path,
    *,
    ide: Ide,
    prefer_global_cli: bool = False,
) -> dict[str, str]:
    skill_id = skill["id"]
    source = (skill.get("source_url") or "").strip()

    if not skill_matches_ide(skill, ide):
        return {
            "id": skill_id,
            "status": "skipped",
            "path": "",
            "detail": f"wrong ecosystem for {ide}",
        }

    ck = _cursor_kit_parts(skill_id)
    if ck:
        kind, name = ck
        path = _install_cursor_kit(kind, name, target, prefer_global_cli)
        return {"id": skill_id, "status": "installed", "path": path}

    if skill.get("local"):
        path = _install_local(skill, target, ide)
        return {"id": skill_id, "status": "installed", "path": path}

    raw = github_blob_to_raw(source) if source else None
    if raw:
        dest = _dest_for_blob(skill, raw, target, ide)
        _write_bytes(dest, _fetch(raw))
        return {"id": skill_id, "status": "installed", "path": str(dest)}

    tree = parse_github_tree(source) if source else None
    if tree:
        repo, branch, path = tree
        if ide == "claude":
            dest = target / ".claude" / "skills" / skill_id
        else:
            dest = target / ".cursor" / "skills" / skill_id
        _sparse_copy(repo, branch, path, dest)
        return {"id": skill_id, "status": "installed", "path": str(dest)}

    return {
        "id": skill_id,
        "status": "skipped",
        "path": "",
        "detail": source or "no install source",
    }


def install_skills(
    skills: list[dict[str, Any]],
    *,
    ide: Ide = "cursor",
    scope: Scope = "project",
    target_dir: str = ".",
    prefer_global_cli: bool = False,
) -> dict[str, Any]:
    target = resolve_target(scope, target_dir)
    target.mkdir(parents=True, exist_ok=True)
    root = install_root(target, ide)
    results: list[dict[str, str]] = []
    seen: set[str] = set()
    for skill in skills:
        sid = skill.get("id")
        if not sid or sid in seen:
            continue
        seen.add(sid)
        try:
            results.append(
                install_one(skill, target, ide=ide, prefer_global_cli=prefer_global_cli)
            )
        except Exception as e:  # ponytail: surface per-skill failures; continue rest
            results.append({"id": sid, "status": "error", "path": "", "detail": str(e)})
    installed = sum(1 for r in results if r["status"] == "installed")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    return {
        "ide": ide,
        "scope": scope,
        "target": str(target),
        "install_root": str(root),
        "installed": installed,
        "skipped": skipped,
        "results": results,
    }
