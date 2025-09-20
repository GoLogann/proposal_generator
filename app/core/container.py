from dependency_injector import containers, providers
from app.core.config import settings
from app.repositories.proposal_repository import LocalProposalRepository
from app.services.docx_renderer import DocxRenderer
from app.services.parsers import DocxTextParser
from app.graph.proposal_graph import ProposalGraph
from app.graph.nodes.extract import ExtractNode
from app.graph.nodes.plan import PlanNode
from app.graph.nodes.render import RenderNode
from app.llm.bedrock_service import BedrockService

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.proposal_router", 
            "app.api.proposal_chat_ws", 
            "app.api.upload_router",
            "app.api.proposal_chat_http",
            ]
        )

    # Infra básica
    proposal_repo = providers.Singleton(LocalProposalRepository, base_path=settings.STORAGE_BASE_PATH)
    renderer = providers.Singleton(DocxRenderer, template_path=settings.TEMPLATE_PATH)
    parser = providers.Singleton(DocxTextParser)

    # LLM (Bedrock)
    bedrock = providers.Singleton(BedrockService)

    # Nós do grafo
    extract_node = providers.Singleton(ExtractNode, llm_service=bedrock)
    plan_node = providers.Singleton(
        PlanNode,
        llm_service=bedrock,
        sp_to_hours=settings.SP_TO_HOURS,
        sprint_medium_hours=settings.SPRINT_MEDIUM_HOURS,
        sprint_small_hours=settings.SPRINT_SMALL_HOURS,
        hours_per_day=settings.HOURS_PER_DAY,
    )
    render_node = providers.Singleton(RenderNode, renderer=renderer, repo=proposal_repo)

    # Grafo principal
    proposal_graph = providers.Singleton(
        ProposalGraph,
        extract_node=extract_node,
        plan_node=plan_node,
        render_node=render_node,
    )
