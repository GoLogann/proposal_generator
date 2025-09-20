import re
import os
from app.core.config import settings
from app.services.parsers import DocxTextParser
from app.core.container import Container

async def handle_message(session, msg: dict):
    if session.status == "collecting":
        if msg["type"] == "user":
            content = msg["message"]

            # Extrair arquitetos e cliente
            arqs_match = re.search(r"arquiteto[s]?: (.+?)(;|, cliente|$)", content, re.I)
            cli_match = re.search(r"cliente[: ]+(.+)", content, re.I)

            if arqs_match:
                session.architects = [a.strip() for a in re.split(r",|;", arqs_match.group(1))]
            if cli_match:
                session.client = cli_match.group(1).strip()

            # Verifica se doc_id foi enviado agora
            doc_id = msg.get("doc_id")
            if doc_id:
                upload_dir = os.path.join(settings.STORAGE_BASE_PATH, "uploads")
                files = [f for f in os.listdir(upload_dir) if f.startswith(doc_id)]
                if not files:
                    return {"role": "system", "message": "❌ Documento não encontrado."}

                doc_path = os.path.join(upload_dir, files[0])
                session.docs[doc_id] = doc_path

                with open(doc_path, "rb") as f:
                    raw = f.read()

                parser = DocxTextParser()
                session.assessment_text = parser.to_text(raw)

                extract = Container.extract_node()
                session.extracted = extract.run(session.assessment_text)

                session.status = "scoping"
                return {
                    "role": "assistant",
                    "message": (
                        f"📄 Assessment processado!\n\n"
                        f"- Cliente: {session.client or 'não informado'}\n"
                        f"- Arquitetos: {', '.join(session.architects) if session.architects else 'não informado'}\n"
                        f"- Descrição: {session.extracted['description']}\n"
                        f"- Ambientes: {session.extracted['environments']}\n"
                        f"- Integrações: {session.extracted['integrations']}\n"
                        f"- Restrições: {session.extracted['constraints']}\n"
                        f"- Fora do escopo: {session.extracted['out_of_scope']}\n\n"
                        "Agora podemos detalhar o escopo. O que deseja ajustar?"
                    )
                }
            else:
                return {"role": "system", "message": "⚠️ Nenhum documento anexado. Faça upload e envie o doc_id ao menos uma vez."}

    elif session.status == "scoping":
        if msg["type"] == "user":
            content = msg["message"].lower()

            # Fechamento do escopo
            if any(k in content for k in ["fechar escopo", "gerar proposta", "não desejo ajuste"]):
                if not session.extracted:
                    return {"role": "system", "message": "❌ Não há assessment processado nesta sessão."}

                plan = Container.plan_node()
                render = Container.render_node()

                items, totals, effort_label = plan.run(
                    description=session.extracted["description"],
                    integrations=session.extracted["integrations"],
                    constraints=session.extracted["constraints"],
                )

                pid, path = render.run(
                    client=session.client or "Cliente não informado",
                    architect=", ".join(session.architects) if session.architects else "Arquiteto não informado",
                    description=session.extracted["description"],
                    deliverables=items,
                    out_of_scope=session.extracted.get("out_of_scope", []),
                    effort_label=effort_label,
                )

                session.status = "closed"
                session.doc_url = path

                return {
                    "role": "assistant",
                    "message": (
                        f"✅ Escopo fechado e proposta gerada!\n\n"
                        f"- Proposta ID: {pid}\n"
                        f"- Esforço estimado: {effort_label}\n"
                        f"📥 Baixe o documento final no link abaixo:"
                    ),
                    "download_url": path,
                }

            session.adjustments.append(msg["message"])
            return {
                "role": "assistant",
                "message": f"Ajuste registrado: {msg['message']}\nDiga 'fechar escopo' quando quiser gerar a proposta."
            }

    elif session.status == "closed":
        return {
            "role": "system",
            "message": "Sessão já encerrada. Abra uma nova sessão para outra proposta."
        }
