from crewai.tools import BaseTool
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os

class GoogleDocsWriterTool(BaseTool):
    name: str = "Google Docs Writer"
    description: str = "Cria um novo documento no Google Docs com o conteúdo fornecido."

    def _run(self, title: str, content: str) -> str:
        creds_path = os.path.join(os.getcwd(), 'credentials.json')
        
        if not os.path.exists(creds_path):
            return "Erro: Arquivo credentials.json não encontrado."

        try:
            scopes = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
            creds = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
            service = build('docs', 'v1', credentials=creds)
            drive_service = build('drive', 'v3', credentials=creds)

            # 1. Cria o documento vazio
            doc_body = {'title': title}
            doc = service.documents().create(body=doc_body).execute()
            doc_id = doc.get('documentId')

            # 2. Insere o conteúdo
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                }
            ]
            
            service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

            # 3. (Opcional) Move para uma pasta específica se necessário
            
            return f"Documento criado com sucesso! Link: https://docs.google.com/document/d/{doc_id}"

        except Exception as e:
            return f"Erro ao criar Google Doc: {str(e)}"
