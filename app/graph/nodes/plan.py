from typing import List, Dict, Tuple
import statistics
import json
import re
from app.domain.models.proposal import Deliverable
from app.llm.bedrock_service import BedrockService

PLAN_SYS = """Você é um ARQUITETO DE SOFTWARE. Converta a descrição e contexto em um backlog
de ENTREGÁVEIS em DUAS categorias: "Desenvolvimento" e "Infraestrutura".
REGRAS:
- Responda SOMENTE com JSON válido no formato:
  {
    "dev": [{"title":"...","description":"..."}],
    "infra": [{"title":"...","description":"..."}]
  }
- Os títulos devem ser curtos, autoexplicativos e não duplicados.
- Inclua apenas itens pertinentes ao escopo descrito.
- Não invente integrações não mencionadas (a menos que marcadas como 'assumido').
"""

POKER_SYS = """Você é um time fazendo Planning Poker.
Para cada item, retorne SOMENTE um JSON array com objetos:
[{ "title": "...", "sp": 1|2|3|5|8|13, "rationale": "curto e objetivo" }]
Persona: {persona}. Seja consistente; não invente itens."""

def _json_only(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.IGNORECASE | re.MULTILINE)
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1:
        return s[start:end+1]
    start = s.find("[")
    end = s.rfind("]")
    return s[start:end+1] if start != -1 and end != -1 else s

class PlanNode:
    def __init__(
        self,
        llm_service: BedrockService,
        sp_to_hours: float,
        sprint_medium_hours: int,
        sprint_small_hours: int,
        hours_per_day: int = 6
    ):
        self.llm = llm_service.get_llm()
        self.sp_to_hours = sp_to_hours
        self.sprint_medium_hours = sprint_medium_hours
        self.sprint_small_hours = sprint_small_hours
        self.hours_per_day = hours_per_day

    def _backlog(self, description: str, integrations: list, constraints: list) -> List[Deliverable]:
        ctx = (
            f"{PLAN_SYS}\n"
            f"Descrição:\n{description}\n"
            f"Integrações:\n{integrations}\n"
            f"Restrições:\n{constraints}\n"
        )
        res = self.llm.invoke(ctx).content or ""
        raw = _json_only(res)
        try:
            data = json.loads(raw)
            dev = [Deliverable(category="Desenvolvimento", title=i["title"], description=i.get("description")) for i in data.get("dev", [])]
            infra = [Deliverable(category="Infraestrutura", title=i["title"], description=i.get("description")) for i in data.get("infra", [])]
            seen = set()
            ordered = []
            for d in dev + infra:
                if d.title not in seen:
                    ordered.append(d)
                    seen.add(d.title)
            return ordered
        except Exception:
            return [
                Deliverable("Desenvolvimento", "Orquestrador de agentes"),
                Deliverable("Desenvolvimento", "Agente de extração"),
                Deliverable("Desenvolvimento", "Agente de estimativa (Poker)"),
                Deliverable("Infraestrutura", "Infra as Code + deploy"),
            ]

    def _poker(self, items: List[Deliverable], persona: str) -> Dict[str, Dict]:
        ask = f"{POKER_SYS}".replace("{persona}", persona) + "\nItens:\n" + "\n".join([f"- {i.title}" for i in items])
        res = self.llm.invoke(ask).content or ""
        raw = _json_only(res)
        try:
            arr = json.loads(raw)
            return {x["title"]: {"sp": int(x["sp"]), "rationale": x.get("rationale", "")} for x in arr}
        except Exception:
            return {i.title: {"sp": 5, "rationale": f"{persona} fallback"} for i in items}

    def _medianize(self, items: List[Deliverable], p1, p2, p3) -> List[Deliverable]:
        out: List[Deliverable] = []
        for d in items:
            sps = [p[d.title]["sp"] for p in (p1, p2, p3) if d.title in p]
            d.story_points = int(statistics.median(sps or [5]))
            d.rationale = " | ".join([p[d.title]["rationale"] for p in (p1, p2, p3) if d.title in p])
            out.append(d)
        return out

    def _summarize(self, items: List[Deliverable]) -> Dict[str, int]:
        sp_dev = sum(d.story_points or 0 for d in items if d.category == "Desenvolvimento")
        sp_infra = sum(d.story_points or 0 for d in items if d.category == "Infraestrutura")
        sp_total = sp_dev + sp_infra
        hours_total = int(sp_total * self.sp_to_hours)
        days_total = (hours_total + self.hours_per_day - 1) // self.hours_per_day
        return {
            "sp_dev": sp_dev,
            "sp_infra": sp_infra,
            "sp_total": sp_total,
            "hours_total": hours_total,
            "days_total": days_total,
        }

    def _sprint_label(self, hours_total: int, totals: Dict[str, int]) -> str:
        medium = hours_total // self.sprint_medium_hours
        rem = hours_total % self.sprint_medium_hours
        small = 0
        if rem > 0:
            if rem <= self.sprint_small_hours:
                small = 1
            else:
                medium += 1
                
        parts = [
            f"Sprints previstas: {medium} sprint(s) média(s)" + (f" + {small} sprint pequena" if small else ""),
            f"Totais: {totals['sp_total']} SP (Dev: {totals['sp_dev']}, Infra: {totals['sp_infra']})",
            f"Esforço estimado: {totals['hours_total']} horas (~{totals['days_total']} dias úteis, capacidade {self.hours_per_day}h/dia)",
            "Observações: estimativas por Planning Poker (mediana entre cenários otimista/realista/pessimista), sem considerar impedimentos externos."
        ]
        return " | ".join(parts)

    def run(self, description: str, integrations: list, constraints: list) -> Tuple[List[Deliverable], Dict[str, int], str]:
        items = self._backlog(description, integrations, constraints)
        p_opt = self._poker(items, "otimista")
        p_real = self._poker(items, "realista")
        p_pes = self._poker(items, "pessimista")
        items_scored = self._medianize(items, p_opt, p_real, p_pes)
        totals = self._summarize(items_scored)
        effort_label = self._sprint_label(totals["hours_total"], totals)
        return items_scored, totals, effort_label
