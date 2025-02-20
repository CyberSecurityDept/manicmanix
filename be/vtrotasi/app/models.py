from pydantic import BaseModel
from typing import List


class AddKeysRequest(BaseModel):
    keys: List[str]


class ScanFilesRequest(BaseModel):
    file_paths: List[str]
