from crewai.tools import BaseTool
import csv
import os
import re

class CSVGeneratorTool(BaseTool):
    name: str = "CSV Generator"
    description: str = "Converte uma tabela Markdown de palavras-chave em um arquivo CSV para download."

    def _run(self, markdown_table: str, filename: str = "palavras_chave.csv") -> str:
        try:
            # Caminho absoluto para salvar o arquivo (na raiz do projeto para o Flask servir)
            output_path = os.path.join(os.getcwd(), filename)
            
            # Limpa e extrai as linhas da tabela Markdown
            lines = markdown_table.strip().split("\n")
            
            # Filtra apenas as linhas que parecem ser da tabela (contém |)
            table_lines = [line for line in lines if "|" in line and "---" not in line]
            
            if not table_lines:
                return "Erro: Nenhuma tabela Markdown válida encontrada."

            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                for line in table_lines:
                    # Remove | do início e fim e dá split
                    row = [cell.strip() for cell in line.strip('|').split('|')]
                    writer.writerow(row)
            
            return f"Arquivo CSV '{filename}' gerado com sucesso em {output_path}."
        except Exception as e:
            return f"Erro ao gerar CSV: {str(e)}"
