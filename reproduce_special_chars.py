import dj_database_url
import os

# Test a URL with unescaped special characters in the password
# Example: password is "p@ssword"
url = "postgresql://user:p@ssword@host:5432/db"
os.environ['DATABASE_URL'] = url

try:
    config = dj_database_url.config()
    print("Successfully parsed URL:")
    print(config)
except Exception as e:
    print(f"Failed to parse URL: {e}")
