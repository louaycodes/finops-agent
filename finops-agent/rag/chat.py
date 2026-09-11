"""
Module Chat — RAG Agent
Prend une question et le contexte ChromaDB, appelle Groq avec un system prompt
"assistant FinOps AWS", retourne la réponse en langage naturel.
"""

import json
import os
from groq import Groq


SYSTEM_PROMPT = """Tu es un assistant FinOps AWS expert et pédagogue.
Tu aides les équipes Cloud à comprendre et optimiser leurs coûts AWS.
Tu reçois des extraits de rapports FinOps (anomalies, prévisions, recommandations)
et tu réponds aux questions en t'appuyant UNIQUEMENT sur ces informations.
Si l'information n'est pas dans le contexte fourni, dis-le clairement.
Réponds en français, de manière concise et actionnable."""


def chat(question: str, context: str, config: dict) -> str:
    """
    Envoie la question + contexte à Groq et retourne la réponse en langage naturel.
    """
    llm_config = config["rag"]["llm"]
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("Variable d'environnement GROQ_API_KEY non définie.")
    model = llm_config["model"]
    max_tokens = llm_config["max_tokens"]

    client = Groq(api_key=api_key)

    user_message = f"""Voici les informations FinOps disponibles :

{context}

---
Question : {question}

Réponds en te basant uniquement sur le contexte ci-dessus."""

    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    content = response.choices[0].message.content.strip()

    # Supprimer le bloc <think>...</think> si présent
    if "<think>" in content:
        content = content.split("</think>")[-1].strip()

    return content
