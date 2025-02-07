import json

USER_DATA_FILE = "config/user_details.json"
PUBLIC_HOLIDAYS_FILE = "config/ph.json"

# ✅ Load data from a JSON file
def load_json(file_path):
    """Load data from a JSON file."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {file_path}: {e}")
        return {}

# ✅ Validate the structure of user details
def validate_user_details(data):
    """Validate the user details JSON."""
    required_keys = {"name", "skill_level", "role_specialization", "group_specialization", "contractor"}
    for user_id, user_info in data.items():
        if not required_keys.issubset(user_info.keys()):
            print(f"User ID {user_id} is missing required keys: {required_keys - user_info.keys()}")
    return data

# ✅ Ensure USER_DETAILS is initialized
USER_DETAILS = {}

# ✅ Load and store USER_DETAILS globally
def load_user_details():
    """Reload USER_DETAILS from the JSON file."""
    global USER_DETAILS  # ✅ Declare before using
    USER_DETAILS = validate_user_details(load_json(USER_DATA_FILE))  # ✅ Assign instead of clearing
    return USER_DETAILS  # ✅ Return updated dictionary

# ✅ Save user data to JSON
def save_user_data(updated_user_details):
    """Save USER_DETAILS back to JSON file."""
    with open(USER_DATA_FILE, "w") as file:
        json.dump(updated_user_details, file, indent=4)

# ✅ Initialize USER_DETAILS on import
USER_DETAILS = load_user_details()  # ✅ Ensures it is accessible for imports

# ✅ Load other configurations
PUBLIC_HOLIDAYS = load_json(PUBLIC_HOLIDAYS_FILE)
