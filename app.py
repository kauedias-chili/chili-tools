from flask import Flask, render_template_string, request, jsonify
import subprocess
import os
import sys

# Define onde o app.py está rodando
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# LISTA DE CAMINHOS CORRIGIDA (Baseada na sua estrutura atual)
possible_paths = [
    # Caminho correto: app.py e backend são vizinhos
    os.path.join(BASE_DIR, 'backend', 'crewai_app', 'main.py'),
    
    # Tentativa caso esteja solto na backend
    os.path.join(BASE_DIR, 'backend', 'main.py'),

    # Tentativa caso esteja na mesma pasta do app.py
    os.path.join(BASE_DIR, 'main.py'),
    
    # Tentativa completa (hardcoded) caso tudo falhe
    r'C:\xampp\htdocs\crewIA\multi-agent-system\backend\crewai_app\main.py'
]

SCRIPT_PATH = None
for path in possible_paths:
    if os.path.exists(path):
        SCRIPT_PATH = path
        print(f"✅ Arquivo main.py ENCONTRADO em: {path}")
        break

if not SCRIPT_PATH:
    print("❌ ERRO CRÍTICO: Não encontrei o arquivo main.py em lugar nenhum!")
    print("Pastas verificadas:")
    for p in possible_paths:
        print(f" - {p}")

