from pydantic import BaseModel


class Answer(BaseModel):
    decision: str
    reason: str
