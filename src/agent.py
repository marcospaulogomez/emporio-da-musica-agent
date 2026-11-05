import json
import os
import httpx
from dotenv import load_dotenv
from src.prompts import STORE_SYSTEM_PROMPT
from src.tools import (
    search_products,
    check_order_status,
    consult_store_policies,
    handle_out_of_scope_request,
    AVAILABLE_TOOLS,
)
from src.memory import ConversationMemory

TOOL_DISPATCH = {
    "search_products": search_products,
    "check_order_status": check_order_status,
    "consult_store_policies": consult_store_policies,
    "handle_out_of_scope_request": handle_out_of_scope_request,
}

OPENAI_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": (
                "Searches the Empório da Música instrument catalog with filters for name/description, "
                "category (1: Guitarras, 2: Baixos, 3: Baterias e Percussão, 4: Teclados e Pianos, "
                "5: Violões, 6: Instrumentos de Sopro Madeiras, 7: Instrumentos de Sopro Metais, "
                "8: Cordas Orquestrais, 9: Ukuleles), maximum budget in BRL, and stock availability."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term for instrument name, brand, or specs (e.g., 'Takamine GD20', 'nylon', 'ukulele').",
                    },
                    "category_id": {
                        "type": "integer",
                        "description": "Category ID (1: Guitarras, 2: Baixos, 3: Baterias, 4: Teclados, 5: Violões, 6: Sopro Madeiras, 7: Sopro Metais, 8: Cordas Orquestrais, 9: Ukuleles).",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price in BRL (e.g., 1000.0).",
                    },
                    "only_available": {
                        "type": "boolean",
                        "description": "Whether to filter only in-stock active products (default: true).",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": (
                "Checks the status, tracking code, estimated delivery, payment method, and items "
                "of a customer order using the numerical order_id or customer_name."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "Numerical order ID (e.g., 8).",
                    },
                    "customer_name": {
                        "type": "string",
                        "description": "Customer full or partial name (e.g., 'Ana Carolina Ferreira').",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consult_store_policies",
            "description": (
                "Searches the Empório da Música internal policy manual (PDF) for official rules regarding "
                "store hours, address/contacts, payment & installment rules, return/exchange rights, "
                "shipping rates/deadlines, promotions rules, and warranty."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Keywords describing the policy topic (e.g., 'arrependimento devolução troca', 'endereço horário', 'frete entrega', 'parcelamento pix').",
                    },
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "handle_out_of_scope_request",
            "description": (
                "Handles requests for accessories or non-instrument items (strings, picks, cables, "
                "cases, pedals, amplifiers, maintenance services, or off-topic subjects)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "item_requested": {
                        "type": "string",
                        "description": "Name of the accessory or out-of-scope item requested by the customer.",
                    },
                },
                "required": ["item_requested"],
            },
        },
    },
]


