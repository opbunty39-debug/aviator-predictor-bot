import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from tinydb import TinyDB, Query

# ----- CONFIG -----
BOT_TOKEN = "8320730361:AAG5h5Idrvt_olsvsZ6LYoPIpnklN6QL89I"
ADMIN_ID =  7296485222  # apna Telegram ID daalo
UPAISA_NUMBER = "03303097845"

# ----- DATABASE -----
db = TinyDB("users.json")
User = Query()

# ----- LOGGING -----
logging.basicConfig(level=logging.INFO)

# ----- START -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get(User.id == user_id)

    if not user:
        db.insert({"id": user_id, "coins": 0, "is_paid": 0})

    user = db.get(User.id == user_id)

    if user["is_paid"] == 0:
        await update.message.reply_text(
            f"Assalamualaikum!\n\n"
            f"Bot use karne ke liye pehle 1000 PKR pay karo.\n\n"
            f"💳 Upaisa Number: {03303097845}\n\n"
            "Payment karke screenshot admin ko bhejo.\n"
            "Approval ke baad tumhe 1000 coins milenge."
        )
    else:
        await update.message.reply_text(
            f"Welcome {update.effective_user.first_name}!\n"
            f"Tumhare paas {user['coins']} coins hain.\n\n"
            "Lion tap game start karne ke liye /game likho 🦁"
        )

# ----- APPROVE -----
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Sirf admin is command ka use kar sakta hai.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /approve <telegram_id>")
        return

    tg_id = int(context.args[0])
    user = db.get(User.id == tg_id)

    if user:
        db.update({"is_paid": 1, "coins": 1000}, User.id == tg_id)
        await update.message.reply_text(f"User {tg_id} approved ✅ (1000 coins added).")
    else:
        await update.message.reply_text("User not found.")

# ----- BLOCK -----
async def block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Sirf admin is command ka use kar sakta hai.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /block <telegram_id>")
        return

    tg_id = int(context.args[0])
    user = db.get(User.id == tg_id)

    if user:
        db.update({"is_paid": 0, "coins": 0}, User.id == tg_id)
        await update.message.reply_text(f"User {tg_id} blocked ❌")
    else:
        await update.message.reply_text("User not found.")

# ----- BALANCE -----
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get(User.id == user_id)

    if not user or user["is_paid"] == 0:
        await update.message.reply_text("Pehle 1000 PKR pay karo aur admin approval lo.")
        return

    await update.message.reply_text(f"Tumhare paas {user['coins']} coins hain 🪙")

# ----- GAME -----
async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get(User.id == user_id)

    if not user or user["is_paid"] == 0:
        await update.message.reply_text("Pehle 1000 PKR pay karo aur admin approval lo.")
        return

    keyboard = [[InlineKeyboardButton("🦁 Tap Lion", callback_data="tap")]]
    await update.message.reply_text(
        "Lion tap game start ho gaya! Har tap se tumhe +1 coin milega.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user = db.get(User.id == user_id)

    if query.data == "tap" and user and user["is_paid"] == 1:
        new_coins = user["coins"] + 1
        db.update({"coins": new_coins}, User.id == user_id)
        await query.answer(f"+1 Coin! Total: {new_coins}")
    else:
        await query.answer("Pehle 1000 PKR pay karo aur admin approval lo.", show_alert=True)

# ----- MAIN -----
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("block", block))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("game", game))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
