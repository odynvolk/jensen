import os
from dotenv import load_dotenv
from llama_cpp import Llama
from telegram import Bot, Update, constants
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

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("about", self.about))
        application.add_handler(CommandHandler("help", self.help))
        application.add_handler(CommandHandler("clear", self.clear))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.assist))
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    def split_string(self, string, n = 4000):
        return [string[i:i+n] for i in range(0, len(string), n)]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Welcome back sir!")

    async def about(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("I'm Jensen your personal Llama 2 powered chatbot.")

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("To engage in a conversatiom with me just start typing.\n\nThe commands I understand:\n/about - some information about me Jensen\n/clear - clear prompt history")

    async def clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.history = ""
        await update.message.reply_text("Prompt history cleared.")
    
    async def assist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        print("-------------- assist --------------")
        await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=constants.ChatAction.TYPING)
        prompt = f"{self.history}User: {update.message.text}\nAssistant: "
        # prompt = f"User: {update.message.text}\nAssistant: "
        print(prompt)
        output = self.LLM(prompt, max_tokens=self.MAX_TOKENS)
        assistant = output["choices"][0]["text"]

        print(assistant)
        self.history = f"${self.history}{prompt}{assistant}\n"
        print("-------------- history --------------")
        print(self.history)

        for reply in self.split_string(assistant):
            await update.message.reply_text(reply)

if __name__ == "__main__":
    import traceback
    try:
        robin = Robin()
        robin.run()
    except Exception:
        print(traceback.format_exc())
        