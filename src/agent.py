from google import genai
from google.genai import types
from google.genai.errors import APIError
from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.prompts import STORE_SYSTEM_PROMPT
from src.tools import AVAILABLE_TOOLS
from src.memory import ConversationMemory


class EmporioMusicAgent:
    """
    Main agent controller integrating the official google-genai SDK,
    native automatic tool calling, system instructions, and conversation memory.
    """

    def __init__(self):
        if not GEMINI_API_KEY or GEMINI_API_KEY == "sua_chave_api_do_gemini_aqui":
            raise ValueError(
                "GEMINI_API_KEY não configurada. Por favor, defina sua chave no arquivo .env."
            )

        clean_key = GEMINI_API_KEY.strip().strip('"').strip("'")
        self.client = genai.Client(api_key=clean_key)
        self.model = GEMINI_MODEL
        self.memory = ConversationMemory()

        self.config = types.GenerateContentConfig(
            system_instruction=STORE_SYSTEM_PROMPT,
            tools=AVAILABLE_TOOLS,
            temperature=0.2,
        )

        # Native multi-turn chat session with automatic function calling (AFC)
        self._chat_session = self.client.chats.create(
            model=self.model,
            config=self.config,
        )

    def chat(self, user_message: str) -> str:
        """
        Sends a user message to the Gemini chat session, automatically executes
        any required Python tools, and returns the final assistant response.
        """
        try:
            response = self._chat_session.send_message(user_message)
            reply = response.text or "Desculpe, não consegui processar sua resposta no momento."
            self.memory.add_turn(user_message, reply)
            return reply
        except APIError as e:
            return (
                f"⚠️ Erro na comunicação com a API do Gemini (código {e.code}): {e.message}. "
                f"Verifique se o modelo '{self.model}' e sua GEMINI_API_KEY no arquivo .env estão válidos."
            )
        except Exception as e:
            return f"⚠️ Ocorreu um erro inesperado ao processar sua mensagem: {e}"

    def reset(self):
        """Resets the conversation history in memory and starts a fresh chat session."""
        self.memory.clear()
        self._chat_session = self.client.chats.create(
            model=self.model,
            config=self.config,
        )
