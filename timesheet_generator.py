from openpyxl import Workbook
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from datetime import datetime, timedelta
from calendar import monthrange
import os
from utils.utils import PUBLIC_HOLIDAYS, USER_DETAILS

def generate_timesheet_excel(user_id, month, year, leave_details):
    print(f"Generating timesheet for User ID: {user_id}, Month: {month}, Year: {year}")

    # ✅ Debug: Print Public Holidays for Verification
    print("Public Holidays Loaded:", PUBLIC_HOLIDAYS)

    # ✅ Fetch User Details
    user_details = USER_DETAILS.get(user_id)
    if not user_details:
        print(f"Error: User with ID {user_id} not found.")
        raise ValueError(f"User with ID {user_id} not found.")

    # Extract user details
    name = user_details["name"]
    skill_level = user_details["skill_level"]
    role_specialization = user_details["role_specialization"]
    group_specialization = user_details["group_specialization"]
    contractor = user_details["contractor"]
    po_ref = user_details["po_ref"]
    po_date = user_details["po_date"]
    description = user_details["description"]
    reporting_officer = user_details["reporting_officer"]

    # ✅ File Setup
    month_name = datetime(year, month, 1).strftime("%B")
    filename = f"{month_name}_{year}_Timesheet_{name.replace(' ', '_')}.xlsx"
    output_dir = "generated_timesheets"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, filename)

    # ✅ Workbook & Worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = f"{month_name} {year} Timesheet"

    # ✅ Styles
    thin_border = Border(left=Side(style="thin"), right=Side(style="thin"),
                         top=Side(style="thin"), bottom=Side(style="thin"))
    yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    bold_font = Font(bold=True)
    center_alignment = Alignment(horizontal="center", vertical="center")

    # ✅ Header Section (PO Details)
    ws["A1"] = "Description"
    ws["B1"] = description
    ws["B1"].fill = yellow_fill
    ws["A3"] = "PO Ref"
    ws["B3"] = po_ref
    ws["B3"].fill = yellow_fill
    ws["A4"] = "PO Date"
    ws["B4"] = po_date
    ws["B4"].fill = yellow_fill

    ws["D1"] = "Month/Year"
    ws["E1"] = f"{month_name} - {year}"
    ws["E1"].fill = yellow_fill
    ws["D3"] = "Contractor"
    ws["E3"] = contractor
    ws["E3"].fill = yellow_fill

    # ✅ User Details
    ws["A6"] = "Name"
    ws["B6"] = name
    ws["B6"].fill = yellow_fill
    ws["D6"] = "Skill Level"
    ws["E6"] = skill_level
    ws["E6"].fill = yellow_fill
    ws["A7"] = "Role Specialization"
    ws["B7"] = role_specialization
    ws["B7"].fill = yellow_fill
    ws["D7"] = "Group/Specialization"
    ws["E7"] = group_specialization
    ws["E7"].fill = yellow_fill

    # ✅ Table Headers
    headers = ["SN", "Date", "At Work", "Public Holiday", "Sick Leave", "Childcare Leave", "Annual Leave", "Remarks"]
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=9, column=col_num, value=header)
        cell.fill = yellow_fill
        cell.font = bold_font
        cell.alignment = center_alignment
        cell.border = thin_border

    # ✅ **Expand Leave Data**
    expanded_leave_details = []
    for leave_entry in leave_details:
        if len(leave_entry) == 3:  # (start_date, end_date, leave_type)
            start_date, end_date, leave_type = leave_entry
            start_date = datetime.strptime(start_date, "%d-%B").replace(year=year)
            end_date = datetime.strptime(end_date, "%d-%B").replace(year=year)

            while start_date <= end_date:
                expanded_leave_details.append((start_date.strftime("%Y-%m-%d"), leave_type))
                start_date += timedelta(days=1)
        else:
            expanded_leave_details.append(leave_entry)

    # ✅ **Data Rows**
    current_row = 10
    _, days_in_month = monthrange(year, month)
    totals = {"At Work": 0, "Public Holiday": 0, "Sick Leave": 0, "Childcare Leave": 0, "Annual Leave": 0}

    for day in range(1, days_in_month + 1):
        date_obj = datetime(year, month, day)
        formatted_date = date_obj.strftime("%Y-%m-%d")  # Ensure public holiday format matches
        weekday = date_obj.weekday()

        # ✅ Debug: Print each date processed
        print(f"Processing Date: {formatted_date}")

        # Default Values
        at_work, public_holiday, sick_leave, childcare_leave, annual_leave = 1, 0, 0, 0, 0
        remark = ""

        # ✅ **Handle Weekends**
        if weekday == 5:
            at_work = 0
            remark = "Saturday"
        elif weekday == 6:
            at_work = 0
            remark = "Sunday"

        # ✅ **Handle Public Holidays**
        if formatted_date in PUBLIC_HOLIDAYS:
            print(f"📌 Found Public Holiday on {formatted_date}: {PUBLIC_HOLIDAYS[formatted_date]}")
            at_work = 0
            public_holiday = 1
            remark = PUBLIC_HOLIDAYS[formatted_date]

        # ✅ **Handle User Leaves**
        if formatted_date not in PUBLIC_HOLIDAYS and remark not in ["Saturday", "Sunday"]:
            for leave_date, leave_type in expanded_leave_details:
                if leave_date == formatted_date:
                    print(f"📌 Found Leave on {formatted_date}: {leave_type}")
                    at_work = 0
                    if leave_type == "Sick Leave":
                        sick_leave = 1
                    elif leave_type == "Childcare Leave":
                        childcare_leave = 1
                    elif leave_type == "Annual Leave":
                        annual_leave = 1
                    remark = leave_type

        # ✅ **Update Totals**
        totals["At Work"] += at_work
        totals["Public Holiday"] += public_holiday
        totals["Sick Leave"] += sick_leave
        totals["Childcare Leave"] += childcare_leave
        totals["Annual Leave"] += annual_leave

        # ✅ **Insert Data**
        row_data = [current_row - 9, formatted_date, at_work, public_holiday, sick_leave, childcare_leave, annual_leave, remark]
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=current_row, column=col_num, value=value)
            cell.alignment = center_alignment
            cell.border = thin_border
            if value == 1 or remark:
                cell.fill = yellow_fill  # Highlight leave & public holiday cells


        current_row += 1

    # ✅ **Totals Row**
    ws[f"A{current_row}"] = "Total"
    ws[f"A{current_row}"].font = bold_font
    for col_num, key in enumerate(totals.keys(), 3):
        ws.cell(row=current_row, column=col_num, value=totals[key]).font = bold_font

    # ✅ **Signature Section**
    current_date = datetime.now().strftime("%d - %B - %Y")
    ws[f"A{current_row + 2}"] = "Officer"
    ws[f"B{current_row + 2}"] = name
    ws[f"A{current_row + 3}"] = "Signature"
    ws[f"B{current_row + 3}"] = name
    ws[f"A{current_row + 4}"] = "Date"
    ws[f"B{current_row + 4}"] = current_date

    ws[f"D{current_row + 2}"] = "Reporting Officer"
    ws[f"E{current_row + 2}"] = reporting_officer
    ws[f"D{current_row + 3}"] = "Signature"
    ws[f"E{current_row + 3}"] = ""  # ✅ Leave Empty for Manager
    ws[f"D{current_row + 4}"] = "Date"
    ws[f"E{current_row + 4}"] = ""  # ✅ Leave Empty for Manager

    # ✅ **Save File**
    wb.save(output_file)
    print(f"Timesheet saved -> {output_file}")
    return output_file
