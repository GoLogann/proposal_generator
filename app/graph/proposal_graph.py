from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph

class ProposalState(TypedDict):
    assessment_text: str
    client: str
    architect: str
    extracted: Dict[str, Any]
    items: List
    totals: Dict[str, int]
    effort_label: str
    result: Dict[str, str]

class ProposalGraph:
    def __init__(self, extract_node, plan_node, render_node):
        self.extract_node = extract_node
        self.plan_node = plan_node
        self.render_node = render_node
        self.graph = self._build()

    def _build(self):
        g = StateGraph(ProposalState)

        def node_extract(state: ProposalState):
            data = self.extract_node.run(state["assessment_text"])
            return {"extracted": data}

        def node_plan(state: ProposalState):
            data = state["extracted"]
            items, totals, label = self.plan_node.run(
                description=data.get("description", ""),
                integrations=data.get("integrations", []),
                constraints=data.get("constraints", [])
            )
            return {"items": items, "totals": totals, "effort_label": label}

        def node_render(state: ProposalState):
            pid, path = self.render_node.run(
                client=state["client"],
                architect=state["architect"],
                description=state["extracted"].get("description", ""),
                deliverables=state["items"],
                out_of_scope=state["extracted"].get("out_of_scope", []),
                effort_label=state["effort_label"]
            )
            return {"result": {"proposal_id": pid, "download_url": path}}

        g.add_node("extract", node_extract)
        g.add_node("plan", node_plan)
        g.add_node("render", node_render)
        g.set_entry_point("extract")
        g.add_edge("extract", "plan")
        g.add_edge("plan", "render")
        return g.compile()

    async def run(self, *, client: str, architect: str, assessment_text: str) -> dict:
        initial = {"client": client, "architect": architect, "assessment_text": assessment_text}
        out = await self.graph.ainvoke(initial)
        return out["result"]
