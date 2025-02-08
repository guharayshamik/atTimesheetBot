import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.utils import load_user_details, save_user_data  # ✅ Import functions from utils
import re

# ✅ Function to sanitize user input
def sanitize_input(user_input):
    """Sanitize user input to prevent injection attacks."""
    return re.sub(r"[^\w\s-]", "", user_input.strip())[:50]  # Allow only alphanumeric, spaces, and dashes (limit 50 chars)

# ✅ Function to register a new user
async def register_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)


    # ✅ Reload USER_DETAILS dynamically
    user_details = load_user_details()

    if user_id in user_details:
        return  # ✅ User already exists, no need to register again

    await update.message.reply_text("👋 Welcome! Please enter your full name:")
    context.user_data["registration_step"] = "name"


# async def capture_user_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = str(update.effective_user.id)
#     user_message = update.message.text.strip()
#     step = context.user_data.get("registration_step")
#
#     if not step:
#         await update.message.reply_text("❌ Registration error. Please type /start to retry.")
#         return
#
#     # ✅ Load latest user details before modifying
#     user_details = load_user_details()
#
#     # ✅ Ensure user exists before modifying
#     if user_id not in user_details:
#         user_details[user_id] = {}
#
#     if step == "name":
#         user_details[user_id]["name"] = user_message  # ✅ Save immediately
#         context.user_data["registration_step"] = "skill_level"
#         save_user_data(user_details)  # ✅ Save data to JSON
#
#         # ✅ Quick-select buttons for skill level
#         buttons = [
#             [InlineKeyboardButton("Beginner", callback_data="skill_level_Beginner")],
#             [InlineKeyboardButton("Intermediate", callback_data="skill_level_Intermediate")],
#             [InlineKeyboardButton("Professional", callback_data="skill_level_Professional")],
#             [InlineKeyboardButton("Expert", callback_data="skill_level_Expert")]
#         ]
#         reply_markup = InlineKeyboardMarkup(buttons)
#         await update.message.reply_text("🔹 Enter your Skill Level or tap a button:", reply_markup=reply_markup)
#
#     elif step == "group_specialization":
#         user_details[user_id]["group_specialization"] = user_message  # ✅ Save immediately
#         context.user_data["registration_step"] = "contractor"
#         save_user_data(user_details)  # ✅ Save data to JSON
#
#         # ✅ Quick-select buttons for contractor
#         buttons = [
#             [InlineKeyboardButton("PALO IT", callback_data="contractor_PALO IT")],
#             [InlineKeyboardButton("Accenture", callback_data="contractor_Accenture")],
#             [InlineKeyboardButton("Deloitte", callback_data="contractor_Deloitte")],
#             [InlineKeyboardButton("Freelancer", callback_data="contractor_Freelancer")]
#         ]
#         reply_markup = InlineKeyboardMarkup(buttons)
#         await update.message.reply_text("🔹 Enter your Contractor or tap a button:", reply_markup=reply_markup)
#
#     elif step == "contractor":
#         user_details[user_id]["contractor"] = user_message  # ✅ Save immediately
#         context.user_data["registration_step"] = "po_ref"
#         save_user_data(user_details)  # ✅ Save data to JSON
#         await update.message.reply_text("📄 Enter your PO Reference Number:\n\n```\n12345-ABC\n```",
#                                         parse_mode="MarkdownV2")
#
#     elif step == "po_ref":
#         user_details[user_id]["po_ref"] = user_message
#         context.user_data["registration_step"] = "po_date"
#         save_user_data(user_details)
#         await update.message.reply_text("📅 Enter your PO Date Range:\n\n```\n1 May 24 - 30 Apr 25\n```",
#                                         parse_mode="MarkdownV2")
#
#     elif step == "po_date":
#         user_details[user_id]["po_date"] = user_message
#         context.user_data["registration_step"] = "description"
#         save_user_data(user_details)
#         await update.message.reply_text("📝 Enter your Job Description:\n\n```\nAgile Co-Development Services\n```",
#                                         parse_mode="MarkdownV2")
#
#     elif step == "description":
#         user_details[user_id]["description"] = user_message
#         context.user_data["registration_step"] = "reporting_officer"
#         save_user_data(user_details)
#         await update.message.reply_text("👤 Enter your Reporting Officer's Name:\n\n```\nJohn Doe\n```",
#                                         parse_mode="MarkdownV2")
#
#     elif step == "reporting_officer":
#         user_details[user_id]["reporting_officer"] = user_message
#         save_user_data(user_details)  # ✅ Save final data
#
#         logging.info(f"✅ User {user_id} completed registration: {user_details[user_id]}")
#         await update.message.reply_text("✅ Registration complete! Type /start to begin using the bot.")
#

