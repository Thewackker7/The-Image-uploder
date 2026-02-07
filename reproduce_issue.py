import dj_database_url
import os

# Test the IPv6 URL from the .env file
url = "postgresql://postgres:PQ4aRW0cHhXesgXS@[2406:da18:243:741e:6c74:2a21:37e7:f48f]:5432/postgres"
os.environ['DATABASE_URL'] = url

try:
    config = dj_database_url.config()
    print("Successfully parsed URL:")
    print(config)
except Exception as e:
    print(f"Failed to parse URL: {e}")
