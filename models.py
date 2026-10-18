from typing import Literal

from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    task: str = Field(description="A clear action to be completed.")
    owner: str = Field(description="Person responsible, or 'Not mentioned'.")
    due_date: str = Field(description="Deadline/date, or 'Not mentioned'.")
    priority: Literal["High", "Medium", "Normal"] = Field(
        description="Use High only when urgency is explicit; otherwise Medium or Normal."
    )


class MeetingNotes(BaseModel):
    title: str = Field(description="Short meeting title based only on the transcript.")
    one_line_summary: str = Field(description="One sentence describing the meeting outcome.")
    summary_points: list[str] = Field(description="3 to 5 concise summary bullets.")
    decisions: list[str] = Field(description="Decisions actually made in the meeting.")
    action_items: list[ActionItem] = Field(description="Concrete follow-up actions.")
    key_points: list[str] = Field(description="Important facts, blockers, risks, or discussion points.")
    next_meeting_focus: str = Field(
        description="What should be checked next, or 'Not mentioned' when unclear."
    )
