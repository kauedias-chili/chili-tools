from crewai import Agent
from crewai import LLM
import os
from dotenv import load_dotenv

def create_agents(gemini_api_key, ahrefs_api_key=None, drive_folder_id=None):
    # Inicializa o LLM com a chave fornecida
    # O Gemini 2.5 Flash é o melhor custo-benefício atual (Rápido e Inteligente)
    gemini_llm = LLM(
        model='gemini/gemini-2.5-flash', 
        api_key=gemini_api_key,
        temperature=0.2 # Um pouco de criatividade para o Writer
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

    # --- 1. Onboarding Auditor ---
    auditor = Agent(
        role="Onboarding & Brand Auditor",
        goal="Entender profundamente a identidade da marca, público-alvo e proposição de valor do site {website}.",
        backstory="""Você é especialista em branding e análise de mercado. Sua missão é extrair a 'alma' do negócio
        do cliente através do site fornecido e de documentos no Drive, garantindo que o tom de voz seja capturado.""",
        tools=[drive_tool, scrape_tool],
        llm=gemini_llm,
        verbose=True
    )

    # --- 2. SEO Strategist ---
    planner = Agent(
        role="SEO Strategist",
        goal="Realizar pesquisa de palavras-chave avançada (exatamente 50 termos) e clusterização semântica para {topic}.",
        backstory="""Você é um estrategista de SEO sênior. Você usa dados para identificar oportunidades de tráfego.
        Sua saída deve ser uma tabela Markdown organizada por clusters, com Volume, KD e Intenção.""",
        tools=[ahrefs_tool],
        llm=gemini_llm,
        verbose=True
    )

    # --- 3. Briefing Architect ---
    briefing_agent = Agent(
        role="Briefing Architect",
        goal="Transformar a estratégia de SEO e dados da marca em um Content Brief detalhado e estruturado.",
        backstory="""Você cria roteiros para escritores. Seu brief deve conter: Título Sugerido, Objetivo, 
        Público-alvo, Palavras-chave primárias/secundárias e uma estrutura detalhada de H1, H2 e H3.""",
        llm=gemini_llm,
        verbose=True
    )

    # --- 4. Content Developer ---
    writer = Agent(
        role="Content Developer",
        goal="Escrever um artigo de alta conversão e autoridade baseado estritamente no Content Brief fornecido.",
        backstory="""Você é um redator premiado. Você sabe como prender a atenção do leitor enquanto otimiza 
        para buscadores. Você usa os dados do site {website} para garantir precisão técnica.""",
        tools=[scrape_tool],
        llm=gemini_llm,
        verbose=True
    )

    # --- 5. SEO Quality Manager ---
    quality_manager = Agent(
        role="SEO Quality Manager",
        goal="Realizar um On-page Audit técnico no conteúdo desenvolvido, garantindo perfeição em SEO e legibilidade.",
        backstory="""Você é implacável. Você verifica densidade de palavras-chave, meta tags sugeridas, 
        tamanho dos parágrafos e se o tom de voz está alinhado com o onboarding.""",
        llm=gemini_llm,
        verbose=True
    )

    # --- 6. Implementation Manager ---
    implementation_agent = Agent(
        role="Implementation Manager",
        goal="Preparar o documento final e garantir a implementação/postagem no Google Docs.",
        backstory="""Você é o responsável final pela entrega. Você organiza o conteúdo, adiciona as notas de auditoria 
        e salva no Google Docs usando a ferramenta apropriada.""",
        tools=[docs_tool],
        llm=gemini_llm,
        verbose=True
    )

    return auditor, planner, briefing_agent, writer, quality_manager, implementation_agent