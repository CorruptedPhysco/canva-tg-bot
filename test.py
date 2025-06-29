# join_canva_bot.py

import telebot
import requests
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Set up simple logging for non-coders to understand what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Replace with your actual bot token from BotFather
BOT_TOKEN = '7994669050:AAFs_lDAbkUbKMkekKuxJMIjviupGX6Nu-o'

# Replace with your actual API URL
API_URL = 'https://canva-api.onrender.com/get-canva'

bot = telebot.TeleBot(BOT_TOKEN)

# /start command handler
@bot.message_handler(commands=['start'])
def send_join_button(message):
    # Send loading message first
    loading_msg = bot.send_message(message.chat.id, "⏳ Loading Canva team link... Please wait.")
    
    try:
        logger.info(f"User {message.from_user.username or message.from_user.id} requested Canva link")
        
        # Fetch the link from API
        logger.info("Fetching link from API...")
        response = requests.get(API_URL, timeout=10)  # 10 second timeout
        response.raise_for_status()
        
        link = response.text.strip().strip('"')  # Remove quotes if present
        
        # Check if link is valid
        if not link or link.lower() in ['null', 'none', 'error', 'unavailable']:
            logger.warning("API returned invalid or unavailable link")
            bot.edit_message_text(
                "❌ Canva team link is currently unavailable.\n\n"
                "⏰ Please try again after 1 hour - the link will be available again!",
                chat_id=message.chat.id,
                message_id=loading_msg.message_id
            )
            return
        
        logger.info("Successfully fetched valid link from API")
        
        # Create button with the link
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton("🎨 Join Canva Team", url=link)
        markup.add(button)

        # Update the loading message with the actual content
        bot.edit_message_text(
            "✅ Here's your Canva team link!\n\n"
            "Click the button below to join:",
            chat_id=message.chat.id,
            message_id=loading_msg.message_id,
            reply_markup=markup
        )
        
        logger.info(f"Successfully sent Canva link to user {message.from_user.username or message.from_user.id}")

    except requests.exceptions.Timeout:
        logger.error("API request timed out")
        bot.edit_message_text(
            "⏰ Request timed out. The server is taking too long to respond.\n\n"
            "Please try again in a few minutes.",
            chat_id=message.chat.id,
            message_id=loading_msg.message_id
        )
        
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to API server")
        bot.edit_message_text(
            "🌐 Connection error. Unable to reach the server.\n\n"
            "Please try again after 1 hour - the service will be back online!",
            chat_id=message.chat.id,
            message_id=loading_msg.message_id
        )
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        bot.edit_message_text(
            "❌ Server error occurred.\n\n"
            "⏰ Please try again after 1 hour - the service will be restored!",
            chat_id=message.chat.id,
            message_id=loading_msg.message_id
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        bot.edit_message_text(
            "❌ Something went wrong while fetching the link.\n\n"
            "⏰ Please try again after 1 hour - the issue will be resolved!",
            chat_id=message.chat.id,
            message_id=loading_msg.message_id
        )

# Start polling
if __name__ == "__main__":
    logger.info("Starting Canva Bot...")
    logger.info("Bot is now running and listening for messages...")
    bot.polling()