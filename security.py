import re

# ✅ Block common SQL injection attempts
SQL_BLOCKLIST = [
    "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "WHERE", "TABLE", "FROM", "UNION", "OR", "AND", "EXEC",
    "xp_cmdshell", "INFORMATION_SCHEMA", "LOAD_FILE", "OUTFILE", "DATABASES"
]

def contains_path_traversal(user_input):
    """Detect directory traversal attempts like ../ or accessing sensitive system files."""
    return any(
        pattern in user_input.lower()
        for pattern in ["../", "/etc/passwd", "/root", "/home", "C:\\", "D:\\", "%SYSTEMROOT%"]
    )

def sanitize_input(user_input, allow_brackets=False, max_words=5, clean_numbers=False):
    """Sanitize user input to remove injections, enforce word limits, and optionally clean numbers."""

    # ✅ Block path traversal attempts
    if contains_path_traversal(user_input):
        return ""

    # ✅ Remove unwanted characters (Keep only alphanumeric, spaces, ., -, /, brackets if allowed)
    if allow_brackets:
        sanitized_text = re.sub(r"[^\w\s.,()/-]", "", user_input.strip())  # Allow (, )
    else:
        sanitized_text = re.sub(r"[^\w\s.,/-]", "", user_input.strip())  # Remove (, )

    # ✅ Prevent SQL Injection
    words = sanitized_text.split()
    words = [word for word in words if word.upper() not in SQL_BLOCKLIST]  # Remove SQL injection words
    sanitized_text = " ".join(words[:max_words])  # Enforce max words

    # ✅ Remove numbers (Only for name & reporting_officer)
    if clean_numbers:
        sanitized_text = re.sub(r"\d", "", sanitized_text).strip()

    # ✅ Normalize spaces (Remove multiple spaces)
    sanitized_text = re.sub(r"\s+", " ", sanitized_text).strip()

    return sanitized_text
