import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.utils import load_user_details, save_user_data

# Function to escape MarkdownV2 special characters e.g. "/"
def escape_markdown_v2(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

# Function to confirm de-registration
async def confirm_deregistration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask the user for confirmation before deregistering."""
    user_id = str(update.effective_user.id)
    user_details = load_user_details()

    if user_id not in user_details:
        await update.message.reply_text("⚠️ You are not registered yet! Type /start to begin.")
        return

    # Escape MarkdownV2 special characters
    warning_text = escape_markdown_v2(
        "⚠️ Are you sure you want to *reset* your registration data?\n\n"
        "This action *CANNOT* be undone."
    )

    # Confirmation message with buttons
    buttons = [
        [InlineKeyboardButton("✅ Yes, Reset My Data", callback_data="deregister_confirm")],
        [InlineKeyboardButton("❌ No, Keep My Data", callback_data="deregister_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(warning_text, reply_markup=reply_markup, parse_mode="MarkdownV2")


# Function to handle de-registration button responses
async def handle_deregistration_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles user's choice after confirming de-registration."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    callback_data = query.data

    if callback_data == "deregister_confirm":
        user_details = load_user_details()

        if user_id in user_details:
            del user_details[user_id]  # Remove user data
            save_user_data(user_details)  # Save updated data

            logging.info(f"🗑️ User {user_id} data removed.")
            await query.message.reply_text(
                "✅ Your registration data has been **reset**.\n\nType /start to register again.")

        else:
            await query.message.reply_text("⚠️ You are not registered yet! Type /start to begin.")

    elif callback_data == "deregister_cancel":
        await query.message.reply_text("✅ Your data is **safe**! No changes were made.")

