import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.utils import load_user_details, save_user_data
from security import sanitize_input
import re
# def escape_markdown_v2(text):
#     escape_chars = r'\_[]()~`>#+-=|{}.!'
#     return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def escape_markdown_v2(text):
    """
    Properly escapes MarkdownV2 special characters.
    """
    if not text:
        return ""

    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

# --- TEST CASES ---

async def test_bold_text(update, context):
    # 1️⃣ Simple MarkdownV2 without escaping
    await update.message.reply_text("**Shamik**", parse_mode="MarkdownV2")

    # 2️⃣ Escaped MarkdownV2 (Safe)
    await update.message.reply_text(r"\*\*Shamik\*\*", parse_mode="MarkdownV2")

    # 3️⃣ Using escape function
    await update.message.reply_text(f"**{escape_markdown_v2('Shamik')}**", parse_mode="MarkdownV2")

    # 4️⃣ Adding a greeting with MarkdownV2
    await update.message.reply_text(f"Hi **{escape_markdown_v2('Shamik')}**", parse_mode="MarkdownV2")

    # 5️⃣ Test with space before bold
    await update.message.reply_text(f"Hi\ **{escape_markdown_v2('Shamik')}**", parse_mode="MarkdownV2")

    # 6️⃣ HTML Formatting (Alternative)
    await update.message.reply_text("<b>Shamik</b>", parse_mode="HTML")

    # 7️⃣ HTML Formatting with a sentence
    await update.message.reply_text("Hi <b>Shamik</b>, welcome!", parse_mode="HTML")


# Function to register a new user
async def register_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_details = load_user_details()

    if user_id in user_details:
        return  # User already registered

    await update.message.reply_text("👋 Welcome New User!\n\nPlease enter your Full Name:")
    context.user_data["registration_step"] = "name"

