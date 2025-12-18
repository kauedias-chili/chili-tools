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
    from tools.ahrefs_tool import AhrefsKeywordTool, AhrefsDomainStatsTool, AhrefsTopPagesTool
    from tools.google_drive_tool import GoogleDriveLoaderTool, GoogleDriveUploaderTool
    from tools.google_docs_tool import GoogleDocsWriterTool
    from tools.csv_tool import CSVGeneratorTool
    from crewai_tools import ScrapeWebsiteTool

    # Instancia as Tools
    ahrefs_kw = AhrefsKeywordTool()
    ahrefs_stats = AhrefsDomainStatsTool()
    ahrefs_top = AhrefsTopPagesTool()
    
    drive_loader = GoogleDriveLoaderTool()
    drive_uploader = GoogleDriveUploaderTool()
    docs_tool = GoogleDocsWriterTool()
    csv_tool = CSVGeneratorTool()
    scrape_tool = ScrapeWebsiteTool()

    # --- 1. Onboarding Auditor ---
    auditor = Agent(
        role="Onboarding & Brand Auditor",
        goal="Entender a identidade da marca e analisar a saúde atual do site {website} usando métricas do Ahrefs (DR, Tráfego) e Top Pages.",
        backstory="""Você é especialista em branding e análise técnica inicial. Sua missão é extrair a 'alma' do negócio
        e também reportar como o site {website} está performando hoje no Google (DR e páginas que mais trazem tráfego).""",
        tools=[drive_loader, scrape_tool, ahrefs_stats, ahrefs_top],
        llm=gemini_llm,
        verbose=True
    )

    # --- 2. SEO Strategist ---
    planner = Agent(
        role="SEO Strategist",
        goal="Realizar pesquisa de palavras-chave avançada e clusterização para {topic}, validando volumes no Ahrefs.",
        backstory="""Você é um estrategista de SEO sênior. Você usa o Ahrefs Keyword Explorer para validar se os termos 
        escolhidos têm volume real e KD aceitável. Sua saída deve ser uma tabela Markdown organizada.""",
        tools=[ahrefs_kw],
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
        goal="Consolidar a entrega final, gerar o CSV de palavras-chave e arquivar todos os documentos no Google Drive (Pasta: {drive_folder_id}).",
        backstory="""Você é o responsável final pela entrega. Sua missão é:
        1. Gerar o CSV das palavras-chave pesquisadas.
        2. Fazer o upload de TODOS os arquivos de progresso (.md) e do CSV para o Google Drive na pasta {drive_folder_id}.
        3. Salvar o artigo final no Google Docs.
        """,
        tools=[docs_tool, drive_uploader, csv_tool],
        llm=gemini_llm,
        verbose=True
    )

    return auditor, planner, briefing_agent, writer, quality_manager, implementation_agent