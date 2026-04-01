# 🥚 Egg Candling AI

Sistema inteligente de detecção de fertilidade em ovos utilizando **Inteligência Artificial** e **Deep Learning**.

![Egg Candling AI](https://img.shields.io/badge/AI-Deep%20Learning-orange?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0.1-green?style=for-the-badge&logo=flask)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-red?style=for-the-badge&logo=pytorch)
![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)

## 🎯 Visão Geral

O **Egg Candling AI** é uma aplicação web que utiliza algoritmos de inteligência artificial para classificar ovos como **fértil** ou **infértil** através da análise de imagens. O sistema foi desenvolvido para auxiliar produtores rurais e avicultores na identificação precisa da fertilidade dos ovos.

Documentação ampliada (objetivo, funcionalidades, tecnologias, serviço de IA, diagrama MVC + microserviço): [`docs/documentacao-sistema.md`](docs/documentacao-sistema.md).

### ✨ Características Principais

- 🔍 **Detecção Automática**: Identifica ovos em imagens automaticamente
- 🧠 **IA**: Modelo YOLOv8 treinado especificamente para ovos
- 📱 **Interface**: Design responsivo
- 📷 **Captura Flexível**: Upload de imagens ou captura via câmera
- 📊 **Resultados**: Classificação com nível de confiança
- ⚡ **Tempo Real**: Análise rápida e eficiente

## 🚀 Tecnologias Utilizadas

### Backend
- **Python 3.13** - Linguagem principal
- **Flask 2.0.1** - Framework web
- **YOLOv8 (Ultralytics)** - Modelo de detecção
- **PIL (Pillow)** - Processamento de imagens
- **Flask-CORS** - Controle de CORS
- **Requests** - Cliente HTTP para o microserviço de inferência

### Frontend
- **HTML5** - Estrutura
- **CSS3** - Estilização customizada
- **Alpine.js** - Reatividade
- **UnoCSS** - Framework CSS utilitário
- **Font Awesome** - Ícones

### IA/ML
- **YOLOv8n** - Modelo de detecção de objetos
- **Deep Learning** - Rede neural convolucional
- **Computer Vision** - Processamento de imagens

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/fcarlosmonteiro/egg-candling-ai.git
cd egg-candling-ai
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
```

### 3. Ative o ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Instale as dependências
```bash
pip install -r requirements.txt
```

Para **imagens Docker separadas** (web leve vs serviço com GPU), você pode dividir manualmente: web precisa de Flask, Werkzeug, flask-cors e requests; o microserviço precisa também de numpy, pillow e ultralytics.

### 5. Execute a aplicação

A arquitetura é sempre em **dois processos**: microserviço de IA + app web.

**Terminal 1** — inferência (porta 5002, monitoramento em `GET /health`):
```bash
cd app
python inference_server.py
```

**Terminal 2** — interface web (porta 5001):
```bash
cd app
python app.py
```

Por padrão a app já usa `http://127.0.0.1:5002` para o microserviço. Em produção ou outra porta, defina `INFERENCE_SERVICE_URL` (veja `env.example`).

### 6. Acesse a aplicação
Abra seu navegador e acesse: `http://localhost:5001`

## 📁 Estrutura do Projeto

```
egg-candling-ai/
├── app/
│   ├── controllers/
│   │   └── egg_detector.py      # Controladores Flask
│   ├── services/
│   │   ├── inference_service.py # YOLO + desenho das detecções
│   │   └── inference_remote.py  # Cliente HTTP → microserviço
│   ├── static/
│   │   └── css/
│   │       └── main.css         # Estilos customizados
│   ├── templates/
│   │   ├── base.html           # Template base
│   │   ├── home.html           # Página inicial
│   │   └── app.html            # Aplicação principal
│   ├── app.py                  # Aplicação Flask principal
│   ├── inference_server.py     # Microserviço HTTP só de inferência
│   └── config.py               # Configurações compartilhadas (limiares + URL)
├── requirements.txt            # Dependências (web + microserviço)
├── env.example
└── README.md
```

O peso `egg_detection_yolov8n_final.pt` deve estar em `app/services/`, `app/` ou na raiz (ou use `MODEL_PATH`).

## 🎮 Como Usar

### 1. **Acesse o Sistema**
- Abra o navegador e vá para `http://localhost:5001`
- Clique em **"ENTRAR"** na página inicial

### 2. **Capture ou Carregue uma Imagem**
- **Upload**: Clique em "Selecionar Arquivo" e escolha uma imagem
- **Câmera**: Clique em "Abrir Câmera" para capturar uma foto

### 3. **Analise a Imagem**
- Clique em **"Analisar Imagem"**
- Aguarde o processamento (alguns segundos)

### 4. **Visualize os Resultados**
- Veja o resumo: ovos férteis, inférteis e total
- Examine a imagem com as detecções marcadas
- Analise os detalhes de cada detecção com nível de confiança

## ⚙️ Configurações

### Parâmetros do modelo (microserviço)
No `app/config.py`: `CONFIDENCE_THRESHOLD`, `IOU_THRESHOLD` (usados pelo `inference_server`).

### Variáveis de ambiente
- **`INFERENCE_SERVICE_URL`** — URL do microserviço; se omitida, usa `http://127.0.0.1:5002` (desenvolvimento local).
- **`INFERENCE_SERVER_PORT`** — porta do `inference_server.py` (padrão 5002).
- **`INFERENCE_REQUEST_TIMEOUT`** — timeout do cliente HTTP na web (padrão 120 s).
- **`MODEL_PATH`** — caminho absoluto do `.pt`, se não usar os diretórios padrão.

### Porta da app web
Em `app/app.py`, altere `port=5001` em `app.run(...)`.

## 🧪 Testando o Sistema

### Imagens Recomendadas
- **Formato**: JPG, PNG, JPEG
- **Tamanho**: Máximo 10MB
- **Qualidade**: Boa iluminação e foco
- **Conteúdo**: Ovos em diferentes estágios de desenvolvimento

### Dicas para Melhores Resultados
1. Use boa iluminação
2. Mantenha a câmera estável
3. Evite reflexos excessivos
4. Capture ovos individuais ou em pequenos grupos

## 📊 Performance

- **Velocidade**: ~100ms por imagem (GPU) / ~1s (CPU)
- **Precisão**: >95% em condições ideais
- **Modelo**: YOLOv8n (nano) - otimizado para velocidade
- **Tamanho**: Modelo compacto (~6MB)