from typing import Dict, Optional
from app.domain.models.session import ProposalSession

class ProposalSessionManager:
    def __init__(self):
        self.sessions: Dict[str, ProposalSession] = {}

    def start_session(self, user_id: str) -> ProposalSession:
        # Encerra sessão anterior se já existir
        if user_id in self.sessions:
            self.sessions[user_id].status = "closed"
        session = ProposalSession(user_id)
        self.sessions[user_id] = session
        return session

    def get_session(self, user_id: str) -> Optional[ProposalSession]:
        return self.sessions.get(user_id)

    def end_session(self, user_id: str):
        if user_id in self.sessions:
            self.sessions[user_id].status = "closed"
            del self.sessions[user_id]
    
    def list_active_sessions(self):
        """Lista todas as sessões ativas"""
        return list(self.sessions.keys())
