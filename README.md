
# Note Taking App

This project is a GUI-based note-taking application written in Python using Tkinter. It is intentionally designed to be **vulnerable to CWE-312: Cleartext Storage of Sensitive Information**.  
The application works as a realistic “normal-use” program, but internally stores sensitive data insecurely, allowing an attacker to retrieve it using a provided exploit.

----------

#  High-Level Description

### Vulnerable Application

-   GUI-based Tkinter app with:
    
    -   User registration and login
        
    -   Admin login with management panel
        
    -   Users can create, edit, delete notes
        
    -   Notes and passwords stored using **pickle**
        
    -   Passwords stored using only hashing (still CWE-312 vulnerable)
        
    -   Notes stored **in plaintext** inside `notes.pkl`
        
    -   No encryption is used for any sensitive data
        

###  The Vulnerability: CWE-312

This application violates CWE-312 – Cleartext Storage of Sensitive Information because:
    
-   All passwords and usernames are hashed and stored inside unencrypted `.pkl` files. Although they're hashed but just hashing without salting and peppering at this day and age is the same as just plaintext.
-   All user notes are stored as plaintext
    
-   An attacker can simply read these files and decode them using Python’s pickle module
    
-   No other encryption, no access control, and no data protection is implemented
    

###  The Exploit

Provided exploit scripts:

-   `dump_credentials.py` → extracts all usernames + hashed passwords
    
-   `dump_notes.py` → extracts all user notes
    
-   `auto_login.py` → logs attacker in by reading stored credentials
    

The exploit works because both `.pkl` files are readable and unencrypted.

----------

# How to Compile/Run the App

### ### **Requirements**

Runs on any departmental Linux server (csx1–csx3) with Python 3 installed.

### ### **To run the app:**

`cd app
python3 main.py` 

This launches the Tkinter GUI.

Default admin credentials (auto-created if `users.pkl` is empty):

`username: admin  password: admin123` 

**Note:**  
The application automatically re-creates insecure storage files if deleted.

----------

# ##  Team

Ahmed Tahmid 
Labib Ahmed 
Meenu Maheru
Umer Rahman 
Deepinder Kaur
