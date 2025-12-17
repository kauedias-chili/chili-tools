from crewai import Agent
from crewai import LLM
import os
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# MUDANÇA AQUI: Tiramos o "lite" e usamos o flash normal que é mais estável
gemini_llm = LLM(
    model='gemini/gemini-2.0-flash-exp', 
    api_key=gemini_api_key,
    temperature=0.0
)

# 1. Audience & Market Auditor
auditor = Agent(
    name="Audience & Market Auditor",
    role="Strategist",
    description="Analisa o público-alvo e concorrentes antes da produção de conteúdo.",
    goal="Gerar relatório de contexto de público e concorrentes.",
    backstory="Especialista em análise de mercado e audiência.",
    llm=gemini_llm
)

# 2. Keyword Planner
planner = Agent(
    name="Keyword Planner",
    role="Researcher",
    description="Define as melhores palavras-chave usando dados do Auditor e Ahrefs.",
    goal="Selecionar palavras-chave e estruturar o artigo.",
    backstory="Especialista em SEO e pesquisa de palavras-chave.",
    llm=gemini_llm
)

# 3. Content Writer
writer = Agent(
    name="Content Writer",
    role="Executor",
    description="Produz o conteúdo conforme estratégia, SOPs e tom de voz.",
    goal="Redigir o artigo completo com base na estratégia.",
    backstory="Especialista em redação e comunicação.",
    llm=gemini_llm
)

# 4. Content Manager
manager = Agent(
    name="Content Manager",
    role="Boss",
    description="Valida se o texto atende aos requisitos de qualidade e SEO.",
    goal="Garantir a qualidade e aprovação do conteúdo.",
    backstory="Especialista em revisão e gestão de conteúdo.",
    llm=gemini_llm
)