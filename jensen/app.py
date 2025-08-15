import os
import re
from timeit import default_timer as timer

from dotenv import load_dotenv
from llama_cpp import Llama
from telegram import Update, constants
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

class Jensen(object):
    def __init__(self):
        self.MODEL_PATH = os.getenv("MODEL_PATH")
        self.N_CTX = int(os.getenv("N_CTX")) if os.getenv("N_CTX") else 512
        self.N_GPU_LAYERS = (
            int(os.getenv("N_GPU_LAYERS")) if os.getenv("N_GPU_LAYERS") else 0
        )
        self.N_THREADS = int(os.getenv("N_THREADS")) if os.getenv("N_THREADS") else None
        self.MAX_TOKENS = (
            int(os.getenv("MAX_TOKENS")) if os.getenv("MAX_TOKENS") else 512
        )
        self.USE_MLOCK = (
            os.getenv("USE_MLOCK").lower() == "true"
            if os.getenv("USE_MLOCK")
            else False
        )

        self.API_KEY = os.getenv("API_KEY")
        self.POLL_INTERVAL = (
            float(os.getenv("POLL_INTERVAL")) if os.getenv("POLL_INTERVAL") else 1.0
        )

        self.init_prompt()

        self.LLM = Llama(
            model_path=self.MODEL_PATH,
            n_ctx=self.N_CTX,
            n_gpu_layers=self.N_GPU_LAYERS,
            n_threads=self.N_THREADS,
            use_mlock=self.USE_MLOCK,
            ubatch_size=512,
            batch_size=512,
        )

        self.application = Application.builder().token(self.API_KEY).build()

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("about", self.about))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("clear", self.clear))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.assist)
        )

    def run(self):
        self.application.run_polling(
            poll_interval=self.POLL_INTERVAL, allowed_updates=Update.ALL_TYPES
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Welcome back sir!")

    async def about(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "I'm Jensen your personal LLM powered chatbot."
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "To engage in a conversation with me just start typing.\n\nThe commands I understand:\n/about - some information about me Jensen\n/clear - clear prompt history"
        )

    def init_prompt(self):
        system_instruction = os.getenv("SYSTEM_INSTRUCTION") if os.getenv("SYSTEM_INSTRUCTION") else "You are an intelligent assistant providing helpful information."
        self.history = [
            {
                "role": "system",
                "content": system_instruction.strip(),
            },
        ]

    async def clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.init_prompt()
        await update.message.reply_text("Prompt history cleared.")

    def create_prompt(self, string):
        return {"role": "user", "content": string}

    def remove_prompt_from_history(self):
        # Remove fist user prompts and assistant answers
        self.history.pop(1)
        self.history.pop(1)

    def clean_reply(self, reply):
        return reply.replace("<think>\n\n</think>\n\n", "")

    def prompt_llm(self, prompt):
        self.history.append(prompt)
        response = self.LLM.create_chat_completion(
            messages=self.history, max_tokens=self.MAX_TOKENS
        )
        reply = self.clean_reply(response["choices"][0]["message"]["content"])
        self.history.append(
            {
                "role": "assistant",
                "content": reply,
            }
        )
        return reply

    async def assist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=constants.ChatAction.TYPING
        )
        prompt = self.create_prompt(update.message.text.strip())
        print("-------------- PROMPT --------------")
        print(prompt)

        start = timer()

        try:
            reply = self.prompt_llm(prompt)
        except ValueError as e:
            print(e)
            self.init_prompt()
            reply = self.prompt_llm(prompt)

        print(reply)

        end = timer()

        print(f"DURATION: {int(end - start)} seconds.")
        print("-------------------------------------")
        print("-------------- HISTORY --------------")
        print(self.history)
        print("-------------------------------------")

        chunked_replies = self.chunk_string_by_paragraph(reply)
        print(f"chunked_replies: {chunked_replies}")
        for chunked_reply in chunked_replies:
          await update.message.reply_text(chunked_reply)

    def chunk_string_by_paragraph(self, text: str, max_length: int = 3584) -> list[str]:
        """
        Chunks a string into parts of at most `max_length` characters,
        ensuring that each chunk contains complete paragraphs.

        Args:
            text (str): The input string to be chunked.
            max_length (int): The maximum length of each chunk.

        Returns:
            list[str]: A list of chunks, each containing complete paragraphs.
        """
        if not text or max_length <= 0:
            return []

        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + (2 if current_chunk else 0) > max_length:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = ""

            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph

        if current_chunk:
            chunks.append(current_chunk)

        return chunks


if __name__ == "__main__":
    import traceback

    try:
        jensen = Jensen()
        jensen.run()
    except Exception:
        print(traceback.format_exc())
