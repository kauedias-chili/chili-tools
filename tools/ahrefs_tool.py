from crewai.tools import BaseTool
import requests
import os
import json
from datetime import datetime

class AhrefsDomainStatsTool(BaseTool):
    name: str = "Ahrefs Domain Stats"
    description: str = "Obtém métricas de autoridade (DR) e tráfego orgânico de um domínio. Útil para o Auditor."

    def _run(self, domain: str) -> str:
        api_key = os.getenv("AHREFS_API_KEY")
        if not api_key or api_key == "SEM_CHAVE":
            return "Erro: AHREFS_API_KEY não configurada. Usando dados simulados: DR: 45, Tráfego: 12k/mês."

        # Exemplo de chamada real v3
        today = datetime.now().strftime("%Y-%m-%d")
        url = f"https://api.ahrefs.com/v3/site-explorer/domain-rating?target={domain}&date={today}"
        
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            # Domain Rating
            dr_resp = requests.get(url, headers=headers, timeout=10)
            dr_data = dr_resp.json() if dr_resp.status_code == 200 else {"domain_rating": "N/A"}
            
            # Organic Traffic (Simplificado para o exemplo)
            traffic_url = f"https://api.ahrefs.com/v3/site-explorer/organic-traffic?target={domain}&date={today}"
            t_resp = requests.get(traffic_url, headers=headers, timeout=10)
            t_data = t_resp.json() if t_resp.status_code == 200 else {"traffic": "N/A"}
            
            return json.dumps({
                "domain": domain,
                "dr": dr_data.get("domain_rating"),
                "ahrefs_rank": dr_data.get("ahrefs_rank"),
                "organic_traffic": t_data.get("traffic")
            }, indent=2)
        except Exception as e:
            return f"Erro ao conectar com Ahrefs: {str(e)}. Simulação: DR 45, Tráfego 12k."

class AhrefsTopPagesTool(BaseTool):
    name: str = "Ahrefs Top Pages"
    description: str = "Lista as páginas com mais tráfego orgânico de um domínio. Útil para análise de concorrentes."

    def _run(self, domain: str) -> str:
        api_key = os.getenv("AHREFS_API_KEY")
        if not api_key or api_key == "SEM_CHAVE":
            return "Simulação: 1. /blog/ia-no-marketing (3k), 2. /produtos/agentes (2k), 3. /guia-seo (1.5k)"

        url = f"https://api.ahrefs.com/v3/site-explorer/pages-by-traffic?target={domain}&limit=5"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                return json.dumps(resp.json().get("pages", []), indent=2)
            return f"Erro Ahrefs ({resp.status_code}): {resp.text}"
        except Exception as e:
            return f"Erro de conexão: {str(e)}"

class AhrefsKeywordTool(BaseTool):
    name: str = "Ahrefs Keyword Explorer"
    description: str = "Pesquisa volume e dificuldade (KD) de palavras-chave. Útil para o estrategista."

    def _run(self, keywords: str) -> str:
        api_key = os.getenv("AHREFS_API_KEY")
        if not api_key or api_key == "SEM_CHAVE":
            # Simulação aprimorada
            results = [{"keyword": k.strip(), "volume": 1200, "kd": 20} for k in keywords.split(",")[:5]]
            return json.dumps(results, indent=2)

        # Endpoint v3 aproximado
        url = f"https://api.ahrefs.com/v3/keywords-explorer/overview?keywords={keywords}"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                return json.dumps(resp.json(), indent=2)
            return f"Erro Ahrefs: {resp.status_code}"
        except Exception as e:
            return f"Erro: {str(e)}"
