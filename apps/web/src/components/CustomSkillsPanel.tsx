import { useEffect, useState } from "react";
import { addCustomSkill, deleteCustomSkill, listCustomSkills, listLocalSkills } from "../api";
import SkillSourceModal from "./SkillSourceModal";
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
  const [sourceModal, setSourceModal] = useState<{ id: string; title: string } | null>(null);

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
      <div className="custom-skills-head">
        <h2 className="section-title">Your skills</h2>
        <button type="button" className="btn secondary btn-sm" onClick={() => setOpen((v) => !v)}>
          {open ? "Cancel" : "Add custom skill"}
        </button>
      </div>

      <p className="custom-skills-note">
        Local packages in <code>skills/</code> are auto-discovered. Custom skills are saved via the UI.
      </p>

      {localSkills.length > 0 && (
        <>
          <h3 className="subsection-title">Local packages</h3>
          <ul className="custom-skills-list">
          {localSkills.map((skill) => (
            <li key={skill.id} className="custom-skill-row">
              <div>
                <strong>{skill.title}</strong>
                <span className="badge local">Local</span>
                <p className="custom-skill-desc">{skill.description}</p>
                <p className="custom-skill-tags">
                  <button
                    type="button"
                    className="link-btn"
                    onClick={() => setSourceModal({ id: skill.id, title: skill.title })}
                  >
                    README
                  </button>
                </p>
              </div>
            </li>
          ))}
          </ul>
        </>
      )}

      <h3 className="subsection-title">Custom skills</h3>
      {customSkills.length > 0 ? (
        <ul className="custom-skills-list">
          {customSkills.map((skill) => (
            <li key={skill.id} className="custom-skill-row">
              <div>
                <strong>{skill.title}</strong>
                <span className="badge custom">Custom</span>
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
        <p className="custom-skills-empty">No custom skills yet — add one or create a package under skills/.</p>
      )}

      {open && (
        <form className="custom-skill-form" onSubmit={handleAdd}>
          <label>
            Title
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="My Skill"
            />
          </label>
          <label>
            Description
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="What does this skill help with?"
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
            Source path or URL (optional)
            <input
              value={form.source_url}
              onChange={(e) => setForm({ ...form, source_url: e.target.value })}
              placeholder="my-skill/ or https://..."
            />
          </label>
          <button type="submit" className="btn primary" disabled={loading}>
            {loading ? "Saving…" : "Save custom skill"}
          </button>
        </form>
      )}

      {error && <p className="error">{error}</p>}

      {sourceModal && (
        <SkillSourceModal
          skillId={sourceModal.id}
          skillTitle={sourceModal.title}
          onClose={() => setSourceModal(null)}
        />
      )}
    </section>
  );
}
