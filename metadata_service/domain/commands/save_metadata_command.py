from dataclasses import dataclass
from diator.requests import Request

@dataclass(frozen=True, kw_only=True)
class SaveMetadataCommand(Request):
    title: str
    studio: str
    filename: str
    extension: str
