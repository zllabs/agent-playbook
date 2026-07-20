const readmeModules = import.meta.glob("../../../skills/*/README.md", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;

function skillIdFromPath(path: string): string | null {
  const match = path.match(/\/skills\/([^/]+)\/README\.md$/);
  return match ? match[1] : null;
}

const LOCAL_SKILL_IDS = new Set<string>();
for (const path of Object.keys(readmeModules)) {
  const id = skillIdFromPath(path);
  if (id) LOCAL_SKILL_IDS.add(id);
}

export function isLocalSkill(skill: { id: string; local?: boolean }): boolean {
  return Boolean(skill.local) || LOCAL_SKILL_IDS.has(skill.id);
}

export function getLocalSkillReadme(skillId: string): string | null {
  for (const [path, content] of Object.entries(readmeModules)) {
    if (skillIdFromPath(path) === skillId) return content;
  }
  return null;
}
