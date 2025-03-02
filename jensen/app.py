# Paste pre-Pyrfected Python
import os
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
            "I'm Jensen your personal LLaMA 2 powered chatbot."
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "To engage in a conversation with me just start typing.\n\nThe commands I understand:\n/about - some information about me Jensen\n/clear - clear prompt history"
        )

    def init_prompt(self):
        self.history = [
            {
                "role": "system",
                "content": "You are an intelligent assistant providing helpful information.",
            },
        ]

    async def clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.init_prompt()
        await update.message.reply_text("Prompt history cleared.")

    def create_prompt(self, string):
        return {"role": "user", "content": string}

    def remove_prompt_from_history(self):
        # Remove first user and assistant prompts
        self.history.pop(1)
        self.history.pop(1)

    def prompt_llm(self, prompt):
        self.history.append(prompt)
        response = self.LLM.create_chat_completion(
            messages=self.history, max_tokens=self.MAX_TOKENS
        )
        self.history.append(
            {
                "role": "assistant",
                "content": response["choices"][0]["message"]["content"],
            }
        )
        return response["choices"][0]["message"]["content"]

    async def assist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=constants.ChatAction.TYPING
        )
        prompt = self.create_prompt(update.message.text)
        print("-------------- PROMPT --------------")
        print(prompt)

        start = timer()

        try:
            assistant = self.prompt_llm(prompt)
        except ValueError:
            await update.message.reply_text(
                "Woops, something went wrong. Trying again after removing some prompt history."
            )
            self.remove_prompt_from_history()
            prompt = self.create_prompt(update.message.text)
            assistant = self.prompt_llm(prompt)

        print(assistant)

        end = timer()

        print(f"DURATION: {int(end - start)} seconds.")
        print("-------------------------------------")
        print("-------------- HISTORY --------------")
        print(self.history)
        print("-------------------------------------")

        await update.message.reply_text(assistant)


if __name__ == "__main__":
    import traceback

    try:
        jensen = Jensen()
        jensen.run()
    except Exception:
        print(traceback.format_exc())
