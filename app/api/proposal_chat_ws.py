from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.chat_handler import handle_message
from app.services.session_manager import ProposalSessionManager

router = APIRouter()
session_manager = ProposalSessionManager()

@router.websocket("/ws/chat-proposal/{user_id}")
async def chat_proposal(ws: WebSocket, user_id: str):
    await ws.accept()
    session = session_manager.start_session(user_id)

    try:
        await ws.send_json({
            "role": "system",
            "message": (
                "Bem-vindo ao assistente de propostas! 🎉\n\n"
                "Por favor:\n"
                "1. Informe os nomes dos arquitetos DNX\n"
                "2. Informe o nome do cliente\n"
                "3. Anexe o documento de assessment\n\n"
                "Depois disso, enviaremos um overview do assessment para começarmos os ajustes."
            )
        })

        while True:
            msg = await ws.receive_json()
            response = await handle_message(session, msg)
            if response:
                await ws.send_json(response)

    except WebSocketDisconnect:
        session_manager.end_session(user_id)
