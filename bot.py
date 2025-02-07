import os
import logging
from datetime import datetime
from calendar import monthrange
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
#from utils.utils import USER_DETAILS
from timesheet_generator import generate_timesheet_excel
from registration import register_new_user, capture_user_details  # Import registration functions
from telegram.ext import MessageHandler, filters  # ✅ Add MessageHandler and filters
#from utils.utils import USER_DETAILS, load_user_details  # ✅ Import load_user_details
from utils.utils import PUBLIC_HOLIDAYS, load_user_details # ✅ Load dynamically
from registration import register_new_user, capture_user_details, handle_registration_buttons  # ✅ Import the missing function




# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configure logging with DEBUG mode
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Get bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN is missing. Please set it in the .env file.")
    exit(1)

# In-memory storage for user inputs
user_leaves = {}

# ✅ Start Command -- OLD START
#async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    user_id = str(update.effective_user.id)
#    user_details = USER_DETAILS.get(user_id)
#
#    if user_details:
#        name = user_details["name"]
#        buttons = [[InlineKeyboardButton(month, callback_data=f"month_{month}")] for month in [
#            "January", "February", "March", "April", "May", "June",
#            "July", "August", "September", "October", "November", "December"
#        ]]
#        reply_markup = InlineKeyboardMarkup(buttons)
#        logger.info(f"User {name} ({user_id}) started the bot.")
#
#        await update.message.reply_text(f"Welcome, {name}! Please select the month for the timesheet:", reply_markup=reply_markup)
#    else:
#        logger.warning(f"Unregistered user {user_id} attempted to start the bot.")
#        await update.message.reply_text("You are not registered in the system. Please contact your administrator.")

#NEW START FLOW begins from here:

# ✅ **Start Command - Checks if User Exists or Registers New User**
#async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    user_id = str(update.effective_user.id)
#
#    if user_id in USER_DETAILS:
#        name = USER_DETAILS[user_id]["name"]
#        buttons = [[InlineKeyboardButton(month, callback_data=f"month_{month}")] for month in [
#            "January", "February", "March", "April", "May", "June",
#            "July", "August", "September", "October", "November", "December"
#        ]]
#        reply_markup = InlineKeyboardMarkup(buttons)
#        logger.info(f"Returning user {name} ({user_id}) started the bot.")
#        await update.message.reply_text(f"Welcome back, {name}! Select a month for your timesheet:", reply_markup=reply_markup)
#    else:
#        logger.info(f"New user {user_id} detected. Redirecting to registration.")
#        await register_new_user(update, context)  # Call the registration function

#async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    user_id = str(update.effective_user.id)
#    user_details = USER_DETAILS.get(user_id)  # ✅ Now updates correctly after registration!
#
#    if user_details:
#        name = user_details["name"]
#        buttons = [[InlineKeyboardButton(month, callback_data=f"month_{month}")] for month in [
#            "January", "February", "March", "April", "May", "June",
#            "July", "August", "September", "October", "November", "December"
#        ]]
#        reply_markup = InlineKeyboardMarkup(buttons)
#        logger.info(f"User {name} ({user_id}) started the bot.")
#
#        await update.message.reply_text(f"Welcome, {name}! Please select the month for the timesheet:", reply_markup=reply_markup)
#    else:
#        logger.info(f"New user {user_id} detected. Redirecting to registration.")
#        await register_new_user(update, context)
#
#async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    user_id = str(update.effective_user.id)
#
#    # ✅ Force reload USER_DETAILS to reflect new registrations
#    load_user_details()
#
#    user_details = USER_DETAILS.get(user_id)  # ✅ Now updates correctly after registration!
#
#    if user_details:
#        name = user_details["name"]
#        buttons = [[InlineKeyboardButton(month, callback_data=f"month_{month}")] for month in [
#            "January", "February", "March", "April", "May", "June",
#            "July", "August", "September", "October", "November", "December"
#        ]]
#        reply_markup = InlineKeyboardMarkup(buttons)
#        logger.info(f"User {name} ({user_id}) started the bot.")
#
#        await update.message.reply_text(f"Welcome, {name}! Please select the month for the timesheet:", reply_markup=reply_markup)
#    else:
#        logger.info(f"New user {user_id} detected. Redirecting to registration.")
#        await register_new_user(update, context)

