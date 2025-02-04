from openpyxl import Workbook
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from utils.utils import PUBLIC_HOLIDAYS, USER_DETAILS
from datetime import datetime, timedelta
from calendar import monthrange
import os


def generate_timesheet_excel(user_id, month, year, leave_details):
    print(f"Debug: Generating timesheet for User ID: {user_id}, Month: {month}, Year: {year}")

    user_details = USER_DETAILS.get(user_id)
    if not user_details:
        print(f"Error: User with ID {user_id} not found.")
        raise ValueError(f"User with ID {user_id} not found.")

    # Extract user details
    name = user_details.get("name", "N/A")
    po_ref = user_details.get("po_ref", "N/A")
    po_date = user_details.get("po_date", "N/A")
    description = user_details.get("description", "N/A")
    reporting_officer = user_details.get("reporting_officer", "N/A")

    print(
        f"Debug: Extracted User Details -> Name: {name}, PO Ref: {po_ref}, PO Date: {po_date}, Reporting Officer: {reporting_officer}")

    # Prepare file and workbook
    month_name = datetime(year, month, 1).strftime("%B")
    filename = f"{month_name}_{year}_Timesheet_{name.replace(' ', '_')}.xlsx"
    output_dir = "generated_timesheets"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, filename)

    print(f"Debug: Output file path -> {output_file}")

    wb = Workbook()
    ws = wb.active
    ws.title = f"{month_name} {year} Timesheet"

    # Define styles (Do not change this part)
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
    yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    bold_font = Font(bold=True)
    center_alignment = Alignment(horizontal="center", vertical="center")

    # ✅ **Fix: Assign values before merging cells**
    header_data = [
        ("Description", description, "A1", "D1"),
        ("PO Ref", po_ref, "A2", "D2"),
        ("PO Date", po_date, "A3", "D3"),
        ("Month/Year", f"{month_name} - {year}", "F1", "H1"),
        ("Contractor", "PALO IT", "F2", "H2"),
        ("Name", name, "A6", "D6"),
        ("Role Specialization", user_details.get("role_specialization", "N/A"), "A7", "D7"),
        ("Group Specialization", user_details.get("group_specialization", "N/A"), "A8", "D8"),
        ("Skill Level", user_details.get("skill_level", "N/A"), "F6", "H6"),
    ]

    for title, value, start_cell, end_cell in header_data:
        ws[start_cell] = title
        ws[start_cell].font = bold_font
        ws[start_cell].alignment = center_alignment
        ws[start_cell].border = thin_border
        ws.merge_cells(f"{start_cell}:{end_cell}")

        value_cell = f"{chr(ord(start_cell[0]) + 1)}{start_cell[1:]}"  # Move to next column
        ws[value_cell] = value
        ws[value_cell].alignment = center_alignment
        ws[value_cell].border = thin_border

    # Add table headers
    headers = ["SN", "Date", "At Work", "Public Holiday", "Sick Leave", "Childcare Leave", "Annual Leave", "Remarks"]
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=10, column=col_num, value=header)
        cell.fill = yellow_fill
        cell.font = bold_font
        cell.alignment = center_alignment
        cell.border = thin_border

    # Process leave details
    expanded_leave_details = []
    for leave_date, leave_type in leave_details:
        expanded_leave_details.append((leave_date, leave_type))

    # Add table data
    current_row = 11
    _, days_in_month = monthrange(year, month)
    total_at_work = total_public_holidays = total_sick_leave = total_childcare_leave = total_annual_leave = 0

    for day in range(1, days_in_month + 1):
        date_obj = datetime(year, month, day)
        formatted_date = date_obj.strftime("%d-%B-%Y")
        weekday = date_obj.weekday()

        # Default values
        at_work, public_holiday, sick_leave, childcare_leave, annual_leave = 1, 0, 0, 0, 0
        remark = ""

        # Check weekends
        if weekday >= 5:
            at_work = 0
            remark = "Saturday" if weekday == 5 else "Sunday"

        # Check public holidays
        if date_obj.strftime("%Y-%m-%d") in PUBLIC_HOLIDAYS:
            at_work = 0
            public_holiday = 1
            remark = PUBLIC_HOLIDAYS[date_obj.strftime("%Y-%m-%d")]

        # Check leave details
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

        # Update totals
        total_at_work += at_work
        total_public_holidays += public_holiday
        total_sick_leave += sick_leave
        total_childcare_leave += childcare_leave
        total_annual_leave += annual_leave

        # Write row data
        row_data = [current_row - 10, formatted_date, at_work, public_holiday, sick_leave, childcare_leave,
                    annual_leave, remark]
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=current_row, column=col_num, value=value)
            cell.alignment = center_alignment
            cell.border = thin_border

        current_row += 1

    # Add totals row
    totals_row = current_row
    ws[f"A{totals_row}"] = "Total"
    ws[f"A{totals_row}"].font = bold_font
    ws[f"A{totals_row}"].alignment = center_alignment
    ws[f"A{totals_row}"].border = thin_border

    totals = [total_at_work, total_public_holidays, total_sick_leave, total_childcare_leave, total_annual_leave]
    for col_num, total in enumerate(totals, 3):
        cell = ws.cell(row=totals_row, column=col_num, value=total)
        cell.font = bold_font
        cell.alignment = center_alignment
        cell.border = thin_border

    # ✅ **Fix: Correct footer formatting**
    footer = [
        ("Officer", name, "A45", "D45"),
        ("Signature", name, "A46", "D46"),
        ("Date", datetime.now().strftime("%d - %b - %Y"), "A47", "D47"),
        ("Reporting Officer", reporting_officer, "A49", "D49"),
        ("Signature", "", "A50", "D50"),
        ("Date", "", "A51", "D51"),
    ]

    for title, value, start_cell, end_cell in footer:
        ws[start_cell] = title
        ws[start_cell].font = bold_font
        ws[start_cell].alignment = center_alignment
        ws[start_cell].border = thin_border
        ws.merge_cells(f"{start_cell}:{end_cell}")

        value_col = chr(ord(start_cell[0]) + 1)  # Move to next column
        value_cell = f"{value_col}{start_cell[1:]}"
        ws[value_cell] = value
        ws[value_cell].alignment = center_alignment
        ws[value_cell].border = thin_border
        ws.merge_cells(f"{value_cell}:{end_cell}")

    # Save the workbook
    wb.save(output_file)
    print(f"Debug: Timesheet saved successfully -> {output_file}")
    return output_file
