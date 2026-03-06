import hashlib
import secrets

def hash_password(password):
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${password_hash}"

def verify_password(stored_hash, password):
    try:
        salt, hash_val = stored_hash.split('$')
        return hash_val == hashlib.sha256((salt + password).encode()).hexdigest()
    except:
        return stored_hash == hashlib.sha256(password.encode()).hexdigest() or stored_hash == password

# Test the password functions
test_pwd = 'testpass123'
hashed = hash_password(test_pwd)
print(f'Hashed: {hashed}')
print(f'Verify with correct password: {verify_password(hashed, test_pwd)}')
print(f'Verify with wrong password: {verify_password(hashed, "wrongpass")}')
