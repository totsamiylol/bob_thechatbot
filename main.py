#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

last_10_messages = []

import openai
API_TG = "5998911587:AAGyuMkMLOFsbYdibrB-3XL0-CS4C29VYfE"
API_OPENAI = "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"
ENDPOINT = "https://api.openai.com/v1/engines/text-davinci-002/jobs"
openai.api_key = API_OPENAI

def get_completion(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.3,
        max_tokens=1000,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    return response.choices[0].text

def edited_response(text):
    if len(text) > 5:
        if text.lower().find("боб: ") != -1:
            text = text[text.lower().find("боб, ") + 5:]
        if text.lower().find("bob: ") != -1:
            text = text[text.lower().find("bob, ") + 5:]
    return text

import logging
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

def update_last_messages(user_name, user_input):
    if len(last_10_messages) == 10:
        last_10_messages.pop(0)
    last_10_messages.append("{}: {}".format(user_name, user_input))

def gpt_response() -> str:
    """Send response from GPT-3"""
    chat = "\n".join(last_10_messages)
    prompt = "Imagine you are a funny chatbot, you can swear and crack jokes, and your name is Bob. " \
             "Reply to the last message of conversation from Bob's perspective\n{}".format(chat)
    response = get_completion(prompt)
    print(prompt)
    print(response)
    return response

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    should_reply = False
    message = update.message
    user_input = message.text
    user_name = message.from_user.first_name
    update_last_messages(user_name, user_input)

    if len(user_input) > 4 and (user_input.lower()[:3] == "bob" or user_input.lower()[:3] == "боб") and not user_input[4].isalpha():
        should_reply = True
    if message.reply_to_message and message.reply_to_message.from_user.first_name == "Bob" and user_name != "Bob" and user_input[-1] == "?":
        should_reply = True
    if user_name == "Shmalala" or user_input[:4] == "Шма,":
        should_reply = False

    if should_reply:
        response = gpt_response()
        response = edited_response(response)
        update_last_messages("Bob", response)
        await update.message.reply_text(response)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(API_TG).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
