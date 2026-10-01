from pydantic import BaseModel, Field


class PromptGenerationRequest(BaseModel):
    prompt: str = Field(
        description="Natural language description of the dataset.",
    )
    rows: int | None = Field(
        default=None,
        gt=0,
        le=1_000_000,
    )



    # Generate a realistic synthetic HR dataset with 50000 employee records for employee attrition prediction including names, emails, phone numbers, departments, job roles, education, years of experience, joining dates, salaries, bonuses, performance ratings, annual performance reviews, manager feedback, promotion history, work-life balance scores, overtime status, remote work frequency, leave balance, employee satisfaction score, training hours, and attrition labels with realistic relationships between all fields.