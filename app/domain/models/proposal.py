from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Deliverable:
    category: str   # "Desenvolvimento" | "Infraestrutura"
    title: str
    description: Optional[str] = None
    story_points: Optional[int] = None
    rationale: Optional[str] = None

@dataclass
class ProposalAggregate:
    client: str
    architect: str
    description: str
    deliverables: List[Deliverable] = field(default_factory=list)
    out_of_scope: List[str] = field(default_factory=list)
    totals: Dict[str, int] = field(default_factory=dict)  # sp_dev, sp_infra, sp_total, hours_total
    effort_label: str = ""
