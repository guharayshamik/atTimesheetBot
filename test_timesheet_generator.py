from datetime import datetime
from timesheet_generator import generate_timesheet_excel  # Import your function
import os

# Mocked user details (Simulating what load_user_details() would return)
USER_DETAILS_MOCK = {
    "7032290213": {
        "name": "adasd",
        "timesheet_preference": "8.5",
        "skill_level": "Professional",
        "role_specialization": "DevOps Engineer - II",
        "group_specialization": "asdasd",
        "contractor": "PALO IT",
        "po_ref": "GVT000ABC1234",
        "po_date": "1 May 24 - 30",
        "description": "Agile Co-Development Services",
        "reporting_officer": "John Doe"
    }
}

# Fixed Mocked Leave Details with Correct Date Format
MOCK_LEAVE_DETAILS = [
    ("05-February", "07-February", "Annual Leave"),  # Correct format
    ("12-February", "12-February", "Sick Leave"),  # Correct format
    ("20-February", "22-February", "NS Leave")  # Correct format
]

MOCK_LEAVE_DETAILS_JANUARY = [
    ("03-January", "05-January", "Annual Leave"),  # Jan 3rd to 5th
    ("10-January", "10-January", "Sick Leave"),  # Jan 10th
    ("15-January", "17-January", "NS Leave"),  # Jan 15th to 17th
    ("25-January", "25-January", "Childcare Leave")  # Jan 25th
]

MOCK_LEAVE_DETAILS_AUGUST = [
    ("02-August", "04-August", "Annual Leave"),  # Aug 2nd to 4th
    ("08-August", "08-August", "Sick Leave"),  # Aug 8th
  #  ("14-August", "16-August", "NS Leave"),  # Aug 14th to 16th
    ("23-August", "23-August", "Public Holiday")  # Aug 23rd (Simulating a public holiday)
]

MOCK_LEAVE_DETAILS_SEPTEMBER = [
    ("04-September", "06-September", "Annual Leave"),  # Sep 4th to 6th
    ("12-September", "12-September", "Sick Leave"),  # Sep 12th
    ("18-September", "20-September", "NS Leave"),  # Sep 18th to 20th
    ("27-September", "27-September", "Childcare Leave")  # Sep 27th
]

MOCK_LEAVE_DETAILS_DECEMBER = [
    ("05-December", "05-December", "Half Day"),  # Half-day leave on Dec 5th
    ("10-December", "10-December", "Weekend Efforts"),  # Weekend effort on Dec 10th (Assuming Sunday)
    ("15-December", "15-December", "NS Leave"),  # NS Leave on Dec 15th
    ("20-December", "22-December", "Annual Leave"),  # Annual Leave from Dec 20 to Dec 22
    ("25-December", "25-December", "Public Holiday"),  # Public Holiday on Dec 25 (Christmas)
    ("31-December", "31-December", "Weekend Efforts"),  # Weekend effort on Dec 31st (Sunday)
]

MOCK_LEAVE_DETAILS_OCTOBER = [
    ("04-October", "04-October", "Half Day"),  # Half-day leave on Oct 4th
    ("08-October", "08-October", "Weekend Efforts"),  # Weekend effort on Oct 8th (Sunday)
    ("12-October", "12-October", "Annual Leave"),  # Annual Leave on Oct 12th
    ("18-October", "20-October", "Sick Leave"),  # Sick Leave from Oct 18 to Oct 20
    ("28-October", "28-October", "Weekend Efforts"),  # Weekend effort on Oct 28th (Saturday)
    ("31-October", "31-October", "Public Holiday")  # Public Holiday on Oct 31st
]


# Mocked Function: Replace `load_user_details` in your main script
def mock_load_user_details():
    return USER_DETAILS_MOCK

# Inject the mock function
def generate_mocked_timesheet():
    # Parameters
    user_id = "7032290213"
    month = 2  # February
    year = 2025  # Test Year

    # Call function
    excel_file = generate_timesheet_excel(user_id, month, year, MOCK_LEAVE_DETAILS)

    # Check if file exists
    if os.path.exists(excel_file):
        print(f" Test Passed: Timesheet generated successfully -> {excel_file}")
    else:
        print(" Test Failed: No timesheet was generated.")

def generate_mocked_timesheet_for_month(user_id, month, year, leave_details, month_name):
    print(f"Generating timesheet for {month_name} {year}...")
    excel_file = generate_timesheet_excel(user_id, month, year, leave_details)

    if os.path.exists(excel_file):
        print(f"Test Passed: {month_name} timesheet generated successfully -> {excel_file}")
    else:
        print(f"Test Failed: No timesheet was generated for {month_name}.")


if __name__ == "__main__":
    user_id = "7032290213"
    year = 2025  # Test Year

    # Test for January
    generate_mocked_timesheet_for_month(user_id, 1, year, MOCK_LEAVE_DETAILS_JANUARY, "January")

    # Test for August
    generate_mocked_timesheet_for_month(user_id, 8, year, MOCK_LEAVE_DETAILS_AUGUST, "August")

    # Test for September
    generate_mocked_timesheet_for_month(user_id, 9, year, MOCK_LEAVE_DETAILS_SEPTEMBER, "September")

    # Test for October
    generate_mocked_timesheet_for_month(user_id, 10, year, MOCK_LEAVE_DETAILS_OCTOBER, "October")

    # Test for December
    generate_mocked_timesheet_for_month(user_id, 12, year, MOCK_LEAVE_DETAILS_DECEMBER, "December")

    generate_mocked_timesheet()



