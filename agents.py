from crewai import Agent
from crewai import LLM
import os
from dotenv import load_dotenv

def create_agents(gemini_api_key, ahrefs_api_key=None, drive_folder_id=None):
    # Inicializa o LLM com a chave fornecida
    gemini_llm = LLM(
        model='gemini/gemini-2.5-flash', 
        api_key=gemini_api_key,
        temperature=0.0
    )

    # Imports das Tools
    from tools.ahrefs_tool import AhrefsKeywordTool
    from tools.google_drive_tool import GoogleDriveLoaderTool
    from tools.google_docs_tool import GoogleDocsWriterTool
    from crewai_tools import ScrapeWebsiteTool

    # Instancia as Tools
    ahrefs_tool = AhrefsKeywordTool()
    drive_tool = GoogleDriveLoaderTool()
    docs_tool = GoogleDocsWriterTool()
    scrape_tool = ScrapeWebsiteTool()

    # 1. Audience & Market Auditor
    # Contexto específico para o Folder ID
    auditor_description = "Analisa o público-alvo e concorrentes."
    if drive_folder_id:
        auditor_description += f" VOCÊ DEVE USAR a ferramenta GoogleDriveLoaderTool para ler os arquivos da pasta ID: {drive_folder_id}."
    else:
        auditor_description += " (Aviso: Nenhum ID de pasta do Drive fornecido)."
    
    auditor_description += " VOCÊ TAMBÉM DEVE USAR a ferramenta ScrapeWebsiteTool para ler o site do cliente e entender seus produtos/serviços."

    auditor = Agent(
        name="Audience & Market Auditor",
        role="Strategist",
        description=auditor_description,
        goal="Ler os documentos do Drive E o site do cliente para criar um relatório detalhado de Persona, Dores e Concorrentes.",
        backstory="Você é um estrategista de conteúdo sênior. Você cruza dados internos (Drive) com dados públicos (Site) para uma análise completa.",
        tools=[drive_tool, scrape_tool],
        llm=gemini_llm
    )

    # 2. Keyword Planner
    planner = Agent(
        name="Keyword Planner",
        role="Researcher",
        description="Define estratégia de SEO Avançada. REGRAS OBRIGATÓRIAS: 1) Gerar EXATAMENTE 50 palavras-chave. 2) Aplicar método 'Query Fan-out'. 3) Distribuição de Intenção: 50% Comercial (Transacional), 50% Informativa. 4) Distribuição de Cauda: 30% Short-tail, 70% Mid/Long-tail. 5) Agrupar por Clusters Semânticos. VOCÊ DEVE USAR a ferramenta AhrefsKeywordTool para validar volume.",
        goal="Criar um Plano de Palavras-chave Clusterizado. OBRIGATÓRIO: O resultado final deve conter TABELAS MARKDOWN (colunas: Palavra-Chave, Vol, KD, Intenção, Tipo) para cada cluster.",
        backstory="Estrategista de SEO Sênior. Você é obcecado por organização. Você NÃO entrega listas com bullets, você entrega TABELAS MARKDOWN perfeitas.",
        tools=[ahrefs_tool],
        llm=gemini_llm
    )

    # 3. Content Writer
    writer = Agent(
        name="Content Writer",
        role="Executor",
        description="Produz o conteúdo conforme estratégia, SOPs e tom de voz. Pode consultar arquivos de referência.",
        goal="Redigir o artigo completo com base na estratégia, usando markdown perfeito. Valide informações técnicas no site do cliente se necessário.",
        backstory="Redator Copywriter. Você escreve textos engajadores, que seguem estritamente o tom de voz identificado pelo Auditor.",
        tools=[drive_tool, scrape_tool], # Acesso aos SOPs e Site
        llm=gemini_llm
    )

    # 4. Content Manager
    manager = Agent(
        name="Content Manager",
        role="Boss",
        description="Valida se o texto atende aos requisitos e publica no Google Docs.",
        goal="Garantir a qualidade final, revisar erros e OBRIGATORIAMENTE usar o GoogleDocsWriterTool para salvar o artigo final.",
        backstory="Editor Chefe. Você é chato com qualidade. Se estiver ruim, mande refazer. Se estiver bom, VOCÊ PUBLICA NO DOCS.",
        tools=[docs_tool], # Capaz de criar o doc final
        llm=gemini_llm
    )
    
    return auditor, planner, writer, manager