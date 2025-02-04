from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from utils.utils import USER_DETAILS
from timesheet_generator import generate_timesheet_excel
from datetime import datetime
import os
import logging
from dotenv import load_dotenv
from calendar import monthrange

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Get bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN is missing. Please set it in the .env file.")
    exit(1)

# In-memory storage for user inputs
user_leaves = {}

# ✅ Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_details = USER_DETAILS.get(user_id)

    if user_details:
        name = user_details["name"]
        buttons = [[InlineKeyboardButton(month, callback_data=f"month_{month}")] for month in [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        logger.info(f"User {name} ({user_id}) started the bot.")

        await update.message.reply_text(f"Welcome, {name}! Please select the month for the timesheet:", reply_markup=reply_markup)
    else:
        logger.warning(f"Unregistered user {user_id} attempted to start the bot.")
        await update.message.reply_text("You are not registered in the system. Please contact your administrator.")

# ✅ Handle Month Selection
async def month_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_month = query.data.split("_")[1]
    context.user_data["month"] = selected_month
    logger.info(f"User {update.effective_user.id} selected month: {selected_month}")

    buttons = [
        [InlineKeyboardButton("Apply Leave", callback_data="apply_leave")],
        [InlineKeyboardButton("Generate Timesheet Without Leave", callback_data="generate_timesheet_now")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text("Do you want to apply for leave before generating the timesheet?", reply_markup=reply_markup)

# ✅ Handle Apply Leave
async def apply_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info("User selected 'Apply Leave' button.")  # Debugging log
    await show_leave_type_selection(update, context)

# ✅ Show Leave Type Selection
async def show_leave_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    buttons = [
        [InlineKeyboardButton("Sick Leave", callback_data="leave_Sick Leave")],
        [InlineKeyboardButton("Childcare Leave", callback_data="leave_Childcare Leave")],
        [InlineKeyboardButton("Annual Leave", callback_data="leave_Annual Leave")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text("Please choose the leave type:", reply_markup=reply_markup)

# ✅ Handle Leave Type Selection
async def leave_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    leave_type = query.data.split("_")[1]
    context.user_data["leave_type"] = leave_type
    logger.info(f"User selected leave type: {leave_type}")

    await show_start_date_selection(update, context)

# ✅ Show Start Date Selection
async def show_start_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    month = context.user_data.get("month")
    year = datetime.now().year
    month_number = datetime.strptime(month, "%B").month
    _, days_in_month = monthrange(year, month_number)

    buttons = [
        [InlineKeyboardButton(f"{day}-{month}", callback_data=f"start_date_{day}-{month}")
         for day in range(start, min(start + 7, days_in_month + 1))]
        for start in range(1, days_in_month + 1, 7)
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text("Select the **Start Date** for your leave:", reply_markup=reply_markup)

# ✅ Handle Start Date Selection
async def start_date_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_start_date = query.data.split("_")[1]
    context.user_data["start_date"] = selected_start_date
    logger.info(f"User selected start date: {selected_start_date}")

    await show_end_date_selection(update, context)

# ✅ Show End Date Selection (🔧 FIXED MISSING FUNCTION)
async def show_end_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    month = context.user_data.get("month")
    year = datetime.now().year
    month_number = datetime.strptime(month, "%B").month
    _, days_in_month = monthrange(year, month_number)

    buttons = [
        [InlineKeyboardButton(f"{day}-{month}", callback_data=f"end_date_{day}-{month}")
         for day in range(start, min(start + 7, days_in_month + 1))]
        for start in range(1, days_in_month + 1, 7)
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text("Select the **End Date** for your leave:", reply_markup=reply_markup)

# ✅ Handle End Date Selection
async def end_date_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_end_date = query.data.split("_")[1]
    user_id = str(update.effective_user.id)
    month = context.user_data.get("month")
    start_date = context.user_data.get("start_date")
    leave_type = context.user_data.get("leave_type")

    if not start_date or not leave_type:
        await query.message.reply_text("Error: Missing leave details. Please restart.")
        return

    if user_id not in user_leaves:
        user_leaves[user_id] = {}
    if month not in user_leaves[user_id]:
        user_leaves[user_id][month] = []

    user_leaves[user_id][month].append((f"{start_date} to {selected_end_date}", leave_type))

    buttons = [
        [InlineKeyboardButton("Yes, Add More Leaves", callback_data="apply_leave")],
        [InlineKeyboardButton("No, Generate Timesheet", callback_data="generate_timesheet_after_leave")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text("Do you want to add more leaves?", reply_markup=reply_markup)


# ✅ Handle Generate Timesheet
async def generate_timesheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    month = context.user_data.get("month")

    try:
        logger.info(f"Generating timesheet for user {user_id} for month: {month}")

        month_number = datetime.strptime(month, "%B").month
        year = datetime.now().year

        leave_data = user_leaves.get(user_id, {}).get(month, [])

        output_file = generate_timesheet_excel(user_id, month_number, year, leave_data)

        with open(output_file, "rb") as doc:
            await query.message.reply_document(document=doc, filename=os.path.basename(output_file))

        user_leaves[user_id][month] = []

    except Exception as e:
        logger.error(f"Error generating timesheet: {e}")
        await query.message.reply_text(f"Error generating timesheet: {e}")

# ✅ Register Handlers
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(month_handler, pattern="^month_"))
    application.add_handler(CallbackQueryHandler(apply_leave, pattern="^apply_leave$"))  # ✅ FIXED: Handler was missing
    application.add_handler(CallbackQueryHandler(leave_type_handler, pattern="^leave_"))
    application.add_handler(CallbackQueryHandler(start_date_handler, pattern="^start_date_"))
    application.add_handler(CallbackQueryHandler(end_date_handler, pattern="^end_date_"))
    application.add_handler(CallbackQueryHandler(generate_timesheet, pattern="^(generate_timesheet_now|generate_timesheet_after_leave)$"))

    application.run_polling()

if __name__ == "__main__":
    main()