#async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    user_id = str(update.effective_user.id)
#
#    # ✅ Force reload USER_DETAILS to reflect new registrations
#    load_user_details()
#
#    user_details = USER_DETAILS.get(user_id)  # ✅ Now updates correctly after registration!
#
#    if user_details:
#        name = user_details["name"]
#        buttons = [[InlineKeyboardButton(month, callback_data=f"month_{month}")] for month in [
#            "January", "February", "March", "April", "May", "June",
#            "July", "August", "September", "October", "November", "December"
#        ]]
#        reply_markup = InlineKeyboardMarkup(buttons)
#        logger.info(f"User {name} ({user_id}) started the bot.")
#
#        await update.message.reply_text(f"Welcome, {name}! Please select the month for the timesheet:", reply_markup=reply_markup)
#    else:
#        logger.info(f"New user {user_id} detected. Redirecting to registration.")
#        await register_new_user(update, context)

#async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    user_id = str(update.effective_user.id)
#
#    # ✅ Reload user details dynamically
#    USER_DETAILS = load_user_details()
#
#    user_details = USER_DETAILS.get(user_id)
#
#    if user_details:
#        name = user_details["name"]
#        await update.message.reply_text(f"Welcome back, {name}! Select a month for your timesheet.")
#    else:
#        await register_new_user(update, context)  # ✅ Redirect to registration
#

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    # ✅ Reload user details dynamically
    USER_DETAILS = load_user_details()

    user_details = USER_DETAILS.get(user_id)

    if user_details:
        name = user_details["name"]
        buttons = [
            [InlineKeyboardButton(month, callback_data=f"month_{month}")]
            for month in [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        logger.info(f"User {name} ({user_id}) started the bot.")
        await update.message.reply_text(f"Welcome back, {name}! Select a month for your timesheet:", reply_markup=reply_markup)

    else:
        logger.info(f"New user {user_id} detected. Redirecting to registration.")
        await register_new_user(update, context)  # ✅ Redirect to registration


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

    try:
        # Ensure callback data has the correct format: start_date_6-June
        callback_data = query.data
        if not callback_data.startswith("start_date_"):
            logger.error(f"Invalid start date callback data: {callback_data}")
            await query.message.reply_text("Error: Invalid date format received. Please restart.")
            return

        # Extract and validate the date
        selected_start_date = callback_data.replace("start_date_", "")
        datetime.strptime(selected_start_date, "%d-%B")  # Validate format

        # Store the valid date in context
        context.user_data["start_date"] = selected_start_date
        logger.info(f"User selected start date: {selected_start_date}")
        print("selected_start_date chosen by user", selected_start_date)

        # Move to End Date selection
        await show_end_date_selection(update, context)

    except ValueError:
        logger.error(f"Invalid date format received: {callback_data}")
        await query.message.reply_text("Error: Selected date format is incorrect. Please try again.")


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

    try:
        # Ensure callback data has the correct format: end_date_6-June
        callback_data = query.data
        if not callback_data.startswith("end_date_"):
            logger.error(f"Invalid end date callback data: {callback_data}")
            await query.message.reply_text("Error: Invalid date format received. Please restart.")
            return

        # Extract and validate the date
        selected_end_date = callback_data.replace("end_date_", "")
        datetime.strptime(selected_end_date, "%d-%B")  # Validate format

        user_id = str(update.effective_user.id)
        month = context.user_data.get("month")
        start_date = context.user_data.get("start_date")
        leave_type = context.user_data.get("leave_type")

        if not start_date or not leave_type:
            await query.message.reply_text("Error: Missing leave details. Please restart.")
            return

        # ✅ Fix: Validate date format before storing
        start_date_obj = datetime.strptime(start_date, "%d-%B")
        end_date_obj = datetime.strptime(selected_end_date, "%d-%B")

        # ✅ Store properly formatted dates
        if user_id not in user_leaves:
            user_leaves[user_id] = {}
        if month not in user_leaves[user_id]:
            user_leaves[user_id][month] = []

        user_leaves[user_id][month].append((start_date_obj.strftime("%d-%B"), end_date_obj.strftime("%d-%B"), leave_type))
        logger.info(f"Stored leave for {user_id}: {start_date} to {selected_end_date} ({leave_type})")

        buttons = [
            [InlineKeyboardButton("Yes, Add More Leaves", callback_data="apply_leave")],
            [InlineKeyboardButton("No, Generate Timesheet", callback_data="generate_timesheet_after_leave")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.reply_text("Do you want to add more leaves?", reply_markup=reply_markup)

    except ValueError as e:
        logger.error(f"Invalid date format received: {e}")
        await query.message.reply_text("Error: Selected date format is incorrect. Please try again.")


# ✅ Handle Generate Timesheet
async def generate_timesheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    month = context.user_data.get("month")

    try:
        if not month:
            await query.message.reply_text("You must first select a month.")
            return

        logger.info(f"Generating timesheet for user {user_id} for month: {month}")

        month_number = datetime.strptime(month, "%B").month
        year = datetime.now().year
        leave_data = user_leaves.get(user_id, {}).get(month, [])

        # ✅ Debugging: Print stored leave data before processing
        logger.info(f"Raw leave_data for user {user_id}: {leave_data}")

        parsed_leave_data = []
        for leave_entry in leave_data:
            try:
                # ✅ Debugging: Print each leave entry before unpacking
                logger.info(f"Processing leave entry: {leave_entry}")

                # Check tuple length before unpacking
                if not isinstance(leave_entry, tuple):
                    raise ValueError(f"Unexpected type for leave_entry: {type(leave_entry)} - {leave_entry}")
                if len(leave_entry) != 3:
                    raise ValueError(f"Unexpected leave entry format: {leave_entry}")

                start_date_str, end_date_str, leave_type = leave_entry

                # ✅ Debugging: Print extracted values
                logger.info(f"Extracted - Start: {start_date_str}, End: {end_date_str}, Type: {leave_type}")

                # ✅ Validate and convert date format
                start_date_obj = datetime.strptime(start_date_str, "%d-%B").replace(year=year)
                end_date_obj = datetime.strptime(end_date_str, "%d-%B").replace(year=year)

                parsed_leave_data.append((start_date_obj.strftime("%d-%B"), end_date_obj.strftime("%d-%B"), leave_type))

            except ValueError as e:
                logger.error(f"Corrupt leave data detected: {leave_entry} - {e}")
                await query.message.reply_text(f"Error: Corrupt leave data detected. Resetting data.")
                user_leaves[user_id][month] = []
                return

        # ✅ Debugging: Print processed leave data before generating timesheet
        logger.info(f"Final parsed_leave_data: {parsed_leave_data}")

        # ✅ Generate timesheet with correct format
        output_file = generate_timesheet_excel(user_id, month_number, year, parsed_leave_data)

        with open(output_file, "rb") as doc:
            await query.message.reply_document(document=doc, filename=os.path.basename(output_file))

        user_leaves[user_id][month] = []  # ✅ Clear only after successful generation

    except Exception as e:
        logger.error(f"Error generating timesheet: {e}")
        await query.message.reply_text(f"Error generating timesheet: {e}")



# ✅ Register Handlers OLD MAIN
#def main():
#    application = Application.builder().token(BOT_TOKEN).build()
#
#    application.add_handler(CommandHandler("start", start))
#    application.add_handler(CallbackQueryHandler(month_handler, pattern="^month_"))
#    application.add_handler(CallbackQueryHandler(apply_leave, pattern="^apply_leave$"))  # ✅ FIXED: Handler was missing
#    application.add_handler(CallbackQueryHandler(leave_type_handler, pattern="^leave_"))
#    application.add_handler(CallbackQueryHandler(start_date_handler, pattern="^start_date_"))
#    application.add_handler(CallbackQueryHandler(end_date_handler, pattern="^end_date_"))
#    application.add_handler(CallbackQueryHandler(generate_timesheet, pattern="^(generate_timesheet_now|generate_timesheet_after_leave)$"))
#
#    application.run_polling()

#NEW MAIN begins here
# ✅ **Main Function with All Handlers**
#def main():
#    application = Application.builder().token(BOT_TOKEN).build()
#
#    # ✅ Primary Commands
#    application.add_handler(CommandHandler("start", start))
#
#    # ✅ CallbackQuery Handlers
#    application.add_handler(CallbackQueryHandler(month_handler, pattern="^month_"))
#    application.add_handler(CallbackQueryHandler(apply_leave, pattern="^apply_leave$"))
#    application.add_handler(CallbackQueryHandler(leave_type_handler, pattern="^leave_"))
#    application.add_handler(CallbackQueryHandler(start_date_handler, pattern="^start_date_"))
#    application.add_handler(CallbackQueryHandler(end_date_handler, pattern="^end_date_"))
#    application.add_handler(CallbackQueryHandler(generate_timesheet, pattern="^(generate_timesheet_now|generate_timesheet_after_leave)$"))
#
#    # ✅ Capture Registration Data (Handles text input)
#    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_user_details))
#
#    application.run_polling()

#def main():
#    application = Application.builder().token(BOT_TOKEN).build()
#
#    application.add_handler(CommandHandler("start", start))
#    application.add_handler(CommandHandler("register", register_new_user))
#    application.add_handler(CommandHandler("capture", capture_user_details))
#    application.add_handler(CallbackQueryHandler(month_handler, pattern="^month_"))
#    application.add_handler(CallbackQueryHandler(apply_leave, pattern="^apply_leave$"))
#    application.add_handler(CallbackQueryHandler(leave_type_handler, pattern="^leave_"))
#    application.add_handler(CallbackQueryHandler(start_date_handler, pattern="^start_date_"))
#    application.add_handler(CallbackQueryHandler(end_date_handler, pattern="^end_date_"))
#    application.add_handler(CallbackQueryHandler(generate_timesheet, pattern="^(generate_timesheet_now|generate_timesheet_after_leave)$"))
#
#    application.run_polling()

# LATEST main attempt:
#def main():
#    application = Application.builder().token(BOT_TOKEN).build()
#
#    application.add_handler(CommandHandler("start", start))
#    application.add_handler(CommandHandler("register", register_new_user))
#
#    # ✅ Add MessageHandler to capture user input during registration
#    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_user_details))
#
#    application.add_handler(CallbackQueryHandler(month_handler, pattern="^month_"))
#    application.add_handler(CallbackQueryHandler(apply_leave, pattern="^apply_leave$"))
#    application.add_handler(CallbackQueryHandler(leave_type_handler, pattern="^leave_"))
#    application.add_handler(CallbackQueryHandler(start_date_handler, pattern="^start_date_"))
#    application.add_handler(CallbackQueryHandler(end_date_handler, pattern="^end_date_"))
#    application.add_handler(
#        CallbackQueryHandler(generate_timesheet, pattern="^(generate_timesheet_now|generate_timesheet_after_leave)$"))
#
#    application.run_polling()


# ✅ Add this to `main()` in bot.py
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register_new_user))

    # ✅ Add MessageHandler to capture user input during registration
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_user_details))

    # ✅ Fix: Add CallbackQueryHandler for handling quick-select buttons
    #application.add_handler(CallbackQueryHandler(handle_registration_buttons, pattern="^(skill_level|role_specialization|contractor)_"))
    application.add_handler(
        CallbackQueryHandler(handle_registration_buttons, pattern="^(skill_level|role_specialization|contractor)_.+"))

    #application.add_handler(
    #    CallbackQueryHandler(handle_registration_buttons, pattern="^(skill_level|role_specialization|contractor)_.+"))

    application.add_handler(CallbackQueryHandler(month_handler, pattern="^month_"))
    application.add_handler(CallbackQueryHandler(apply_leave, pattern="^apply_leave$"))
    application.add_handler(CallbackQueryHandler(leave_type_handler, pattern="^leave_"))
    application.add_handler(CallbackQueryHandler(start_date_handler, pattern="^start_date_"))
    application.add_handler(CallbackQueryHandler(end_date_handler, pattern="^end_date_"))
    application.add_handler(
        CallbackQueryHandler(generate_timesheet, pattern="^(generate_timesheet_now|generate_timesheet_after_leave)$"))

    application.run_polling()

if __name__ == "__main__":
    main()
