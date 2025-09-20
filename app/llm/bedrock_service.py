import logging
import os

from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable

from app.llm.base_langchain_service import BaseLangChainService


logger = logging.getLogger(__name__)

load_dotenv()

class BedrockService(BaseLangChainService):
    """
    Serviço para interagir com modelos de linguagem do Amazon Bedrock com integração Langfuse otimizada.
    """
    def get_llm(self):
        """
        Retorna o LLM puro (necessário para agentes).
        """
        try:
            return ChatBedrockConverse(
                credentials_profile_name=os.getenv("AWS_PROFILE"),
                region_name=os.getenv("AWS_REGION"),
                model_id=os.getenv("MODEL_ID"),
                temperature=float(os.getenv("TEMPERATURE", "0.7")),
            )
        except Exception as e:
            logger.error("Falha ao inicializar o LLM do Bedrock", exc_info=True)
            raise Exception(f"Falha ao inicializar o LLM do Bedrock: {str(e)}")


    def create_prompt(self, context: str = "") -> ChatPromptTemplate:
        """
        Cria um prompt com contexto customizado (usado em chains).
        """
        system_message = "Você é um assistente de IA prestativo e amigável."
        if context:
            system_message += f"\nUse o seguinte contexto para guiar sua resposta: {context}"

        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])

    def create_chain(self, context: str = "") -> Runnable:
        """
        Retorna um pipeline `prompt | llm`, usado para conversas diretas com histórico.
        NÃO use em agents.
        """
        return self.create_prompt(context) | self.get_llm()