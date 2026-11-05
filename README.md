# Empório da Música — Customer Support Agent

Project built for the AI Engineer technical challenge at Artefact. The goal is to prototype a text-based customer support assistant for **Empório da Música** (a fictional musical instrument store in Campo Grande/MS, Brazil), capable of answering questions about the product catalog, pricing, promotions, order status, and internal store policies.

---

## Project Structure

```text
Marcos_Desafio_Tecnico/
├── data/                       # Operational dataset (.csv) and store policy manual (.pdf)
├── examples/
│   └── exemplos_interacao.md   # Logged conversations tested with the agent
├── src/
│   ├── config.py               # Environment variable loading and data file path resolution
│   ├── data_loader.py          # Data ingestion and table joins using Pandas and PyPDF
│   ├── tools.py                # Query functions exposed to the LLM as tools
│   ├── prompts.py              # System prompt defining store persona and business rules
│   ├── memory.py               # Lightweight JSON conversation history persistence
│   └── agent.py                # LLM API integration and automatic tool execution loop
├── main.py                     # Interactive terminal chat interface (CLI)
├── requirements.txt            # Python dependencies
└── .env.example                # Environment variables template
```

---

## Setup & Execution

### 1. Environment and dependencies
With Python 3.10+ installed, create and activate a virtual environment in the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
*(On Linux/macOS, activate with `source .venv/bin/activate`).*

### 2. Environment variables
Copy `.env.example` to `.env` and set your OpenAI API key:

```powershell
Copy-Item .env.example .env
```

Inside `.env`:
```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
```

### 3. Run the CLI chat
```powershell
python main.py
```

Available CLI commands during the conversation:
- `/historico` — displays the messages recorded in the current session.
- `/limpar` — clears the current history and resets the conversation.
- `/sair` — exits the application.

---

## Technical Decisions

### Approach: Function Calling + Pandas (no vector database)
The store data consists of 6 small relational tables (`products`, `categories`, `promotions`, `orders`, `order_items`, `customers`) and an 8-page PDF manual (`politicas_da_loja.pdf`).

I chose not to use heavy orchestration frameworks (such as LangChain) or vector embeddings for the CSV files. Vector search performs poorly on exact numerical filters (e.g., *"acoustic guitars under R$ 1,000"*) and relational joins across foreign keys. Instead, the CSV tables are loaded and joined in memory using **Pandas** (`src/data_loader.py`), and 4 Python functions (`src/tools.py`) are exposed directly to the model via **Function Calling**:

1. `search_products`: filters the catalog by keyword, category ID, price ceiling, and stock availability.
2. `check_order_status`: looks up orders by ID or customer name, returning purchased items, status, and tracking codes.
3. `consult_store_policies`: retrieves relevant pages from the PDF manual using keyword matching (with a fallback to the full text, given the manual's small footprint).
4. `handle_out_of_scope_request`: handles requests for accessories (strings, cables, picks, amplifiers), which the store does not sell according to the manual, and redirects the customer to a local partner store in Campo Grande.

### Model Choice & Provider Migration (Gemini -> OpenAI)
Development started using the Google Gemini API (`google-genai`). However, during live testing, we ran into authentication conflicts between keys generated under Vertex AI Express mode (`AQ...`) and the standard AI Studio endpoint.

To resolve this bottleneck and ensure reliable tool calling, I migrated the primary provider in `src/agent.py` to **OpenAI (`gpt-4o-mini`)** using direct HTTP requests via `httpx`, while keeping Gemini support in the code as a fallback if `GEMINI_API_KEY` is provided. `gpt-4o-mini` proved fast, cost-effective, and consistent when deciding whether to invoke single or multiple tools in a turn.

### Data Processing & Business Rules
Upon inspecting the CSVs and the policy PDF, several business rules were enforced directly in the data layer (`src/data_loader.py` and `src/tools.py`) rather than relying solely on prompt instructions:

- **Expired vs. active promotions:** In `promotions.csv`, many promotions are marked with `is_active = 0` (for instance, the *Takamine GD20* had a 12% discount in the past that is no longer active). The data layer separates active discounts from expired ones so the agent never applies an inactive discount, while still being able to inform the customer transparently if asked about a past promotion.
- **5% PIX discount rule (Section 6.2):** Store policy states that promotions are not cumulative with the 5% PIX discount. The `pix_price_brl` column is pre-calculated following this rule.
- **Stock and product status:** A product is only marked as available if `status == 'active'` and `stock_quantity > 0` (e.g., the *Giannini GF-3D* has status `active` but `0` stock). When a customer searches for an unavailable item, the tool automatically returns in-stock alternatives from the same category.
- **Query normalization:** Text search strips accents and handles basic Portuguese plurals so queries like *"violões"* or *"violao"* properly match records registered as *"Violão"*.
- **PDF text cleanup:** Raw extraction via `pypdf` broke every word onto a new line; a regex cleanup step was added to normalize whitespace before passing sections to the LLM.

### Conversation History Persistence
Conversation turns are kept in memory during execution to preserve multi-turn context and are also persisted locally to `chat_history.json` (`src/memory.py`), allowing users to inspect or clear the session history.

---

## Interaction Examples

The file [`examples/exemplos_interacao.md`](examples/exemplos_interacao.md) contains 5 complete conversations (in Portuguese, matching the store's customer language) covering the scenarios suggested in the challenge:
1. Searching for available acoustic guitars under R$ 1,000.
2. Checking the price of the Takamine GD20 (handling its expired promotion and calculating PIX/installments).
3. Requesting an order return due to buyer's remorse — combining policy lookup with a real-time check on Order #8.
4. General questions about store address, business hours, and shipping deadlines.
5. Searching for an out-of-stock product combined with an out-of-scope request for accessories.

---

## Known Limitations & Future Improvements

- **Lexical catalog search:** Currently, `search_products` relies on normalized keyword matching across product names, categories, specs, and descriptions. With more time, I would add semantic search (embeddings) alongside the Pandas filters to better support open-ended queries (e.g., *"I want a small instrument to take on a trip"*).
- **Customer authentication for order lookup:** Order status can currently be queried using only the order ID or customer name. In a production environment (and in compliance with the LGPD section of the manual), verification via CPF, phone number, or OTP token would be required before exposing order details.
- **Business hours awareness:** The agent does not yet check the system clock to automatically notify customers when they message outside business hours (Mon–Fri 09:00–18:00, Sat 09:00–13:00).
- **Automated unit tests:** I would add a `pytest` suite to test the pricing/stock rules in `data_loader.py` and prevent prompt regressions.

---

## Use of AI Coding Assistants

I used the IDE's built-in AI assistant (**Antigravity**) during development as part of my workflow:
- Used it to quickly inspect the CSV schemas and cross-check rules from the policy PDF.
- Used it to troubleshoot the authentication issue with the Gemini API key and structure the migration to the OpenAI API in `src/agent.py`.
- Used it to refine the accent-insensitive Pandas search logic, build the terminal UI with `rich`, and review the project documentation.
