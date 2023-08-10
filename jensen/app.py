import os
from dotenv import load_dotenv
from llama_cpp import Llama
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

class Robin(object):
    def __init__(self):
        self.MODEL_PATH = os.getenv("MODEL_PATH")
        self.N_CTX = int(os.getenv("N_CTX"))
        self.MAX_TOKENS = int(os.getenv("MAX_TOKENS"))

        self.API_KEY = os.getenv("API_KEY")

        self.history = ""

        self.LLM = Llama(model_path=self.MODEL_PATH, n_ctx=self.N_CTX)

    def run(self):
        application = Application.builder().token(self.API_KEY).build()

        application.add_handler(CommandHandler("clear", self.clear))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.assist))
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        print("-------------- clear --------------")
        self.history = ""
        await update.message.reply_text("History cleared.")

    async def assist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        prompt = f"{self.history}User: {update.message.text}\nAssistant: "
        print("-------------- assist --------------")
        print(prompt)
        output = self.LLM(prompt, max_tokens=self.MAX_TOKENS)
        assistant = output["choices"][0]["text"]

        print(assistant)
        self.history = f"${self.history}{prompt}{assistant}\n"
        print("-------------- history --------------")
        print(self.history)
        await update.message.reply_text(assistant)

if __name__ == "__main__":
    import traceback
    try:
        robin = Robin()
        robin.run()
    except Exception:
        print(traceback.format_exc())
        