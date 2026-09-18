from pydantic import BaseModel, Field


class AnalysisCreate(BaseModel):
    resume_id: int = Field(gt=0)
    job_id: int = Field(gt=0)
    include_ai: bool = True
