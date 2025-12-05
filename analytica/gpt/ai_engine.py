# ============================================
# ANALYSTIC.A — AI ENGINE (OLLAMA + GEMINI)
# 100% GRATUITO!
# ============================================
import os
import json
import httpx
from typing import Optional

# ============================================
# CONFIGURAÇÕES
# ============================================
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma:2b"  # Modelo local instalado

# Gemini 1.5 Flash API (gratuito com limite generoso)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


# ============================================
# OLLAMA (LOCAL - 100% GRÁTIS)
# ============================================
async def ollama_generate(prompt: str, model: str = OLLAMA_MODEL) -> Optional[str]:
    """
    Gera resposta usando Ollama local.
    Totalmente offline e gratuito!
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 1024
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                print(f"Ollama error: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"Ollama connection error: {e}")
        return None


def ollama_generate_sync(prompt: str, model: str = OLLAMA_MODEL) -> Optional[str]:
    """Versão síncrona do Ollama"""
    try:
        import requests
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1024
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        return None
        
    except Exception as e:
        print(f"Ollama sync error: {e}")
        return None


# ============================================
# GEMINI (GOOGLE - GRATUITO COM LIMITES)
# ============================================
async def gemini_generate(prompt: str) -> Optional[str]:
    """
    Gera resposta usando Google Gemini.
    Gratuito: 60 requisições/minuto
    """
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY não configurada")
        return None
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                json={
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topP": 0.9,
                        "maxOutputTokens": 1024
                    }
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
            else:
                print(f"Gemini error: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        print(f"Gemini error: {e}")
        return None


def gemini_generate_sync(prompt: str) -> Optional[str]:
    """Versão síncrona do Gemini"""
    if not GEMINI_API_KEY:
        return None
        
    try:
        import requests
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1024
                }
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"]
        return None
        
    except Exception as e:
        print(f"Gemini sync error: {e}")
        return None


# ============================================
# FUNÇÃO PRINCIPAL - TENTA OLLAMA, DEPOIS GEMINI
# ============================================
async def generate_ai_response(prompt: str, prefer_local: bool = True) -> dict:
    """
    Gera resposta usando IA disponível.
    Prioriza Ollama (local/gratuito), fallback para Gemini.
    
    Returns:
        dict: {"response": str, "source": str, "success": bool}
    """
    
    # Prompt otimizado para análise de dados
    system_prompt = """Você é o ANALYSTIC.IA, um assistente especializado em análise de dados.
Responda de forma clara, objetiva e em português brasileiro.
Use emojis para deixar as respostas mais visuais.
Foque em insights acionáveis e dados relevantes."""

    full_prompt = f"{system_prompt}\n\nUsuário: {prompt}\n\nAssistente:"
    
    if prefer_local:
        # Tenta Ollama primeiro (local, grátis, sem limites)
        response = await ollama_generate(full_prompt)
        if response:
            return {
                "response": response,
                "source": "🦙 Ollama (Local)",
                "model": OLLAMA_MODEL,
                "success": True
            }
        
        # Fallback para Gemini
        response = await gemini_generate(full_prompt)
        if response:
            return {
                "response": response,
                "source": "✨ Google Gemini",
                "model": "gemini-pro",
                "success": True
            }
    else:
        # Tenta Gemini primeiro
        response = await gemini_generate(full_prompt)
        if response:
            return {
                "response": response,
                "source": "✨ Google Gemini",
                "model": "gemini-pro",
                "success": True
            }
        
        # Fallback para Ollama
        response = await ollama_generate(full_prompt)
        if response:
            return {
                "response": response,
                "source": "🦙 Ollama (Local)",
                "model": OLLAMA_MODEL,
                "success": True
            }
    
    return {
        "response": "❌ Nenhuma IA disponível no momento. Verifique se o Ollama está rodando (ollama serve) ou configure a GEMINI_API_KEY.",
        "source": "Sistema",
        "model": None,
        "success": False
    }


def generate_insights(question: str) -> str:
    """
    Função compatível com o sistema existente.
    Usa versão síncrona.
    """
    # Tenta Ollama primeiro
    response = ollama_generate_sync(question)
    if response:
        return f"{response}\n\n🦙 _Gerado por Ollama ({OLLAMA_MODEL})_"
    
    # Tenta Gemini
    response = gemini_generate_sync(question)
    if response:
        return f"{response}\n\n✨ _Gerado por Google Gemini_"
    
    return "❌ IA não disponível. Execute: `ollama serve` para iniciar o Ollama."


# ============================================
# FUNÇÕES ESPECÍFICAS PARA ANÁLISE DE DADOS
# ============================================
async def analyze_data(data_description: str) -> dict:
    """Analisa dados e retorna insights"""
    prompt = f"""Analise os seguintes dados e forneça:
1. 📊 Resumo estatístico
2. 📈 Tendências identificadas
3. 💡 3 insights principais
4. ⚠️ Pontos de atenção
5. 🎯 Recomendações

Dados:
{data_description}"""
    
    return await generate_ai_response(prompt)


async def predict_trend(historical_data: str) -> dict:
    """Faz previsão baseada em dados históricos"""
    prompt = f"""Com base nos dados históricos abaixo, faça uma previsão para os próximos 3 meses:

{historical_data}

Forneça:
1. 🔮 Previsão de valores
2. 📊 Tendência esperada (crescimento/queda/estável)
3. 🎯 Nível de confiança
4. ⚠️ Fatores de risco"""
    
    return await generate_ai_response(prompt)


async def explain_chart(chart_description: str) -> dict:
    """Explica um gráfico para o usuário"""
    prompt = f"""Explique o seguinte gráfico de forma clara e didática:

{chart_description}

Inclua:
1. 📝 O que o gráfico mostra
2. 📈 Principais tendências
3. 💡 Insights importantes
4. 🎯 Conclusões práticas"""
    
    return await generate_ai_response(prompt)


async def suggest_visualization(data_type: str) -> dict:
    """Sugere o melhor tipo de visualização para os dados"""
    prompt = f"""Para os seguintes dados: {data_type}

Sugira:
1. 📊 Melhor tipo de gráfico
2. 🎨 Cores recomendadas
3. 📐 Layout ideal
4. 💡 Dicas de visualização"""
    
    return await generate_ai_response(prompt)


# ============================================
# CHAT CONVERSACIONAL
# ============================================
class AIChat:
    def __init__(self):
        self.history = []
        self.max_history = 10
    
    async def send_message(self, message: str) -> dict:
        """Envia mensagem mantendo contexto da conversa"""
        
        # Monta contexto com histórico
        context = "\n".join([
            f"{'Usuário' if i % 2 == 0 else 'IA'}: {msg}"
            for i, msg in enumerate(self.history[-6:])  # Últimas 3 trocas
        ])
        
        full_prompt = f"""Contexto da conversa:
{context}

Usuário: {message}

Responda de forma útil e contextualizada:"""
        
        response = await generate_ai_response(full_prompt)
        
        # Salva no histórico
        self.history.append(message)
        if response["success"]:
            self.history.append(response["response"])
        
        # Limita histórico
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history * 2:]
        
        return response
    
    def clear_history(self):
        """Limpa histórico da conversa"""
        self.history = []


# Instância global do chat
ai_chat = AIChat()
