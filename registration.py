import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.utils import load_user_details, save_user_data  # ✅ Import functions from utils

# ✅ Function to register a new user
async def register_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    # ✅ Reload USER_DETAILS dynamically
    user_details = load_user_details()

    if user_id in user_details:
        return  # ✅ User already exists, no need to register again

    await update.message.reply_text("Welcome! Please enter your full name:")
    context.user_data["registration_step"] = "name"

# ✅ Capture user registration details step-by-step
async def capture_user_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_message = update.message.text.strip()
    step = context.user_data.get("registration_step")

    if not step:
        await update.message.reply_text("❌ Registration error. Please type /start to retry.")
        return

    # ✅ Load latest user details before modifying
    user_details = load_user_details()

    if step == "name":
        context.user_data["name"] = user_message
        context.user_data["registration_step"] = "skill_level"
        await update.message.reply_text("Enter your Skill Level (e.g., 'Professional', 'Expert'):")

    elif step == "skill_level":
        context.user_data["skill_level"] = user_message
        context.user_data["registration_step"] = "role_specialization"
        await update.message.reply_text("Enter your Role Specialization (e.g., 'DevOps Engineer - II'):")

    elif step == "role_specialization":
        context.user_data["role_specialization"] = user_message
        context.user_data["registration_step"] = "group_specialization"
        await update.message.reply_text("Enter your Group Specialization (e.g., 'Consultant'):")

    elif step == "group_specialization":
        context.user_data["group_specialization"] = user_message
        context.user_data["registration_step"] = "contractor"
        await update.message.reply_text("Enter your Contractor (e.g., 'PALO IT'):")

    elif step == "contractor":
        context.user_data["contractor"] = user_message
        context.user_data["registration_step"] = "po_ref"
        await update.message.reply_text("Enter your PO Reference Number:")

    elif step == "po_ref":
        context.user_data["po_ref"] = user_message
        context.user_data["registration_step"] = "po_date"
        await update.message.reply_text("Enter your PO Date Range (e.g., '1 May 24 - 30 Apr 25'):")

    elif step == "po_date":
        context.user_data["po_date"] = user_message
        context.user_data["registration_step"] = "description"
        await update.message.reply_text("Enter your Job Description (e.g., 'Agile Co-Development Services'):")

    elif step == "description":
        context.user_data["description"] = user_message
        context.user_data["registration_step"] = "reporting_officer"
        await update.message.reply_text("Enter your Reporting Officer's Name:")

    elif step == "reporting_officer":
        context.user_data["reporting_officer"] = user_message

        # ✅ Save user data with all captured details
        user_details[user_id] = {
            "name": context.user_data["name"],
            "skill_level": context.user_data["skill_level"],
            "role_specialization": context.user_data["role_specialization"],
            "group_specialization": context.user_data["group_specialization"],
            "contractor": context.user_data["contractor"],
            "po_ref": context.user_data["po_ref"],
            "po_date": context.user_data["po_date"],
            "description": context.user_data["description"],
            "reporting_officer": context.user_data["reporting_officer"],
        }
        save_user_data(user_details)  # ✅ Save data without overwriting existing users

        logging.info(f"✅ User {user_id} completed registration: {user_details[user_id]}")

        await update.message.reply_text("✅ Registration complete! Type /start to begin using the bot.")
