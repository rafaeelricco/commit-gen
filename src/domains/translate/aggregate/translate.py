from pydantic import BaseModel


class Translate(BaseModel):
    content: str
    target_language: str = "pt"
