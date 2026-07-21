import { useEffect, useMemo, useRef, useState } from "react";
import { downloadPlaybook, getEdges, searchSkills } from "../api";
import SkillGraph from "../components/SkillGraph";
import SkillSourceModal from "../components/SkillSourceModal";
import { isLocalSkill } from "../localSkills";
import { resolveSourceUrl } from "../sourceUrl";
import type { Playbook, Skill, SkillWithReason } from "../types";

interface Props {
  playbook: Playbook;
  onReset: () => void;
}

export default function Result({ playbook, onReset }: Props) {
  const [focusedId, setFocusedId] = useState<string | null>(null);
  const [addedSkills, setAddedSkills] = useState<SkillWithReason[]>([]);
  const [included, setIncluded] = useState<Set<string>>(
    () => new Set(playbook.skills.map((s) => s.id)),
  );
  const [catalogEdges, setCatalogEdges] = useState(playbook.edges);
  const [addQuery, setAddQuery] = useState("");
  const [addResults, setAddResults] = useState<Skill[]>([]);
  const [addSearching, setAddSearching] = useState(false);
  const [addSearchState, setAddSearchState] = useState<"idle" | "empty" | "duplicate" | "error">(
    "idle",
  );
  const [sourceModal, setSourceModal] = useState<{ id: string; title: string } | null>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const catalogEdgesRef = useRef(playbook.edges);
  catalogEdgesRef.current = catalogEdges;

  const addedIds = useMemo(() => new Set(addedSkills.map((s) => s.id)), [addedSkills]);

  useEffect(() => {
    setAddedSkills([]);
    setIncluded(new Set(playbook.skills.map((s) => s.id)));
    setCatalogEdges(playbook.edges);
    setAddQuery("");
    setAddResults([]);
    setAddSearching(false);
    setAddSearchState("idle");
  }, [playbook]);

  const allSkills = useMemo(() => {
    const seen = new Set<string>();
    const out: SkillWithReason[] = [];
    for (const skill of [...playbook.skills, ...addedSkills]) {
      if (!seen.has(skill.id)) {
        seen.add(skill.id);
        out.push(skill);
      }
    }
    return out;
  }, [playbook.skills, addedSkills]);

  const includedIds = useMemo(
    () => allSkills.filter((s) => included.has(s.id)).map((s) => s.id),
    [allSkills, included],
  );

  useEffect(() => {
    if (includedIds.length === 0) {
      setCatalogEdges([]);
      return;
    }
    let cancelled = false;
    getEdges(includedIds, catalogEdgesRef.current).then((edges) => {
      if (!cancelled) setCatalogEdges(edges);
    });
    return () => {
      cancelled = true;
    };
  }, [includedIds.join(",")]);

  const filteredPlaybook = useMemo(
    () => ({
      ...playbook,
      skills: allSkills.filter((s) => included.has(s.id)),
      edges: catalogEdges,
    }),
    [playbook, allSkills, included, catalogEdges],
  );

  useEffect(() => {
    const q = addQuery.trim();
    if (q.length < 2) {
      setAddResults([]);
      setAddSearching(false);
      setAddSearchState("idle");
      return;
    }
    setAddSearching(true);
    setAddSearchState("idle");
    const timer = setTimeout(async () => {
      const results = await searchSkills(q);
      if (results === null) {
        setAddResults([]);
        setAddSearching(false);
        setAddSearchState("error");
        return;
      }
      const existing = new Set(allSkills.map((s) => s.id));
      const filtered = results.filter((s) => !existing.has(s.id)).slice(0, 8);
      setAddResults(filtered);
      setAddSearching(false);
      if (filtered.length === 0) {
        setAddSearchState(results.length > 0 ? "duplicate" : "empty");
      } else {
        setAddSearchState("idle");
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [addQuery, allSkills]);

  function handleNodeSelect(id: string) {
    setFocusedId(id);
    const el = listRef.current?.querySelector(`[data-skill-id="${id}"]`);
    el?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function toggleSkill(id: string) {
    setIncluded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function addSkill(skill: Skill) {
    setAddedSkills((prev) => [
      ...prev,
      { ...skill, reason: "Added by you to this playbook." },
    ]);
    setIncluded((prev) => new Set(prev).add(skill.id));
    setAddResults((prev) => prev.filter((s) => s.id !== skill.id));
    setAddSearchState("idle");
  }

  const empty = allSkills.length === 0;

  return (
    <div className="page result">
      <header className="result-header">
        <div>
          <p className="brand-sm">Agent Playbook</p>
          <h1 className="playbook-title">{playbook.title}</h1>
          <p className="task-echo">{playbook.task}</p>
        </div>
      </header>

      {empty ? (
        <div className="empty-state">
          <p>No strong matches — try fewer words, different stack terms, or add skills below.</p>
        </div>
      ) : (
        <>
          <section className="skills-section">
            <h2 className="section-title">Recommended resources</h2>
            <p className="skills-hint">Uncheck to exclude from export and graph.</p>
            <ul className="skill-list" ref={listRef}>
              {allSkills.map((skill) => {
                const local = isLocalSkill(skill);
                const sourceHref = local ? null : resolveSourceUrl(skill.source_url, skill.id);
                const checked = included.has(skill.id);
                const isAdded = addedIds.has(skill.id);
                return (
                  <li
                    key={skill.id}
                    data-skill-id={skill.id}
                    className={`skill-row${focusedId === skill.id ? " focused" : ""}${checked ? "" : " excluded"}`}
                    onMouseEnter={() => setFocusedId(skill.id)}
                  >
                    <label className="skill-check">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleSkill(skill.id)}
                      />
                      <span className="sr-only">Include {skill.title}</span>
                    </label>
                    <div className="skill-body">
                      <div className="skill-head">
                        <strong>{skill.title}</strong>
                        {isAdded && <span className="badge added">Added</span>}
                        {skill.custom && <span className="badge custom">Custom</span>}
                        {local && <span className="badge local">Local</span>}
                        {skill.license && <span className="license">{skill.license}</span>}
                      </div>
                      <p className="skill-reason">{skill.reason}</p>
                      <p className="skill-meta">
                        <span>{skill.author}</span>
                        {local ? (
                          <button
                            type="button"
                            className="link-btn"
                            onClick={() => setSourceModal({ id: skill.id, title: skill.title })}
                          >
                            Source
                          </button>
                        ) : sourceHref ? (
                          <a href={sourceHref} target="_blank" rel="noreferrer">
                            Source
                          </a>
                        ) : (
                          <span>{skill.source_url}</span>
                        )}
                      </p>
                    </div>
                  </li>
                );
              })}
            </ul>
          </section>

          <SkillGraph playbook={filteredPlaybook} onNodeSelect={handleNodeSelect} />
        </>
      )}

      <section className="add-skill-section">
        <h2 className="section-title">Add a resource</h2>
        <p className="skills-hint">Search the catalog and add resources to expand your playbook.</p>
        <input
          className="add-skill-input"
          type="search"
          value={addQuery}
          onChange={(e) => setAddQuery(e.target.value)}
          placeholder="e.g. playwright, stripe, graphql"
        />
        {addSearching && <p className="add-skill-hint">Searching…</p>}
        {!addSearching && addSearchState === "empty" && (
          <p className="add-skill-empty">No skills found for “{addQuery.trim()}”.</p>
        )}
        {!addSearching && addSearchState === "duplicate" && (
          <p className="add-skill-empty">Matching skills are already in your playbook.</p>
        )}
        {!addSearching && addSearchState === "error" && (
          <p className="add-skill-empty">Search unavailable — check that the API is running.</p>
        )}
        {addResults.length > 0 && (
          <ul className="add-skill-results">
            {addResults.map((skill) => (
              <li key={skill.id}>
                <button type="button" className="add-skill-btn" onClick={() => addSkill(skill)}>
                  + {skill.title}
                </button>
                <span className="add-skill-tags">{skill.tags.slice(0, 4).join(", ")}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <footer className="result-footer">
        <button
          type="button"
          className="btn primary"
          disabled={filteredPlaybook.skills.length === 0}
          onClick={() => downloadPlaybook(filteredPlaybook)}
        >
          Export JSON ({filteredPlaybook.skills.length})
        </button>
        <button type="button" className="btn secondary" onClick={onReset}>
          New task
        </button>
      </footer>

      {sourceModal && (
        <SkillSourceModal
          skillId={sourceModal.id}
          skillTitle={sourceModal.title}
          onClose={() => setSourceModal(null)}
        />
      )}
    </div>
  );
}
