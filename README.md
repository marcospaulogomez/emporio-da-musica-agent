# 🎸 Empório da Música — Agente Inteligente de Atendimento ao Cliente

> **Desafio Técnico — AI Engineer (Artefact)**  
> Protótipo de agente conversacional em Python para automação e suporte ao atendimento da **Empório da Música** (Campo Grande/MS), integrando **Function Calling (OpenAI `gpt-4o-mini` / Gemini)**, **consulta relacional em tempo real (Pandas)** e **recuperação contextual de políticas (PDF)**.

---

## 📌 Visão Geral da Solução

A **Empório da Música** é uma loja especializada exclusivamente em instrumentos musicais, fundada em 2008 em Campo Grande/MS. Para aliviar a sobrecarga da equipe de atendimento humano com dúvidas recorrentes (preços, estoque, promoções, rastreio de pedidos, prazos de entrega e regras de troca/devolução), este projeto implementa o **`EmporioMusicAgent`**.

O agente foi projetado para:
1. **Assumir a persona oficial da loja** (Seção 7.1 do manual): tom informal, acolhedor, prestativo e tecnicamente seguro — como um amigo músico experiente.
2. **Consultar dados operacionais em tempo real** (`data/*.csv`): cruzando produtos, categorias, promoções ativas/expiradas, clientes, pedidos e itens de pedido sem alucinar valores.
3. **Aplicar regras de negócio complexas do manual interno** (`data/politicas_da_loja.pdf`):
   - **Não cumulatividade de descontos (Seção 6.2):** O desconto de 5% no PIX aplica-se apenas a produtos sem promoção ativa (`is_active == 1`).
   - **Transparência em promoções expiradas (Seção 7.3):** Identifica campanhas vencidas (`is_active == 0`), informa o preço vigente e nunca promete descontos encerrados.
   - **Produtos sem estoque ou descontinuados (Seção 7.3):** Filtra disponibilidade real (`status == 'active'` e `stock_quantity > 0`) e sugere automaticamente substitutos equivalentes da mesma categoria.
   - **Direito de arrependimento, trocas e garantias (Seção 4 e 8):** Distingue devolução online (7 dias corridos após o recebimento), troca por preferência (7 dias), troca por defeito na loja (30 dias) e garantia legal/fabricante (90 dias / 6 meses a 2 anos).
4. **Impor Guardrails de Escopo (Seção 1 e 7.1):** Recusa educadamente a venda de acessórios (cordas avulsas, cabos, palhetas, cases, pedais, amplificadores), redirecionando o cliente para uma loja parceira local em Campo Grande/MS, além de tratar perguntas fora do contexto da loja.

---

## 🏗️ Arquitetura do Projeto

```text
Marcos_Desafio_Tecnico/
├── data/
│   ├── categories.csv          # Categorias de instrumentos (IDs 1 a 9)
│   ├── customers.csv           # Cadastro de clientes
│   ├── orders.csv              # Pedidos, status, rastreio e método de pagamento
│   ├── order_items.csv         # Relação N:N entre pedidos e produtos
│   ├── products.csv            # Catálogo de instrumentos, preços, specs e estoque
│   ├── promotions.csv          # Histórico de promoções ativas (1) e expiradas (0)
│   └── politicas_da_loja.pdf   # Manual oficial de políticas e procedimentos (v2.1)
├── examples/
│   └── exemplos_interacao.md   # 5 conversas completas demonstrando cenários reais e não triviais
├── src/
│   ├── __init__.py
│   ├── config.py               # Carregamento de variáveis de ambiente (.env) e resolução de caminhos
│   ├── data_loader.py          # Camada de ingestão, limpeza e joins relacionais (StoreDataStore)
│   ├── tools.py                # Ferramentas (Tools) expostas ao LLM via Function Calling
│   ├── prompts.py              # System Prompt estruturado com persona e guardrails de negócio
│   ├── memory.py               # Gerenciamento e persistência local do histórico (JSON)
│   └── agent.py                # Controlador principal (EmporioMusicAgent) com OpenAI Function Calling
├── main.py                     # Interface de linha de comando (CLI) interativa com Rich
├── requirements.txt            # Dependências do projeto
├── .env.example                # Template de configuração de variáveis de ambiente
└── README.md                   # Documentação técnica e justificativas de arquitetura
```

