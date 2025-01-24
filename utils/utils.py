import json

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
def validate_user_details(data):
    """Validate the user details JSON."""
    required_keys = {"name", "skill_level", "role_specialization", "group_specialization", "contractor"}
    for user_id, user_info in data.items():
        if not required_keys.issubset(user_info.keys()):
            print(f"User ID {user_id} is missing required keys: {required_keys - user_info.keys()}")
    return data

USER_DETAILS = validate_user_details(load_json("config/user_details.json"))

# Load specific configurations
PUBLIC_HOLIDAYS = load_json("config/ph.json")
USER_DETAILS = load_json("config/user_details.json")
