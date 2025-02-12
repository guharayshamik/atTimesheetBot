import os
import logging
from datetime import datetime
from calendar import monthrange
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from timesheet_generator import generate_timesheet_excel
from utils.utils import PUBLIC_HOLIDAYS, load_user_details  # Load dynamically
from registration import register_new_user, capture_user_details, \
    handle_registration_buttons  # Import the missing function
from de_registration import confirm_deregistration, handle_deregistration_buttons
import asyncio
from collections import deque
import time
import configparser


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configure logging with DEBUG mode
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()

# Global queue dictionary to queue tasks per user
user_task_queues = {}

# Load config
config = configparser.ConfigParser()
config.read("config/config.ini")

# Now this works because we have a [rate_limit] section
MAX_ATTEMPTS = int(config["rate_limit"]["MAX_ATTEMPTS"])
TIME_WINDOW = int(config["rate_limit"]["TIME_WINDOW"])
AWAIT = float(config["race"]["AWAIT"])

#print(f"MAX_ATTEMPTS: {MAX_ATTEMPTS}, TIME_WINDOW: {TIME_WINDOW}, AWAIT: {AWAIT}")

# Rate limiter dictionary {user_id: deque of timestamps}
rate_limits = {}

# Ensure required values are present
if "rate_limit" not in config or "MAX_ATTEMPTS" not in config["rate_limit"] or "TIME_WINDOW" not in config["rate_limit"]:
    raise ValueError("Missing rate limit configuration in config.ini!")

# Get bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN is missing. Please set it in the .env file.")
    exit(1)

