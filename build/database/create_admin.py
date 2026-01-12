import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(admin_password.encode("utf-8"), salt)
hashed_str = hashed.decode("utf-8")

print("-- Admin user insert statement")
print("INSERT INTO USERS (email, password, username, role, banned)")
print(f"VALUES ('admin@umontpellier.fr', '{hashed_str}', 'Admin', 'ADMIN', FALSE);")
