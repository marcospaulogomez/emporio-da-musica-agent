# Empório da Música — Agente de Atendimento

Projeto desenvolvido para o desafio técnico de AI Engineer da Artefact. O objetivo é prototipar um assistente de atendimento por texto para a **Empório da Música** (loja fictícia de instrumentos musicais em Campo Grande/MS), capaz de tirar dúvidas sobre catálogo, preços, promoções, status de pedidos e políticas internas.

---

## Estrutura do Projeto

```text
Marcos_Desafio_Tecnico/
├── data/                       # Base de dados operacional (.csv) e manual (.pdf)
├── examples/
│   └── exemplos_interacao.md   # Registro de conversas testadas com o agente
├── src/
│   ├── config.py               # Carregamento do .env e localização dos arquivos de dados
│   ├── data_loader.py          # Leitura e cruzamento das tabelas com Pandas e PyPDF
│   ├── tools.py                # Funções de consulta disponibilizadas para o modelo
│   ├── prompts.py              # Prompt de sistema com tom de voz e regras da loja
│   ├── memory.py               # Persistência simples do histórico em JSON
│   └── agent.py                # Integração com a API da LLM e execução das tools
├── main.py                     # Interface de chat via terminal (CLI)
├── requirements.txt            # Dependências Python
└── .env.example                # Exemplo de configuração de variáveis de ambiente
```

---

## Como Rodar

### 1. Ambiente e dependências
Com Python 3.10+ instalado, crie e ative um ambiente virtual na raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
*(No Linux/macOS, ative com `source .venv/bin/activate`).*

### 2. Variáveis de ambiente
Copie o arquivo `.env.example` para `.env` e adicione sua chave da OpenAI:

```powershell
Copy-Item .env.example .env
```

No arquivo `.env`:
```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
```

### 3. Executar o chat
```powershell
python main.py
```

Comandos úteis durante a conversa no terminal:
- `/historico` — mostra as mensagens trocadas na sessão.
- `/limpar` — apaga o histórico atual e reinicia a conversa.
- `/sair` — fecha o programa.

---

## Decisões Técnicas

### Abordagem: Function Calling + Pandas (sem banco vetorial)
Os dados da loja estão divididos em 6 tabelas pequenas (`products`, `categories`, `promotions`, `orders`, `order_items`, `customers`) e um PDF de 8 páginas (`politicas_da_loja.pdf`).

Optei por não usar frameworks pesados (como LangChain) nem RAG com embeddings para os arquivos CSV. Busca vetorial não funciona bem para filtros numéricos exatos (ex.: *"violões até R$ 1.000"*) ou cruzamento de chaves estrangeiras. Em vez disso, carreguei e relacionei os CSVs em memória usando **Pandas** (`src/data_loader.py`) e criei 4 ferramentas diretas em Python (`src/tools.py`) que o modelo chama sob demanda via **Function Calling**:

1. `search_products`: filtra produtos por termo, categoria, teto de preço e disponibilidade em estoque.
2. `check_order_status`: busca pedidos por ID ou nome do cliente, já trazendo os itens comprados e código de rastreio.
3. `consult_store_policies`: busca as páginas relevantes do manual em PDF por palavras-chave (com fallback para o texto completo, já que o manual todo é curto).
4. `handle_out_of_scope_request`: trata pedidos de acessórios (cordas, cabos, palhetas, amplificadores), que a loja não vende conforme o manual, indicando uma loja parceira em Campo Grande.

### Escolha do Modelo e Migração de Provedor (Gemini -> OpenAI)
O projeto começou sendo desenvolvido com a API do Google Gemini (`google-genai`). Porém, durante os testes práticos, tivemos conflitos de autenticação entre chaves geradas no modo Express da Vertex AI (`AQ...`) e o endpoint padrão do AI Studio.

Para destravar o desenvolvimento e garantir estabilidade na chamada de ferramentas, migrei o provedor principal em `src/agent.py` para a **OpenAI (`gpt-4o-mini`)** via requisições HTTP diretas com `httpx`, mantendo o suporte ao Gemini no código apenas como fallback caso alguém configure uma `GEMINI_API_KEY`. O `gpt-4o-mini` se mostrou rápido, barato e muito consistente para decidir quando chamar uma ou mais ferramentas na mesma pergunta.

