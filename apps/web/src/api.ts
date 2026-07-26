import catalog from "../../../data/catalog.json";
import { getLocalSkillReadme } from "./localSkills";
import type { CreateCustomSkillInput, Playbook, PlaybookEdge, Skill } from "./types";

const API = "/api";

const CATALOG_EDGES: PlaybookEdge[] = (catalog.edges ?? []).map((e) => ({
  from: e.from_id,
  to: e.to_id,
  type: e.type,
}));

function filterEdges(edges: PlaybookEdge[], ids: string[]): PlaybookEdge[] {
  const idSet = new Set(ids);
  return edges.filter((e) => idSet.has(e.from) && idSet.has(e.to));
}

function mergeEdges(edges: PlaybookEdge[], ids: string[]): PlaybookEdge[] {
  const idSet = new Set(ids);
  const seen = new Map<string, PlaybookEdge>();
  for (const edge of edges) {
    if (!idSet.has(edge.from) || !idSet.has(edge.to)) continue;
    seen.set(`${edge.from}|${edge.to}|${edge.type}`, edge);
  }
  return [...seen.values()];
}

export async function recommend(task: string): Promise<Playbook> {
  const res = await fetch(`${API}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? "Failed to assemble playbook");
  }
  return res.json();
}

export async function searchSkills(q: string): Promise<Skill[] | null> {
  if (!q.trim()) return [];
  const res = await fetch(`${API}/skills?q=${encodeURIComponent(q)}`);
  if (!res.ok) return null;
  return res.json();
}

export async function fetchLocalSkillSource(id: string): Promise<string | null> {
  const bundled = getLocalSkillReadme(id);
  if (bundled) return bundled;
  const res = await fetch(
    `${API}/local-skills/${encodeURIComponent(id)}/source?format=text`,
  );
  if (!res.ok) return null;
  return res.text();
}

export async function listLocalSkills(): Promise<Skill[]> {
  const res = await fetch(`${API}/local-skills`);
  if (!res.ok) return [];
  return res.json();
}

export async function listCustomSkills(): Promise<Skill[]> {
  const res = await fetch(`${API}/custom-skills`);
  if (!res.ok) return [];
  return res.json();
}

export async function addCustomSkill(input: CreateCustomSkillInput): Promise<Skill> {
  const res = await fetch(`${API}/custom-skills`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(typeof err.detail === "string" ? err.detail : "Failed to add skill");
  }
  return res.json();
}

export async function deleteCustomSkill(id: string): Promise<void> {
  const res = await fetch(`${API}/custom-skills/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(typeof err.detail === "string" ? err.detail : "Failed to delete skill");
  }
}

export async function getEdges(
  ids: string[],
  fallback: PlaybookEdge[] = [],
): Promise<PlaybookEdge[]> {
  if (ids.length === 0) return [];
  const kept = filterEdges(fallback, ids);
  const fromCatalog = filterEdges(CATALOG_EDGES, ids);
  const res = await fetch(`${API}/edges?ids=${encodeURIComponent(ids.join(","))}`);
  if (!res.ok) return mergeEdges([...kept, ...fromCatalog], ids);
  const fetched: PlaybookEdge[] = await res.json();
  return mergeEdges([...kept, ...fromCatalog, ...fetched], ids);
}

export function downloadPlaybook(playbook: Playbook) {
  const blob = new Blob([JSON.stringify(playbook, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "playbook.json";
  a.click();
  URL.revokeObjectURL(url);
}

export interface InstallResponse {
  ide: string;
  scope: string;
  target: string;
  install_root: string;
  installed: number;
  skipped: number;
  results: { id: string; status: string; path: string; detail?: string }[];
}

export async function installPlaybook(
  playbook: Playbook,
  options: {
    targetDir?: string;
    globalCli?: boolean;
    scope?: "project" | "user";
    ide?: "cursor" | "claude";
  } = {},
): Promise<InstallResponse> {
  const res = await fetch(`${API}/playbook/install`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      skills: playbook.skills,
      target_dir: options.targetDir ?? ".",
      global_cli: options.globalCli ?? false,
      scope: options.scope ?? "project",
      ide: options.ide ?? "cursor",
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    if (res.status === 404) {
      throw new Error(
        "Install API not found — restart the API (./dev.sh). Port 8000 may still be an old process.",
      );
    }
    throw new Error(typeof err.detail === "string" ? err.detail : "Install failed");
  }
  return res.json();
}
