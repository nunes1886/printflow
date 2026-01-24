# 🖨️ PrintFlow - Sistema de Gestão de Produção Gráfica

> **Versão Atual:** v2.3 (Mobile First & WhatsApp Integration)

O **PrintFlow** é um sistema web de gestão estilo Kanban desenvolvido sob medida para otimizar o fluxo de trabalho em gráficas e empresas de comunicação visual. Focado em **performance local** e **usabilidade**, ele elimina a dependência de internet externa e centraliza a comunicação da equipe.

## 🚀 Funcionalidades Principais

### 📋 Gestão Visual (Kanban)

- **Drag & Drop Fluido:** Arraste e solte pedidos entre setores (Atendimento, Impressão, Produção, Expedição).
- **Semáforo de Prazos:** (Em Breve) Indicadores visuais de urgência baseados na data de entrega.
- **Busca Instantânea:** Filtre pedidos por nome do cliente, número da OS ou título em tempo real.

### 📱 Mobile First (Novidade v2.3)

- **Design Responsivo:** Interface 100% adaptada para Celulares e Tablets.
- **Touch Otimizado:** Rolagem horizontal inteligente e gestos de toque calibrados para evitar arrastar cards por engano.
- **Modais Fullscreen:** Telas de edição expandidas em dispositivos móveis para facilitar o preenchimento.

### 💬 Comunicação Integrada

- **Botão WhatsApp Inteligente:** O sistema detecta telefones no cadastro e gera um botão direto para iniciar conversa com o cliente já citando o pedido.
- **Chat Interno (Local):** Chat da equipe com notificações sonoras ("Ding-Dong") e visuais em tempo real via polling.

### 📂 Arquivos e Organização

- **Upload de Prints:** Cole imagens (Ctrl+V) ou faça upload direto no card.
- **Arquivamento:** Limpeza visual do quadro mantendo histórico recuperável.
- **Segurança:** Níveis de acesso (Admin vs Colaborador) para proteção de dados sensíveis.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.10+, Flask, Flask-SQLAlchemy.
- **Frontend:** HTML5, Bootstrap 5, JavaScript Puro (Vanilla JS).
- **Banco de Dados:** SQLite (Ideal para aplicações portáteis/locais).
- **Servidor:** Waitress (WSGI Production Server).
- **Compilação:** PyInstaller (Gera executável .exe standalone).

---

## 📦 Como Rodar o Projeto

### Pré-requisitos

- Python 3.10+ instalado.

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU-USUARIO/PrintFlow.git](https://github.com/SEU-USUARIO/PrintFlow.git)
   cd PrintFlow
   ```