### Tratamento dos Dados e Regras de Negócio
Ao analisar os CSVs e o PDF de políticas, tratei alguns pontos direto no código (`src/data_loader.py` e `src/tools.py`) para não depender apenas da interpretação do LLM:

- **Promoções vencidas vs. ativas:** No `promotions.csv`, várias promoções estão com `is_active = 0` (por exemplo, o violão *Takamine GD20* teve 12% de desconto no passado, mas hoje está inativo). O código separa promoções ativas das expiradas para que o agente nunca aplique um desconto vencido, mas saiba avisar o cliente caso ele pergunte da promoção antiga.
- **Desconto de 5% no PIX (Seção 6.2):** O manual define que promoções não são cumulativas com os 5% do PIX. A coluna `pix_price_brl` já é calculada respeitando essa regra.
- **Estoque e status:** Um produto só é considerado disponível se `status == 'active'` e `stock_quantity > 0` (o violão *Giannini GF-3D*, por exemplo, está ativo mas tem estoque `0`). Quando o cliente busca um item indisponível, a ferramenta já retorna alternativas da mesma categoria em estoque.
- **Normalização de busca:** A busca textual remove acentos e trata plurais simples para que termos como *"violões"* ou *"violao"* encontrem registros cadastrados como *"Violão"*.
- **Limpeza do PDF:** A extração bruta do `pypdf` quebrava cada palavra do manual em uma linha nova; apliquei uma limpeza simples com regex para normalizar o texto.

### Persistência de Histórico
O histórico da conversa fica salvo em memória durante a execução para manter o contexto entre as perguntas e também é gravado localmente em `chat_history.json` (`src/memory.py`), permitindo consultar ou limpar a sessão.

---

## Exemplos de Interação

No arquivo [`examples/exemplos_interacao.md`](examples/exemplos_interacao.md) estão registradas 5 conversas cobrindo os cenários pedidos no desafio:
1. Busca de violões disponíveis até R$ 1.000.
2. Consulta de preço do Takamine GD20 (tratando a promoção inativa e cálculo de PIX/parcelamento).
3. Pedido de devolução por arrependimento cruzando as regras do manual com a consulta em tempo real ao Pedido #8.
4. Dúvidas gerais sobre endereço, horário de funcionamento e frete.
5. Busca por produto sem estoque combinada com pedido de acessórios fora do escopo da loja.

---

## Limitações Conhecidas e O Que Faria Com Mais Tempo

- **Busca puramente lexical no catálogo:** Hoje a busca em `search_products` depende de palavras-chave contidas no nome, categoria, especificações ou descrição. Com mais tempo, adicionaria busca semântica (embeddings) combinada aos filtros do Pandas para lidar melhor com perguntas abertas (ex.: *"quero um instrumento pequeno para levar em viagem"*).
- **Validação de segurança para pedidos:** A consulta de pedidos aceita apenas o ID ou nome do cliente. Em um cenário real (e considerando a seção de LGPD do manual), seria necessário validar CPF, telefone ou token antes de exibir dados da compra.
- **Consciência de horário comercial:** O agente ainda não checa o horário atual do sistema para avisar automaticamente que o atendimento humano está fora do expediente (Seg–Sex 09h–18h, Sáb 09h–13h).
- **Testes automatizados:** Criaria uma suíte com `pytest` para validar separadamente as regras de preço/estoque do `data_loader.py` e casos de regressão do prompt.

---

## Uso de Assistentes de IA

Utilizei o assistente de IA integrado à IDE (**Antigravity**) como apoio durante o desenvolvimento. O fluxo de trabalho foi dividido assim:
- Usei a ferramenta para inspecionar rapidamente a estrutura dos CSVs e conferir as regras do PDF de políticas.
- Pedi ajuda para depurar o erro de autenticação que estava ocorrendo com a chave do Gemini e estruturar a troca rápida para a API da OpenAI em `src/agent.py`.
- Também utilizei para refinar a normalização de acentos nas buscas com Pandas, montar a interface no terminal com a biblioteca `rich` e revisar a documentação do projeto.
