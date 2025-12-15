
  

# Note Taking App

  

This is a GUI-based note-taking application written in Python using Tkinter. It is intentionally designed to be **vulnerable to CWE-312: Cleartext Storage of Sensitive Information**.

The application works as a realistic “normal-use” program, but internally stores sensitive data insecurely, allowing an attacker to retrieve it using a provided exploit.

  

----------

  

# High-Level Description

  

### Vulnerable Application (in `app/`)

  

- GUI-based Tkinter app with:

- User registration and login

- Admin login with management panel

- Users can create, edit, delete notes

- Notes and passwords stored using **pickle**

- Passwords stored using only hashing (still CWE-312 vulnerable)

- Notes stored **in plaintext** inside `notes.pkl`

- No encryption is used for any sensitive data
### Exploit (in `exploit/`)
- A standalone Python script that demonstrates **CWE-312 (Cleartext Storage of Sensitive Information)** by directly reading the application’s pickle storage files.

- It loads `users.pkl` and `notes.pkl` using `pickle` and prints:
  - usernames + stored password material (hash/plaintext field if present)
  - all notes (titles + contents) for each user
  

### The Vulnerability: CWE-312

  

This application violates CWE-312 – Cleartext Storage of Sensitive Information because:

- All passwords and usernames are hashed and stored inside unencrypted `.pkl` files. Although they're hashed but just hashing without salting and peppering at this day and age is the same as just plaintext.

- All user notes are stored as plaintext

- An attacker can simply read these files and decode them using Python’s pickle module

- No other encryption, no access control, and no data protection is implemented

  

----------

  

# How to run the App

  

### ### **Requirements**

  

Runs on any departmental Linux server (csx1–csx3) with Python 3 installed.

  

### ### **To run the app:**

  


```bash
cd app
python3 main.py
```  

This launches the Tkinter GUI.

  

Default admin credentials (auto-created if `users.pkl` is empty):

  ### Admin credentials

The admin login is hard-coded in `app/auth_manager.py`:
```bash
username: admin 
password: admin123
```  
  

**Note:**

The application automatically re-creates insecure storage files if deleted.

  ## How to run the exploit



### Run steps

From the repository root:
```bash
cd exploit
python3 CWE-312-exploit.py
```  

The exploit expects the repository layout to be unchanged and reads the storage files from:

-   `../app/storage/users.pkl`
    
-   `../app/storage/notes.pkl`
    

If you have not run the app yet (and the `.pkl` files don’t exist), run the application once first to generate them.

----------

  

# ## Team

  

Ahmed Tahmid

Labib Ahmed

Meenu Maheru

Umer Rahman

Deepinder Kaur