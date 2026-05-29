# Authentication module for the Graduation Project Registration System.

# A ready-made library in Python for encrypting texts
import hashlib        

# A function that takes the password and encrypts it
def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()

# A function that checks the password (must consist of at least 8 characters and include numbers and letters)
def validate_password(password):

    if len(password) < 8 :
        return False , " The password must be at least 8 characters. "

    elif password.isdigit():
        return False , " The password must consist of numbers and letters. "

    elif password.isalpha():
        return False , " The password must consist of numbers and letters. "

    return True , " "
    


# A class that manages login and authentication for all user roles (student, faculty, admin)
class AuthManager :
    def __init__(self,db):
        self.db = db 

    # Verifies the user via email and password and returns the role (student, faculty, admin)    
    def login(self, email, password):
        if not email or not password:
            return False, "Email and password are required."
        
        row = self.db.get_user_by_email(email)
        if row and row["password"] == hash_password(password):
            return True, row["role"]
        
        return False, "Invalid email or password."