from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from utils.utils import PUBLIC_HOLIDAYS, USER_DETAILS
from timesheet_generator import generate_timesheet_excel
from datetime import datetime, timedelta
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Get the bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN is missing. Please set it in the .env file.")
    exit(1)

# In-memory leave storage
user_leaves = {}


# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_details = USER_DETAILS.get(user_id, None)

    if user_details:
        name = user_details["name"]
        buttons = [
            [InlineKeyboardButton("Generate Timesheet", callback_data="generate_timesheet")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        logger.info(f"User {name} ({user_id}) started the bot.")
        await update.message.reply_text(f"Welcome, {name}! What would you like to do?", reply_markup=reply_markup)
    else:
        logger.warning(f"Unregistered user {user_id} attempted to start the bot.")
        await update.message.reply_text("You are not registered in the system. Please contact your administrator.")


# Handle main menu selection
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "generate_timesheet":
        # Prompt for month selection
        buttons = [[InlineKeyboardButton(month, callback_data=f"month_{month}")] for month in [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        logger.info(f"User {update.effective_user.id} selected 'Generate Timesheet'.")
        await query.message.reply_text("Please select the month for the timesheet:", reply_markup=reply_markup)


# Handle month selection
async def month_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_month = query.data.split("_")[1]

    # Store the selected month in user_data
    context.user_data["month"] = selected_month
    logger.info(f"User {update.effective_user.id} selected month: {selected_month}.")
    await query.message.reply_text(f"You selected {selected_month}. Please enter the leave details in the format:\n\n"
                                    "`01-01: Sick Leave`\n`01-05 to 01-07: Annual Leave`\n\n"
                                    "You can add multiple leaves, one per line.", parse_mode="Markdown")


# Handle leave details input
# Handle leave details input
async def leave_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    leave_details = update.message.text.strip().split("\n")
    month = context.user_data.get("month")
    year = datetime.now().year  # Default to the current year

    if not month:
        await update.message.reply_text("Please select a month first.")
        return

    # Map month name to number
    try:
        month_number = datetime.strptime(month, "%B").month
    except ValueError:
        await update.message.reply_text(f"Invalid month: {month}")
        return

    # Validate and parse leave details
    invalid_dates = []
    valid_leaves = []
    for leave in leave_details:
        try:
            if "to" in leave:
                # Handle date ranges
                date_range, leave_type = leave.split(":")
                start_date, end_date = date_range.split("to")
                start_date = datetime.strptime(f"{start_date.strip()}-{year}", "%d-%m-%Y")
                end_date = datetime.strptime(f"{end_date.strip()}-{year}", "%d-%m-%Y")

                if start_date > end_date:
                    raise ValueError("Start date cannot be after end date.")

                # Add all dates in the range
                for single_date in (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)):
                    if single_date.month != month_number:
                        continue  # Skip dates outside the selected month
                    valid_leaves.append((single_date.strftime("%Y-%m-%d"), leave_type.strip()))
            else:
                # Handle single dates
                date, leave_type = leave.split(":")
                single_date = datetime.strptime(f"{date.strip()}-{year}", "%d-%m-%Y")
                if single_date.month != month_number:
                    continue  # Skip dates outside the selected month
                valid_leaves.append((single_date.strftime("%Y-%m-%d"), leave_type.strip()))
        except (ValueError, IndexError):
            invalid_dates.append(leave)

    # Filter out weekends and public holidays
    final_leaves = []
    invalid_leave_days = []
    for date, leave_type in valid_leaves:
        if date in PUBLIC_HOLIDAYS or datetime.strptime(date, "%Y-%m-%d").weekday() >= 5:
            invalid_leave_days.append(date)
        else:
            final_leaves.append((date, leave_type))

    # Store the valid leaves
    if user_id not in user_leaves:
        user_leaves[user_id] = {}
    user_leaves[user_id][month] = final_leaves

    # Build the response message
    response = ""
    if invalid_dates:
        response += f"Invalid entries skipped: {', '.join(invalid_dates)}\n"
    if invalid_leave_days:
        response += f"Cannot apply leaves on public holidays or weekends: {', '.join(invalid_leave_days)}\n"
    response += f"Valid leaves for {month}: {final_leaves}\n\nType `/generate` to create the timesheet."

    await update.message.reply_text(response)



# Generate timesheet command
async def generate_timesheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    month = context.user_data.get("month")

    if not month or user_id not in user_leaves:
        logger.warning(f"User {user_id} attempted to generate a timesheet without providing complete details.")
        await update.message.reply_text("You must first select a month and update leave details.")
        return

    # Map month name to number
    month_number = datetime.strptime(month, "%B").month
    year = datetime.now().year

    try:
        # Generate Excel timesheet
        logger.info(f"Generating timesheet for user {user_id} for {month} {year}.")
        output_file = generate_timesheet_excel(user_id, month_number, year, user_leaves[user_id].get(month, []))
        await update.message.reply_text("Generating your timesheet...")
        await update.message.reply_document(document=open(output_file, "rb"), filename=os.path.basename(output_file))
        logger.info(f"Timesheet generated and sent to user {user_id}.")
    except Exception as e:
        logger.error(f"Error generating timesheet for user {user_id}: {e}")
        await update.message.reply_text(f"Error generating timesheet: {e}")


# Main function to run the bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler, pattern="^generate_timesheet$"))
    application.add_handler(CallbackQueryHandler(month_handler, pattern="^month_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, leave_input_handler))
    application.add_handler(CommandHandler("generate", generate_timesheet))

    # Start bot
    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
