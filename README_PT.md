# Sistema de telemetria da equipe Mangue Baja

[Read in English](./README_EN.md)

Esse repositório foi criado por mim para a equipe Mangue Baja, a qual com alegria faço parte.

Um código eficiente e elegante é muito importante, portanto sinta-se convidado a ler o código fonte.

Se você é de outra equipe, sinta-se a vontade para usar de acordo com a licença (eu consigo saber!)

Não esqueça de deixar uma estrela, obrigado.


## O porquê das coisas

### Backend em python 

O backend (ou servidor) em python tem suas vantagens e desvantagens, inicialmente eu pensei 
em fazer em C, Go ou Rust, porém python se apresentou mais útil não apenas pela sintaxe mais 
fácil, tornando o código mais compreensível para todos da equipe, mas também pela maior quantidade 
de bibliotecas relacionadas a conectividade das coisas, com python, facilmente pude implementar 
MQTT, WebSocket, API routing, etc. Desta maneira, e tendo em vista que a performance oferecida pelo 
fastAPI, optei por python pelo momento.

Mas tenho a vontade de trocar o backend para C ou Rust eventualmente.

### Frontend em react-ts

O front em react-ts é muito útil pois permite um ambiente de desenvolvimento cheio de 
variedade de bibliotecas do react, e a incrível velocidade do typescript. Utilizando 
javascript não era possível renderizar mais de 20 dados por segundo nos gráficos, agora 
com react, a interface consegue renderizar tranquilamente todos os dados que queremos sem 
nenhuma latência.

### Starter

O script "starter" não veio por escolha, mas sim por necessidade da equipe. Em caso de 
alguém leigo precisar utilizar a interface, abrir um shell-script é impossível (visto que 
a pessoa muito provavelmente usa windows) e pedir para que o leigo saiba utilizar o terminal 
para instalar os pré-requesitos, iniciar o backend e iniciar a interface é pedir demais.

Além de poupar tempo, a interface se torna mais acessível a todos, não apenas aos membros 
com mais entendimento de eletrônica e programação.

## Features/TODO:

### Starter
- Instalador e iniciador simples [X]
- Transformar o starter em um centro de aplicações [ ]
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