---

## ⚙️ Instruções para Rodar o Projeto

### 1. Pré-requisitos
- **Python 3.10+** instalado.
- Uma chave de API da **OpenAI** (`OPENAI_API_KEY`, ex.: `sk-...`). *(O controlador também suporta chaves do Google Gemini `GEMINI_API_KEY` de forma transparente caso o avaliador prefira).*

### 2. Configuração do Ambiente Virtual e Dependências

No terminal (PowerShell, CMD, Bash ou Zsh), na pasta raiz do projeto:

```bash
# 1. Crie o ambiente virtual (caso ainda não exista)
python -m venv .venv

# 2. Ative o ambiente virtual
# No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# No Linux / macOS:
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração das Variáveis de Ambiente (`.env`)

Copie o arquivo `.env.example` para `.env` e insira sua chave de API da OpenAI:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

Conteúdo do arquivo `.env`:
```env
OPENAI_API_KEY=sua_chave_api_da_openai_aqui
OPENAI_MODEL=gpt-4o-mini
```

### 4. Executando o Agente (CLI Interativa)

```bash
python main.py
```

Durante a execução na CLI, você pode conversar livremente com o assistente ou usar os comandos especiais:
- `/historico` — Exibe todos os turnos salvos na sessão atual.
- `/limpar` — Reinicia o contexto da conversa e limpa o arquivo de histórico local.
- `/sair` — Encerra o atendimento.

---

## 🧠 Justificativa das Decisões Técnicas

### 1. Framework e Abordagem do Agente: *Híbrido (Function Calling + Camada Relacional Pandas + Retrieval de PDF)*
Em vez de utilizar frameworks pesados com múltiplas camadas de abstração (como LangChain ou LlamaIndex) para um conjunto de dados estruturado e de volume controlado, optamos por um ciclo enxuto e transparente de **Tool/Function Calling** combinado a uma camada de dados determinística em **Pandas** (`StoreDataStore`).
- **Por que não usar RAG vetorial para os CSVs?** Embeddings vetoriais são imprecisos para filtros numéricos exatos (`preço <= R$ 1.000`, `stock_quantity > 0`), agregações e joins entre 6 tabelas (`products`, `categories`, `promotions`, `orders`, `order_items`, `customers`). Ao pré-processar os relacionamentos no `data_loader.py` e expor funções tipadas em Python (`search_products`, `check_order_status`), garantimos **100% de exatidão matemática** nos preços, descontos e estoques.
- **Por que Retrieval por Seções Ranqueadas para o PDF?** O manual `politicas_da_loja.pdf` possui 8 páginas enxutas (~1.200 palavras). A ferramenta `consult_store_policies` extrai o texto via `pypdf`, normaliza acentuação, remove *stopwords* e ranqueia as páginas por densidade de palavras-chave (com *fallback* para o documento integral). Isso elimina dependências externas de bancos vetoriais (Chroma/FAISS), reduz a latência a zero e evita perda de contexto em regras cruzadas.

### 2. Modelo e Provedor: *OpenAI (`gpt-4o-mini`) com suporte dual a Gemini*
- Escolhemos o **`gpt-4o-mini`** da OpenAI como modelo principal por sua altíssima confiabilidade em **Function Calling multi-ferramenta** (sendo capaz de chamar `consult_store_policies` e `check_order_status` na mesma rodada ou em sequência), excelente domínio do Português do Brasil, baixa latência e ótimo custo-benefício.
- Adicionalmente, o controlador `EmporioMusicAgent` em `src/agent.py` foi arquitetado de forma agnóstica para aceitar também `GEMINI_API_KEY` (`gemini-2.5-flash`), facilitando os testes pelo time avaliador independentemente do provedor que tenham disponível.
- A temperatura foi configurada em **`0.2`** para priorizar fidelidade factual aos dados retornados pelas ferramentas, mantendo a fluidez e simpatia da persona.

### 3. Tratamento de Dados e Regras de Negócio Pré-Computadas (`src/data_loader.py`)
Durante a análise exploratória das tabelas em `data/`, identificamos situações críticas de negócio que foram tratadas diretamente na camada de dados:
- **Relacionamento de Promoções Ativas vs. Expiradas:** A tabela `promotions.csv` contém tanto promoções vigentes (`is_active == 1`) quanto encerradas (`is_active == 0`), inclusive com múltiplas entradas históricas para um mesmo produto (ex.: ID 93 e ID 96). O `StoreDataStore` separa ambas, calcula `final_price_brl` aplicando apenas descontos ativos e mantém o registro da promoção expirada (`expired_promo_name`) para que o agente possa explicar transparentemente ao cliente quando uma oferta já encerrou (ex.: *Takamine GD20* com 12% OFF expirado).
- **Cálculo Determinístico do PIX (Seção 6.2):** A coluna `pix_price_brl` já aplica automaticamente os 5% de desconto apenas quando `has_active_promo == False`, impedindo que o LLM acumule descontos indevidamente.
- **Disponibilidade Real (`is_available`):** Combina `status == "active"` e `stock_quantity > 0`. Produtos esgotados (como *Giannini GF-3D*, estoque `0`), descontinuados (*Shelby SN-7C*, *Ibanez Bass 2X*) ou em pré-lançamento (*Kala KA-ABP-CTG*, `coming_soon`) são sinalizados com transparência e acompanhados automaticamente de até 5 sugestões disponíveis da mesma categoria (`src/tools.py`).
- **Busca Insensível a Acentos e Plurais:** A função `search_products` normaliza caracteres Unicode (`NFKD`) e radicais em português (permitindo que buscas por `"violões"`, `"violao"` ou `"violão"` encontrem todos os itens relevantes combinando nome, descrição, categoria e JSON de `specs`).

### 4. Persistência do Histórico de Conversa (`src/memory.py`)
- O contexto multi-turno em tempo de execução é mantido na lista estruturada de mensagens (`self._messages`) do controlador, permitindo que o agente lembre o nome do cliente, o produto discutido na mensagem anterior e o histórico de chamadas de ferramentas.
- Adicionalmente, implementamos a classe `ConversationMemory`, que persiste cada turno (`timestamp`, `user`, `assistant`) em disco no arquivo `chat_history.json`, permitindo auditoria das conversas e consulta via comando `/historico` na CLI.

### 5. Estratégia de Prompt e Guardrails (`src/prompts.py`)
- O `STORE_SYSTEM_PROMPT` foi desenhado com instruções hierárquicas claras:
  1. **Persona e Fluxo de Atendimento (Seção 7.1 e 7.2):** Saudação cordial, investigação da necessidade, consulta obrigatória às ferramentas, resposta estruturada e fechamento amigável.
  2. **Guardrail Anti-Alucinação:** Proibição explícita de responder sobre preços, estoque ou pedidos sem invocar as ferramentas.
  3. **Guardrail de Escopo e Redirecionamento (Seção 1 e 7.1):** Como o manual instrui sugerir lojas parceiras quando o cliente pede acessórios, definimos uma parceira local fictícia em Campo Grande/MS (**Pantanal Music & Acessórios**) na ferramenta `handle_out_of_scope_request`, garantindo uma experiência consistente e prestativa.

---

## 💬 Exemplos de Interação

Os exemplos completos de conversas (incluindo os cenários sugeridos no desafio e situações não triviais de cruzamento de dados em tempo real) estão documentados em:
👉 **[`examples/exemplos_interacao.md`](examples/exemplos_interacao.md)**

Cenários cobertos no documento:
1. *"Quais opções de violões disponíveis custando até R$ 1.000?"* (Filtro de catálogo + regra do PIX + exclusão de esgotados).
2. *"Quanto custa o Takamine GD20? Ele ainda está naquela promoção de 12%?"* (Consulta de preço + transparência sobre promoção expirada + regras de parcelamento e frete grátis em Campo Grande).
3. *"Me arrependi da minha compra, posso devolver meu pedido?"* (Conversa multi-turno não trivial cruzando regras do CDC/Manual de Políticas com consulta em tempo real ao Pedido #8 da cliente Ana Carolina Ferreira).
4. *"Qual o endereço e o horário de funcionamento da loja? Vocês entregam em Dourados/MS?"* (Informações gerais e prazos de PAC, SEDEX e Jadlog).
5. *"Vocês têm o violão Giannini GF-3D Sunburst? E quero levar cordas, cabo P10 e amplificador."* (Tratamento simultâneo de produto sem estoque com sugestão de substitutos + guardrail de acessórios fora do escopo).

---

## ⚠️ Limitações Conhecidas e Próximos Passos (Com Mais Tempo)

1. **Busca Semântica Híbrida (BM25 + Embeddings):** Atualmente, a busca no catálogo utiliza correspondência lexical normalizada por tokens/radicais e filtros estruturados. Com mais tempo e para um catálogo de milhares de itens, implementaríamos uma busca híbrida combinando filtros SQL/Pandas com *embeddings* semânticos (ex.: quando o cliente pede *"um instrumento acústico leve para tocar na praia"*, associando semanticamente a ukuleles e violões compactos).
2. **Autenticação e Segurança na Consulta de Pedidos (LGPD — Seção 9):** Atualmente, `check_order_status` permite buscar pedidos pelo `order_id` ou `customer_name`. Em produção, exigiríamos validação de dois fatores (ex.: confirmação de CPF/telefone ou token via WhatsApp) antes de exibir dados de endereço/entrega.
3. **Verificação Automática de Horário de Expediente:** Integrar o relógio do sistema (`America/Campo_Grande`, UTC-4) ao agente para detectar automaticamente quando uma mensagem chega fora do horário comercial (Seg–Sex 09h–18h, Sáb 09h–13h) e incluir o aviso automático de retorno humano previsto na Seção 2 e 7.1 do manual.
4. **Registro Persistente de Reclamações e Devoluções (Write Tools):** Criar ferramentas de escrita em banco de dados (SQLite/PostgreSQL) para abrir protocolos formais de devolução ou registrar reclamações com SLA de 24 horas úteis (Seção 7.3).
5. **Interface Web / Integração WhatsApp:** Expor o agente via **FastAPI** integrado à API oficial do WhatsApp Business (Meta Cloud API) ou a uma interface web interativa em **Streamlit / Chainlit**.

---

## 🤖 Uso de Assistentes de Código (Workflow com IA)

Em conformidade com as diretrizes de transparência do desafio:
- **Ferramenta utilizada:** Assistente de IA integrado à IDE (**Google Antigravity**).
- **Como foi utilizado no workflow:**
  1. **Análise Exploratória e Verificação de Regras:** Apoio na inspeção cruzada entre as 6 tabelas `.csv` e as 8 páginas do `politicas_da_loja.pdf` para mapear casos de borda (como promoções expiradas `is_active == 0`, produtos com `stock_quantity == 0` ou status `discontinued`/`coming_soon`, e não cumulatividade do PIX).
  2. **Depuração e Refinamento de Código:** Implementação de Function Calling com suporte a OpenAI (`gpt-4o-mini`) e Gemini, normalização de acentuação/plurais nas buscas em Pandas (`src/tools.py`), tratamento de codificação UTF-8 no terminal Windows e construção da interface CLI com a biblioteca `rich` (`main.py`).
  3. **Documentação e Casos de Teste:** Estruturação da documentação técnica no `README.md` e validação dos cenários de conversação em `examples/exemplos_interacao.md`.
