# import logging
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import ContextTypes
# from utils.utils import load_user_details, save_user_data
# from security import sanitize_input
#
# # Escape special characters for MarkdownV2
# def escape_markdown_v2(text):
#     escape_chars = r'\_*[]()~`>#+-=|{}.!'
#     return ''.join(f'\\{char}' if char in escape_chars else char for char in text)
#
# # Function to register a new user
# async def register_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = str(update.effective_user.id)
#     user_details = load_user_details()
#
#     if user_id in user_details:
#         return  # User already registered
#
#     await update.message.reply_text("👋 Welcome New User!\n\nPlease enter your Full Name:")
#     context.user_data["registration_step"] = "name"
#
# # Handles the user registration process
# async def capture_user_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not update.message or not update.message.text:
#         await update.message.reply_text("❌ Invalid input. Please try again.")
#         return
#
#     user_id = str(update.effective_user.id)
#     user_message = update.message.text.strip()
#     step = context.user_data.get("registration_step")
#
#     if not step:
#         await update.message.reply_text("❌ Registration error. Type /start to retry.\nUse /reset or /deregister to start over.")
#         return
#
#     user_details = load_user_details()
#     user_details.setdefault(user_id, {})
#
#     # Apply sanitization only for specific steps
#     if step != "po_date":
#         sanitized_message = sanitize_input(
#             user_message,
#             allow_brackets=step in ["description", "role_specialization", "group_specialization", "contractor"],
#             max_words={"description": 30, "name": 10}.get(step, 5),
#             clean_numbers=step in ["name", "reporting_officer"]
#         )
#     else:
#         sanitized_message = user_message  # Store as raw input
#
#     field_mapping = {
#         "name": "skill_level",
#         "role_specialization": "group_specialization",  # Issue was here (Fixed!)
#         "group_specialization": "contractor",
#         "contractor": "po_ref",
#         "po_ref": "po_date",
#         "po_date": "description",
#         "description": "reporting_officer",
#     }
#
#     # ✅ Save user input and correctly update the next step
#     user_details[user_id][step] = sanitized_message
#     save_user_data(user_details)
#
#     next_step = field_mapping.get(step)
#     context.user_data["registration_step"] = next_step  # Ensure step moves forward
#
#     # ✅ Move directly to the next step instead of repeating the previous one
#     if step == "name":
#         await send_inline_buttons(update, "↘️ Choose your Skill Level:", "skill_level", ["Beginner", "Intermediate", "Professional", "Expert"])
#     elif step == "role_specialization":  # Ensure it moves to the next step!
#         await send_inline_buttons(update, "↘️ Select your Contractor:", "contractor", ["PALO IT", "Freelancer"])
#     elif step == "po_ref":
#         await update.message.reply_text("📅 Enter your PO Date Range:\n\neg:\n```\n1 May 24 - 30 Apr 25\n```", parse_mode="MarkdownV2")
#     elif step == "po_date":
#         await update.message.reply_text("↘️ Enter your Job Description:\n\neg:\n```\nAgile Co-Development Services\n```", parse_mode="MarkdownV2")
#     elif step == "description":
#         await update.message.reply_text("👤 Enter your Reporting Officer's Name:\n\neg:\n```\nJohn Doe\n```", parse_mode="MarkdownV2")
#     elif step == "reporting_officer":
#         logging.info(f"User {user_id} completed registration: {user_details[user_id]}")
#         await update.message.reply_text("✅ Registration complete!\n\nType /start to begin using the bot.\n\nUse /reset or /deregister to restart.")
#
# # Sends inline buttons for quick selection
# async def send_inline_buttons(update: Update, prompt: str, callback_prefix: str, options: list):
#     buttons = [[InlineKeyboardButton(option, callback_data=f"{callback_prefix}_{option}")] for option in options]
#     reply_markup = InlineKeyboardMarkup(buttons)
#     await update.message.reply_text(prompt, reply_markup=reply_markup)
#
# # Handles button-based selections
# async def handle_registration_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#
#     user_id = str(update.effective_user.id)
#     callback_data = query.data.strip()
#     logging.info(f"Callback received: {callback_data} from user {user_id}")
#
#     # Correct splitting mechanism
#     if "_" not in callback_data:
#         logging.error(f"Invalid callback data format: {callback_data}")
#         await query.message.reply_text("⚠️ Unknown selection. Please try again.")
#         return
#
#     category, value = callback_data.rsplit("_", 1)  # Ensure category-value split correctly
#
#     user_details = load_user_details()
#     user_details.setdefault(user_id, {})
#
#     field_step_mapping = {
#         "skill_level": "role_specialization",
#         "role_specialization": "group_specialization",
#         "group_specialization": "contractor",
#         "contractor": "po_ref",
#     }
#
#     if category in field_step_mapping:
#         user_details[user_id][category] = value
#         context.user_data["registration_step"] = field_step_mapping[category]
#         save_user_data(user_details)
#
#         if category == "skill_level":
#             await query.message.reply_text(
#                 f"✔️ Skill Level set to: {value}\n\n↘️ Enter your Role Specialization:\n\neg:\n"
#                 "```\nDevOps Engineer - II\n```"
#                 "```\nSoftware Engineer - III\n```"
#                 "```\nCloud Consultant\n```"
#                 "```\nData Engineer\n```",
#                 parse_mode="MarkdownV2"
#             )
#         elif category == "group_specialization":
#             await send_inline_buttons(update, "↘️ Select your Contractor:", "contractor", ["PALO IT", "Freelancer"])
#         elif category == "contractor":
#             await query.message.reply_text(f"✔️ Contractor set to: {value}\n\n↘️ Enter your PO Reference Number:\n\neg:\n```\nGVT000ABC1234\n```", parse_mode="MarkdownV2")
#     else:
#         logging.error(f"Unhandled category: {category} - Value: {value}")
#         await query.message.reply_text("⚠️ Unknown selection. Please try again.")
#

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.utils import load_user_details, save_user_data
from security import sanitize_input

