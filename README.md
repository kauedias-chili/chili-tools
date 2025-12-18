# Chili Tools | Advanced SEO Agentic AI

[English](#english) | [Português](#português)

---

## English

Advanced 6-stage SEO content generation pipeline powered by CrewAI and Google Gemini 2.5 Flash.

### 🚀 Features
- **6 Specialized Agents**: Onboarding Auditor, SEO Strategist, Briefing Architect, Content Developer, SEO Quality Manager, and Implementation Manager.
- **Asynchronous Execution**: Background task processing using threading to prevent server timeouts.
- **Real-time Polling**: Modern UI with status updates and SEO Pro-tips during processing.
- **Cloud Ready**: Optimized for Render deployment with dynamic port and path handling.

### 🛠️ Tech Stack
- **Backend**: Python, Flask, CrewAI.
- **LLM**: Google Gemini 2.5 Flash.
- **UI**: HTML5, CSS3 (Glassmorphism), JavaScript (jQuery, Marked.js).
- **Tools**: Custom Ahrefs tool, Google Drive/Docs integration.

### ⚙️ Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in a `.env` file:
   ```env
   GEMINI_API_KEY=your_key_here
   AHREFS_API_KEY=your_key_here (optional)
   ```
4. Run the application:
   ```bash
   python app.py
   ```

---

## Português

Pipeline avançado de SEO de 6 estágios alimentado por CrewAI e Google Gemini 2.5 Flash.

### 🚀 Funcionalidades
- **6 Agentes Especialistas**: Auditor de Onboarding, Estrategista SEO, Arquiteto de Briefing, Desenvolvedor de Conteúdo, Gestor de Qualidade SEO e Gerente de Implementação.
- **Execução Assíncrona**: Processamento de tarefas em segundo plano usando threading para evitar timeouts no servidor.
- **Polling em Tempo Real**: Interface moderna com atualizações de status e Dicas Pro de SEO durante o processamento.
- **Pronto para Nuvem**: Otimizado para deploy no Render com gerenciamento dinâmico de portas e caminhos.

### 🛠️ Tecnologias
- **Backend**: Python, Flask, CrewAI.
- **LLM**: Google Gemini 2.5 Flash.
- **UI**: HTML5, CSS3 (Glassmorphism), JavaScript (jQuery, Marked.js).
- **Ferramentas**: Ferramenta Ahrefs customizada, integração Google Drive/Docs.

### ⚙️ Instalação
1. Clone o repositório.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente em um arquivo `.env`:
   ```env
   GEMINI_API_KEY=sua_chave_aqui
   AHREFS_API_KEY=sua_chave_aqui (opcional)
   ```
4. Execute a aplicação:
   ```bash
   python app.py
   ```

### 👔 Fluxo de Trabalho
1. **Onboarding**: Entendimento da marca e persona.
2. **Estratégia**: Pesquisa de 50 keywords e clusterização.
3. **Briefing**: Estruturação técnica do artigo.
4. **Desenvolvimento**: Redação IA de alta qualidade.
5. **Auditoria**: Checklist SEO On-page rigoroso.
6. **Implementação**: Entrega final no Google Docs.