from docxtpl import DocxTemplate
from io import BytesIO
from typing import List
from app.domain.models.proposal import Deliverable

class DocxRenderer:
    def __init__(self, template_path: str):
        self.template_path = template_path

    def render(
        self,
        *,
        client: str,
        architect: str,
        description: str,
        dev_items: List[Deliverable],
        infra_items: List[Deliverable],
        out_of_scope: list[str],
        effort_label: str
    ) -> bytes:
        doc = DocxTemplate(self.template_path)
        ctx = {
            "cliente": client,
            "architect": architect,
            "descricao": description,
            "entregaveis_dev": [{"titulo": d.title, "sp": d.story_points or 0} for d in dev_items],
            "entregaveis_infra": [{"titulo": d.title, "sp": d.story_points or 0} for d in infra_items],
            "fora_do_escopo": out_of_scope,
            "esforco": effort_label,
        }
        doc.render(ctx)
        buf = BytesIO()
        doc.save(buf)
        return buf.getvalue()
