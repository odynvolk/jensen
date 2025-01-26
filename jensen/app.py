import os
from timeit import default_timer as timer

from dotenv import load_dotenv
from llama_cpp import Llama
from telegram import Bot, Update, constants
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()


class Jensen(object):
    def __init__(self):
        self.MODEL_PATH = os.getenv("MODEL_PATH")
        self.N_CTX = int(os.getenv("N_CTX")) if os.getenv("N_CTX") else 512
        self.N_GPU_LAYERS = int(os.getenv("N_GPU_LAYERS")) if os.getenv("N_GPU_LAYERS") else 0
        self.N_THREADS = int(os.getenv("N_THREADS")) if os.getenv("N_THREADS") else None
        self.MAX_TOKENS = int(os.getenv("MAX_TOKENS")) if os.getenv("MAX_TOKENS") else 512
        self.USE_MLOCK = os.getenv("USE_MLOCK").lower() == "true" if os.getenv("USE_MLOCK") else False

        self.PROMPT_FORMAT = os.getenv("PROMPT_FORMAT").lower() if os.getenv("PROMPT_FORMAT") else "vicuna"

        self.API_KEY = os.getenv("API_KEY")
        self.POLL_INTERVAL = float(os.getenv("POLL_INTERVAL")) if os.getenv("POLL_INTERVAL") else 1.0

        self.history = ""

        self.LLM = Llama(model_path=self.MODEL_PATH, n_ctx=self.N_CTX, n_gpu_layers=self.N_GPU_LAYERS,
                         n_threads=self.N_THREADS, use_mlock=self.USE_MLOCK)

        self.application = Application.builder().token(self.API_KEY).build()

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("about", self.about))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("clear", self.clear))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.assist))

    def run(self):
        self.application.run_polling(poll_interval=self.POLL_INTERVAL, allowed_updates=Update.ALL_TYPES)

    def split_string(self, string, n=4000):
        return [string[i:i + n] for i in range(0, len(string), n)]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Welcome back sir!")

    async def about(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("I'm Jensen your personal LLaMA 2 powered chatbot.")

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "To engage in a conversation with me just start typing.\n\nThe commands I understand:\n/about - some information about me Jensen\n/clear - clear prompt history")

    async def clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.history = ""
        await update.message.reply_text("Prompt history cleared.")

    def create_prompt(self, string):
        history = f"{self.history}\n" if len(self.history) > 1 else self.history

        if self.PROMPT_FORMAT == "alpaca":
            return f"{history}### Instruction:\n{string}\n\n### Response:\n"
        elif self.PROMPT_FORMAT == "nous":
            return f"{history}### human:\n{string}\n\n### response:"
        elif self.PROMPT_FORMAT == "openchat":
            return f"{history}\nGPT4 User: {string}<|end_of_turn|>GPT4 Assistant:"
        elif self.PROMPT_FORMAT == "mistral":
            return f"{history}\n[INST]{string}[/INST]\n"
        elif self.PROMPT_FORMAT == "deepseek":
            system_prompt = "You are a helpful assistant"
            return f"{history}\n<｜begin▁of▁sentence｜>{system_prompt}<｜User｜>{string}<｜Assistant｜>"
        return f"{history}USER: {string}\nASSISTANT: "

    def remove_prompt_from_history(self, n=2):
        if self.PROMPT_FORMAT == "alpaca":
            prompt_string = "### Instruction:"
        elif self.PROMPT_FORMAT == "nous":
            prompt_string = "### human:"
        else:
            prompt_string = "USER:"

        try:
            for i in range(n):
                start_index = self.history.index(prompt_string)
                end_index = self.history.index(prompt_string, start_index + 7)
                self.history = f"{self.history[0:start_index]}{self.history[end_index:]}"
                print("------------ NEW HISTORY ------------")
                print(self.history)
                print("-------------------------------------")
        except ValueError:
            pass

    def prompt_llm(self, prompt):
        output = self.LLM(prompt, max_tokens=self.MAX_TOKENS)
        text = output["choices"][0]["text"];
        return text[text.index("</think>") + 10:]

    async def assist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=constants.ChatAction.TYPING)
        prompt = self.create_prompt(update.message.text)
        print("-------------- PROMPT --------------")
        print(prompt)

        start = timer()

        try:
            assistant = self.prompt_llm(prompt)
        except ValueError:
            await update.message.reply_text(
                "Woops, something went wrong. Trying again after removing some prompt history.")
            self.remove_prompt_from_history()
            prompt = self.create_prompt(update.message.text)
            assistant = self.prompt_llm(prompt)

        print(assistant)

        end = timer()

        print(f"DURATION: {int(end - start)} seconds.")
        self.history = f"{prompt}{assistant}"
        print("-------------------------------------")
        print("-------------- HISTORY --------------")
        print(self.history)
        print("-------------------------------------")

        for reply in self.split_string(assistant):
            stripped = reply.strip()
            if len(stripped) == 0:
                await update.message.reply_text("I'm sorry, I don't have an answer.")
            else:
                await update.message.reply_text(stripped)


if __name__ == "__main__":
    import traceback

    try:
        jensen = Jensen()
        jensen.run()
    except Exception:
        print(traceback.format_exc())