app = Flask(__name__)

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
                    <div class="step" id="step1" title="Auditor"><i class="fa-solid fa-user-group"></i></div>
                    <div class="step" id="step2" title="Planner"><i class="fa-solid fa-magnifying-glass-chart"></i></div>
                    <div class="step" id="step3" title="Writer"><i class="fa-solid fa-pen-nib"></i></div>
                    <div class="step" id="step4" title="Manager"><i class="fa-solid fa-check-double"></i></div>
                </div>

                <div class="result-content">
                    <div id="loadingText" style="text-align: center; color: var(--text-secondary); margin-bottom: 1rem;">
                        <i class="fa-solid fa-circle-notch fa-spin"></i> Inicializando agentes...
                    </div>
                    <div id="outputContent" class="markdown-body"></div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        // Função para simular progresso visual
        function simulateProgress(speed = 2000) {
            const steps = ['step1', 'step2', 'step3', 'step4'];
            let current = 0;
            
            // Ativa o primeiro
            $('#'+steps[0]).addClass('active');
            $('#loadingText').html('<i class="fa-solid fa-spinner fa-spin"></i> Auditor analisando mercado...');

            const interval = setInterval(() => {
                $('#'+steps[current]).removeClass('active').addClass('completed');
                current++;
                
                if (current < steps.length) {
                    $('#'+steps[current]).addClass('active');
                    const msgs = ['Planner definindo keywords...', 'Writer redigindo conteúdo...', 'Manager revisando qualidade...'];
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
                    }, 6000); // Espera a animação acabar +/-
                }
            });
        });

        // Run Real Mode
        $('#aiForm').on('submit', function(e) {
            e.preventDefault();
            const btn = $('#btnRun');
            const demoBtn = $('#btnDemo');
            
            btn.prop('disabled', true).html('<i class="fa-solid fa-circle-notch fa-spin"></i> Processando...');
            demoBtn.prop('disabled', true);
            
            $('#resultContainer').show();
            $('#outputContent').empty();
            $('#loadingText').show();
            
            // Progresso mais lento para execução real (apenas visual, não sincronizado real-time ainda)
            simulateProgress(5000); 

            $.ajax({
                url: '/run-crew',
                type: 'POST',
                data: $(this).serialize(),
                success: function(r) {
                    btn.prop('disabled', false).html('<i class="fa-solid fa-play"></i> Iniciar Agentes');
                    demoBtn.prop('disabled', false);
                    
                    if(r.status === 'success'){
                        $('#outputContent').html(marked.parse(r.data));
                        // Força conclusão visual
                        $('.step').removeClass('active').addClass('completed');
                        $('#loadingText').html('<i class="fa-solid fa-check-circle" style="color: var(--accent-color)"></i> Finalizado com sucesso!');
                    } else {
                        $('#outputContent').html(`<div style="color: var(--danger-color); padding: 1rem; border: 1px solid var(--danger-color); border-radius: 8px;">${r.message}</div>`);
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
    # Dados fictícios bonitos para impressionar (Atualizado com SEO Avançado)
    mock_response = """
## 📋 Relatório de Estratégia & Conteúdo

### 🔍 1. Análise do Auditor
**Público-Alvo**: Gestores de Marketing e CEOs de SaaS B2B.
**Contexto**: Buscam eficiência operacional e redução de CAC.
**Estratégia**: Dominar a SERP para termos de "Automação com IA".

---

### 🧠 2. Planejamento SEO (50 Keywords Clusterizadas)

**Resumo da Estratégia**:
*   **Método**: Query Fan-out
*   **Split Intenção**: 50% Comercial / 50% Informacional
*   **Cauda**: 30% Short / 70% Long

#### 📂 Cluster A: Automação de Marketing (Comercial)
| Palavra-Chave | Vol | KD | Intenção | Tipo |
| :--- | :--- | :--- | :--- | :--- |
| **agentes autônomos marketing** | 1.2k | 15 | Comercial | Short |
| comprar software ia marketing | 800 | 25 | Comercial | Mid |
| melhor ferramenta automação b2b | 450 | 10 | Comercial | Long |
| ... (simulando +20 linhas) | ... | ... | ... | ... |

#### 📂 Cluster B: Tendências e Futuro (Informacional)
| Palavra-Chave | Vol | KD | Intenção | Tipo |
| :--- | :--- | :--- | :--- | :--- |
| o futuro do marketing digital | 5k | 40 | Info | Short |
| como usar ia no marketing | 3.2k | 20 | Info | Mid |
| benefícios agentes autônomos empresa | 200 | 5 | Info | Long |
| ... (simulando +25 linhas) | ... | ... | ... | ... |

---

### ✍️ 3. Artigo Final (Baseado no Cluster A)
**Título**: Agentes Autônomos: A Revolução B2B

(Conteúdo do artigo gerado com H2 e H3 otimizados para as palavras-chave acima...)

> "A automação inteligente é o novo diferencial competitivo."

---

### ✅ 4. Aprovação do Manager
*   **Checklist SEO**: Densidade de palavras-chave atingida (Aprovado).
*   **Clusterização**: Cobertura semântica completa (Aprovado).
*   **Status**: **PRONTO PARA PUBLICAR** 🚀
    """
    return jsonify({'status': 'success', 'message': mock_response})

@app.route('/run-crew', methods=['POST'])
def run_crew():
    if not SCRIPT_PATH:
        return jsonify({'status': 'error', 'message': 'ERRO NO SERVIDOR: O arquivo main.py não foi encontrado. Verifique o terminal do Python.'})

    c = request.form.get('cliente')
    t = request.form.get('topico')
    s = request.form.get('site')
    
    # Obtém as chaves do form ou tenta pegar do ambiente se estiver vazio (fallback)
    gemini_key = request.form.get('gemini_key') or os.getenv('GEMINI_API_KEY')
    ahrefs_key = request.form.get('ahrefs_key') or os.getenv('AHREFS_API_KEY') or "SEM_CHAVE"

    if not gemini_key:
         return jsonify({'status': 'error', 'message': 'ERRO: A Gemini API Key é obrigatória!'})

    try:
        # Usa o sys.executable para garantir que usa o Python da .venv
        # Passa as chaves como novos argumentos
        cmd = [sys.executable, SCRIPT_PATH, c, t, s, gemini_key, ahrefs_key]
        
        # check=True faz o python avisar se o script der erro
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            return jsonify({'status': 'success', 'data': result.stdout})
        else:
            # Retorna o erro exato que deu no script
            return jsonify({'status': 'error', 'message': f"Erro no script:\n{result.stderr}\n\nSaída:\n{result.stdout}"})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    print("--- INICIANDO SERVIDOR ---")
    app.run(debug=True, port=5000)