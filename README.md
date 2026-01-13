# 🖨️ PrintFlow - Sistema de Gestão de Produção Gráfica

O **PrintFlow** é um sistema web de gestão estilo Kanban desenvolvido para otimizar o fluxo de trabalho em gráficas e empresas de comunicação visual. Ele permite acompanhar pedidos desde o atendimento até a expedição, com comunicação em tempo real entre os setores.

## 🚀 Funcionalidades

- **Quadro Kanban Interativo:** Arraste e solte (Drag & Drop) para mover pedidos entre setores (Atendimento, Impressão, Produção, Expedição).
- **Chat em Tempo Real:** Comunicação interna integrada com notificações sonoras e visuais.
- **Status Personalizáveis:** Etiquetas coloridas para indicar o estado do pedido (Fila, Rodando, Aguardando Material, etc.).
- **Gestão de Arquivos:** Upload e visualização de prints/artes diretamente no card do pedido.
- **Sistema de Arquivamento:** Limpeza visual do quadro sem perda de histórico.
- **Controle de Acesso:** Níveis de permissão para Administradores e Colaboradores.
- **Modo Servidor Local:** Configurado para rodar em rede local via **Waitress** ou como executável portátil (`.exe`).

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login.
- **Frontend:** HTML5, Bootstrap 5, JavaScript (Fetch API), SortableJS (Drag & Drop).
- **Banco de Dados:** SQLite.
- **Servidor:** Waitress (WSGI).
- **Compilação:** PyInstaller.

## 📦 Como Rodar o Projeto

### Pré-requisitos

- Python 3.10+ instalado.

### Passo a Passo

1.  **Clone o repositório:**

    ```bash
    git clone [https://github.com/SEU-USUARIO/PrintFlow.git](https://github.com/SEU-USUARIO/PrintFlow.git)
    cd PrintFlow
    ```

2.  **Crie e ative um ambiente virtual:**

    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o sistema:**
    ```bash
    python server.py
    ```
    O sistema estará disponível em: `http://localhost:8080` (ou no IP da máquina na rede local).

> **Nota:** O banco de dados `printflow.db` será criado automaticamente na primeira execução com usuário `admin` e senha `admin`.

## 🖥️ Criando o Executável (Windows)

Para distribuir o sistema sem necessidade de instalar Python nas máquinas clientes, utilize o PyInstaller:

```bash
pyinstaller --name PrintFlow --onefile server.py
```
