# Mangue Baja Telemetry System

Este projeto é o sistema de **telemetria da equipe Mangue Baja UFPE**,
desenvolvido para coletar, armazenar, simular e visualizar dados em
tempo real durante os testes e competições.

------------------------------------------------------------------------

## 📌 Visão Geral

O sistema é composto por duas partes principais:

-   **Backend (FastAPI + WebSockets + SQLite/MQTT)**\
    Responsável por capturar os dados do carro (via MQTT), simular dados
    quando necessário e disponibilizá-los para os clientes via
    WebSocket.\
    Arquivo principal: [`main.py`](./main.py)

-   **Frontend (React + TypeScript)**\
    Uma interface de dashboard interativa para visualizar os dados de
    telemetria em diferentes layouts (mapa, gráficos, dados numéricos).\
    Arquivo principal: [`Dashboard.tsx`](./Dashboard.tsx)

------------------------------------------------------------------------

## ⚙️ Funcionalidades

-   Captura de dados de sensores em tempo real.\
-   Simulação de dados para testes (modo `SIMULAR_INTERFACE`).\
-   Armazenamento em banco de dados SQLite para análise posterior.\
-   Comunicação em tempo real com clientes via WebSockets.\
-   Dashboard interativo com múltiplos layouts de visualização.

------------------------------------------------------------------------

## 🚀 Como Rodar o Projeto

### 1. Clonar o repositório

``` bash
git clone https://github.com/seu-usuario/mangue-baja-telemetry.git
cd mangue-baja-telemetry
```

### 2. Criar ambiente virtual e instalar dependências

``` bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### 3. Configurar credenciais

Crie um arquivo `credentials.env` na raiz do projeto com:

``` ini
HOSTNAME=seu_host
PORT=sua_porta
USERNAME=seu_usuario
PASSWORD=sua_senha
```

### 4. Rodar o servidor

``` bash
uvicorn main:app --reload
```

O servidor estará disponível em:\
👉 `ws://localhost:8000/ws/telemetry`

### 5. Rodar o frontend

Se estiver usando React:

``` bash
npm install
npm run dev
```

------------------------------------------------------------------------

## 📡 Endpoints

-   **WebSocket de Telemetria**\
    `ws://localhost:8000/ws/telemetry`\
    Recebe dados de simulação ou dados reais do carro.

------------------------------------------------------------------------

## 🛠️ Tecnologias

### Backend

-   [FastAPI](https://fastapi.tiangolo.com/)\
-   [WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)\
-   [SQLite](https://www.sqlite.org/index.html)\
-   [MQTT](https://mqtt.org/) (opcional para dados reais)

### Frontend

-   [React](https://react.dev/)\
-   [TypeScript](https://www.typescriptlang.org/)

------------------------------------------------------------------------

## 📂 Estrutura do Projeto

    .
    ├── main.py                # Servidor backend (FastAPI + WebSockets)
    ├── Dashboard.tsx          # Interface de dashboard (React + TS)
    ├── requirements.txt       # Dependências Python
    ├── credentials.env        # Credenciais de conexão (ignorado no git)
    ├── telemetry/             # Lógica de captura MQTT
    ├── data/                  # Banco de dados e schema
    ├── simuladores/           # Simulação de dados

------------------------------------------------------------------------

## 🤝 Contribuição

Sinta-se à vontade para abrir **issues** e enviar **pull requests** com
melhorias.

------------------------------------------------------------------------

## 📜 Licença

Este projeto é desenvolvido para a competição **Baja SAE** pela equipe
**Mangue Baja UFPE**.\
Uso e redistribuição restritos ao contexto acadêmico e de pesquisa da
equipe.
