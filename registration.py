import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.utils import load_user_details, save_user_data
import re
from security import sanitize_input


# Function to register a new user
async def register_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    # Reload USER_DETAILS dynamically
    user_details = load_user_details()

    if user_id in user_details:
        return  # User already exists, no need to register again

    await update.message.reply_text("👋 Welcome New User!\n\nPlease enter your Full Name:")
    context.user_data["registration_step"] = "name"

def escape_markdown_v2(text):
    """Escape special characters for Telegram MarkdownV2 formatting."""
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

async def capture_user_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Invalid input. Please try again.")
        return

    user_id = str(update.effective_user.id)
    user_message = update.message.text.strip()
    step = context.user_data.get("registration_step")

    if not step:
        #await update.message.reply_text("❌ Registration error. Please type /start to retry.")
        await update.message.reply_text(
            "❌ Registration error. Please type /start to retry.\n\n"
            "To correct or remove your data and reregister, use /reset or /deregister."
        )
        return

    # Load latest user details before modifying
    user_details = load_user_details()

    # Ensure user exists before modifying
    if user_id not in user_details:
        user_details[user_id] = {}

    sanitized_message = sanitize_input(
        user_message,
        allow_brackets=(step in ["description", "role_specialization", "group_specialization", "contractor"]),
        max_words=30 if step == "description" else 10 if step == "name" else 5,
        clean_numbers=(step in ["name", "reporting_officer"])  # Remove numbers in Name & Reporting Officer
    )

    if step == "name":
        user_details[user_id]["name"] = sanitized_message
        context.user_data["registration_step"] = "skill_level"
        save_user_data(user_details)

        # Quick-select buttons for skill level
        buttons = [
            [InlineKeyboardButton("Beginner", callback_data="skill_level_Beginner")],
            [InlineKeyboardButton("Intermediate", callback_data="skill_level_Intermediate")],
            [InlineKeyboardButton("Professional", callback_data="skill_level_Professional")],
            [InlineKeyboardButton("Expert", callback_data="skill_level_Expert")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("↘️ Tap a button to enter your Skill Level:", reply_markup=reply_markup)

    elif step == "role_specialization":
        user_details[user_id]["role_specialization"] = sanitized_message
        context.user_data["registration_step"] = "group_specialization"
        save_user_data(user_details)

        # Instead of prompting for Role Specialization again, move to Group Specialization
        await update.message.reply_text(f"✔️ Role Specialization set to: {escape_markdown_v2(sanitized_message)}\n\n↘️ Enter your Group Specialization:\n\neg:\n```\nConsulting```", parse_mode="MarkdownV2")

    elif step == "group_specialization":
        user_details[user_id]["group_specialization"] = sanitized_message
        context.user_data["registration_step"] = "contractor"
        save_user_data(user_details)

        # Quick-select buttons for contractor
        buttons = [
            [InlineKeyboardButton("PALO IT", callback_data="contractor_PALO IT")],
            #[InlineKeyboardButton("Accenture", callback_data="contractor_Accenture")],
            #[InlineKeyboardButton("Deloitte", callback_data="contractor_Deloitte")],
            [InlineKeyboardButton("Freelancer", callback_data="contractor_Freelancer")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("↘️ Enter your Contractor or tap a button:", reply_markup=reply_markup)

    elif step == "contractor":
        user_details[user_id]["contractor"] = sanitized_message
        context.user_data["registration_step"] = "po_ref"
        save_user_data(user_details)
        await update.message.reply_text("➡ Enter your PO Reference Number:\n\neg:\n```\nGVT000ABC1234\n```",
                                        parse_mode="MarkdownV2")

    elif step == "po_ref":
        user_details[user_id]["po_ref"] = sanitized_message
        context.user_data["registration_step"] = "po_date"
        save_user_data(user_details)
        await update.message.reply_text("📅 Enter your PO Date Range:\n\neg:\n```\n1 May 24 - 30 Apr 25\n```",
                                        parse_mode="MarkdownV2")

    elif step == "po_date":
        user_details[user_id]["po_date"] = sanitized_message
        context.user_data["registration_step"] = "description"
        save_user_data(user_details)
        await update.message.reply_text("↘️ Enter your Job Description:\n\neg:\n```\nAgile Co-Development Services\n```",
                                        parse_mode="MarkdownV2")

    elif step == "description":
        user_details[user_id]["description"] = sanitized_message
        context.user_data["registration_step"] = "reporting_officer"
        save_user_data(user_details)
        await update.message.reply_text("👤 Enter your Reporting Officer's Name:\n\neg:\n```\nJohn Doe\n```",
                                        parse_mode="MarkdownV2")

    elif step == "reporting_officer":
        user_details[user_id]["reporting_officer"] = sanitized_message
        save_user_data(user_details)  # Save final data

        logging.info(f"User {user_id} completed registration: {user_details[user_id]}")
        #await update.message.reply_text("✅ Registration complete! \n\nType /start to begin using the bot.\n\n")
        await update.message.reply_text(
            "✅ Registration complete! \n\n"
            "Type /start to begin using the bot.\n\n"
            "If you wish to remove your data and reregister, use /reset or /deregister."
        )



async def handle_registration_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    callback_data = query.data.strip()
    logging.info(f"Callback received: {callback_data} from user {user_id}")

    # Fix splitting issue (Ensures correct category extraction)
    parts = callback_data.split("_", 2)
    if len(parts) < 2:
        logging.error(f"Invalid callback data format: {callback_data}")
        await query.message.reply_text("⚠️ Unknown selection. Please try again.")
        return

    category = f"{parts[0]}_{parts[1]}" if len(parts) == 3 else parts[0]  # Corrects category
    value = parts[2] if len(parts) == 3 else parts[1]  # Extracts correct value

    user_details = load_user_details()
    if user_id not in user_details:
        user_details[user_id] = {}

    if category == "skill_level":  # Now matches correctly
        user_details[user_id]["skill_level"] = value
        context.user_data["registration_step"] = "role_specialization"
        save_user_data(user_details)

        await query.message.reply_text(
            f"✔️ Skill Level set to: {value}\n\n↘️ Enter your Role Specialization:\n\neg:\n"
            "```\nDevOps Engineer - II\n```"
            "```\nSoftware Engineer - III\n```"
            "```\nCloud Consultant\n```"
            "```\nData Engineer\n```",
            parse_mode="MarkdownV2"
        )

    elif category == "role_specialization":
        user_details[user_id]["role_specialization"] = value
        context.user_data["registration_step"] = "group_specialization"
        save_user_data(user_details)

        await query.message.reply_text(
            f"✔️ Role Specialization set to: {value}\n\n↘️ Enter your Group Specialization:\n\n```\nConsulting\nTech Support\n```",
            parse_mode="MarkdownV2"
        )

    elif category == "group_specialization":
        user_details[user_id]["group_specialization"] = value
        context.user_data["registration_step"] = "contractor"
        save_user_data(user_details)

        await query.message.reply_text(
            f"✔️ Group Specialization set to: {value}\n\n↘️ Enter your Contractor or tap a button:",
            parse_mode="MarkdownV2"
        )

    elif category == "contractor":
        user_details[user_id]["contractor"] = value
        context.user_data["registration_step"] = "po_ref"
        save_user_data(user_details)

        await query.message.reply_text(
            f"✔️ Contractor set to: {value}\n\n↘️ Enter your PO Reference Number:\n\neg:\n```\nGVT000ABC1234\n```",
            parse_mode="MarkdownV2"
        )

    else:
        logging.error(f"Unhandled category: {category} - Value: {value}")
        await query.message.reply_text("⚠️ Unknown selection. Please try again.")
