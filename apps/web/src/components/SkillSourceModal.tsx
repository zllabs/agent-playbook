import { useEffect, useState } from "react";
import { fetchLocalSkillSource } from "../api";

interface Props {
  skillId: string;
  skillTitle: string;
  onClose: () => void;
}

export default function SkillSourceModal({ skillId, skillTitle, onClose }: Props) {
  const [body, setBody] = useState<string | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setBody(null);
    setError("");
    fetchLocalSkillSource(skillId).then((text) => {
      if (cancelled) return;
      if (text === null) {
        setError("Could not load skill README.");
        return;
      }
      setBody(text);
    });
    return () => {
      cancelled = true;
    };
  }, [skillId]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="source-overlay" onClick={onClose} role="presentation">
      <div
        className="source-panel"
        role="dialog"
        aria-labelledby="source-panel-title"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="source-panel-head">
          <h3 id="source-panel-title">{skillTitle}</h3>
          <button type="button" className="btn-text" onClick={onClose}>
            Close
          </button>
        </header>
        {error && <p className="error">{error}</p>}
        {!error && body === null && <p className="source-loading">Loading…</p>}
        {body && <pre className="source-body">{body}</pre>}
      </div>
    </div>
  );
}