# Handles user registration process (text inputs)
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
#     # Apply sanitization
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
#     # Save user input
#     user_details[user_id][step] = sanitized_message
#     save_user_data(user_details)
#
#     # Field mapping for step transitions
#     field_mapping = {
#         "name": "timesheet_preference",
#         "timesheet_preference": "skill_level",
#         "skill_level": "role_specialization",
#         "role_specialization": "group_specialization",
#         "group_specialization": "contractor",
#         "contractor": "po_ref",
#         "po_ref": "po_date",
#         "po_date": "description",
#         "description": "reporting_officer",
#     }
#
#     next_step = field_mapping.get(step)
#     context.user_data["registration_step"] = next_step  # Ensure step moves forward
#
#     # ✅ **Fixed Bold Text in Messages**
#     if step == "name":
#         await update.message.reply_text(f"Hi <b>{sanitized_message}</b>", parse_mode="HTML")
#         await send_inline_buttons(update, "⏳ Do you enter your timesheet as full day = 1.0 or 8.5?", "timesheet_preference", ["1.0", "8.5"])
#
#     elif step == "timesheet_preference":
#         await update.message.reply_text(f"Your full day preference is **{escape_markdown_v2(sanitized_message)}**", parse_mode="MarkdownV2")
#         await send_inline_buttons(update, "↘️ Choose your Skill Level:", "skill_level", ["Beginner", "Intermediate", "Professional", "Expert"])
#
#     elif step == "role_specialization":
#         await update.message.reply_text(
#             f"✔️ Role Specialization set to: **{escape_markdown_v2(sanitized_message)}**\n\n"
#             "↘️ Enter your Group Specialization:\n\n"
#             "```\nConsulting```",
#             parse_mode="MarkdownV2"
#         )
#
#     elif step == "group_specialization":
#         await update.message.reply_text(f"Your Group/Specialization is set to **{escape_markdown_v2(sanitized_message)}**", parse_mode="MarkdownV2")
#         await send_inline_buttons(update, "↘️ Select your Contractor:", "contractor", ["PALO IT", "Freelancer"])
#
#     elif step == "po_ref":
#         await update.message.reply_text(
#             f"✔️ PO Reference Number set to: **{escape_markdown_v2(sanitized_message)}**\n\n"
#             "📅 Enter your PO Date Range:\n\neg:\n```\n1 May 24 - 30 Apr 25\n```",
#             parse_mode="MarkdownV2"
#         )
#
#     elif step == "po_date":
#         await update.message.reply_text(
#             f"✔️ PO Date set to: **{escape_markdown_v2(sanitized_message)}**\n\n"
#             "↘️ Enter your Job Description:\n\neg:\n```\nAgile Co-Development Services\n```",
#             parse_mode="MarkdownV2"
#         )
#
#     elif step == "description":
#         await update.message.reply_text(
#             f"✔️ Job Description set to: **{escape_markdown_v2(sanitized_message)}**\n\n"
#             "👤 Enter your Reporting Officer's Name:\n\neg:\n```\nJohn Doe\n```",
#             parse_mode="MarkdownV2"
#         )
#
#     elif step == "reporting_officer":
#         logging.info(f"User {user_id} completed registration: {user_details[user_id]}")
#         await update.message.reply_text(
#             "✅ Registration complete! \n\n"
#             "Type /start to begin using the bot.\n\n"
#             "If you wish to remove your data and reregister, use /reset or /deregister."
#         )

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

    # Apply sanitization
    if step != "po_date":
        sanitized_message = sanitize_input(
            user_message,
            allow_brackets=step in ["description", "role_specialization", "group_specialization", "contractor"],
            max_words={"description": 30, "name": 10}.get(step, 5),
            clean_numbers=step in ["name", "reporting_officer"]
        )
    else:
        sanitized_message = user_message  # Store as raw input

    # Save user input
    user_details[user_id][step] = sanitized_message
    save_user_data(user_details)

    # Field mapping for step transitions
    field_mapping = {
        "name": "timesheet_preference",
        "timesheet_preference": "skill_level",
        "skill_level": "role_specialization",
        "role_specialization": "group_specialization",
        "group_specialization": "contractor",
        "contractor": "po_ref",
        "po_ref": "po_date",
        "po_date": "description",
        "description": "reporting_officer",
    }

    next_step = field_mapping.get(step)
    context.user_data["registration_step"] = next_step  # Ensure step moves forward

    # ✅ **Fixed Bold Text in Messages (Using HTML)**
    if step == "name":
        await update.message.reply_text(f"Hi <b>{sanitized_message}</b>", parse_mode="HTML")
        await send_inline_buttons(update, "⏳ Do you enter your timesheet as full day = 1.0 or 8.5?", "timesheet_preference", ["1.0", "8.5"])

    elif step == "timesheet_preference":
        await update.message.reply_text(f"Your full day preference is <b>{sanitized_message}</b>", parse_mode="HTML")
        await send_inline_buttons(update, "↘️ Choose your Skill Level:", "skill_level", ["Beginner", "Intermediate", "Professional", "Expert"])

    elif step == "role_specialization":
        await update.message.reply_text(
            f"✔️ Role Specialization set to: <b>{sanitized_message}</b>\n\n"
            "↘️ Enter your Group Specialization:\n\n"
            "<code>Consulting</code>",
            parse_mode="HTML"
        )

    elif step == "group_specialization":
        await update.message.reply_text(f"Your Group/Specialization is set to <b>{sanitized_message}</b>", parse_mode="HTML")
        await send_inline_buttons(update, "↘️ Select your Contractor:", "contractor", ["PALO IT", "Freelancer"])

    elif step == "po_ref":
        await update.message.reply_text(
            f"✔️ PO Reference Number set to: <b>{sanitized_message}</b>\n\n"
            "📅 Enter your PO Date Range:\n\neg:\n<code>1 May 24 - 30 Apr 25</code>",
            parse_mode="HTML"
        )

    elif step == "po_date":
        await update.message.reply_text(
            f"✔️ PO Date set to: <b>{sanitized_message}</b>\n\n"
            "↘️ Enter your Job Description:\n\neg:\n<code>Agile Co-Development Services</code>",
            parse_mode="HTML"
        )

    elif step == "description":
        await update.message.reply_text(
            f"✔️ Job Description set to: <b>{sanitized_message}</b>\n\n"
            "👤 Enter your Reporting Officer's Name:\n\neg:\n<code>John Doe</code>",
            parse_mode="HTML"
        )

    elif step == "reporting_officer":
        logging.info(f"User {user_id} completed registration: {user_details[user_id]}")
        await update.message.reply_text(
            "✅ <b>Registration complete!</b> \n\n"
            "Type /start to begin using the bot.\n\n"
            "If you wish to remove your data and reregister, use /reset or /deregister.",
            parse_mode="HTML"
        )



