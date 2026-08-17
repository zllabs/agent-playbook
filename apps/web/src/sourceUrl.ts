const PLAYBOOK_REPO = "https://github.com/zllabs/agent-playbook/tree/main";

export function resolveSourceUrl(sourceUrl: string, skillId?: string): string | null {
  if (!sourceUrl) return skillId ? `${PLAYBOOK_REPO}/skills/${skillId}` : null;
  if (sourceUrl.startsWith("http://") || sourceUrl.startsWith("https://")) {
    return sourceUrl;
  }
  const path = sourceUrl.replace(/^\//, "");
  return `${PLAYBOOK_REPO}/${path}`;
}
