from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Skill(BaseModel):
    id: str
    title: str
    description: str
    tags: list[str]
    ecosystem: str
    repo_url: str
    source_url: str
    author: str
    license: Optional[str] = None
    version: Optional[str] = None
    custom: bool = False
    local: bool = False
    install_ides: Optional[list[str]] = None


class CreateCustomSkillRequest(BaseModel):
    title: str
    description: str
    tags: list[str]
    id: Optional[str] = None
    ecosystem: str = "cursor"
    repo_url: str = ""
    source_url: str = ""
    author: str = "You"
    license: str = "MIT"


class SkillWithReason(Skill):
    reason: str


class Edge(BaseModel):
    from_id: str
    to_id: str
    type: str


class PlaybookEdge(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: str = Field(alias="from", serialization_alias="from")
    to: str
    type: str


class Playbook(BaseModel):
    title: str
    task: str
    skills: list[SkillWithReason]
    edges: list[PlaybookEdge]
    generated_at: str


class InstallRequest(BaseModel):
    skills: list[SkillWithReason]
    target_dir: str = "."
    global_cli: bool = False
    scope: str = "project"  # project | user
    ide: str = "cursor"  # cursor | claude


class InstallResultItem(BaseModel):
    id: str
    status: str
    path: str = ""
    detail: str = ""


class InstallResponse(BaseModel):
    ide: str
    scope: str
    target: str
    install_root: str
    installed: int
    skipped: int = 0
    results: list[InstallResultItem]


class RecommendRequest(BaseModel):
    task: str


class HealthResponse(BaseModel):
    status: str
    skill_count: int
