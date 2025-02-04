from openpyxl import Workbook
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from datetime import datetime, timedelta
from calendar import monthrange
import os
from utils.utils import PUBLIC_HOLIDAYS, USER_DETAILS

def generate_timesheet_excel(user_id, month, year, leave_details):
    print(f"Generating timesheet for User ID: {user_id}, Month: {month}, Year: {year}")

    user_details = USER_DETAILS.get(user_id)
    if not user_details:
        print(f"Error: User with ID {user_id} not found.")
        raise ValueError(f"User with ID {user_id} not found.")

    # Extract user details
    name = user_details.get("name", "N/A")

    # File Setup
    month_name = datetime(year, month, 1).strftime("%B")
    filename = f"{month_name}_{year}_Timesheet_{name.replace(' ', '_')}.xlsx"
    output_dir = "generated_timesheets"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, filename)

    # Workbook & Worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = f"{month_name} {year} Timesheet"

    # Styles
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )
    yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    bold_font = Font(bold=True)
    center_alignment = Alignment(horizontal="center", vertical="center")

    # Column Headers (Only Table, No Headers)
    table_headers = ["SN", "Date", "At Work", "Public Holiday", "Sick Leave", "Childcare Leave", "Annual Leave", "Remarks"]
    for col_num, header in enumerate(table_headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = yellow_fill
        cell.font = bold_font
        cell.alignment = center_alignment
        cell.border = thin_border

    # Expand Leave Data
    expanded_leave_details = []
    for leave_date, leave_type in leave_details:
        if "to" in leave_date:
            start_date, end_date = map(lambda x: datetime.strptime(x.strip(), "%d-%B"), leave_date.split("to"))
            while start_date <= end_date:
                expanded_leave_details.append((start_date.strftime("%d-%B-%Y"), leave_type))
                start_date += timedelta(days=1)
        else:
            expanded_leave_details.append((leave_date, leave_type))

    # Data Rows
    current_row = 2  # Start data after headers
    _, days_in_month = monthrange(year, month)
    totals = {"At Work": 0, "Public Holiday": 0, "Sick Leave": 0, "Childcare Leave": 0, "Annual Leave": 0}

    for day in range(1, days_in_month + 1):
        date_obj = datetime(year, month, day)
        formatted_date = date_obj.strftime("%d-%B-%Y")
        weekday = date_obj.weekday()

        # Default Values
        at_work, public_holiday, sick_leave, childcare_leave, annual_leave = 1, 0, 0, 0, 0
        remark = ""

        # Weekends
        if weekday >= 5:
            at_work = 0
            remark = "Saturday" if weekday == 5 else "Sunday"

        # Public Holidays
        if formatted_date in PUBLIC_HOLIDAYS:
            at_work = 0
            public_holiday = 1
            remark = PUBLIC_HOLIDAYS[formatted_date]

        # User Leaves
        for leave_date, leave_type in expanded_leave_details:
            if leave_date == formatted_date:
                at_work = 0
                if leave_type == "Sick Leave":
                    sick_leave = 1
                elif leave_type == "Childcare Leave":
                    childcare_leave = 1
                elif leave_type == "Annual Leave":
                    annual_leave = 1
                remark = leave_type

        # Update Totals
        totals["At Work"] += at_work
        totals["Public Holiday"] += public_holiday
        totals["Sick Leave"] += sick_leave
        totals["Childcare Leave"] += childcare_leave
        totals["Annual Leave"] += annual_leave

        # Insert Data
        row_data = [current_row - 1, formatted_date, at_work, public_holiday, sick_leave, childcare_leave, annual_leave, remark]
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=current_row, column=col_num, value=value)
            cell.alignment = center_alignment
            cell.border = thin_border
            if value == 1:
                cell.fill = yellow_fill  # Highlight leave cells

        current_row += 1

    # Totals Row
    ws[f"A{current_row}"] = "Total"
    ws[f"A{current_row}"].font = bold_font
    for col_num, key in enumerate(totals.keys(), 3):
        ws.cell(row=current_row, column=col_num, value=totals[key]).font = bold_font

    # Save File
    wb.save(output_file)
    print(f"Timesheet saved -> {output_file}")
    return output_file