async def capture_user_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_message = update.message.text.strip()
    step = context.user_data.get("registration_step")

    if not step:
        await update.message.reply_text("❌ Registration error. Please type /start to retry.")
        return

    # ✅ Load latest user details before modifying
    user_details = load_user_details()

    # ✅ Ensure user exists before modifying
    if user_id not in user_details:
        user_details[user_id] = {}

    # ✅ Apply sanitization before saving user input
    sanitized_message = sanitize_input(user_message)  # ✅ Apply sanitization

    if step == "name":
        user_details[user_id]["name"] = sanitized_message
        context.user_data["registration_step"] = "skill_level"
        save_user_data(user_details)

        # ✅ Quick-select buttons for skill level
        buttons = [
            [InlineKeyboardButton("Beginner", callback_data="skill_level_Beginner")],
            [InlineKeyboardButton("Intermediate", callback_data="skill_level_Intermediate")],
            [InlineKeyboardButton("Professional", callback_data="skill_level_Professional")],
            [InlineKeyboardButton("Expert", callback_data="skill_level_Expert")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("🔹 Enter your Skill Level or tap a button:", reply_markup=reply_markup)

    elif step == "group_specialization":
        user_details[user_id]["group_specialization"] = sanitized_message
        context.user_data["registration_step"] = "contractor"
        save_user_data(user_details)

        # ✅ Quick-select buttons for contractor
        buttons = [
            [InlineKeyboardButton("PALO IT", callback_data="contractor_PALO IT")],
            [InlineKeyboardButton("Accenture", callback_data="contractor_Accenture")],
            [InlineKeyboardButton("Deloitte", callback_data="contractor_Deloitte")],
            [InlineKeyboardButton("Freelancer", callback_data="contractor_Freelancer")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("🔹 Enter your Contractor or tap a button:", reply_markup=reply_markup)

    elif step == "contractor":
        user_details[user_id]["contractor"] = sanitized_message
        context.user_data["registration_step"] = "po_ref"
        save_user_data(user_details)
        await update.message.reply_text("📄 Enter your PO Reference Number:\n\n```\n12345-ABC\n```",
                                        parse_mode="MarkdownV2")

    elif step == "po_ref":
        user_details[user_id]["po_ref"] = sanitized_message
        context.user_data["registration_step"] = "po_date"
        save_user_data(user_details)
        await update.message.reply_text("📅 Enter your PO Date Range:\n\n```\n1 May 24 - 30 Apr 25\n```",
                                        parse_mode="MarkdownV2")

    elif step == "po_date":
        user_details[user_id]["po_date"] = sanitized_message
        context.user_data["registration_step"] = "description"
        save_user_data(user_details)
        await update.message.reply_text("📝 Enter your Job Description:\n\n```\nAgile Co-Development Services\n```",
                                        parse_mode="MarkdownV2")

    elif step == "description":
        user_details[user_id]["description"] = sanitized_message
        context.user_data["registration_step"] = "reporting_officer"
        save_user_data(user_details)
        await update.message.reply_text("👤 Enter your Reporting Officer's Name:\n\n```\nJohn Doe\n```",
                                        parse_mode="MarkdownV2")

    elif step == "reporting_officer":
        user_details[user_id]["reporting_officer"] = sanitized_message
        save_user_data(user_details)  # ✅ Save final data

        logging.info(f"✅ User {user_id} completed registration: {user_details[user_id]}")
        await update.message.reply_text("✅ Registration complete! Type /start to begin using the bot.")


# ✅ Handle Quick-Select Button Clicks
# ✅ Handle Quick-Select Button Clicks
# ✅ Handle Quick-Select Button Clicks
async def handle_registration_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    callback_data = query.data

    # ✅ Debugging log
    logging.info(f"📥 Callback received: {callback_data} from user {user_id}")

    # ✅ Fix: Ensure callback_data is split correctly
    parts = callback_data.split("_", 2)  # ✅ Now properly handles categories with two parts (e.g., "skill_level_Beginner")

    if len(parts) < 2:
        logging.error(f"❌ Invalid callback data format: {callback_data}")
        await query.message.reply_text("⚠️ Unknown selection. Please try again.")
        return

    category = f"{parts[0]}_{parts[1]}" if len(parts) == 3 else parts[0]  # ✅ Reconstruct category (e.g., "skill_level")
    value = parts[2] if len(parts) == 3 else parts[1]  # ✅ Extract value correctly

    # ✅ Reload user details
    user_details = load_user_details()

    # ✅ Ensure user exists before modifying
    if user_id not in user_details:
        user_details[user_id] = {}

    # ✅ Handle Skill Level Selection
    if category == "skill_level":
        user_details[user_id]["skill_level"] = value
        context.user_data["registration_step"] = "role_specialization"
        save_user_data(user_details)

        logging.info(f"✅ Skill Level updated: {value} for user {user_id}")

        # ✅ Provide next selection options
        buttons = [
            [InlineKeyboardButton("Software Engineer", callback_data="role_specialization_Software Engineer")],
            [InlineKeyboardButton("DevOps Engineer", callback_data="role_specialization_DevOps Engineer")],
            [InlineKeyboardButton("Data Scientist", callback_data="role_specialization_Data Scientist")],
            [InlineKeyboardButton("Consultant", callback_data="role_specialization_Consultant")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.reply_text(f"✅ Skill Level set to: {value}\n\n💼 Select your Role Specialization:", reply_markup=reply_markup)

    # ✅ Handle Role Specialization
    elif category == "role_specialization":
        user_details[user_id]["role_specialization"] = value
        context.user_data["registration_step"] = "group_specialization"
        save_user_data(user_details)

        logging.info(f"✅ Role Specialization updated: {value} for user {user_id}")

        await query.message.reply_text(f"✅ Role Specialization set to: {value}\n\n🏢 Enter your Group Specialization:\n\n```\nConsulting\nTech Support\n```",
                                       parse_mode="MarkdownV2")

    # ✅ Handle Contractor Selection
    elif category == "contractor":
        user_details[user_id]["contractor"] = value
        context.user_data["registration_step"] = "po_ref"
        save_user_data(user_details)

        logging.info(f"✅ Contractor updated: {value} for user {user_id}")

        await query.message.reply_text(f"✅ Contractor set to: {value}\n\n📄 Enter your PO Reference Number:\n\n```\n12345-ABC\n```",
                                       parse_mode="MarkdownV2")

    else:
        logging.error(f"❌ Unhandled category: {category} - Value: {value}")
        await query.message.reply_text("⚠️ Unknown selection. Please try again.")

