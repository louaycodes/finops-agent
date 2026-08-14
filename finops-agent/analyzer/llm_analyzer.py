"""
Module LLM Analyzer — Analyzer Agent
Envoie les métriques à Groq et parse les anomalies détectées.
"""

import json
from groq import Groq


SYSTEM_PROMPT = """Tu es un expert FinOps spécialisé dans l'analyse des coûts AWS.
Tu reçois un résumé des métriques de coûts et d'utilisation d'un compte AWS.
Tu dois détecter les anomalies et inefficacités, et retourner UNIQUEMENT un JSON valide.

Format de réponse STRICT (rien d'autre que ce JSON) :
{
  "anomalies": [
    {
      "service": "nom du service AWS",
      "resource_id": "id de la ressource ou null",
      "type": "type d'anomalie (cost_spike, idle_resource, orphan_resource, oversized, runaway)",
      "severity": "High|Medium|Low",
      "description": "explication claire en français",
      "estimated_savings_usd": 0.0,
      "recommendation": "action concrète à prendre"
    }
  ],
  "total_anomalies": 0,
  "total_estimated_savings_usd": 0.0,
  "summary": "résumé global en une phrase"
}"""


def analyze(summary: dict, config: dict) -> dict:
    """
    Envoie le résumé des métriques à Groq et retourne les anomalies détectées.
    """
    llm_config = config["analyzer"]["llm"]
    api_key = llm_config["api_key"]
    model = llm_config["model"]
    max_tokens = llm_config["max_tokens"]

    client = Groq(api_key=api_key)

    user_message = f"""Voici les métriques AWS collectées :

{json.dumps(summary, indent=2, ensure_ascii=False)}

Analyse ces données et détecte toutes les anomalies de coûts et d'utilisation.
Retourne UNIQUEMENT le JSON demandé, sans texte avant ou après."""

    print("📡 Appel API Groq en cours...")

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
    print(f"DEBUG après think : {repr(content[:300])}")

    # Nettoyage backticks
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()

    result = json.loads(content)
    print(f"✅ Groq : {result.get('total_anomalies', 0)} anomalies détectées")
    return result