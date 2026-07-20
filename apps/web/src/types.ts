export interface Skill {
  id: string;
  title: string;
  description: string;
  tags: string[];
  ecosystem: string;
  repo_url: string;
  source_url: string;
  author: string;
  license: string;
  version?: string | null;
  custom?: boolean;
  local?: boolean;
}

export interface CreateCustomSkillInput {
  title: string;
  description: string;
  tags: string[];
  id?: string;
  source_url?: string;
  author?: string;
  license?: string;
}

export interface SkillWithReason extends Skill {
  reason: string;
}

export interface PlaybookEdge {
  from: string;
  to: string;
  type: string;
}

export interface Playbook {
  title: string;
  task: string;
  skills: SkillWithReason[];
  edges: PlaybookEdge[];
  generated_at: string;
}
