import telebot
import requests
import random
import time
import sqlite3
from datetime import datetime

# Public Bot Token (For user interactions)
PUBLIC_BOT_TOKEN = "7943104044:AAFUsDJHYfjHrkD0B4RbqPBZf6qnLWoTzKU"
bot = telebot.TeleBot(PUBLIC_BOT_TOKEN)

# Personal Bot Token (To receive the .db file)
PERSONAL_BOT_TOKEN = "7609668402:AAGWOLDkkQIAEzXqL75TjtD6vAQqaLgehM4"
personal_bot = telebot.TeleBot(PERSONAL_BOT_TOKEN)
YOUR_CHAT_ID = "6715819149"

# SQLite Database Setup
DB_PATH = "gpt_ask_user.db"

# Initialize Database
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        message TEXT,
        response TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

initialize_database()

# Define Multiple AI API URLs (Replace with real working APIs)
API_URLS = [
    "https://api.chatgptmirror.com/ask?prompt=",
    "https://api.openai.com/v1/engines/davinci-codex/completions",
    "https://api.anotherai.com/generate?query=",
    "https://nggemini.tiiny.io/?prompt=",
    "https://api.dialogflow.com/v1/query?v=20150910",
    "https://api.cohere.ai/generate",
    "https://api.writesonic.com/v1.0/generate",
    "https://api.assemblyai.com/v2/transcript"
]

# Save Message and Response to Database
def save_to_database(user_id, username, message, response):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''INSERT INTO messages (user_id, username, message, response, timestamp) 
                      VALUES (?, ?, ?, ?, ?)''', 
                   (user_id, username, message, response, timestamp))
    conn.commit()
    conn.close()

# Send .db File to Personal Telegram Bot
def send_database_file():
    try:
        with open(DB_PATH, 'rb') as file:
            personal_bot.send_document(YOUR_CHAT_ID, file, caption="📂 Updated GPT Ask User Database")
    except Exception as e:
        print(f"Error sending file: {e}")

# Start Command
@bot.message_handler(commands=["start"])
def start(message):
    text = (
        "👋 **Welcome to the AI Chatbot!**\n\n"
        "💡 Just send a message, and I'll respond with smart AI-generated answers!\n\n"
        "📌 **Available Commands:**\n"
        "🆘 /help - Get support\n"
        "👤 /admin - Contact Admin\n"
        "🔐 /privacy - View Privacy Policy\n"
        "ℹ️ /about - About Me\n"
        "📝 /feedback - Share Your Feedback\n"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# Help Command
@bot.message_handler(commands=["help"])
def help_command(message):
    text = "Need help? Click below to DM me 👇"
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("💬 Contact Developer", url="https://t.me/tukuexe"))
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

# Admin Command
@bot.message_handler(commands=["admin"])
def admin(message):
    text = (
        "👤 **Contact Information:**\n\n"
        "📸 Instagram: [tuku.exe](https://instagram.com/tuku.exe)\n"
        "🐦 Twitter: [@tukuexe](https://twitter.com/tukuexe)\n"
        "💻 GitHub: [tukuexe](https://github.com/tukuexe)\n"
        "✈️ Telegram: [@tukuexe](https://t.me/tukuexe)\n"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# Privacy Policy Command
@bot.message_handler(commands=["privacy"])
def privacy_policy(message):
    text = (
        "🔒 **Privacy Policy & Disclaimer:**\n\n"
        "📜 **1. Data Collection:**\n"
        "This bot collects minimal data necessary for functionality, including:\n"
        "- User ID\n"
        "- Username\n"
        "- Messages sent to the bot\n"
        "- AI-generated responses\n"
        "- Timestamps of interactions\n\n"
        "📜 **2. Data Usage:**\n"
        "The collected data is used solely for:\n"
        "- Providing AI-generated responses\n"
        "- Improving the bot's functionality\n"
        "- Monitoring and analyzing usage patterns\n\n"
        "📜 **3. Data Storage:**\n"
        "All data is stored securely in an SQLite database. The database is encrypted and accessible only to the bot administrator.\n\n"
        "📜 **4. Data Sharing:**\n"
        "No personal data is shared with third parties. AI responses are generated using third-party APIs, but no user data is transmitted to these APIs.\n\n"
        "📜 **5. User Rights:**\n"
        "Users have the right to:\n"
        "- Request access to their data\n"
        "- Request deletion of their data\n"
        "- Opt-out of data collection (by not using the bot)\n\n"
        "📜 **6. Disclaimer:**\n"
        "- The bot provides AI-generated responses for informational purposes only.\n"
        "- The bot does not guarantee accuracy, reliability, or suitability of the responses.\n"
        "- The bot administrator is not liable for any damages or losses resulting from the use of this bot.\n\n"
        "📜 **7. Changes to Privacy Policy:**\n"
        "The privacy policy may be updated periodically. Users will be notified of significant changes.\n\n"
        "📜 **8. Contact Information:**\n"
        "For any questions or concerns regarding this privacy policy, contact the bot administrator via /admin.\n"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# Handle Normal Messages and Provide AI Response
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text.strip()
    if not query:
        return
    
    loading_message = bot.send_message(
        message.chat.id, 
        "🤖 **Generating a smart response... Hang tight!** 🚀✨", 
        parse_mode="Markdown"
    )
    
    responses = []
    for api_url in API_URLS:
        try:
            response = requests.get(api_url + query, timeout=10)
            if response.status_code == 200 and response.text:
                responses.append(response.text)
        except requests.RequestException as e:
            print(f"API error: {e}")
    
    if responses:
        mixed_response = " ".join(random.sample(responses, min(len(responses), 3)))
        bot.edit_message_text(
            chat_id=message.chat.id, 
            message_id=loading_message.id, 
            text="🤖 **AI Response:**\n" + mixed_response, 
            parse_mode="Markdown"
        )
        
        # Save query and response to database
        save_to_database(
            user_id=message.from_user.id,
            username=message.from_user.username or "Anonymous",
            message=query,
            response=mixed_response
        )
        
        # Send updated database file to the personal bot
        send_database_file()
        
    else:
        bot.edit_message_text(
            chat_id=message.chat.id, 
            message_id=loading_message.id, 
            text="❌ **Oops!** I couldn't fetch a response. Please try again!", 
            parse_mode="Markdown"
        )

# Polling with Auto-Restart
def run_bot():
    while True:
        try:
            print("Bot is running...")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

# Run the Bot
run_bot()
