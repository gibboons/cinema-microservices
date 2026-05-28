from dataclasses import dataclass
from diator.requests import Request

@dataclass(frozen=True, kw_only=True)
class CreateTranscodingJobCommand(Request):
    title: str
    studio: str
