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
            scopes = ['https://www.googleapis.com/auth/drive']
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

class GoogleDriveUploaderTool(BaseTool):
    name: str = "Google Drive Uploader"
    description: str = "Faz upload de um arquivo local para uma pasta específica do Google Drive."

    def _run(self, file_path: str, folder_id: str) -> str:
        creds_path = os.path.join(os.getcwd(), 'credentials.json')
        if not os.path.exists(creds_path):
            return "Erro: credentials.json não encontrado."

        try:
            from googleapiclient.http import MediaFileUpload
            scopes = ['https://www.googleapis.com/auth/drive']
            creds = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
            service = build('drive', 'v3', credentials=creds)

            file_metadata = {
                'name': os.path.basename(file_path),
                'parents': [folder_id]
            }
            media = MediaFileUpload(file_path, resumable=True)
            
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return f"Arquivo '{os.path.basename(file_path)}' enviado com sucesso! ID: {file.get('id')}"

        except Exception as e:
            return f"Erro no upload para o Drive: {str(e)}"
