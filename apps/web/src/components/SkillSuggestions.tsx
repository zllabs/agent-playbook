import type { Skill } from "../types";

interface Props {
  skills: Skill[];
}

export default function SkillSuggestions({ skills }: Props) {
  if (skills.length === 0) return null;

  return (
    <div className="suggestions">
      <p className="suggestions-label">Matching resources</p>
      <ul className="suggestions-list">
        {skills.map((skill) => (
          <li key={skill.id} className="suggestion-item">
            <span className="suggestion-title">{skill.title}</span>
            {skill.custom && <span className="badge saved">Saved</span>}
            {skill.local && <span className="badge bundled">Bundled</span>}
            <span className="suggestion-tags">{skill.tags.slice(0, 4).join(", ")}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
