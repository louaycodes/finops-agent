"""
Module LLM Recommender — Recommender Agent
Appelle Groq avec le contexte anomalies + prévisions et retourne
des recommandations FinOps structurées en JSON.
"""

import json
import os
from groq import Groq


SYSTEM_PROMPT = """Tu es un consultant FinOps AWS senior avec 10 ans d'expérience.
Tu reçois un rapport d'anomalies de coûts AWS détectées et une prévision budgétaire 30 jours.
Tu dois produire des recommandations d'optimisation concrètes et chiffrées.
Retourne UNIQUEMENT un JSON valide, sans aucun texte avant ou après.

Format de réponse STRICT (rien d'autre que ce JSON) :
{
  "recommendations": [
    {
      "action": "description précise de l'action à effectuer",
      "priority": "High|Medium|Low",
      "service": "nom du service AWS concerné",
      "estimated_savings_usd": 0.0,
      "implementation_delay": "délai estimé (ex: 1 jour, 1 semaine, 1 mois)"
    }
  ],
  "total_estimated_savings_usd": 0.0,
  "executive_summary": "résumé exécutif en 2-3 phrases pour un directeur financier"
}"""


def recommend(inputs: dict, config: dict) -> dict:
    """
    Envoie les anomalies + prévisions à Groq et retourne les recommandations.
    """
    llm_config = config["recommender"]["llm"]
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("Variable d'environnement GROQ_API_KEY non définie.")
    model = llm_config["model"]
    max_tokens = llm_config["max_tokens"]

    client = Groq(api_key=api_key)

    anomalies = inputs["anomalies"]
    forecast = inputs["forecast"]

    user_message = f"""Voici le rapport d'anomalies AWS détectées :

{json.dumps(anomalies, indent=2, ensure_ascii=False)}

Voici la prévision budgétaire pour les 30 prochains jours :

{json.dumps(forecast, indent=2, ensure_ascii=False)}

Sur la base de ces données, génère des recommandations FinOps concrètes et priorisées.
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
    nb = len(result.get("recommendations", []))
    savings = result.get("total_estimated_savings_usd", 0.0)
    print(f"✅ Groq : {nb} recommandations — économies estimées ${savings:.2f}")
    return result
