import secrets

# Generate SECRET_KEY (32 bytes = 64 hex characters)
secret_key = secrets.token_hex(32)
print(f"SECRET_KEY={secret_key}")

# Generate SECURITY_PASSWORD_SALT (16 bytes = 32 hex characters)
password_salt = secrets.token_hex(16)
print(f"SECURITY_PASSWORD_SALT={password_salt}")
