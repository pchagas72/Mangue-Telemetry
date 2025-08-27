# Sistema de telemetria da equipe Mangue Baja

Esse repositório foi criado por mim para a equipe Mangue Baja, a qual com alegria faço parte.

Um código eficiente e elegante é muito importante, portanto sinta-se convidado a ler o código fonte.

Se você é de outra equipe, sinta-se a vontade para usar de acordo com a licença (eu consigo saber!)

Não esqueça de deixar uma estrela, obrigado.

## Features/TODO:

### Geral
- Instalador e iniciador simples [X]
- Documentação completa [ ]

### Backend (server)

- Broadcast de telemetria via MQTT [X]
- Data-storage com SQLite [X]
- Simulação de dados para testes [X]
- Leitura de ENV para autenticação [X]
- Broadcast de telemetria via LoRa [ ]
- Replay de sessões passadas [ ]
- Interface para debug e "box" de ECU's [ ]
- Aplicar filtros do ilogger [ ]
- Criar executável [ ]

### Frontend (interface)

- Recepção e processamento dos dados [X]
- Mapa RT [X]
- Modelo do carro RT [X]
- Serial de análise RT [X]
- Temperaturas, velocidade, RPM, acelerações, posição geográfica e ângulo [X]
- Estado da bateria [X]
- Gráficos de vel,RPM,temperaturas e acelerações [X]
- Interface de replay [ ]
- Rede neural preventiva de falhas [ ]
- Debug e "box" de ECU's [ ]
- Página de exposição dos dados do ilogger em gráficos [ ]
- Criar executável [ ]


## Como utilizar

### Tecnologias:

* Python 3.11+
* FastAPI + Uvicorn
* MQTT (aiomqtt/paho-mqtt)
* SQLite
* React + Vite (frontend)

#### Estrutura do código

```
.
├── LICENSE
├── README.md
├── interface/        # Frontend (React + Vite + TypeScript)
├── server/           # Backend (Python + FastAPI + MQTT)
```

---

#### Backend (server)

**1. Criar e ativar ambiente virtual**

```bash
cd server
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

**2. Instalar dependências**

```bash
pip install -r requirements.txt
```

**3. Configurar variáveis de ambiente**
Crie um arquivo `.env` baseado em `credentials.env`, contendo:

```
HOSTNAME=broker.exemplo.com
PORT=1883
USERNAME=usuario
PASSWORD=senha
```

**4. Executar servidor**

```bash
python3 run.py
```

Lembre-se de fazer as alterações corretas para o pacote CAN do seu carro.

Leia o código!

---

####  Frontend (interface)

**1. Instalar dependências**

```bash
cd interface
npm install
```

**2. Ajustes necessários**
Se estiver usando outro pacote/protocolo CAN, altere os arquivos em:
`./interface/src/hooks/useTelemetry.ts`
`./interface/src/pages/Dashboard.ts`

E outros que forem necessários.

**3. Rodar aplicação**

```bash
npm run dev
```

A interface estará disponível em:
👉 [http://localhost:5173](http://localhost:5173)

## Lembretes

Obrigado por utilizar o nosso software! Lembre-se de manter a licença sempre em mente.
