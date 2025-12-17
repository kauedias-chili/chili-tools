import sys
import os
import time
from dotenv import load_dotenv
from crewai import Task, Crew, Process

# 1. Configuração essencial para Windows + PHP (evita erros de acentuação)
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Ajuste de caminho para encontrar o agents.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    from agents import create_agents # Importa a factory
except ImportError as e:
    print(f"Erro ao importar agentes: {e}")
    sys.exit(1)

def run_workflow(client, topic, website, gemini_key, ahrefs_key, drive_folder_id=None):
    # print(f"DEBUG: Iniciando para {client}...") # Comentado para limpar a saída do PHP
    
    # Cria os agentes dinamicamente
    auditor, planner, writer, manager = create_agents(gemini_key, ahrefs_key, drive_folder_id)

    # --- Definição das Tasks ---
    auditor_task = Task(
        description=f"Analise o público e concorrentes do site {website} para o tópico '{topic}'.",
        agent=auditor,
        expected_output="Relatório de contexto de público e concorrentes."
    )
    
    planner_task = Task(
        description="Com base no relatório do auditor, defina as melhores palavras-chave e a estrutura do artigo.",
        agent=planner,
        expected_output="Lista de palavras-chave e estrutura do artigo."
    )
    
    writer_task = Task(
        description="Com base na estrutura do planner, escreva o artigo seguindo o tom de voz da marca.",
        agent=writer,
        expected_output="Artigo completo redigido."
    )
    
    manager_task = Task(
        description="Revise o artigo do writer e valide se está pronto para publicação.",
        agent=manager,
        expected_output="Artigo revisado e aprovado para publicação."
    )

    # --- Execução da Crew ---
    crew = Crew(
        agents=[auditor, planner, writer, manager],
        tasks=[auditor_task, planner_task, writer_task, manager_task],
        verbose=True, # Útil para ver o log no PHP se der erro
        process=Process.sequential,
        
        # MODO DE SEGURANÇA: 3 RPM
        # Isso força o Python a esperar ~20s entre requisições.
        # É lento, mas evita o bloqueio da conta Free.
        max_rpm=3
    )
    
    result = crew.kickoff()
    return result

if __name__ == "__main__":
    # 2. Captura os dados enviados pelo comando shell_exec do PHP
    # 2. Captura os dados enviados pelo comando shell_exec do PHP
    # Ordem: script.py [1]Cliente [2]Topico [3]Site [4]GeminiKey [5]AhrefsKey [6]DriveFolderID (Opcional)
    if len(sys.argv) > 5:
        client_arg = sys.argv[1]
        topic_arg = sys.argv[2]
        website_arg = sys.argv[3]
        gemini_key_arg = sys.argv[4]
        ahrefs_key_arg = sys.argv[5]
        # Pega o arg 6 s existir, senão None
        drive_folder_arg = sys.argv[6] if len(sys.argv) > 6 else None
    else:
        # Defaults or Error - Forcing error if keys missing in prod context, but keeping safe for dev
        print("Erro: Chaves de API não fornecidas via argumentos.")
        sys.exit(1)

    try:
        # Executa o workflow
        resultado_final = run_workflow(client_arg, topic_arg, website_arg, gemini_key_arg, ahrefs_key_arg, drive_folder_arg)
        
        # 3. O print final é o que o PHP vai capturar e mostrar na tela
        print("\n--- INÍCIO DO CONTEÚDO ---\n")
        print(str(resultado_final))
        print("\n--- FIM DO CONTEÚDO ---")
        
    except BaseException as e:
        error_message = str(e)
        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            print("\n--- INÍCIO DO CONTEÚDO ---\n")
            print(f"""
⚠️ AVISO: A cota gratuita da API do Gemini foi excedida. 
Abaixo segue um RESULTADO FICTÍCIO (MOCK) para demonstração do fluxo:

# Estratégia de Conteúdo para: {topic_arg}
**Agente Auditor**: Análise concluída. O site {website_arg} tem oportunidades de crescimento em SEO.
**Agente Planner**: Palavras-chave sugeridas: Marketing, Estratégia, Vendas Online.

## Artigo Gerado (Simulação):

**Título: Como Dominar o {topic_arg} em 2025**

Introdução:
O mercado de {topic_arg} está em constante evolução. Para o cliente {client_arg}, focamos em resultados rápidos.

Corpo:
1. **Entenda seu público**: Essencial para conversão.
2. **Use dados**: A análise do {website_arg} mostrou potencial inexplorado.
3. **Automação**: O futuro é agora.

Conclusão:
Aplicando essas técnicas, o sucesso é garantido.

*(Fim do conteúdo gerado via fallback)*
            """)
            print("\n--- FIM DO CONTEÚDO ---")
        else:
            print(f"Erro Fatal na Execução: {e}")