# Escape special characters for MarkdownV2
def escape_markdown_v2(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

# Function to register a new user
async def register_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_details = load_user_details()

    if user_id in user_details:
        return  # User already registered

    await update.message.reply_text("👋 Welcome New User!\n\nPlease enter your Full Name:")
    context.user_data["registration_step"] = "name"

# Handles the user registration process
async def capture_user_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Invalid input. Please try again.")
        return

    user_id = str(update.effective_user.id)
    user_message = update.message.text.strip()
    step = context.user_data.get("registration_step")

    if not step:
        await update.message.reply_text("❌ Registration error. Type /start to retry.\nUse /reset or /deregister to start over.")
        return

    user_details = load_user_details()
    user_details.setdefault(user_id, {})

    # Apply sanitization only for specific steps
    if step != "po_date":
        sanitized_message = sanitize_input(
            user_message,
            allow_brackets=step in ["description", "role_specialization", "group_specialization", "contractor"],
            max_words={"description": 30, "name": 10}.get(step, 5),
            clean_numbers=step in ["name", "reporting_officer"]
        )
    else:
        sanitized_message = user_message  # Store as raw input

    # Updated field mapping with timesheet_preference step
    field_mapping = {
        "name": "timesheet_preference",  # NEW STEP ADDED HERE
        "timesheet_preference": "skill_level",  # Moves to Skill Level after timesheet selection
        "skill_level": "role_specialization",
        "role_specialization": "group_specialization",
        "group_specialization": "contractor",
        "contractor": "po_ref",
        "po_ref": "po_date",
        "po_date": "description",
        "description": "reporting_officer",
    }

    # ✅ Save user input and correctly update the next step
    user_details[user_id][step] = sanitized_message
    save_user_data(user_details)

    next_step = field_mapping.get(step)
    context.user_data["registration_step"] = next_step  # Ensure step moves forward

    # ✅ Move directly to the next step instead of repeating the previous one
    if step == "name":
        await send_inline_buttons(update, "⏳ Do you enter your timesheet as full day = 1.0 or 8.5?", "timesheet_preference", ["1.0", "8.5"])
    elif step == "timesheet_preference":
        await send_inline_buttons(update, "↘️ Choose your Skill Level:", "skill_level", ["Beginner", "Intermediate", "Professional", "Expert"])
    elif step == "role_specialization":
        await send_inline_buttons(update, "↘️ Select your Contractor:", "contractor", ["PALO IT", "Freelancer"])
    elif step == "po_ref":
        await update.message.reply_text("📅 Enter your PO Date Range:\n\neg:\n```\n1 May 24 - 30 Apr 25\n```", parse_mode="MarkdownV2")
    elif step == "po_date":
        await update.message.reply_text("↘️ Enter your Job Description:\n\neg:\n```\nAgile Co-Development Services\n```", parse_mode="MarkdownV2")
    elif step == "description":
        await update.message.reply_text("👤 Enter your Reporting Officer's Name:\n\neg:\n```\nJohn Doe\n```", parse_mode="MarkdownV2")
    elif step == "reporting_officer":
        logging.info(f"User {user_id} completed registration: {user_details[user_id]}")
        await update.message.reply_text(
            "✅ Registration complete! \n\n"
            "Type /start to begin using the bot.\n\n"
            "If you wish to remove your data and reregister, use /reset or /deregister."
        )

# ✅ Fix: Check if update.message exists before replying
async def send_inline_buttons(update: Update, prompt: str, callback_prefix: str, options: list):
    buttons = [[InlineKeyboardButton(option, callback_data=f"{callback_prefix}_{option}")] for option in options]
    reply_markup = InlineKeyboardMarkup(buttons)

    if update.message:  # If it's a normal message (not a callback query)
        await update.message.reply_text(prompt, reply_markup=reply_markup)
    elif update.callback_query:  # If it's from a callback query (button press)
        await update.callback_query.message.reply_text(prompt, reply_markup=reply_markup)

# ✅ Fix: Handle CallbackQuery properly in handle_registration_buttons
async def handle_registration_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    callback_data = query.data.strip()
    logging.info(f"Callback received: {callback_data} from user {user_id}")

    # Correct splitting mechanism
    if "_" not in callback_data:
        logging.error(f"Invalid callback data format: {callback_data}")
        await query.message.reply_text("⚠️ Unknown selection. Please try again.")
        return

    category, value = callback_data.rsplit("_", 1)  # Ensure category-value split correctly

    user_details = load_user_details()
    user_details.setdefault(user_id, {})

    field_step_mapping = {
        "timesheet_preference": "skill_level",  # New step included
        "skill_level": "role_specialization",
        "role_specialization": "group_specialization",
        "group_specialization": "contractor",
        "contractor": "po_ref",
    }

    if category in field_step_mapping:
        user_details[user_id][category] = value
        context.user_data["registration_step"] = field_step_mapping[category]
        save_user_data(user_details)

        if category == "timesheet_preference":
            await send_inline_buttons(update, "↘️ Choose your Skill Level:", "skill_level", ["Beginner", "Intermediate", "Professional", "Expert"])
        elif category == "skill_level":
            await query.message.reply_text(
                f"✔️ Skill Level set to: {value}\n\n↘️ Enter your Role Specialization:\n\neg:\n"
                "```\nDevOps Engineer - II\n```"
                "```\nSoftware Engineer - III\n```"
                "```\nCloud Consultant\n```"
                "```\nData Engineer\n```",
                parse_mode="MarkdownV2"
            )
        elif category == "group_specialization":
            await send_inline_buttons(update, "↘️ Select your Contractor:", "contractor", ["PALO IT", "Freelancer"])
        elif category == "contractor":
            await query.message.reply_text(f"✔️ Contractor set to: {value}\n\n↘️ Enter your PO Reference Number:\n\neg:\n```\nGVT000ABC1234\n```", parse_mode="MarkdownV2")
    else:
        logging.error(f"Unhandled category: {category} - Value: {value}")
        await query.message.reply_text("⚠️ Unknown selection. Please try again.")
