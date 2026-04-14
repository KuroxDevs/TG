import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, PollAnswerHandler, ContextTypes, CommandHandler

# --- CONFIGURATION ---
TOKEN = '8430599563:AAFI1Uk3y2nfHiNPHv9KhCNuwKyzXCqVYe4'
MY_ID = 5962552713
DB_PATH = '/storage/emulated/0/votes_data.db'

# Logging Setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS votes 
                      (user_id INTEGER, name TEXT, username TEXT, poll_id TEXT, option_index INTEGER)''')
    conn.commit()
    conn.close()

# --- FUNCTIONS ---
async def post_init(application):
    """Bot startup notification"""
    try:
        init_db()
        await application.bot.send_message(chat_id=MY_ID, text="𓂻 **Am_Maverick Online!**\nDatabase Ready. Tracking active.", parse_mode='Markdown')
        print("✅ Bot is live and connected.")
    except Exception as e:
        print(f"❌ Startup Error: {e}")

async def track_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles real-time voting tracking"""
    answer = update.poll_answer
    user = answer.user
    poll_id = answer.poll_id
    selected_options = answer.option_ids[0] if answer.option_ids else None

    if selected_options is None: return # Vote retract handle

    name = user.full_name
    uid = user.id
    username = f"@{user.username}" if user.username else "N/A"

    # Database me save karna
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO votes VALUES (?, ?, ?, ?, ?)", (uid, name, username, poll_id, selected_options))
    conn.commit()
    conn.close()

    # Message to Admin
    msg = (
        f"🎯 **New Vote Detected!**\n\n"
        f"👤 **Name:** {name}\n"
        f"🔗 **User:** {username}\n"
        f"🆔 **ID:** `{uid}`\n"
        f"📊 **Selected Index:** `{selected_options}`\n"
        f"--------------------------"
    )
    await context.bot.send_message(chat_id=MY_ID, text=msg, parse_mode='Markdown')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check total votes in DB"""
    if update.effective_user.id != MY_ID: return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM votes")
    count = cursor.fetchone()[0]
    conn.close()
    await update.message.reply_text(f"📊 **Total Votes Logged:** {count}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    app.add_handler(PollAnswerHandler(track_vote))
    app.add_handler(CommandHandler("stats", stats))

    print("🚀 Starting Bot Polling...")
    app.run_polling(stop_signals=None)
