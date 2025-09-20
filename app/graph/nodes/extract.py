from typing import Dict, Any
from app.llm.bedrock_service import BedrockService
import json
import re

EXTRACT_SYS = """Você é um analista de soluções SÊNIOR.
Tarefa: Ler o assessment e extrair um resumo técnico estruturado.
REGRAS:
- Responda SOMENTE com JSON VÁLIDO (sem comentários, sem markdown).
- Nunca inclua texto fora do JSON.
- Use strings vazias, listas vazias ou objetos vazios quando algo não existir.

SCHEMA EXATO:
{
  "description": "string - descrição técnica clara do objetivo e do escopo, incluindo motivadores de negócio, restrições-chave e critérios de sucesso",
  "environments": ["dev|homolog|prod|..."],
  "volumetry": {
    "users": "int|unknown",
    "tps": "float|unknown",
    "tokens_in": "int|unknown",
    "tokens_out": "int|unknown",
    "data_volume": "string|unknown"
  },
  "integrations": ["sistema ou API externa (nome e função resumida)"],
  "constraints": ["restrições e premissas técnicas/organizacionais"],
  "risks": ["riscos técnicos relevantes (ex: latência, compliance, custos de inferência, SLAs)"],
  "assumptions": ["assunções razoáveis quando o texto for omisso (marcar como 'assumido')"],
  "out_of_scope": ["itens explicitamente fora do escopo"]
}

ESTILO:
- Sumarize e normalize nomes de sistemas.
- Se o assessment não trouxer algo, registre 'unknown' ou adicione uma 'assumption' marcada como 'assumido'.
"""

def _json_only(s: str) -> str:
    """Remove cercas de código e coleta apenas o bloco JSON."""
    s = s.strip()
    # Remove cercas ```json ... ``` ou ```
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.IGNORECASE | re.MULTILINE)
    # Heurística simples: pega do primeiro { ao último }
    start = s.find("{")
    end = s.rfind("}")
    return s[start:end+1] if start != -1 and end != -1 else s

class ExtractNode:
    def __init__(self, llm_service: BedrockService):
        self.llm = llm_service.get_llm()

    def run(self, assessment_text: str) -> Dict[str, Any]:
        prompt = f"{EXTRACT_SYS}\n---\nASSESSMENT:\n{assessment_text}\n---"
        result = self.llm.invoke(prompt)
        raw = _json_only(result.content or "")
        try:
            data = json.loads(raw)
        except Exception:
            data = {
                "description": "Resumo não estruturado a partir do assessment.",
                "environments": [],
                "volumetry": {"users":"unknown","tps":"unknown","tokens_in":"unknown","tokens_out":"unknown","data_volume":"unknown"},
                "integrations": [],
                "constraints": [],
                "risks": [],
                "assumptions": ["assumido: volumetria não informada"],
                "out_of_scope": []
            }

        data.setdefault("description", "")
        data.setdefault("environments", [])
        data.setdefault("volumetry", {})
        data.setdefault("integrations", [])
        data.setdefault("constraints", [])
        data.setdefault("risks", [])
        data.setdefault("assumptions", [])
        data.setdefault("out_of_scope", [])
        return data
