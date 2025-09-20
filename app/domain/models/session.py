from typing import Optional, List, Dict
from uuid import uuid4

class ProposalSession:
    def __init__(self, user_id: str):
        self.id = str(uuid4())
        self.user_id = user_id
        self.client: Optional[str] = None
        self.architects: List[str] = []
        self.docs: Dict[str, str] = {}  # {doc_id: path}
        self.assessment_text: Optional[str] = None
        self.extracted: Optional[Dict] = None
        self.items = []
        self.totals = {}
        self.effort_label = ""
        self.adjustments: List[str] = []
        self.status = "collecting"  # collecting | scoping | closed
        self.doc_url: Optional[str] = None
