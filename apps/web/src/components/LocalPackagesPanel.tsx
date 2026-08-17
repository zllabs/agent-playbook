import { useEffect, useMemo, useState } from "react";
import SkillSourceModal from "./SkillSourceModal";
import type { Skill } from "../types";

interface Props {
  skills: Skill[];
}

const SEARCH_THRESHOLD = 4;
const DEFAULT_OPEN_MAX = 2;

function matchesQuery(skill: Skill, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  const haystack = [
    skill.title,
    skill.description,
    skill.id,
    ...skill.tags,
  ]
    .join(" ")
    .toLowerCase();
  return haystack.includes(q);
}

function ideLabel(ide: string): string {
  return ide === "claude" ? "Claude" : "Cursor";
}

export default function LocalPackagesPanel({ skills }: Props) {
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState(skills.length <= DEFAULT_OPEN_MAX);
  const [sourceModal, setSourceModal] = useState<{ id: string; title: string } | null>(
    null,
  );

  useEffect(() => {
    setExpanded(skills.length <= DEFAULT_OPEN_MAX);
  }, [skills.length]);

  const filtered = useMemo(
    () => skills.filter((skill) => matchesQuery(skill, query)),
    [skills, query],
  );

  if (skills.length === 0) return null;

  function handleToggle(e: React.SyntheticEvent<HTMLDetailsElement>) {
    setExpanded(e.currentTarget.open);
  }

  return (
    <details className="local-packages" open={expanded} onToggle={handleToggle}>
      <summary className="local-packages-summary">
        <span className="local-packages-summary-text">
          Bundled skills
          <span className="local-packages-count">{skills.length}</span>
        </span>
        <span className="local-packages-summary-hint">
          {expanded ? "Installable · skills/" : "Expand to browse"}
        </span>
      </summary>

      <div className="local-packages-body">
        <p className="resource-section-intro">
          Full packages with Cursor rules and Claude skills — install from a playbook result.
        </p>
        {skills.length >= SEARCH_THRESHOLD && (
          <input
            type="search"
            className="local-packages-search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Filter bundled skills…"
            aria-label="Filter bundled skills"
          />
        )}

        {filtered.length === 0 ? (
          <p className="local-packages-empty">No bundled skills match “{query.trim()}”.</p>
        ) : (
          <ul className="local-packages-grid">
            {filtered.map((skill) => (
              <li key={skill.id} className="local-package-card">
                <div className="local-package-head">
                  <strong className="local-package-title">{skill.title}</strong>
                  {skill.install_ides && skill.install_ides.length > 0 && (
                    <span className="local-package-ides">
                      {skill.install_ides.map((ide) => (
                        <span key={ide} className="local-package-ide">
                          {ideLabel(ide)}
                        </span>
                      ))}
                    </span>
                  )}
                </div>
                <p className="local-package-desc">{skill.description}</p>
                {skill.tags.length > 0 && (
                  <p className="local-package-tags">{skill.tags.slice(0, 4).join(", ")}</p>
                )}
                <button
                  type="button"
                  className="link-btn local-package-readme"
                  onClick={() => setSourceModal({ id: skill.id, title: skill.title })}
                >
                  README
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {sourceModal && (
        <SkillSourceModal
          skillId={sourceModal.id}
          skillTitle={sourceModal.title}
          onClose={() => setSourceModal(null)}
        />
      )}
    </details>
  );
}
