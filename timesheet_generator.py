class TimesheetGenerator:
    def __init__(self, user_details, public_holidays):
        self.user_details = user_details
        self.public_holidays = public_holidays

    def generate(self, user_id, month, year):
        print(f"Generating timesheet for User {user_id} - {month}/{year}")
