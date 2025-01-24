from openpyxl import Workbook
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from utils.utils import PUBLIC_HOLIDAYS, USER_DETAILS
from datetime import datetime
from calendar import monthrange
import os


def generate_timesheet_excel(user_id, month, year, leave_details):
    user_details = USER_DETAILS.get(user_id)

    if not user_details:
        raise ValueError(f"User with ID {user_id} not found.")

    # Extract user details
    name = user_details["name"]
    po_ref = user_details["po_ref"]
    po_date = user_details["po_date"]
    description = user_details["description"]
    reporting_officer = user_details["reporting_officer"]

    # Prepare file and workbook
    month_name = datetime(year, month, 1).strftime("%B")
    filename = f"{month_name}_{year}_Timesheet_{name.replace(' ', '_')}.xlsx"
    output_dir = "generated_timesheets"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, filename)

    wb = Workbook()
    ws = wb.active
    ws.title = f"{month_name} {year} Timesheet"

    # Define border style
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    # Add header rows
    ws["A1"] = "Description"
    ws["B1"] = description
    ws.merge_cells("B1:D1")
    ws["A2"] = "PO Ref"
    ws["B2"] = po_ref
    ws.merge_cells("B2:D2")
    ws["A3"] = "PO Date"
    ws["B3"] = po_date
    ws.merge_cells("B3:D3")
    ws["F1"] = "Month/Year"
    ws["G1"] = f"{month_name} - {year}"
    ws.merge_cells("G1:H1")
    ws["F2"] = "Contractor"
    ws["G2"] = "PALO IT"
    ws.merge_cells("G2:H2")
    ws["A6"] = "Name"
    ws["B6"] = name
    ws.merge_cells("B6:D6")
    ws["A7"] = "Role Specialization"
    ws["B7"] = user_details["role_specialization"]
    ws.merge_cells("B7:D7")
    ws["A8"] = "Group Specialization"
    ws["B8"] = user_details["group_specialization"]
    ws.merge_cells("B8:D8")
    ws["F6"] = "Skill Level"
    ws["G6"] = user_details["skill_level"]
    ws.merge_cells("G6:H6")

    # Format headers
    for row in range(1, 9):
        for col in range(1, 9):
            cell = ws.cell(row=row, column=col)
            cell.border = thin_border
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # Add table headers
    headers = ["SN", "Date", "At Work", "Public Holiday", "Sick Leave", "Childcare Leave", "Annual Leave", "Remarks"]
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=10, column=col_num, value=header)
        cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    # Fill table data
    current_row = 11
    _, days_in_month = monthrange(year, month)
    for day in range(1, days_in_month + 1):
        date_obj = datetime(year, month, day)
        formatted_date = date_obj.strftime("%d-%B-%Y")
        weekday = date_obj.weekday()

        # Initialize default values
        at_work = 1.0
        public_holiday = 0.0
        sick_leave = 0.0
        childcare_leave = 0.0
        annual_leave = 0.0
        remark = ""

        # Check if the date is a weekend
        if weekday >= 5:
            at_work = 0.0
            remark = "Saturday" if weekday == 5 else "Sunday"

        # Check if the date is a public holiday
        if date_obj.strftime("%Y-%m-%d") in PUBLIC_HOLIDAYS:
            at_work = 0.0
            public_holiday = 1.0
            remark = PUBLIC_HOLIDAYS[date_obj.strftime("%Y-%m-%d")]

        # Check if the date matches any leave entry
        for leave_date, leave_type in leave_details:
            if leave_date == date_obj.strftime("%Y-%m-%d"):
                at_work = 0.0
                if leave_type == "Sick Leave":
                    sick_leave = 1.0
                elif leave_type == "Childcare Leave":
                    childcare_leave = 1.0
                elif leave_type == "Annual Leave":
                    annual_leave = 1.0
                remark = leave_type

        # Write data to the row
        ws.append([
            current_row - 10, formatted_date, at_work, public_holiday,
            sick_leave, childcare_leave, annual_leave, remark
        ])
        current_row += 1

    # Add totals row
    totals_row = current_row
    ws[f"A{totals_row}"] = "Total"
    for col in range(3, 8):
        column_letter = ws.cell(row=10, column=col).column_letter
        total_formula = f"=SUM({column_letter}11:{column_letter}{totals_row-1})"
        ws.cell(row=totals_row, column=col).value = total_formula
        ws.cell(row=totals_row, column=col).font = Font(bold=True)
        ws.cell(row=totals_row, column=col).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=totals_row, column=col).border = thin_border

    # Add footer
    ws["A45"] = "Officer"
    ws["B45"] = name
    ws.merge_cells("B45:D45")
    ws["A46"] = "Signature"
    ws["B46"] = name
    ws.merge_cells("B46:D46")
    ws["A47"] = "Date"
    ws["B47"] = datetime.now().strftime("%d - %b - %Y")
    ws.merge_cells("B47:D47")
    ws["A49"] = "Reporting Officer"
    ws["B49"] = reporting_officer
    ws.merge_cells("B49:D49")
    ws["A50"] = "Signature"
    ws.merge_cells("B50:D50")
    ws["A51"] = "Date"
    ws.merge_cells("B51:D51")

    # Style footer
    for row in range(45, 52):
        for col in range(1, 5):
            cell = ws.cell(row=row, column=col)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # Save the workbook
    wb.save(output_file)
    return output_file
