from openpyxl import Workbook
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from datetime import datetime, timedelta
from calendar import monthrange
import os
from utils.utils import PUBLIC_HOLIDAYS, load_user_details  # Import function instead of USER_DETAILS
from styles import (  # Import styles from styles.py
    thin_border, white_fill, yellow_fill, light_green_fill, lighter_green_fill, light_yellow_fill, light_blue_fill,
    light_red_fill, bold_font, red_font, black_font, center_alignment, right_alignment)

def generate_timesheet_excel(user_id, month, year, leave_details):
    print(f"Generating timesheet for User ID: {user_id}, Month: {month}, Year: {year}")

    # Fetch Latest User Details
    USER_DETAILS = load_user_details()  # Ensures it fetches the latest data

    # Debug: Print Public Holidays for Verification
    print("Public Holidays Loaded:", PUBLIC_HOLIDAYS)
    print("User details Loaded:", USER_DETAILS)

    # Fetch User Details
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

    # # Header Section (PO Details)
    # ws["A1"], ws["B1"] = "Description", description
    # ws["A2"], ws["B2"] = "PO Ref", po_ref
    # ws["A3"], ws["B3"] = "PO Date", po_date
    # ws["D1"], ws["E1"] = "Month/Year", f"{month_name} - {year}"
    # ws["D2"], ws["E2"] = "Contractor", contractor

    # # Header Section (PO Details) - Start from Row 2
    # ws["A2"], ws["B2"] = "Description", description
    # ws["A3"], ws["B3"] = "PO Ref", po_ref
    # ws["A4"], ws["B4"] = "PO Date", po_date
    # ws["D2"], ws["E2"] = "Month/Year", f"{month_name} - {year}"
    # ws["D3"], ws["E3"] = "Contractor", contractor
    #
    # # Apply Borders for Header Sections
    # for row in range(2, 5):
    #     for col in ["A", "B"]:
    #         ws[f"{col}{row}"].border = thin_border  # Description to PO Date
    # for row in range(2, 4):
    #     for col in ["D", "E"]:
    #         ws[f"{col}{row}"].border = thin_border  # Month/Year to Contractor
    #
    # # Apply Yellow Fill and Center Alignment to Static Cells in Column B (Second Column)
    # for row in [2, 3, 4]:  # Rows to be highlighted in Column B
    #     cell = ws[f"B{row}"]
    #     cell.fill = yellow_fill
    #     cell.alignment = center_alignment  # Corrected alignment syntax
    #
    # # Apply Yellow Fill and Center Alignment to Static Cells in Column E1 (Fifth Column)
    # for row in [2]:  # Rows to be highlighted in Column E
    #     cell = ws[f"E{row}"]
    #     cell.fill = yellow_fill
    #     cell.alignment = center_alignment  # Corrected alignment syntax
    #
    # # Apply Yellow Fill and Center Alignment to Static Cells in Column E2
    # for row in [2]:  # Rows to be highlighted in Column E
    #     cell = ws[f"E{row}"]
    #     cell.alignment = center_alignment  # Corrected alignment syntax
    #
    # # Apply Yellow Fill and Center Alignment to Static Cells in Column E6
    # for row in [6]:  # Rows to be highlighted in Column E
    #     cell = ws[f"E{row}"]
    #     cell.alignment = center_alignment  # Corrected alignment syntax
    #
    # # Ensure Row 1 is left unformatted (No Border, No Yellow Fill)
    # for col in ["A", "B", "C", "D", "E"]:
    #     ws[f"{col}1"].border = None
    #     ws[f"{col}1"].fill = None

    # # Header Section (PO Details) - Start from Row 2
    # ws["A2"], ws["B2"] = "Description", description
    # ws["A3"], ws["B3"] = "PO Ref", po_ref
    # ws["A4"], ws["B4"] = "PO Date", po_date
    # ws["D2"], ws["E2"] = "Month/Year", f"{month_name} - {year}"
    # ws["D3"], ws["E3"] = "Contractor", contractor
    #
    # # Apply Borders for Header Sections (Only from Row 2 onwards)
    # for row in range(2, 5):  # Row 1 is skipped
    #     for col in ["A", "B"]:
    #         ws[f"{col}{row}"].border = thin_border  # Description to PO Date
    # for row in range(2, 4):  # Row 1 is skipped
    #     for col in ["D", "E"]:
    #         ws[f"{col}{row}"].border = thin_border  # Month/Year to Contractor
    #
    # # Apply Yellow Fill and Center Alignment to Static Cells in Column B (Description, PO Ref, PO Date)
    # for row in [2, 3, 4]:
    #     cell = ws[f"B{row}"]
    #     cell.fill = yellow_fill
    #     cell.alignment = center_alignment
    #
    # # Apply Yellow Fill and Center Alignment to Column E (Month/Year)
    # ws["E2"].fill = yellow_fill
    # ws["E2"].alignment = center_alignment  # Removed redundant lines
    #
    # # Apply Center Alignment Only to E3 (Contractor)
    # ws["E3"].alignment = center_alignment
    #
    # # Ensure Row 1 is left unformatted (No Border, No Yellow Fill)
    # for col in ["A", "B", "C", "D", "E"]:
    #     ws[f"{col}1"].border = Border()  # Reset border
    #     ws[f"{col}1"].fill = PatternFill(fill_type=None)  # Ensure fill is removed
    #
    # # User Details
    # ws["A6"], ws["B6"] = "Name", name
    # ws["D6"], ws["E6"] = "Skill Level", skill_level
    # ws["A7"], ws["B7"] = "Role Specialization", role_specialization
    # ws["A8"], ws["B8"] = "Group/Specialization", group_specialization
    #
    # # Apply Yellow Fill to Static Cells in Columns B & E
    # static_fields = ["B6", "B7", "B8", "E6"]  # Include all necessary fields
    # for cell in static_fields:
    #     ws[cell].fill = yellow_fill
    #
    #     # Apply Borders for User Details
    #     for row in range(6, 9):
    #         for col in ["A", "B"]:
    #             ws[f"{col}{row}"].border = thin_border  # Name to Group
    #     ws["D6"].border = thin_border  # Skill Level Label
    #     ws["E6"].border = thin_border  # Skill Level Value

    #LATEST MERGE CELL CHANGES
    # Merge and Format Header Section (PO Details)
    from openpyxl.styles import Alignment, PatternFill, Font, Border, Side

    # Merge and Format Header Section (PO Details)
    ws.merge_cells("B2:D2")  # Merge Description value
    ws.merge_cells("B3:D3")  # Merge PO Ref value
    ws.merge_cells("B4:D4")  # Merge PO Date value
    ws.merge_cells("G2:H2")  # Merge Month/Year value
    ws.merge_cells("G3:H3")  # Merge Contractor value

    ws["A2"], ws["B2"] = "Description", description
    ws["A3"], ws["B3"] = "PO Ref", po_ref
    ws["A4"], ws["B4"] = "PO Date", po_date
    ws["F2"], ws["G2"] = "Month/Year", f"{month_name} - {year}"
    ws["F3"], ws["G3"] = "Contractor", contractor

    # Apply Borders for Header Sections
    for row in range(2, 5):  # A-D Borders for Description, PO Ref, PO Date
        for col in ["A", "B", "C", "D"]:
            ws[f"{col}{row}"].border = thin_border

    for row in range(2, 4):  # F-H Borders for Month/Year and Contractor
        for col in ["F", "G", "H"]:
            ws[f"{col}{row}"].border = thin_border

    # Apply Borders for Month/Year (Fully Inside a Box)
    for col in ["F", "G", "H"]:
        ws[f"{col}2"].border = thin_border

    # Apply Yellow Fill to Values Only (B-D, G-H)
    for row in range(2, 5):
        for col in ["B", "C", "D"]:
            ws[f"{col}{row}"].fill = yellow_fill  # Apply to Description, PO Ref, PO Date

    for row in range(2, 4):
        for col in ["G", "H"]:
            ws[f"{col}{row}"].fill = yellow_fill  # Apply to Month/Year and Contractor

    # Ensure Column E is empty (No Borders, No Fill)
    for row in range(2, 5):
        ws[f"E{row}"].border = Border()
        ws[f"E{row}"].fill = PatternFill(fill_type=None)

    # **Apply Bottom Alignment for Values (B-D)**
    for row in range(2, 5):
        for col in ["B", "C", "D"]:
            ws[f"{col}{row}"].alignment = Alignment(horizontal="center", vertical="bottom")

    # **Keep Column A Left-Aligned**
    for row in range(2, 5):
        ws[f"A{row}"].alignment = Alignment(horizontal="left", vertical="bottom")

    # **Apply Center Alignment for Skill Level, Contractor, and Month/Year Values**
    for row in [2, 3, 6]:  # Month/Year, Contractor, Skill Level
        for col in ["G", "H"]:
            ws[f"{col}{row}"].alignment = Alignment(horizontal="center", vertical="bottom")

    # **Wrap Text for Description (B2:D2)**
    for col in ["B", "C", "D"]:
        ws[f"{col}2"].alignment = Alignment(horizontal="center", vertical="bottom", wrap_text=True)
        ws[f"{col}2"].font = Font(bold=False)  # Ensure text is not bold

    # Merge and Format User Details
    ws.merge_cells("B6:D6")  # Merge Name
    ws.merge_cells("B7:D7")  # Merge Role Specialization
    ws.merge_cells("B8:D8")  # Merge Group Specialization
    ws.merge_cells("G6:H6")  # Merge Skill Level

    ws["A6"], ws["B6"] = "Name", name
    ws["A7"], ws["B7"] = "Role Specialization", role_specialization
    ws["A8"], ws["B8"] = "Group/Specialization", group_specialization
    ws["F6"], ws["G6"] = "Skill Level", skill_level

    # Apply Borders for User Details
    for row in range(6, 9):  # A-D Borders for Name, Role Specialization, Group
        for col in ["A", "B", "C", "D"]:
            ws[f"{col}{row}"].border = thin_border

    for row in [6]:  # F-H Borders for Skill Level
        for col in ["F", "G", "H"]:
            ws[f"{col}{row}"].border = thin_border

    # Apply Yellow Fill to Values Only (B-D, G-H)
    for row in range(6, 9):
        for col in ["B", "C", "D"]:
            ws[f"{col}{row}"].fill = yellow_fill  # Name, Role, Group

    for row in [6]:
        for col in ["G", "H"]:
            ws[f"{col}{row}"].fill = yellow_fill  # Skill Level

    # Ensure Column E is empty (No Borders, No Fill)
    for row in range(6, 9):
        ws[f"E{row}"].border = Border()
        ws[f"E{row}"].fill = PatternFill(fill_type=None)

    # **Left Align Name, Role Specialization, Group Specialization Values**
    for row in range(6, 9):
        ws[f"B{row}"].alignment = Alignment(horizontal="left", vertical="bottom")  # Left align

    print("✅ Final formatting and bottom alignment applied successfully!")

    # Table Headers
    headers = ["SN", "Date", "At Work", "Public Holiday", "Sick Leave", "Childcare Leave", "Annual Leave", "Remarks"]
    header_fills = [white_fill, white_fill, light_green_fill, light_yellow_fill, lighter_green_fill, white_fill,
                    light_blue_fill, white_fill]  # Corresponding fill colors

    for col_num, (header, fill) in enumerate(zip(headers, header_fills), 1):
        cell = ws.cell(row=10, column=col_num, value=header)
        cell.font = Font(bold=True, color="000000")  # Bold font with black text
        cell.alignment = Alignment(horizontal="center", vertical="center")  # Center alignment
        cell.border = Border(bottom=Side(style="medium"))  # Apply bottom border
        cell.border = thin_border  # Apply thin border
        cell.fill = fill  # Apply the respective color

    # **Expand Leave Data**
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

    # **Data Rows**
    current_row = 11
    _, days_in_month = monthrange(year, month)
    totals = {"At Work": 0.0, "Public Holiday": 0.0, "Sick Leave": 0.0, "Childcare Leave": 0.0, "Annual Leave": 0.0}

    for day in range(1, days_in_month + 1):
        date_obj = datetime(year, month, day)
        formatted_date = date_obj.strftime("%d-%B-%Y")  # Display format
        public_holiday_check = date_obj.strftime("%Y-%m-%d")  # Match keys in PUBLIC_HOLIDAYS
        weekday = date_obj.weekday()

        # Default Values as Floats
        at_work, public_holiday, sick_leave, childcare_leave, annual_leave = 1.0, 0.0, 0.0, 0.0, 0.0
        remark = "-"  # Default empty remark

        # **Handle Weekends**
        if weekday == 5:
            at_work = 0.0
            remark = "Saturday"
        elif weekday == 6:
            at_work = 0.0
            remark = "Sunday"

        # **Handle Public Holidays (Fixed)**
        if public_holiday_check in PUBLIC_HOLIDAYS:
            print(f"📌 Public Holiday Found: {public_holiday_check} - {PUBLIC_HOLIDAYS[public_holiday_check]}")
            at_work = 0.0
            public_holiday = 1.0
            remark = PUBLIC_HOLIDAYS[public_holiday_check]  # Now shows "New Year's Day", "Labor Day", etc.

        # **Handle User Leaves**
        for leave_date, leave_type in expanded_leave_details:
            if leave_date == date_obj.strftime("%Y-%m-%d"):  # Correct comparison
                if public_holiday == 0.0 and weekday not in [5, 6]:
                    at_work = 0.0  # Ensure work is set to 0.0
                    if leave_type == "Sick Leave" : #and leave_date != public_holiday_check:
                        sick_leave = 1.0
                    elif leave_type == "Childcare Leave": # and leave_date != public_holiday_check:
                        childcare_leave = 1.0
                    elif leave_type == "Annual Leave" : #and leave_date != public_holiday_check:
                        annual_leave = 1.0
                #remark = leave_type  # DONT NEED TO Display leave type in the remarks column

        # **Update Totals**
        totals["At Work"] += at_work
        totals["Public Holiday"] += public_holiday
        totals["Sick Leave"] += sick_leave
        totals["Childcare Leave"] += childcare_leave
        totals["Annual Leave"] += annual_leave

        # **Ensure "-" for Empty Cells**
        public_holiday_display = "-" if public_holiday == 0.0 else f"{public_holiday:.1f}"
        remark_display = remark if remark else "-"

        # **Insert Data**
        row_data = [
            current_row - 10,
            formatted_date,
            "" if at_work == 0.0 else f"{at_work:.1f}",
            public_holiday_display,  # Keep public holiday column unchanged
            "" if sick_leave == 0.0 else f"{sick_leave:.1f}",
            "" if childcare_leave == 0.0 else f"{childcare_leave:.1f}",
            "" if annual_leave == 0.0 else f"{annual_leave:.1f}",
            remark_display
        ]

        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=current_row, column=col_num, value=value)
            cell.alignment = center_alignment
            cell.border = thin_border

            # Highlight Leave & Public Holiday Cells
            if col_num in [3, 4, 5, 6, 7]:  # At Work, Public Holiday, Sick Leave, Childcare Leave, Annual Leave
                cell.fill = yellow_fill if value not in ["", "-"] else white_fill

            # Highlight Remarks for Public Holidays & Leaves | remove redudant  code
            if col_num == 8 and remark_display not in ["-", ""]:
                cell.fill = light_red_fill
            #   cell.font = bold_font

        # Apply Yellow Fill for At Work, Sick Leave, Childcare Leave, and Annual Leave up to row 31
        for row in range(11, 11 + days_in_month):  # Assuming row 11 is the first data row, row 41 is the last (31st day)
            for col_num in [3, 5, 6,
                                7]:  # Columns: At Work (C), Sick Leave (E), Childcare Leave (F), Annual Leave (G)
                    cell = ws.cell(row=row, column=col_num)
                    cell.fill = yellow_fill

        # Apply right aligned for At Work, Public Holiday, Sick Leave, Childcare Leave, and Annual Leave up to row 31
        for row in range(11, 11 + days_in_month):  # Assuming row 11 is the first data row, row 41 is the last (31st day)
            for col_num in [3, 4, 5, 6,
                                7]:  # Columns: At Work (C), Sick Leave (E), Childcare Leave (F), Annual Leave (G)
                    cell = ws.cell(row=row, column=col_num)
                    cell.alignment = right_alignment

        # Code to Apply Red Font & Right Alignment to Remarks (Rows 1-42)
        for row in range(11, 53):  # Adjusting for row range from 11 to 42 (inclusive)
            cell = ws.cell(row=row, column=8)  # Column 8 is "Remarks"
            if cell.value not in ["-", ""]:  # Apply styles only to meaningful values
                cell.font = red_font
                cell.alignment = right_alignment  # Apply right alignment
            else:  # If the value is "-", keep it black
                cell.font = black_font
                cell.alignment = right_alignment


        current_row += 1

    current_row += 2
    ws[f"A{current_row}"] = "Total"
    ws[f"A{current_row}"].font = bold_font
    ws[f"A{current_row}"].alignment = center_alignment

