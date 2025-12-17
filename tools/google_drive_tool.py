from crewai.tools import BaseTool
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os

class GoogleDriveLoaderTool(BaseTool):
    name: str = "Google Drive Loader"
    description: str = "Lê arquivos de texto/PDF de uma pasta específica do Google Drive para servir de contexto."

    def _run(self, folder_id: str) -> str:
        # Caminho para o arquivo de credenciais que o usuário deve fornecer depois
        creds_path = os.path.join(os.getcwd(), 'credentials.json')
        
        if not os.path.exists(creds_path):
            return "Erro: Arquivo credentials.json não encontrado na raiz do projeto."

        try:
            scopes = ['https://www.googleapis.com/auth/drive.readonly']
            creds = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
            service = build('drive', 'v3', credentials=creds)

            # Lista arquivos na pasta
            results = service.files().list(
                q=f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.document'",
                pageSize=10, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                return "Nenhum arquivo encontrado na pasta especificada."

            docs_content = []
            # TODO: Adicionar lógica para ler o conteúdo de cada arquivo (exportText)
            for item in items:
                docs_content.append(f"Arquivo encontrado: {item['name']} (ID: {item['id']})")

            return "\n".join(docs_content)

        except Exception as e:
            return f"Erro ao acessar Google Drive: {str(e)}"