class EmporioMusicAgent:
    """
    Main agent controller supporting OpenAI (gpt-4o-mini / gpt-4o) with automatic
    function calling, system instructions, and persistent conversation memory.
    """

    def __init__(self):
        load_dotenv(override=True)
        raw_openai_key = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
        raw_gemini_key = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")

        # Accept OpenAI key from either OPENAI_API_KEY or GEMINI_API_KEY (if user pasted sk-... there)
        if raw_openai_key and not raw_openai_key.startswith("cole_sua_chave") and not raw_openai_key.startswith("sua_chave"):
            self.api_key = raw_openai_key
            self.provider = "openai"
        elif raw_gemini_key.startswith("sk-"):
            self.api_key = raw_gemini_key
            self.provider = "openai"
        elif raw_gemini_key and not raw_gemini_key.startswith("sua_chave"):
            self.api_key = raw_gemini_key
            self.provider = "gemini"
        else:
            raise ValueError(
                "Chave de API não configurada! Abra o arquivo .env, cole sua chave em "
                "OPENAI_API_KEY=sk-... e salve o arquivo (Ctrl+S)."
            )

        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() if self.provider == "openai" else os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.memory = ConversationMemory()
        self._messages: list[dict] = [
            {"role": "system", "content": STORE_SYSTEM_PROMPT}
        ]

        if self.provider == "gemini":
            from google import genai
            from google.genai import types
            use_vertex = self.api_key.startswith("AQ.")
            self.gemini_client = genai.Client(api_key=self.api_key, vertexai=use_vertex)
            self.gemini_config = types.GenerateContentConfig(
                system_instruction=STORE_SYSTEM_PROMPT,
                tools=AVAILABLE_TOOLS,
                temperature=0.2,
            )
            self._chat_session = self.gemini_client.chats.create(
                model=self.model,
                config=self.gemini_config,
            )

    def _chat_openai(self, user_message: str) -> str:
        """Executes multi-turn chat and automatic tool calling against the OpenAI API."""
        self._messages.append({"role": "user", "content": user_message})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=45.0) as client:
            for _ in range(6):
                payload = {
                    "model": self.model,
                    "messages": self._messages,
                    "tools": OPENAI_TOOLS_SCHEMA,
                    "tool_choice": "auto",
                    "temperature": 0.2,
                }
                resp = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )

                if resp.status_code != 200:
                    try:
                        err_detail = resp.json().get("error", {}).get("message", resp.text)
                    except Exception:
                        err_detail = resp.text
                    # Remove failed user turn so user can retry cleanly
                    self._messages.pop()
                    return (
                        f"⚠️ Erro na API da OpenAI (código {resp.status_code}): {err_detail}\n"
                        f"Verifique se sua `OPENAI_API_KEY` no arquivo `.env` está correta e possui saldo/créditos."
                    )

                data = resp.json()
                choice_msg = data["choices"][0]["message"]
                self._messages.append(choice_msg)

                tool_calls = choice_msg.get("tool_calls")
                if not tool_calls:
                    reply = choice_msg.get("content") or "Desculpe, não consegui processar sua resposta."
                    self.memory.add_turn(user_message, reply)
                    return reply

                # Execute each requested tool call and append results to conversation
                for tc in tool_calls:
                    fn_name = tc["function"]["name"]
                    raw_args = tc["function"].get("arguments", "{}")
                    try:
                        fn_args = json.loads(raw_args) if raw_args else {}
                    except Exception:
                        fn_args = {}

                    fn = TOOL_DISPATCH.get(fn_name)
                    if fn:
                        try:
                            tool_output = str(fn(**fn_args))
                        except Exception as exc:
                            tool_output = f"Erro ao executar ferramenta {fn_name}: {exc}"
                    else:
                        tool_output = f"Ferramenta '{fn_name}' não encontrada."

                    self._messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": fn_name,
                        "content": tool_output,
                    })

        return "Desculpe, o limite de chamadas de ferramentas foi excedido para esta pergunta."

    def chat(self, user_message: str) -> str:
        """
        Sends a user message to the configured LLM provider (OpenAI by default),
        automatically executes any required Python tools, and returns the response.
        """
        if self.provider == "openai":
            try:
                return self._chat_openai(user_message)
            except Exception as e:
                return f"⚠️ Erro ao comunicar com a OpenAI: {e}"

        try:
            response = self._chat_session.send_message(user_message)
            reply = response.text or "Desculpe, não consegui processar sua resposta."
            self.memory.add_turn(user_message, reply)
            return reply
        except Exception as e:
            return f"⚠️ Erro ao comunicar com a API: {e}"

    def reset(self):
        """Resets the conversation history in memory and starts a fresh chat session."""
        self.memory.clear()
        self._messages = [
            {"role": "system", "content": STORE_SYSTEM_PROMPT}
        ]
        if self.provider == "gemini":
            self._chat_session = self.gemini_client.chats.create(
                model=self.model,
                config=self.gemini_config,
            )