# In-memory storage for user inputs
user_leaves = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id).strip()
    query = update.callback_query  # Capture callback query

    USER_DETAILS = load_user_details()
    user_details = USER_DETAILS.get(user_id)

    # Check if this was triggered by a callback button
    message = update.message if update.message else query.message

    if user_details:
        name = user_details["name"]

        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        buttons = [
            [InlineKeyboardButton(months[i], callback_data=f"month_{months[i]}"),
             InlineKeyboardButton(months[i + 1], callback_data=f"month_{months[i + 1]}"),
             InlineKeyboardButton(months[i + 2], callback_data=f"month_{months[i + 2]}")]
            for i in range(0, len(months), 3)
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        logger.info(f"User {name} ({user_id}) started the bot.")

        await message.reply_text(
            f"👋 **Welcome back, {name}!**\n\n"
            "📅 **Select a month for your timesheet:**",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        logger.info(f"New user {user_id} detected. Redirecting to registration.")
        await register_new_user(update, context)


# Handle Month Selection
async def month_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_month = query.data.split("_")[1]
    context.user_data["month"] = selected_month
    context.user_data["waiting_for_button"] = True  # Expect button input next

    logger.info(f"User {update.effective_user.id} selected month: {selected_month}")

    buttons = [
        [InlineKeyboardButton("📝 Apply Leave", callback_data="apply_leave")],
        [InlineKeyboardButton("📊 Generate Timesheet Without Leave", callback_data="generate_timesheet_now")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await query.message.reply_text(
        f"📆 **You selected {selected_month}**\n\n"
        "Would you like to apply for leave before generating your timesheet?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# Handle Apply Leave
async def apply_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info("User selected 'Apply Leave' button.")  # Debugging log
    await show_leave_type_selection(update, context)


# Show Leave Type Selection
async def show_leave_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    buttons = [
        [InlineKeyboardButton("Sick Leave", callback_data="leave_Sick Leave")],
        [InlineKeyboardButton("Childcare Leave", callback_data="leave_Childcare Leave")],
        [InlineKeyboardButton("Annual Leave", callback_data="leave_Annual Leave")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    #await query.message.reply_text("Please choose the leave type:", reply_markup=reply_markup)
    await query.message.reply_text(
        "**Please choose the type of leave you want to apply for:**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# Handle Leave Type Selection
async def leave_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    leave_type = query.data.split("_")[1]
    context.user_data["leave_type"] = leave_type
    logger.info(f"User selected leave type: {leave_type}")

    await show_start_date_selection(update, context)


# Show START DATE Selection
async def show_start_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    month = context.user_data.get("month")
    short_month = month[:3]  # Get short month format (e.g., "January" -> "Jan")
    year = datetime.now().year
    month_number = datetime.strptime(month, "%B").month
    _, days_in_month = monthrange(year, month_number)

    buttons = []
    row = []
    for day in range(1, days_in_month + 1):
        row.append(InlineKeyboardButton(f"{day}-{short_month}", callback_data=f"start_date_{day}-{month}"))
        if len(row) == 5:  # Ensure 5 buttons per row for better visibility
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text(
        "📆 **Select the START DATE for your leave:**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# Handle START DATE Selection
async def start_date_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        # Ensure callback data has the correct format: start_date_6-June
        callback_data = query.data
        if not callback_data.startswith("start_date_"):
            logger.error(f"Invalid START DATE callback data: {callback_data}")
            await query.message.reply_text("⚠️ Invalid date format received.\n\nPlease restart using /start.")
            return

        # Extract and validate the date
        selected_start_date = callback_data.replace("start_date_", "")
        start_date_obj = datetime.strptime(selected_start_date, "%d-%B")  # Validate format

        user_id = str(update.effective_user.id)
        month = context.user_data.get("month")

        if not month:
            await query.message.reply_text("⚠️ Please select a month before choosing leave dates.")
            return

        # Ensure leave tracking exists
        if user_id not in user_leaves:
            user_leaves[user_id] = {}
        if month not in user_leaves[user_id]:
            user_leaves[user_id][month] = []

        # **Check if the selected START DATE overlaps with an existing leave**
        for existing_start, existing_end, existing_leave_type in user_leaves[user_id][month]:
            existing_start_date = datetime.strptime(existing_start, "%d-%B")
            existing_end_date = datetime.strptime(existing_end, "%d-%B")

            # Check if the selected start date falls within an existing leave period
            if existing_start_date <= start_date_obj <= existing_end_date:
                logger.warning(f"User {user_id} attempted overlapping start date: {selected_start_date}")
                await query.message.reply_text(
                    f"⚠️ The selected START DATE *overlaps* with an existing leave:\n"
                    f"📅 {existing_start} - {existing_end} ({existing_leave_type})\n\n"
                    "🔄 *Please select a different START DATE.*",
                    parse_mode="Markdown"
                )
                await show_start_date_selection(update, context)  # Prompt for a new start date
                return  # Stop execution

        # **If no overlap, proceed with storing the start date**
        context.user_data["start_date"] = selected_start_date
        logger.info(f"User {user_id} selected START DATE: {selected_start_date}")

        # Move to END DATE selection
        await show_end_date_selection(update, context)

    except ValueError:
        logger.error(f"Invalid date format received: {callback_data}")
        await query.message.reply_text("⚠️ Selected date format is incorrect. Please try again.")


# Show END DATE Selection ( FIXED MISSING FUNCTION )
async def show_end_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    month = context.user_data.get("month")
    short_month = month[:3]  # Convert "January" -> "Jan"
    year = datetime.now().year
    month_number = datetime.strptime(month, "%B").month
    _, days_in_month = monthrange(year, month_number)

    buttons = []
    row = []
    for day in range(1, days_in_month + 1):
        row.append(InlineKeyboardButton(f"{day}-{short_month}", callback_data=f"end_date_{day}-{month}"))
        if len(row) == 5:  # Ensure 5 buttons per row for better alignment
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text(
        "📆 **Select the END DATE for your leave:**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# Handle END DATE Selection
async def end_date_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        # Ensure callback data has the correct format: end_date_6-June
        callback_data = query.data
        if not callback_data.startswith("end_date_"):
            logger.error(f"Invalid END DATE callback data: {callback_data}")
            await query.message.reply_text("⚠️ Invalid date format received.\n\nPlease restart using /start.")
            return

        # Extract and validate the date
        selected_end_date = callback_data.replace("end_date_", "")
        end_date_obj = datetime.strptime(selected_end_date, "%d-%B")  # Convert to datetime object

        user_id = str(update.effective_user.id)
        month = context.user_data.get("month")
        start_date = context.user_data.get("start_date")
        leave_type = context.user_data.get("leave_type")

        if not start_date or not leave_type:
            await query.message.reply_text("⚠️ Missing leave START DATE or Leave Type.\n\nPlease restart using /start.")
            return

        # Convert START DATE to datetime object
        start_date_obj = datetime.strptime(start_date, "%d-%B")

        # **Validation: Check if START DATE is greater than END DATE**
        if start_date_obj > end_date_obj:
            logger.warning(f"User {user_id} entered invalid date range: Start {start_date}, End {selected_end_date}")
            await query.message.reply_text(
                "⚠️ Invalid Date Range!\n\nThe START DATE cannot be later than the END DATE. "
                "Please select the correct dates again."
            )

            # Prompt the user to reselect the dates
            await show_start_date_selection(update, context)
            return  # Stop further execution

        # Store properly formatted dates
        if user_id not in user_leaves:
            user_leaves[user_id] = {}
        if month not in user_leaves[user_id]:
            user_leaves[user_id][month] = []


        # **Check for overlapping leave periods**
        for existing_start, existing_end, existing_leave_type in user_leaves[user_id][month]:
            existing_start_date = datetime.strptime(existing_start, "%d-%B")
            existing_end_date = datetime.strptime(existing_end, "%d-%B")

            # Check if the new leave overlaps with any existing leave
            if not (end_date_obj < existing_start_date or start_date_obj > existing_end_date):
                logger.warning(f"User {user_id} attempted overlapping leave: {start_date} - {selected_end_date}")
                await query.message.reply_text(
                    f"⚠️ The selected leave period *overlaps* with an existing leave:\n"
                    f"📅 {existing_start} - {existing_end} ({existing_leave_type})\n\n"
                    "🔄 *Please reselect the START and END dates.*",
                    parse_mode="Markdown"
                )
                await show_start_date_selection(update, context)  # Prompt for new dates
                return  # Stop execution

        # **If no overlap, add leave entry**

        user_leaves[user_id][month].append(
            (start_date_obj.strftime("%d-%B"), end_date_obj.strftime("%d-%B"), leave_type))
        logger.info(f"Stored leave for {user_id}: {start_date} to {selected_end_date} ({leave_type})")

        buttons = [
            [InlineKeyboardButton("📝 Yes, Add More Leaves", callback_data="apply_leave")],
            [InlineKeyboardButton("📊 No, Generate Timesheet", callback_data="generate_timesheet_after_leave")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.reply_text("Do you want to add more leaves?", reply_markup=reply_markup)

    except ValueError as e:
        logger.error(f"Invalid date format received: {e}")
        await query.message.reply_text("⚠️ Selected date format is incorrect. Please try again.")


# Handle Generate Timesheet

async def generate_timesheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id).strip()
    month = context.user_data.get("month")

    if not month:
        await query.message.reply_text("You must first select a month.")
        return

    # Reset button expectation since we are now processing the timesheet
    context.user_data.pop("waiting_for_button", None)

    # Ensure user details exist
    USER_DETAILS = load_user_details()
    user_details = USER_DETAILS.get(user_id, {})

    # Required fields for generating a timesheet
    required_keys = {"name", "skill_level", "role_specialization", "group_specialization", "contractor"}
    missing_keys = required_keys - user_details.keys()

    if missing_keys:
        logger.warning(f"User ID {user_id} is missing required keys: {missing_keys}")
        await query.message.reply_text(
            "⚠️ *It looks like your registration is incomplete.*\n\n"
            "Please complete your registration to generate a timesheet.\n"
            "You can use /reset to clear your current profile and restart registration.",
            parse_mode="Markdown"
        )
        return

    # RATE LIMITING LOGIC
    now = time.time()
    rate_limits.setdefault(user_id, deque())

    # Remove old timestamps outside the time window
    while rate_limits[user_id] and now - rate_limits[user_id][0] > TIME_WINDOW:
        rate_limits[user_id].popleft()

    # Check if the user exceeded the limit
    if len(rate_limits[user_id]) >= MAX_ATTEMPTS:
        await query.message.reply_text(
            "⚠️ *Attempt threshold reached!*\n\n"
            "You have reached the maximum allowed attempts within a short period. "
            "Please wait and try again after a few seconds.",
            parse_mode="Markdown"
        )
        return

    # Add current timestamp to track usage
    rate_limits[user_id].append(now)

    # Ensure a queue exists for the user
    user_task_queues.setdefault(user_id, asyncio.Queue())

    # Add timesheet generation task to the queue
    await user_task_queues[user_id].put((query, context))

    # Start processing the queue if it's the first task
    if user_task_queues[user_id].qsize() == 1:
        asyncio.create_task(process_queue(user_id))


async def process_queue(user_id):
    while not user_task_queues[user_id].empty():
        query, context = await user_task_queues[user_id].get()

        try:
            month = context.user_data.get("month")
            if not month:
                await query.message.reply_text("You must first select a month.")
                continue

            logger.info(f"📝 Generating timesheet for user {user_id} for month: {month}")

            month_number = datetime.strptime(month, "%B").month
            year = datetime.now().year

            # Ensure leave data exists
            user_leaves.setdefault(user_id, {}).setdefault(month, [])

            leave_data = user_leaves[user_id][month]
            logger.info(f"Raw leave_data for user {user_id}: {leave_data}")

            parsed_leave_data = []
            for leave_entry in leave_data:
                if not isinstance(leave_entry, tuple) or len(leave_entry) != 3:
                    raise ValueError(f"Invalid leave entry format: {leave_entry}")

                start_date_str, end_date_str, leave_type = leave_entry
                start_date_obj = datetime.strptime(start_date_str, "%d-%B").replace(year=year)
                end_date_obj = datetime.strptime(end_date_str, "%d-%B").replace(year=year)

                parsed_leave_data.append((start_date_obj.strftime("%d-%B"), end_date_obj.strftime("%d-%B"), leave_type))

            logger.info(f"Final parsed_leave_data for user {user_id}: {parsed_leave_data}")

            await asyncio.sleep(AWAIT)  # Delay to prevent race conditions

            output_file = generate_timesheet_excel(user_id, month_number, year, parsed_leave_data)

            if not os.path.exists(output_file):
                raise FileNotFoundError(f"Timesheet file not found: {output_file}")

            with open(output_file, "rb") as doc:
                await query.message.reply_document(document=doc, filename=os.path.basename(output_file))

            # Clear leave data only after a successful generation
            user_leaves[user_id][month] = []

            # **NEW: Add a Restart Button**
            restart_button = [
                [InlineKeyboardButton("🔄 Start Again", callback_data="restart_timesheet")]
            ]
            reply_markup = InlineKeyboardMarkup(restart_button)

            await query.message.reply_text(
                "✅ *Timesheet successfully generated!* \n\n"
                "Would you like to generate another timesheet?",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Error generating timesheet for user {user_id}: {e}")
            await query.message.reply_text(f"Error generating timesheet: {e}")

        if not user_task_queues[user_id].empty():
            user_task_queues[user_id].task_done()

async def restart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    context.user_data.clear()  # Reset session data
    user_leaves.pop(user_id, None)  # Remove old leave records

    logger.info(f"User {user_id} restarted the timesheet process.")

    # Call start function
    await start(update, context)

async def handle_unexpected_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles unexpected text inputs during button-based workflows.
    Guides users to tap buttons instead of typing random text.
    """
    user_id = str(update.effective_user.id)

    # Check if user is in a step that requires button selection (e.g., timesheet generation)
    if "waiting_for_button" in context.user_data:
        await update.message.reply_text(
            "⚠️ *Please tap the button to proceed.*\n\n"
            "This bot works through interactive buttons, kindly select from the options provided.",
            parse_mode="Markdown"
        )
        return

    # If the user is not in a button-based flow, ignore or provide help.
    await update.message.reply_text(
        "🤖 If you need assistance, use /start to begin."
    )

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Determines if the text input should be processed for registration
    or handled as an unexpected input in timesheet generation.
    """
    user_id = str(update.effective_user.id)
    step = context.user_data.get("registration_step")  # Check if user is in registration mode

    if step:  # If the user is in the registration process, process the input for registration
        await capture_user_details(update, context)
    else:  # If not in registration, handle unexpected input
        await handle_unexpected_text(update, context)


# main function in bot.py
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register_new_user))

    # # Add MessageHandler to capture user input during registration
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_user_details))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unexpected_text))
    # Register a **single** message handler that decides the flow
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    # Fix: Add CallbackQueryHandler for handling quick-select buttons
    application.add_handler(
        CallbackQueryHandler(handle_registration_buttons, pattern="^(skill_level|role_specialization|contractor)_.+"))

    application.add_handler(CallbackQueryHandler(month_handler, pattern="^month_"))
    application.add_handler(CallbackQueryHandler(apply_leave, pattern="^apply_leave$"))
    application.add_handler(CallbackQueryHandler(leave_type_handler, pattern="^leave_"))
    application.add_handler(CallbackQueryHandler(start_date_handler, pattern="^start_date_"))
    application.add_handler(CallbackQueryHandler(end_date_handler, pattern="^end_date_"))
    application.add_handler(
        CallbackQueryHandler(generate_timesheet, pattern="^(generate_timesheet_now|generate_timesheet_after_leave)$"))

    # Restart Button Handler
    application.add_handler(CallbackQueryHandler(restart_handler, pattern="^restart_timesheet$"))

    # De-registration handlers
    application.add_handler(CommandHandler("reset", confirm_deregistration))
    application.add_handler(CommandHandler("deregister", confirm_deregistration))
    application.add_handler(CallbackQueryHandler(handle_deregistration_buttons, pattern="^deregister_"))

    application.run_polling()


if __name__ == "__main__":
    main()