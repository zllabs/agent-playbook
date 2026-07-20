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


class RecommendRequest(BaseModel):
    task: str


class HealthResponse(BaseModel):
    status: str
    skill_count: int