# ✅ Send inline buttons for quick selection
async def send_inline_buttons(update: Update, prompt: str, callback_prefix: str, options: list):
    buttons = [[InlineKeyboardButton(option, callback_data=f"{callback_prefix}_{option}")] for option in options]
    reply_markup = InlineKeyboardMarkup(buttons)

    if update.message:
        await update.message.reply_text(prompt, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(prompt, reply_markup=reply_markup)

# ✅ Handle inline button-based selections
# async def handle_registration_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#
#     user_id = str(update.effective_user.id)
#     callback_data = query.data.strip()
#     logging.info(f"Callback received: {callback_data} from user {user_id}")
#
#     if "_" not in callback_data:
#         logging.error(f"Invalid callback data format: {callback_data}")
#         await query.message.reply_text("⚠️ Unknown selection. Please try again.")
#         return
#
#     category, value = callback_data.rsplit("_", 1)
#
#     user_details = load_user_details()
#     user_details.setdefault(user_id, {})
#
#     field_step_mapping = {
#         "timesheet_preference": "skill_level",
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
#         if category == "timesheet_preference":
#             await query.message.reply_text(f"Your full day preference is **{escape_markdown_v2(value)}**", parse_mode="MarkdownV2")
#             await send_inline_buttons(update, "↘️ Choose your Skill Level:", "skill_level", ["Beginner", "Intermediate", "Professional", "Expert"])
#
#         elif category == "skill_level":
#             await query.message.reply_text(f"✔️ Skill Level set to: **{escape_markdown_v2(value)}**\n\n↘️ Enter your Role Specialization:\n\neg:\n```\nDevOps Engineer - II\n```", parse_mode="MarkdownV2")
#
#         elif category == "role_specialization":
#             await query.message.reply_text(f"✔️ Role Specialization set to: **{escape_markdown_v2(value)}**\n\n↘️ Enter your Group Specialization:\n\n```\nConsulting```", parse_mode="MarkdownV2")
#
#         elif category == "group_specialization":
#             await query.message.reply_text(f"Your Group/Specialization is set to **{escape_markdown_v2(value)}**", parse_mode="MarkdownV2")
#             await send_inline_buttons(update, "↘️ Select your Contractor:", "contractor", ["PALO IT", "Freelancer"])
#
#         elif category == "contractor":
#             await query.message.reply_text(f"✔️ Contractor set to: **{escape_markdown_v2(value)}**\n\n↘️ Enter your PO Reference Number:\n\neg:\n```\nGVT000ABC1234\n```", parse_mode="MarkdownV2")
#     else:
#         logging.error(f"Unhandled category: {category} - Value: {value}")
#         await query.message.reply_text("⚠️ Unknown selection. Please try again.")

async def handle_registration_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    callback_data = query.data.strip()
    logging.info(f"Callback received: {callback_data} from user {user_id}")

    if "_" not in callback_data:
        logging.error(f"Invalid callback data format: {callback_data}")
        await query.message.reply_text("⚠️ Unknown selection. Please try again.")
        return

    category, value = callback_data.rsplit("_", 1)

    user_details = load_user_details()
    user_details.setdefault(user_id, {})

    field_step_mapping = {
        "timesheet_preference": "skill_level",
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
            await query.message.reply_text(f"Your full day preference is <b>{value}</b>", parse_mode="HTML")
            await send_inline_buttons(update, "↘️ Choose your Skill Level:", "skill_level", ["Beginner", "Intermediate", "Professional", "Expert"])

        elif category == "skill_level":
            await query.message.reply_text(f"✔️ Skill Level set to: <b>{value}</b>\n\n↘️ Enter your Role Specialization:\n\neg:\n<code>DevOps Engineer - II</code>", parse_mode="HTML")

        elif category == "role_specialization":
            await query.message.reply_text(f"✔️ Role Specialization set to: <b>{value}</b>\n\n↘️ Enter your Group Specialization:\n\n<code>Consulting</code>", parse_mode="HTML")

        elif category == "group_specialization":
            await query.message.reply_text(f"Your Group/Specialization is set to <b>{value}</b>", parse_mode="HTML")
            await send_inline_buttons(update, "↘️ Select your Contractor:", "contractor", ["PALO IT", "Freelancer"])

        elif category == "contractor":
            await query.message.reply_text(f"✔️ Contractor set to: <b>{value}</b>\n\n↘️ Enter your PO Reference Number:\n\neg:\n<code>GVT000ABC1234</code>", parse_mode="HTML")
    else:
        logging.error(f"Unhandled category: {category} - Value: {value}")
        await query.message.reply_text("⚠️ Unknown selection. Please try again.")

