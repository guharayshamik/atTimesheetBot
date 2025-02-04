from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from utils.utils import PUBLIC_HOLIDAYS, USER_DETAILS
from timesheet_generator import generate_timesheet_excel
from datetime import datetime, timedelta
import os
import logging
from dotenv import load_dotenv
from calendar import monthrange

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

# In-memory storage for user inputs
user_leaves = {}

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_details = USER_DETAILS.get(user_id, None)

    if user_details:
        name = user_details["name"]
        buttons = [[InlineKeyboardButton("Generate Timesheet", callback_data="generate_timesheet")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        logger.info(f"User {name} ({user_id}) started the bot.")
        await update.message.reply_text(f"Welcome, {name}! What would you like to do?", reply_markup=reply_markup)
    else:
        logger.warning(f"Unregistered user {user_id} attempted to start the bot.")
        await update.message.reply_text("You are not registered in the system. Please contact your administrator.")

# Handle "Generate Timesheet" Selection
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info(f"User {update.effective_user.id} selected 'Generate Timesheet'. Showing month selection.")

    # Show month selection
    buttons = [[InlineKeyboardButton(month, callback_data=f"month_{month}")] for month in [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text("Please select the month for the timesheet:", reply_markup=reply_markup)

# Handle Month Selection and Proceed to Date Selection
async def month_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_month = query.data.split("_")[1]

    context.user_data["month"] = selected_month
    logger.info(f"User {update.effective_user.id} selected month: {selected_month}. Showing date selection.")

    await show_date_selection(update, context)

# Show a list of dates for the selected month
async def show_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    month = context.user_data.get("month")
    year = datetime.now().year

    if not month:
        await update.message.reply_text("Please select a month first.")
        return

    month_number = datetime.strptime(month, "%B").month
    _, days_in_month = monthrange(year, month_number)

    # Create date selection buttons
    buttons = []
    for day in range(1, days_in_month + 1, 7):  # Show 7 dates per row
        row = [
            InlineKeyboardButton(f"{day}-{month}", callback_data=f"date_{day}-{month}")
            for day in range(day, min(day + 7, days_in_month + 1))
        ]
        buttons.append(row)

    reply_markup = InlineKeyboardMarkup(buttons)
    logger.info(f"User {user_id} is selecting a date for leave in {month}.")
    await update.callback_query.message.reply_text("Please choose a date for leave:", reply_markup=reply_markup)

# Handle Date Selection and Proceed to Leave Type Selection
async def date_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_date = query.data.split("_")[1]

    context.user_data["selected_date"] = selected_date
    logger.info(f"User {update.effective_user.id} selected date: {selected_date}. Showing leave type selection.")

    # Show leave type selection
    buttons = [
        [InlineKeyboardButton("Sick Leave", callback_data="leave_Sick Leave")],
        [InlineKeyboardButton("Childcare Leave", callback_data="leave_Childcare Leave")],
        [InlineKeyboardButton("Annual Leave", callback_data="leave_Annual Leave")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text("Please choose the leave type:", reply_markup=reply_markup)

# Handle Leave Type Selection and Ask if More Leaves are Needed
async def leave_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    leave_type = query.data.split("_")[1]
    user_id = str(update.effective_user.id)

    selected_date = context.user_data.get("selected_date")
    month = context.user_data.get("month")

    if not selected_date or not month:
        await query.message.reply_text("Something went wrong. Please start again.")
        return

    # Store the leave details
    if user_id not in user_leaves:
        user_leaves[user_id] = {}
    if month not in user_leaves[user_id]:
        user_leaves[user_id][month] = []

    user_leaves[user_id][month].append((selected_date, leave_type))
    logger.info(f"User {user_id} added leave: {selected_date} - {leave_type}")

    # Ask if more leaves need to be added
    buttons = [
        [InlineKeyboardButton("Yes, Add More Leaves", callback_data="add_more_leaves")],
        [InlineKeyboardButton("No, Generate Timesheet", callback_data="final_generate_timesheet")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text("Do you want to add more leaves?", reply_markup=reply_markup)

# Handle More Leaves or Proceed to Generate Timesheet
async def more_leaves_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add_more_leaves":
        logger.info(f"User {update.effective_user.id} is adding more leaves.")
        await show_date_selection(update, context)  # Restart leave selection
        print("await show_date_selection")
    if query.data == "final_generate_timesheet":
        logger.info(f"User {update.effective_user.id} selected 'No, Generate Timesheet'. Proceeding to generation.")
        await generate_timesheet(update, context)
        print("await generate_timesheet")

# ✅ **Ensure the timesheet is generated properly**
async def generate_timesheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    month = context.user_data.get("month")

    try:
        if not month or user_id not in user_leaves or not user_leaves[user_id].get(month):
            logger.warning(f"User {user_id} attempted to generate a timesheet without providing complete details.")
            await update.message.reply_text("You must first select a month and update leave details.")
            return

        month_number = datetime.strptime(month, "%B").month
        year = datetime.now().year
        leave_data = user_leaves[user_id][month]

        logger.info(f"Generating timesheet for user {user_id} for {month} {year} with leaves: {leave_data}")

        output_file = generate_timesheet_excel(user_id, month_number, year, leave_data)
        await update.message.reply_document(document=open(output_file, "rb"), filename=os.path.basename(output_file))

        del user_leaves[user_id]
        context.user_data.clear()
    except Exception as e:
        logger.error(f"Error generating timesheet for user {user_id}: {e}")
        await update.message.reply_text(f"Error generating timesheet: {e}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"An error occurred: {context.error}")
# Register Handlers
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))

    # CallbackQuery handlers for user selections
    application.add_handler(CallbackQueryHandler(menu_handler, pattern="^generate_timesheet$"))
    application.add_handler(CallbackQueryHandler(month_handler, pattern="^month_"))
    application.add_handler(CallbackQueryHandler(date_handler, pattern="^date_"))
    application.add_handler(CallbackQueryHandler(leave_type_handler, pattern="^leave_"))
    application.add_handler(CallbackQueryHandler(more_leaves_handler, pattern="^(add_more_leaves|final_generate_timesheet)$"))

    # Error handler to catch exceptions
    application.add_error_handler(error_handler)

    logger.info("Bot has started successfully. Waiting for user input...")
    application.run_polling()


if __name__ == "__main__":
    main()
