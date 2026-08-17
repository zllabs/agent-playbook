import { useEffect, useState } from "react";
import { addCustomSkill, deleteCustomSkill, listCustomSkills, listLocalSkills } from "../api";
import LocalPackagesPanel from "./LocalPackagesPanel";
import type { Skill } from "../types";

interface Props {
  onChange?: () => void;
}

const EMPTY = { title: "", description: "", tags: "", source_url: "" };

export default function CustomSkillsPanel({ onChange }: Props) {
  const [localSkills, setLocalSkills] = useState<Skill[]>([]);
  const [customSkills, setCustomSkills] = useState<Skill[]>([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function refresh() {
    const [local, custom] = await Promise.all([listLocalSkills(), listCustomSkills()]);
    setLocalSkills(local);
    setCustomSkills(custom);
    onChange?.();
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    const tags = form.tags.split(",").map((t) => t.trim()).filter(Boolean);
    if (!form.title.trim() || !form.description.trim() || tags.length === 0) {
      setError("Title, description, and at least one tag are required.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      await addCustomSkill({
        title: form.title.trim(),
        description: form.description.trim(),
        tags,
        source_url: form.source_url.trim() || undefined,
      });
      setForm(EMPTY);
      setOpen(false);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add skill");
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string) {
    setError("");
    try {
      await deleteCustomSkill(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete skill");
    }
  }

  return (
    <section className="custom-skills">
      <h2 className="section-title">Your catalog</h2>
      <p className="custom-skills-note">
        Two ways to extend what Agent Playbook can recommend:{" "}
        <strong>bundled skills</strong> are full installable packages under{" "}
        <code>skills/</code>; <strong>saved entries</strong> are lightweight bookmarks you add
        here (metadata only — good for external rules you want in search).
      </p>

      <LocalPackagesPanel skills={localSkills} />

      <div className="catalog-entries-head">
        <div>
          <h3 className="subsection-title">Saved entries</h3>
          <p className="resource-section-intro">
            Title, description, and tags for personal bookmarks. Optional source URL for attribution.
          </p>
        </div>
        <button type="button" className="btn secondary btn-sm" onClick={() => setOpen((v) => !v)}>
          {open ? "Cancel" : "Add saved entry"}
        </button>
      </div>

      {customSkills.length > 0 ? (
        <ul className="custom-skills-list">
          {customSkills.map((skill) => (
            <li key={skill.id} className="custom-skill-row">
              <div>
                <strong>{skill.title}</strong>
                <span className="badge saved">Saved</span>
                <p className="custom-skill-desc">{skill.description}</p>
                <p className="custom-skill-tags">{skill.tags.join(", ")}</p>
              </div>
              <button
                type="button"
                className="btn-text danger"
                onClick={() => handleDelete(skill.id)}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="custom-skills-empty">
          No saved entries yet — add a bookmark, or create an installable package under{" "}
          <code>skills/</code>.
        </p>
      )}

      {open && (
        <form className="custom-skill-form" onSubmit={handleAdd}>
          <p className="custom-skill-form-intro">
            Saved entries appear in search and playbooks. They are not installable unless you provide
            a fetchable source URL.
          </p>
          <label>
            Title
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="My team's API testing rule"
            />
          </label>
          <label>
            Description
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="What does this resource help with?"
              rows={2}
            />
          </label>
          <label>
            Tags (comma-separated)
            <input
              value={form.tags}
              onChange={(e) => setForm({ ...form, tags: e.target.value })}
              placeholder="python, testing, api"
            />
          </label>
          <label>
            Source URL (optional)
            <input
              value={form.source_url}
              onChange={(e) => setForm({ ...form, source_url: e.target.value })}
              placeholder="https://github.com/.../rule.mdc"
            />
          </label>
          <button type="submit" className="btn primary" disabled={loading}>
            {loading ? "Saving…" : "Save entry"}
          </button>
        </form>
      )}

      {error && <p className="error">{error}</p>}
    </section>
  );
}
