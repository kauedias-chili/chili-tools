from flask import Flask, render_template_string, request, jsonify
import subprocess
import os
import sys
import threading
import uuid
import time

# Configuração de caminhos dinâmica (Compatível com Windows e Linux/Render)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(BASE_DIR, 'backend', 'crewai_app', 'main.py')

if not os.path.exists(SCRIPT_PATH):
    # Tenta caminho alternativo
    SCRIPT_PATH = os.path.join(BASE_DIR, 'main.py')

if not os.path.exists(SCRIPT_PATH):
    print(f"❌ ERRO CRÍTICO: main.py não encontrado em {SCRIPT_PATH}")

if not SCRIPT_PATH:
    print("❌ ERRO CRÍTICO: Não encontrei o arquivo main.py em lugar nenhum!")
    print("Pastas verificadas:")
    for p in possible_paths:
        print(f" - {p}")

app = Flask(__name__)

# Memória temporária para armazenar o status das tarefas
# { 'task_id': { 'status': 'running', 'result': None, 'error': None } }
tasks_db = {}

# --- (O resto do HTML continua igual, apenas resumido aqui) ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chili Tools | AI Studio</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --bg-color: #050505;
            --card-bg: rgba(20, 20, 20, 0.6);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #ffffff;
            --text-secondary: #9ca3af;
            --accent-color: #00ff9d;
            --accent-glow: rgba(0, 255, 157, 0.2);
            --danger-color: #ff4d4d;
            --input-bg: rgba(255, 255, 255, 0.03);
            --gradient-1: linear-gradient(135deg, #00ff9d 0%, #00b8ff 100%);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; }
        
        body { 
            background-color: var(--bg-color); 
            color: var(--text-primary); 
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(0, 255, 157, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(0, 184, 255, 0.05) 0%, transparent 40%);
            padding: 2rem;
        }

        .container {
            width: 100%;
            max-width: 900px;
        }

        .brand-header {
            text-align: center;
            margin-bottom: 3rem;
            position: relative;
        }

        .brand-badge {
            background: rgba(0, 255, 157, 0.1);
            color: var(--accent-color);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            border: 1px solid rgba(0, 255, 157, 0.2);
            display: inline-block;
            margin-bottom: 1rem;
            backdrop-filter: blur(10px);
        }

        .brand-title {
            font-size: 3rem;
            font-weight: 700;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -1px;
        }

        .brand-subtitle {
            color: var(--text-secondary);
            font-size: 1.1rem;
            font-weight: 300;
        }

        .main-card { 
            background: var(--card-bg); 
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border-color); 
            border-radius: 24px;
            padding: 3rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            position: relative;
            overflow: hidden;
        }

        .main-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
            opacity: 0.5;
        }

        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .form-group { margin-bottom: 1.5rem; }
        .form-group.full-width { grid-column: span 2; }
        
        .form-label { 
            display: block; 
            font-size: 0.85rem; 
            color: var(--text-secondary); 
            margin-bottom: 0.5rem; 
            font-weight: 500;
        }
        
        .form-control { 
            width: 100%; 
            background: var(--input-bg); 
            border: 1px solid var(--border-color); 
            color: var(--text-primary); 
            padding: 1rem 1.25rem;
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--accent-color);
            background: rgba(0, 255, 157, 0.05);
            box-shadow: 0 0 0 4px rgba(0, 255, 157, 0.1);
        }

        .result-box { 
            margin-top: 2rem;
            background: #000; 
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            font-family: 'JetBrains Mono', 'Fira Code', monospace; 
            font-size: 0.85rem;
            line-height: 1.6;
            color: #d4d4d8;
            white-space: pre-wrap; 
            display: none;
            overflow-x: auto;
        }

        /* Table Styling */
        .markdown-body table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
        .markdown-body th, .markdown-body td { 
            border: 1px solid var(--border-color); 
            padding: 0.75rem; 
            text-align: left; 
        }
        .markdown-body th { background: rgba(0, 255, 157, 0.05); color: var(--accent-color); }

        .spinner {
            display: none;
            margin: 1.5rem auto 0;
            width: 24px;
            height: 24px;
            border: 3px solid rgba(16, 185, 129, 0.3);
            border-radius: 50%;
            border-top-color: var(--accent-color);
            animation: spin 1s ease-in-out infinite;
        }

        .actions {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }

        .btn {
            flex: 1;
            padding: 1.25rem;
            border: none;
            border-radius: 14px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: var(--accent-color);
            color: #000;
            box-shadow: 0 4px 20px var(--accent-glow);
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px var(--accent-glow);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }

        /* Result Section */
        #resultContainer {
            margin-top: 3rem;
            border-top: 1px solid var(--border-color);
            padding-top: 2rem;
            display: none;
            animation: fadeIn 0.5s ease;
        }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .progress-steps {
            display: flex;
            justify-content: space-between;
            margin-bottom: 2rem;
            position: relative;
        }

        .progress-steps::before {
            content: '';
            position: absolute;
            top: 50%; left: 0; right: 0;
            height: 2px;
            background: var(--border-color);
            z-index: 0;
            transform: translateY(-50%);
        }

        .step {
            position: relative;
            z-index: 1;
            background: var(--bg-color);
            border: 2px solid var(--border-color);
            width: 40px; text-align: center;
            height: 40px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            color: var(--text-secondary);
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }

        .step.active {
            border-color: var(--accent-color);
            background: var(--bg-color);
            color: var(--accent-color);
            box-shadow: 0 0 15px var(--accent-glow);
        }
        
        .step.completed {
            background: var(--accent-color);
            border-color: var(--accent-color);
            color: #000;
        }

        .result-content {
            background: rgba(0,0,0,0.3);
            border-radius: 16px;
            padding: 2rem;
            border: 1px solid var(--border-color);
        }

        .markdown-body {
            color: #d4d4d8;
            line-height: 1.7;
        }

        .tip-box {
            margin-top: 2rem;
            padding: 1.5rem;
            background: rgba(0, 255, 157, 0.03);
            border: 1px dashed rgba(0, 255, 157, 0.2);
            border-radius: 12px;
            display: none;
            animation: fadeIn 0.5s ease;
        }

        .tip-header {
            font-size: 0.75rem;
            color: var(--accent-color);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .tip-content {
            font-size: 0.9rem;
            color: var(--text-secondary);
            font-style: italic;
        }
        
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {
            color: var(--text-primary);
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .markdown-body strong { color: var(--accent-color); }
        .markdown-body ul { padding-left: 1.5rem; margin-bottom: 1rem; }

        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="brand-header">
            <span class="brand-badge">Agentic AI Powered</span>
            <h1 class="brand-title">Chili Tools</h1>
            <p class="brand-subtitle">Orquestração de Agentes Autônomos de Marketing</p>
        </div>

        <div class="main-card">
            <form id="aiForm">
                <div class="form-grid">
                    <div class="form-group full-width">
                         <div style="display: flex; align-items: center; justify-content: space-between;">
                             <label class="form-label">CHAVES DE API</label>
                             <span style="font-size: 0.75rem; color: var(--accent-color);">*Necessário apenas para execução real</span>
                         </div>
                    </div>
                    <div class="form-group">
                        <input type="password" class="form-control" name="gemini_key" placeholder="Gemini API Key">
                    </div>
                    <div class="form-group">
                        <input type="password" class="form-control" name="ahrefs_key" placeholder="Ahrefs API Key (Opcional)">
                    </div>

                    <div class="form-group full-width" style="height: 1px; background: var(--border-color); margin: 0.5rem 0 1.5rem 0;"></div>

                    <div class="form-group full-width">
                        <label class="form-label">Nome do Cliente</label>
                        <input type="text" class="form-control" name="cliente" value="Cliente Teste" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Tópico</label>
                        <input type="text" class="form-control" name="topico" value="Marketing B2B" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Website</label>
                        <input type="text" class="form-control" name="site" value="exemplo.com.br" required>
                    </div>
                </div>

                <div class="actions">
                    <button type="button" class="btn btn-secondary" id="btnDemo">
                        <i class="fa-solid fa-bolt"></i> Ver Demonstração
                    </button>
                    <button type="submit" class="btn btn-primary" id="btnRun">
                        <i class="fa-solid fa-play"></i> Iniciar Agentes
                    </button>
                </div>
            </form>

            <div id="resultContainer">
                <div class="progress-steps">
                    <div class="step" id="step1" title="Onboarding Auditor"><i class="fa-solid fa-id-card"></i></div>
                    <div class="step" id="step2" title="SEO Strategist"><i class="fa-solid fa-search-plus"></i></div>
                    <div class="step" id="step3" title="Briefing Architect"><i class="fa-solid fa-drafting-compass"></i></div>
                    <div class="step" id="step4" title="Content Developer"><i class="fa-solid fa-pen-nib"></i></div>
                    <div class="step" id="step5" title="SEO Quality Audit"><i class="fa-solid fa-spell-check"></i></div>
                    <div class="step" id="step6" title="Implementation"><i class="fa-solid fa-cloud-upload-alt"></i></div>
                </div>

                <div class="result-content">
                    <div id="loadingText" style="text-align: center; color: var(--text-secondary); margin-bottom: 1rem;">
                        <i class="fa-solid fa-circle-notch fa-spin"></i> Inicializando agentes...
                    </div>
                    
                    <div id="tipBox" class="tip-box">
                        <div class="tip-header"><i class="fa-solid fa-lightbulb"></i> SEO Pro-Tip</div>
                        <div id="tipContent" class="tip-content">Carregando dicas valiosas...</div>
                    </div>

                    <div id="outputContent" class="markdown-body"></div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        const seoTips = [
            "A palavra-chave primária deve aparecer nos primeiros 10% do seu conteúdo.",
            "Links internos ajudam o Google a entender a estrutura e autoridade do seu site.",
            "O tempo de carregamento da página é um fator crítico para o ranking mobile.",
            "Use tabelas e listas (como esta!) para aumentar suas chances de ganhar Featured Snippets.",
            "A Meta Description não afeta o ranking diretamente, mas melhora muito o seu CTR (clique).",
            "Conteúdo focado na Experiência do Usuário (E-E-A-T) é a prioridade do Google em 2025.",
            "H2s e H3s otimizados ajudam o leitor e os bots a escanearem o seu artigo.",
            "Otimize imagens com Alt Text descritivo para aparecer no Google Imagens."
        ];

        function rotateTips() {
            let i = 0;
            $('#tipBox').fadeIn();
            const interval = setInterval(() => {
                if ($('#outputContent').is(':empty')) {
                    $('#tipContent').fadeOut(400, function() {
                        $(this).text(seoTips[i]).fadeIn(400);
                        i = (i + 1) % seoTips.length;
                    });
                } else {
                    clearInterval(interval);
                    $('#tipBox').hide();
                }
            }, 6000);
            $('#tipContent').text(seoTips[0]);
        }

        // Função para simular progresso visual (Atualizada para 6 estágios)
        function simulateProgress(speed = 2000) {
            const steps = ['step1', 'step2', 'step3', 'step4', 'step5', 'step6'];
            let current = 0;
            
            // Ativa o primeiro
            $('#'+steps[0]).addClass('active');
            $('#loadingText').html('<i class="fa-solid fa-spinner fa-spin"></i> Onboarding Auditor analisando site...');
            
            rotateTips();

            const interval = setInterval(() => {
                $('#'+steps[current]).removeClass('active').addClass('completed');
                current++;
                
                if (current < steps.length) {
                    $('#'+steps[current]).addClass('active');
                    const msgs = [
                        'SEO Strategist definindo keywords...', 
                        'Briefing Architect montando roteiro...', 
                        'Content Developer redigindo artigo...', 
                        'SEO Quality Audit revisando on-page...',
                        'Implementation enviando para o Docs...'
                    ];
                    $('#loadingText').html(`<i class="fa-solid fa-spinner fa-spin"></i> ${msgs[current-1]}`);
                } else {
                    clearInterval(interval);
                    $('#loadingText').html('<i class="fa-solid fa-check-circle" style="color: var(--accent-color)"></i> Finalizado com sucesso!').show();
                }
            }, speed);
        }

        // Demo Mode
        $('#btnDemo').click(function() {
            const btn = $(this);
            const runBtn = $('#btnRun');
            
            btn.prop('disabled', true);
            runBtn.prop('disabled', true);
            $('#resultContainer').show();
            $('#outputContent').empty();
            
            // Simula o progresso mais rápido
            simulateProgress(1500);

            // Busca os dados da demo
            $.ajax({
                url: '/demo-data',
                type: 'GET',
                success: function(r) {
                    setTimeout(() => {
                         $('#outputContent').html(marked.parse(r.message));
                         btn.prop('disabled', false);
                         runBtn.prop('disabled', false);
                    }, 9000); // 1500ms * 6 passos = 9000ms
                }
            });
        });

        // Run Real Mode (Atualizado para modo Assíncrono/Polling)
        $('#aiForm').on('submit', function(e) {
            e.preventDefault();
            const btn = $('#btnRun');
            const demoBtn = $('#btnDemo');
            
            btn.prop('disabled', true).html('<i class="fa-solid fa-circle-notch fa-spin"></i> Iniciando...');
            demoBtn.prop('disabled', true);
            
            $('#resultContainer').show();
            $('#outputContent').empty();
            $('#loadingText').show();
            
            simulateProgress(5000); 

            $.ajax({
                url: '/run-crew',
                type: 'POST',
                data: $(this).serialize(),
                success: function(r) {
                    if(r.status === 'started') {
                        // Começa a perguntar pelo status
                        const taskId = r.task_id;
                        const pollInterval = setInterval(() => {
                            $.get(`/check-status/${taskId}`, function(status) {
                                if(status.status === 'completed') {
                                    clearInterval(pollInterval);
                                    btn.prop('disabled', false).html('<i class="fa-solid fa-play"></i> Iniciar Agentes');
                                    demoBtn.prop('disabled', false);
                                    $('#outputContent').html(marked.parse(status.data));
                                    $('.step').removeClass('active').addClass('completed');
                                    $('#loadingText').html('<i class="fa-solid fa-check-circle" style="color: var(--accent-color)"></i> Finalizado com sucesso!');
                                } else if(status.status === 'error') {
                                    clearInterval(pollInterval);
                                    btn.prop('disabled', false).html('<i class="fa-solid fa-play"></i> Iniciar Agentes');
                                    demoBtn.prop('disabled', false);
                                    $('#outputContent').html(`<div style="color: var(--danger-color); padding: 1rem; border: 1px solid var(--danger-color); border-radius: 8px;">${status.message}</div>`);
                                    $('#loadingText').hide();
                                }
                            });
                        }, 5000); // Checa a cada 5 segundos
                    } else {
                        btn.prop('disabled', false).html('<i class="fa-solid fa-play"></i> Iniciar Agentes');
                        demoBtn.prop('disabled', false);
                        alert('Erro ao iniciar agentes: ' + r.message);
                    }
                },
                error: function() {
                    btn.prop('disabled', false).html('<i class="fa-solid fa-play"></i> Iniciar Agentes');
                    demoBtn.prop('disabled', false);
                    alert('Erro de conexão com o servidor.');
                }
            });
        });
    </script>
</body>
</html>
"""

# ... (Resto do app.py igual, adicionando a rota demo)

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/demo-data', methods=['GET'])
def demo_data():
    mock_response = """
## 🏆 Relatório Avançado SEO VIP (6 Estágios)

### 📂 1. Onboarding & Brand Persona
**Marca**: Chili Tools. **Tom de Voz**: Inovador, Tecnológico, Direto.
**Diferencial**: Automação real via Agentes Autônomos.

---

### 🧠 2. Keyword Research (Top 50 terms)
| Palavra-Chave | Vol | KD | Intenção | Cluster |
| :--- | :--- | :--- | :--- | :--- |
| **agentes autônomos marketing** | 1.2k | 15 | Comercial | Automação |
| ferramentas seo ia 2025 | 2.5k | 30 | Info | IA Tools |
| ... (50 termos mapeados com sucesso) | ... | ... | ... | ... |

---

### 📝 3. Content Brief (Estratégico)
**Título**: O Guia Definitivo dos Agentes Autônomos de Marketing em 2025.
**Estrutura**: 
- H2: Por que a IA generativa não é mais suficiente?
- H2: A ascensão da Automação de Agentes (The CrewAI Effect).
- H3: On-page vs Off-page na era dos Agentes.

---

### ✍️ 4. Content Developed
O conteúdo foi desenvolvido seguindo o brief acima. Foco total em autoridade técnica e SEO On-page.
(Texto completo gerado com ~1.500 palavras...)

---

### 🔍 5. On-page SEO Audit
- **Checklist**: Foco na Keyword Primária (OK), Meta Description (Criada), Internlinks (Sugeridos).
- **Audit Score**: 94/100.

---

### 🚀 6. Implementation Status
- **Google Docs**: Documento criado com sucesso.
- **Link**: [Documento Final Chili Tools](https://docs.google.com/...)
    """
    return jsonify({'status': 'success', 'message': mock_response})

def run_background_crew(task_id, cmd):
    try:
        # Executa o script e captura a saída
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            stdout = result.stdout
            if "--- INÍCIO DO CONTEÚDO ---" in stdout and "--- FIM DO CONTEÚDO ---" in stdout:
                parts = stdout.split("--- INÍCIO DO CONTEÚDO ---")
                content = parts[1].split("--- FIM DO CONTEÚDO ---")[0].strip()
            else:
                content = stdout.strip()
            
            tasks_db[task_id] = {'status': 'completed', 'data': content}
        else:
            error_msg = f"Erro no script:\n{result.stderr}\n\nSaída:\n{result.stdout}"
            tasks_db[task_id] = {'status': 'error', 'message': error_msg}
            
    except Exception as e:
        tasks_db[task_id] = {'status': 'error', 'message': str(e)}

@app.route('/run-crew', methods=['POST'])
def run_crew():
    if not SCRIPT_PATH:
        return jsonify({'status': 'error', 'message': 'ERRO NO SERVIDOR: O arquivo main.py não foi encontrado.'})

    c = request.form.get('cliente')
    t = request.form.get('topico')
    s = request.form.get('site')
    
    gemini_key = request.form.get('gemini_key') or os.getenv('GEMINI_API_KEY')
    ahrefs_key = request.form.get('ahrefs_key') or os.getenv('AHREFS_API_KEY') or "SEM_CHAVE"

    if not gemini_key:
         return jsonify({'status': 'error', 'message': 'ERRO: A Gemini API Key é obrigatória!'})

    # Gera um ID único para esta tarefa
    task_id = str(uuid.uuid4())
    tasks_db[task_id] = {'status': 'running'}

    # Comando para rodar
    cmd = [sys.executable, SCRIPT_PATH, c, t, s, gemini_key, ahrefs_key]

    # Inicia a thread em background
    thread = threading.Thread(target=run_background_crew, args=(task_id, cmd))
    thread.start()

    return jsonify({'status': 'started', 'task_id': task_id})

@app.route('/check-status/<task_id>', methods=['GET'])
def check_status(task_id):
    task = tasks_db.get(task_id)
    if not task:
        return jsonify({'status': 'not_found'})
    
    return jsonify(task)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"--- INICIANDO SERVIDOR NA PORTA {port} ---")
    app.run(host='0.0.0.0', port=port, debug=False)
