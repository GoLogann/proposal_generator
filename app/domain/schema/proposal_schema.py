from pydantic import BaseModel
from typing import Optional

class GenerateProposalResponse(BaseModel):
    proposal_id: str
    download_url: str

class GenerateProposalForm(BaseModel):
    client: str
    architect: str
    include_default_oos: bool = True
