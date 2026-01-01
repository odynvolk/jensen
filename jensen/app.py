import os
import re
from timeit import default_timer as timer

from dotenv import load_dotenv
from telegram import Update, constants
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import requests
import json

load_dotenv()


class Jensen(object):
    def __init__(self):
        self.API_KEY = os.getenv("API_KEY")
        self.POLL_INTERVAL = (
            float(os.getenv("POLL_INTERVAL")) if os.getenv("POLL_INTERVAL") else 1.0
        )

        self.init_prompt()

        self.application = Application.builder().token(self.API_KEY).build()

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("about", self.about))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("clear", self.clear))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handleMessage)
        )

    def run(self):
        self.application.run_polling(
            poll_interval=self.POLL_INTERVAL, allowed_updates=Update.ALL_TYPES
        )

    async def start(self, update: Update) -> None:
        await update.message.reply_text("Welcome back sir!")

    async def about(self, update: Update) -> None:
        await update.message.reply_text("I'm Jensen your personal LLM powered chatbot.")

    async def help(self, update: Update) -> None:
        await update.message.reply_text(
            "To engage in a conversation with me just start typing.\n\nThe commands I understand:\n/about - some information about me Jensen\n/clear - clear prompt history"
        )

    def init_prompt(self):
        system_instruction = (
            os.getenv("SYSTEM_INSTRUCTION")
            if os.getenv("SYSTEM_INSTRUCTION")
            else "You are an intelligent assistant providing helpful information."
        )
        self.history = [
            {
                "role": "system",
                "content": system_instruction.strip(),
            },
        ]

    async def clear(self, update: Update) -> None:
        self.init_prompt()
        await update.message.reply_text("Prompt history cleared.")

    def create_prompt(self, string):
        return {"role": "user", "content": string}

    def remove_prompt_from_history(self):
        # Remove fist user prompts and assistant answers
        self.history.pop(1)
        self.history.pop(1)

    async def prompt_llm(self, update: Update, prompt):
        self.history.append(prompt)

        response = requests.post("http://localhost:8700/v1/chat/completions", json={ "messages": self.history, "stream": True}, stream=True)
        completeReply = ""
        reply = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data:"):
                    json_data = decoded_line[len("data:"):].strip()
                    if json_data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(json_data)
                        # Process the token from the chunk
                        if "choices" in chunk and chunk["choices"]:
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content is not None:
                              completeReply += content
                              if "\n\n" in content:
                                paragraphs = content.split("\n\n")
                                await update.message.reply_text(reply + paragraphs[0])
                                reply = paragraphs[1]
                              else:
                                reply += content
                            print(content, end="", flush=True)
                    except json.JSONDecodeError:
                        continue

        await update.message.reply_text(reply)
        self.history.append(
            {
                "role": "assistant",
                "content": completeReply,
            }
        )

    async def handleMessage(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        await context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=constants.ChatAction.TYPING
        )
        prompt = self.create_prompt(update.message.text.strip())
        print("-------------- PROMPT --------------")
        print(prompt)

        start = timer()

        try:
            await self.prompt_llm(update, prompt)
        except ValueError as e:
            print(e)
            self.init_prompt()
            await self.prompt_llm(update, prompt)

        end = timer()

        print(f"\n\nDURATION: {int(end - start)} seconds.\n\n")
        print("-------------------------------------")
        print("-------------- HISTORY --------------")
        print(self.history)
        print("-------------------------------------")


if __name__ == "__main__":
    import traceback

    try:
        jensen = Jensen()
        jensen.run()
    except Exception:
        print(traceback.format_exc())
