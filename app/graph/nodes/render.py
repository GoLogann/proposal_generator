from app.domain.models.proposal import Deliverable
from app.repositories.proposal_repository import ProposalRepository
from app.services.docx_renderer import DocxRenderer

class RenderNode:
    def __init__(self, renderer: DocxRenderer, repo: ProposalRepository):
        self.renderer = renderer
        self.repo = repo

    def run(
        self,
        *,
        client: str,
        architect: str,
        description: str,
        deliverables: list[Deliverable],
        out_of_scope: list[str],
        effort_label: str
    ) -> tuple[str, str]:
        dev = [d for d in deliverables if d.category == "Desenvolvimento"]
        infra = [d for d in deliverables if d.category == "Infraestrutura"]

        content = self.renderer.render(
            client=client,
            architect=architect,
            description=description,
            dev_items=dev,
            infra_items=infra,
            out_of_scope=out_of_scope,
            effort_label=effort_label
        )
        return self.repo.save_docx(content)
