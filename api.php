from flask import Flask, render_template_string, request, jsonify
import subprocess
import os
import sys

# Define a pasta onde está o script da Crew
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Ajuste este caminho se o main.py estiver em outro lugar
SCRIPT_PATH = os.path.join(BASE_DIR, 'main.py') 

app = Flask(__name__)

# O HTML do Front-end (Fica aqui dentro mesmo pra facilitar)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CrewAI Python Server</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #121212; color: #e0e0e0; }
        .card { background-color: #1e1e1e; border: 1px solid #333; }
        .form-control { background-color: #2c2c2c; border: 1px solid #444; color: #fff; }
        .form-control:focus { background-color: #2c2c2c; color: #fff; border-color: #0d6efd; }
        .result-box {
            background: #000; color: #00ff41; padding: 20px;
            border-radius: 8px; font-family: 'Consolas', monospace;
            white-space: pre-wrap; min-height: 100px; display: none;
        }
    </style>
</head>
<body>
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow-lg">
                <div class="card-header bg-success text-white">
                    <h4 class="mb-0">🤖 Agentes CrewAI (Via Python Flask)</h4>
                </div>
                <div class="card-body">
                    <form id="aiForm">
                        <div class="mb-3">
                            <label class="form-label">Cliente</label>
                            <input type="text" class="form-control" name="cliente" value="Cliente X" required>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Tópico</label>
                                <input type="text" class="form-control" name="topico" value="Marketing Digital" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Website</label>
                                <input type="text" class="form-control" name="site" value="exemplo.com" required>
                            </div>
                        </div>
                        <button type="submit" class="btn btn-success w-100" id="btnGerar">INICIAR WORKFLOW</button>
                    </form>
                </div>
            </div>
            <div class="text-center mt-4" id="loadingArea" style="display:none;">
                <div class="spinner-border text-success" role="status"></div>
                <p class="mt-2">Os agentes estão trabalhando... (Aguarde 2 a 3 minutos)</p>
            </div>
            <div class="mt-4"><div id="resultado" class="result-box border border-success"></div></div>
        </div>
    </div>
</div>
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script>
    $('#aiForm').on('submit', function(e) {
        e.preventDefault();
        $('#btnGerar').prop('disabled', true).text('Processando...');
        $('#loadingArea').fadeIn();
        $('#resultado').hide().text('');
        
        $.ajax({
            url: '/run-crew',
            type: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                $('#loadingArea').hide();
                $('#btnGerar').prop('disabled', false).text('INICIAR WORKFLOW');
                if(response.status === 'success') {
                    $('#resultado').text(response.data).fadeIn();
                } else {
                    $('#resultado').text('Erro: ' + response.message).css('color','red').fadeIn();
                }
            },
            error: function() {
                $('#loadingArea').hide();
                $('#btnGerar').prop('disabled', false).text('INICIAR WORKFLOW');
                alert('Erro de conexão com o servidor Python.');
            }
        });
    });
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/run-crew', methods=['POST'])
def run_crew():
    cliente = request.form.get('cliente')
    topico = request.form.get('topico')
    site = request.form.get('site')

    # Executa o seu script main.py como um subprocesso
    # Usa o mesmo executável python que está rodando o Flask
    try:
        # Comando: python main.py "Cliente" "Topico" "Site"
        cmd = [sys.executable, SCRIPT_PATH, cliente, topico, site]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            check=True
        )
        
        return jsonify({'status': 'success', 'data': result.stdout})
        
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': f"Erro no script: {e.stderr}"})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    print(f"Servidor rodando! Acesse http://localhost:5000")
    print(f"Usando script em: {SCRIPT_PATH}")
    app.run(debug=True, port=5000)