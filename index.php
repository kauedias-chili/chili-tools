<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CrewAI - Gerador de Conteúdo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #121212; color: #e0e0e0; }
        .card { background-color: #1e1e1e; border: 1px solid #333; }
        .form-control { background-color: #2c2c2c; border: 1px solid #444; color: #fff; }
        .form-control:focus { background-color: #2c2c2c; color: #fff; border-color: #0d6efd; }
        .result-box {
            background: #000;
            color: #00ff41;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Consolas', monospace;
            white-space: pre-wrap;
            min-height: 100px;
            display: none;
        }
    </style>
</head>
<body>

<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow-lg">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">🤖 Agentes de Marketing (CrewAI)</h4>
                </div>
                <div class="card-body">
                    <form id="aiForm">
                        <div class="mb-3">
                            <label class="form-label">Nome do Cliente</label>
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
                        <button type="submit" class="btn btn-success w-100 fw-bold" id="btnGerar">
                            INICIAR WORKFLOW
                        </button>
                    </form>
                </div>
            </div>

            <div class="text-center mt-4" id="loadingArea" style="display:none;">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-2 text-warning">
                    Os agentes estão trabalhando...<br>
                    <small>(Isso pode levar de 2 a 5 minutos devido ao limite de velocidade da API Gratuita)</small>
                </p>
            </div>

            <div class="mt-4">
                <div id="resultado" class="result-box border border-success"></div>
            </div>
        </div>
    </div>
</div>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script>
    $(document).ready(function() {
        $('#aiForm').on('submit', function(e) {
            e.preventDefault();

            // Bloqueia tela
            $('#btnGerar').prop('disabled', true).text('Processando...');
            $('#loadingArea').fadeIn();
            $('#resultado').hide().text('');

            $.ajax({
                url: 'api.php',
                type: 'POST',
                data: $(this).serialize(),
                dataType: 'json',
                success: function(response) {
                    $('#loadingArea').hide();
                    $('#btnGerar').prop('disabled', false).text('INICIAR WORKFLOW');

                    if (response.status === 'success') {
                        // Formata um pouco a saída para ficar legível
                        $('#resultado').text(response.data).fadeIn();
                    } else {
                        $('#resultado').css('color', 'red').text('ERRO: ' + response.message).fadeIn();
                    }
                },
                error: function(xhr, status, error) {
                    $('#loadingArea').hide();
                    $('#btnGerar').prop('disabled', false).text('INICIAR WORKFLOW');
                    $('#resultado').css('color', 'red').text('Erro de conexão: ' + error).fadeIn();
                }
            });
        });
    });
</script>

</body>
</html>