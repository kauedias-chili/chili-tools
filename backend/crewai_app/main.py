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
    # Cria os 6 agentes especializados
    auditor, strategist, architect, developer, auditor_seo, implementer = create_agents(gemini_key, ahrefs_key, drive_folder_id)

    # --- 1. Onboarding Task ---
    onboarding_task = Task(
        description=f"Realize o onboarding da marca para {website}. Use as ferramentas do Ahrefs para reportar o Domain Rating (DR) e as Top Pages atuais. Extraia persona, tom de voz e diferenciais.",
        agent=auditor,
        expected_output="Relatório de Onboarding incluindo Métricas Ahrefs (DR, Tráfego), Top Pages e Brand Persona."
    )
    
    # --- 2. Keyword Research Task ---
    keywords_task = Task(
        description=f"Pesquise 50 palavras-chave para '{topic}'. Use o Ahrefs Keyword Explorer para validar volume e KD. Mapeie clusters semânticos.",
        agent=strategist,
        expected_output="Tabela Markdown de 50 Palavras-Chave (Volume e KD validados via Ahrefs)."
    )
    
    # --- 3. Content Brief Task ---
    brief_task = Task(
        description="Crie um Content Brief matador usando o onboarding e as palavras-chave. Estruture H1, H2s e objetivos de conversão.",
        agent=architect,
        expected_output="Content Brief estruturado (H1, Seções, Keywords por Seção)."
    )
    
    # --- 4. Development Task ---
    content_task = Task(
        description="Desenvolva o conteúdo completo seguindo rigorosamente o Content Brief e o Onboarding da marca.",
        agent=developer,
        expected_output="Artigo completo redigido em Markdown."
    )

    # --- 5. On-page Audit Task ---
    audit_task = Task(
        description="Realize uma auditoria SEO On-page no artigo. Verifique densidade de termos, Title Tag e Meta Description sugeridas.",
        agent=auditor_seo,
        expected_output="Relatório de Auditoria SEO com checklist de melhorias e meta-dados."
    )
    
    # --- 6. Implementation Task ---
    implementation_task = Task(
        description="Consolide TUDO: O relatório de onboarding (com as métricas de DR e tráfego do Ahrefs), as palavras-chave, o brief, o artigo final e a auditoria SEO. Salve no Google Docs e imprima o conteúdo completo como saída final.",
        agent=implementer,
        expected_output="O documento completo consolidado em Markdown contendo todas as etapas, incluindo as métricas do Ahrefs."
    )

    # --- Execução da Crew ---
    crew = Crew(
        agents=[auditor, strategist, architect, developer, auditor_seo, implementer],
        tasks=[onboarding_task, keywords_task, brief_task, content_task, audit_task, implementation_task],
        verbose=True,
        process=Process.sequential,
        max_rpm=2
    )
    
    result = crew.kickoff()
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