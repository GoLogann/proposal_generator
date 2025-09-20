import os, uuid
from abc import ABC, abstractmethod

class ProposalRepository(ABC):
    @abstractmethod
    def save_docx(self, content: bytes) -> tuple[str, str]:
        ...

class LocalProposalRepository(ProposalRepository):
    def __init__(self, base_path: str):
        self.base = base_path
        os.makedirs(self.base, exist_ok=True)

    def save_docx(self, content: bytes) -> tuple[str, str]:
        pid = str(uuid.uuid4())
        path = os.path.join(self.base, f"{pid}.docx")
        with open(path, "wb") as f: f.write(content)
        return pid, path