#Total cells vlaues changed
    # for col_num, key in enumerate(totals.keys(), 3):
    #     total_value = totals[key]
    #     display_total = "-" if total_value == 0.0 else f"{total_value:.1f}"  # Show "-" if total is zero
    #     cell = ws.cell(row=current_row, column=col_num, value=display_total)
    #     cell.font = bold_font
    #     cell.alignment = right_alignment  # Apply right alignment
    #     cell.border = thin_border
    # Apply Borders to Total Row (Columns A to H - up to "Remarks")
    for col_num, key in enumerate(totals.keys(), 3):  # Starts from column C (At Work) to H (Remarks)
        total_value = totals[key]
        display_total = "-" if total_value == 0.0 else f"{total_value:.1f}"  # Show "-" if total is zero

        cell = ws.cell(row=current_row, column=col_num, value=display_total)
        cell.font = bold_font
        cell.alignment = right_alignment  # Apply right alignment
        cell.border = thin_border  # Apply border to each cell

    # Apply border to column A, B, H (since we skipped it in the loop)
    ws[f"A{current_row}"].border = thin_border
    ws[f"B{current_row}"].border = thin_border
    ws[f"H{current_row}"].border = thin_border

    #current_row += 1 # Add an extra space
    # **Signature Section**
    current_date = datetime.now().strftime("%d - %B - %Y")
    ws[f"A{current_row + 2}"] = "Officer"
    ws[f"B{current_row + 2}"] = name
    ws[f"A{current_row + 3}"] = "Signature"
    ws[f"B{current_row + 3}"] = name
    ws[f"A{current_row + 4}"] = "Date"
    ws[f"B{current_row + 4}"] = current_date

    ws[f"A{current_row + 6}"] = "Reporting Officer"
    ws[f"B{current_row + 6}"] = reporting_officer
    ws[f"A{current_row + 7}"] = "Signature"
    ws[f"B{current_row + 7}"] = ""  # Leave Empty for Manager
    ws[f"A{current_row + 8}"] = "Date"
    ws[f"B{current_row + 8}"] = ""  # Leave Empty for Manager

    # Apply Borders to All Fields (Columns A & B)
    for row in range(current_row + 2, current_row + 9):  # Covers Officer + Reporting Officer sections
        ws[f"A{row}"].border = thin_border
        ws[f"B{row}"].border = thin_border
    for row in [current_row + 2, current_row + 3, current_row + 4, current_row + 6]:
        ws[f"B{row}"].alignment = center_alignment

        # **Save File**
    wb.save(output_file)
    print(f"Timesheet saved -> {output_file}")
    return output_file