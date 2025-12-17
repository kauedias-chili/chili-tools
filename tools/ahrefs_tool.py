from crewai.tools import BaseTool
import requests
import os
import json

class AhrefsKeywordTool(BaseTool):
    name: str = "Ahrefs Keyword Explorer"
    description: str = "Pesquisa volume e dificuldade (KD) de palavras-chave usando a API do Ahrefs. Útil para o Planejador."

    def _run(self, keywords: str, country: str = "br") -> str:
        api_key = os.getenv("AHREFS_API_KEY")
        if not api_key or api_key == "SEM_CHAVE":
            return "Erro: AHREFS_API_KEY não configurada ou inválida."

        # Mock implementation for now as we don't have the exact endpoint/license details confirmed 
        # and Ahrefs API v3 is complex. 
        # Ideally this would look like:
        # headers = {"Authorization": f"Bearer {api_key}"}
        # response = requests.get(...)
        
        # Simulação para validação do fluxo
        results = []
        kw_list = [k.strip() for k in keywords.split(",")]
        
        for kw in kw_list:
            # Simulação de dados
            results.append({
                "keyword": kw,
                "volume": 1000, # Placeholder
                "kd": 15,       # Placeholder
                "traffic_potential": 500
            })
            
        return json.dumps(results, indent=2)

if __name__ == "__main__":
    # Teste rápido
    tool = AhrefsKeywordTool()
    print(tool._run(keywords="marketing digital, seo"))
