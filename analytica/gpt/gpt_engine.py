# ============================================
# ANALYSTIC.A — GPT ENGINE
# Usa Ollama (local) + Gemini (cloud) GRÁTIS!
# ============================================

from gpt.ai_engine import (
    generate_insights as ai_generate_insights,
    ollama_generate_sync,
    gemini_generate_sync,
    generate_ai_response,
    analyze_data,
    predict_trend,
    ai_chat
)

def generate_insights(question: str) -> str:
    """
    Gera insights usando IA gratuita.
    Prioridade: Ollama (local) → Gemini (cloud)
    """
    return ai_generate_insights(question)
