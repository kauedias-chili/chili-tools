import sys
import os
import time
from dotenv import load_dotenv
from crewai import Task, Crew, Process

# 1. Configuração essencial para Windows
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Ajuste de caminho para encontrar o agents.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    from agents import create_agents
except ImportError as e:
    print(f"Erro ao importar agentes: {e}")
    sys.exit(1)
def run_workflow(client, topic, website, gemini_key, ahrefs_key, drive_folder_id=None):
    # Cria os agentes (Mantive sua lógica original)
    auditor, strategist, architect, developer, auditor_seo, implementer = create_agents(gemini_key, ahrefs_key, drive_folder_id)

    # --- 1. Onboarding Task (A Fundação) ---
    onboarding_task = Task(
        description=f"""
        Analise a marca {website} profundamente. 
        1. Use a ferramenta do Ahrefs para extrair DR (Domain Rating) e as 5 Top Pages orgânicas.
        2. Defina a 'Brand Persona' e o Tom de Voz exato (ex: formal, divertido, técnico).
        3. Liste 3 diferenciais competitivos baseados no conteúdo atual.
        """,
        agent=auditor,
        expected_output="Relatório detalhado com Métricas Ahrefs, Persona, Tom de Voz e Diferenciais.",
        output_file="1_onboarding.md" # Salva o progresso
    )
    
    # --- 2. Keyword Research Task (Os Dados) ---
    keywords_task = Task(
        description=f"""
        Realize uma pesquisa de palavras-chave para o tópico: '{topic}'.
        1. Use o Ahrefs para encontrar 50 termos correlatos.
        2. Filtre APENAS palavras com Potencial de Tráfego > 100 e Dificuldade (KD) acessível para o DR do cliente.
        3. Agrupe em clusters semânticos (Intenção Informacional vs. Transacional).
        """,
        agent=strategist,
        context=[onboarding_task], # O estrategista precisa saber o DR do cliente (Task 1)
        expected_output="Tabela de 50 Palavras-Chave validadas com Volume, KD e Intenção de Busca.",
        output_file="2_keywords.md"
    )
    
    # --- 3. Content Brief Task (O Arquiteto) ---
    brief_task = Task(
        description="""
        Crie um Outline (Estrutura) estratégico para o artigo.
        1. H1: Deve ser magnético e incluir a keyword principal.
        2. H2s e H3s: Devem cobrir as dúvidas da Persona (Task 1) e usar as keywords secundárias (Task 2).
        3. Indique onde colocar Links Internos e CTAs (Chamadas para Ação).
        """,
        agent=architect,
        context=[onboarding_task, keywords_task], # Precisa da Persona e das Keywords
        expected_output="Estrutura de artigo (Outline) otimizada para SEO com orientações para o redator.",
        output_file="3_brief.md"
    )
    
    # --- 4. Development Task (A Execução) ---
    content_task = Task(
        description="""
        Escreva o artigo completo.
        REGRA DE OURO: Use EXATAMENTE o Tom de Voz definido no Onboarding (Task 1).
        1. Siga a estrutura do Brief (Task 3) à risca.
        2. O texto deve ser humano, fluido e evitar repetições robóticas.
        3. Use negrito nas partes importantes para escaneabilidade.
        """,
        agent=developer,
        context=[onboarding_task, brief_task], # O redator precisa do Tom de Voz e do Brief
        expected_output="Artigo completo, engajador e formatado em Markdown.",
        output_file="4_draft.md"
    )

    # --- 5. On-page Audit Task (O Auditor) ---
    audit_task = Task(
        description="""
        Atue como um Editor Chefe de SEO.
        1. Analise o artigo escrito (Task 4).
        2. Verifique se a Palavra-Chave principal aparece no H1, primeiro parágrafo e conclusão.
        3. Crie a Meta Title (máx 60 chars) e Meta Description (máx 155 chars) otimizadas.
        4. Se o texto estiver "robótico", indique pontos de melhoria.
        """,
        agent=auditor_seo,
        context=[keywords_task, content_task], # Compara o texto com as keywords alvo
        expected_output="Relatório de Aprovação com Meta Tags e Checklist de SEO verificado.",
        output_file="5_audit.md"
    )
    
    # --- 6. Implementation Task ---
    # Se não tiver drive_folder_id, o agente não conseguirá fazer o upload, mas gera o CSV localmente.
    drive_instructions = f"Fazer o upload de TODOS os arquivos (.md e .csv) para o Drive na pasta {drive_folder_id}." if drive_folder_id else "Arquivar os documentos localmente (Drive Folder ID não configurado)."
    
    implementation_task = Task(
        description=f"""
        Consolide o projeto final.
        1. Gere o arquivo CSV ('keywords.csv') a partir da tabela de palavras-chave (Task 2).
        2. {drive_instructions}
        3. Salve o artigo final (Task 4) no Google Docs.
        4. Imprima o conteúdo completo consolidado para o usuário ver.
        """,
        agent=implementer,
        context=[onboarding_task, keywords_task, content_task, audit_task],
        expected_output="Documento Final Consolidado contendo todas as etapas e confirmação de arquivamento.",
        output_file="FINAL_DELIVERY.md"
    )

    # --- Execução da Crew ---
    crew = Crew(
        agents=[auditor, strategist, architect, developer, auditor_seo, implementer],
        tasks=[onboarding_task, keywords_task, brief_task, content_task, audit_task, implementation_task],
        verbose=True,
        process=Process.sequential,
        max_rpm=2
    )
    
    result = crew.kickoff(inputs={'topic': topic, 'website': website, 'drive_folder_id': drive_folder_id or 'ROOT'})
    return result

if __name__ == "__main__":
    if len(sys.argv) > 5:
        client_arg = sys.argv[1]
        topic_arg = sys.argv[2]
        website_arg = sys.argv[3]
        gemini_key_arg = sys.argv[4]
        ahrefs_key_arg = sys.argv[5]
        drive_folder_arg = sys.argv[6] if len(sys.argv) > 6 else None
    else:
        print("Erro: Chaves de API não fornecidas via argumentos.")
        sys.exit(1)

    try:
        resultado_final = run_workflow(client_arg, topic_arg, website_arg, gemini_key_arg, ahrefs_key_arg, drive_folder_arg)
        
        print("\n--- INÍCIO DO CONTEÚDO ---\n")
        print(str(resultado_final))
        print("\n--- FIM DO CONTEÚDO ---")
        
    except BaseException as e:
        print(f"Erro Fatal na Execução: {e}")