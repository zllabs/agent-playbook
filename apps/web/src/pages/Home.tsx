import { useEffect, useState } from "react";
import { recommend, searchSkills } from "../api";
import CustomSkillsPanel from "../components/CustomSkillsPanel";
import SkillSuggestions from "../components/SkillSuggestions";
import type { Playbook, Skill } from "../types";

const EXAMPLES = [
  "Build OAuth authentication using FastAPI",
  "Refine vague prompts before coding",
  "Add E2E tests for a React dashboard",
];

interface Props {
  onPlaybook: (p: Playbook) => void;
}

export default function Home({ onPlaybook }: Props) {
  const [task, setTask] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [suggestions, setSuggestions] = useState<Skill[]>([]);

  useEffect(() => {
    const q = task.trim();
    if (q.length < 2) {
      setSuggestions([]);
      return;
    }
    const timer = setTimeout(async () => {
      const results = await searchSkills(q);
      setSuggestions(results ? results.slice(0, 6) : []);
    }, 300);
    return () => clearTimeout(timer);
  }, [task]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = task.trim();
    if (!trimmed) return;
    setLoading(true);
    setError("");
    try {
      const pb = await recommend(trimmed);
      onPlaybook(pb);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page home">
      <header className="hero">
        <h1 className="brand">Agent Playbook</h1>
        <p className="tagline">Describe a task. Get a recommended Cursor skill Playbook.</p>
      </header>

      <form className="task-form" onSubmit={handleSubmit}>
        <textarea
          className="task-input"
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder="e.g. Build OAuth authentication using FastAPI"
          rows={4}
          autoFocus
        />
        <SkillSuggestions skills={suggestions} />
        <button type="submit" className="btn primary" disabled={loading || !task.trim()}>
          {loading ? "Assembling…" : "Assemble"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <div className="examples">
        <span className="examples-label">Try:</span>
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            type="button"
            className="chip"
            onClick={() => setTask(ex)}
          >
            {ex}
          </button>
        ))}
      </div>

      <CustomSkillsPanel />
    </div>
  );
}
