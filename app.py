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
    <title>CrewAI Studio</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #09090b;
            --card-bg: rgba(255, 255, 255, 0.03);
            --border-color: rgba(255, 255, 255, 0.1);
            --text-primary: #ededed;
            --text-secondary: #a1a1aa;
            --accent-color: #10b981;
            --accent-hover: #059669;
            --input-bg: rgba(0, 0, 0, 0.3);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
        
        body { 
            background-color: var(--bg-color); 
            color: var(--text-primary); 
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background-image: radial-gradient(circle at top right, rgba(16, 185, 129, 0.1), transparent 40%);
        }

        .container {
            width: 100%;
            max-width: 800px;
            padding: 2rem;
        }

        .card { 
            background: var(--card-bg); 
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-color); 
            border-radius: 24px;
            padding: 3rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        .header { margin-bottom: 2.5rem; text-align: center; }
        .header h1 { font-weight: 600; font-size: 1.5rem; letter-spacing: -0.025em; margin-bottom: 0.5rem; }
        .header p { color: var(--text-secondary); font-size: 0.875rem; }

        .form-group { margin-bottom: 1.5rem; }
        .form-group label { display: block; font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.5rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
        
        .form-control { 
            width: 100%; 
            background: var(--input-bg); 
            border: 1px solid var(--border-color); 
            color: var(--text-primary); 
            padding: 0.875rem 1rem;
            border-radius: 12px;
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--accent-color);
            box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
        }

        .row { display: flex; gap: 1.5rem; }
        .col { flex: 1; }

        .btn {
            width: 100%;
            padding: 1rem;
            background: var(--accent-color);
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-top: 1rem;
        }

        .btn:hover { background: var(--accent-hover); transform: translateY(-1px); }
        .btn:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }

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

        @keyframes spin { to { transform: rotate(360deg); } }
        
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            background: rgba(16, 185, 129, 0.1);
            color: var(--accent-color);
            margin-bottom: 2rem;
        }

    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="header">
                <div class="status-badge">● Sistema Operacional</div>
                <h1>CrewAI Studio</h1>
                <p>Orquestração de agentes autônomos</p>
            </div>
            
            <form id="aiForm">
                <div class="form-group">
                    <label>Cliente</label>
                    <input type="text" class="form-control" name="cliente" value="Cliente Teste" placeholder="Nome da empresa">
                </div>
                
                <div class="row">
                    <div class="col">
                        <div class="form-group">
                            <label>Tópico</label>
                            <input type="text" class="form-control" name="topico" value="Marketing" placeholder="Assunto principal">
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>Website</label>
                            <input type="text" class="form-control" name="site" value="exemplo.com" placeholder="URL para análise">
                        </div>
                    </div>
                </div>

                <button type="submit" class="btn" id="btnGerar">Iniciar Agentes</button>
            </form>

            <div id="loading" class="spinner"></div>
            <div id="resultado" class="result-box"></div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $('#aiForm').on('submit', function(e) {
            e.preventDefault();
            const btn = $('#btnGerar');
            const loader = $('#loading');
            const result = $('#resultado');

            btn.prop('disabled', true).text('Processando...');
            loader.show();
            result.hide().empty();
            
            $.ajax({
                url: '/run-crew',
                type: 'POST',
                data: $(this).serialize(),
                success: function(r) {
                    loader.hide();
                    btn.prop('disabled', false).text('Iniciar Agentes');
                    
                    if(r.status === 'success'){
                        typeWriter(r.data, result);
                    } else {
                        result.text(r.message).css('border-color', '#ef4444').fadeIn();
                    }
                },
                error: function() {
                    loader.hide();
                    btn.prop('disabled', false).text('Iniciar Agentes');
                    alert('Erro de conexão com o servidor.');
                }
            });
        });

        function typeWriter(text, element) {
            element.show();
            element.html(text.replace(/\\n/g, '<br>'));
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/run-crew', methods=['POST'])
def run_crew():
    if not SCRIPT_PATH:
        return jsonify({'status': 'error', 'message': 'ERRO NO SERVIDOR: O arquivo main.py não foi encontrado. Verifique o terminal do Python.'})

    c = request.form.get('cliente')
    t = request.form.get('topico')
    s = request.form.get('site')

    try:
        # Usa o sys.executable para garantir que usa o Python da .venv
        cmd = [sys.executable, SCRIPT_PATH, c, t, s]
        
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