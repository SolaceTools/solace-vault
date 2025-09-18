# Solace Vault

A secure, local-first zero-knowledge vault for storing sensitive data.  

---

## 🚀 Features
- 🔐 Zero-knowledge encryption (AES-256 + Argon2)  
- 📦 Local SQLite database (no cloud storage)  
- 🖥️ Desktop UI with WebView  
- 🛡️ Offline backups + import/export  

---

## 📥 Download (Windows)

- [Download SolaceVault.exe](https://github.com/SolaceTools/solace-vault/releases)  

⚠️ **Note on SmartScreen & Antivirus Warnings:**  
Windows may show a warning because the app is **not digitally signed**. This is common for open-source apps.  
If you trust the source:  
1. Right-click the file → **Properties** → **Unblock** (if available)  
2. Double-click the file  
3. Click **More info** → **Run anyway**  

---

## 🛠️ Run From Source

### Requirements
- Python 3.10+  
- Git  

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/SolaceTools/solace-vault.git
cd solace-vault
```

### 2️⃣ Create a Virtual Environment
This keeps dependencies isolated from your system Python.

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should now see `(venv)` at the start of your terminal prompt.

### 3️⃣ Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
This installs all necessary Python packages (Flask, pywebview, Argon2, etc.) inside your virtual environment.

### 4️⃣ Run the App
```bash
python main.py
```
The app will start a local Flask server and open a WebView window for the UI.  

Your SQLite database and backups are stored locally:

- **Linux/macOS:** `~/.SOLiD_Vault`  
- **Windows:** `%USERPROFILE%\.SOLiD_Vault`  

---

## ⚡ Quickstart
If you just want to run it quickly after cloning:

```bash
cd solace-vault
python -m venv venv
venv\Scripts\activate   # or `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
python main.py
```

---

## 🔄 Updating the App
Pull the latest changes from GitHub:
```bash
git pull origin main
```

If `requirements.txt` changed:
```bash
pip install -r requirements.txt
```

Restart the app:
```bash
python main.py
```

---

## 📝 Troubleshooting

- **App doesn’t start:** Make sure Python 3.10+ is installed and your virtual environment is active.  
- **Dependencies fail:** Upgrade pip with `pip install --upgrade pip` and try again.  
- **Windows shows virus warning:** This is normal for unsigned executables. See the Download section above.  

---

## 📚 Notes
Always run the app inside the activated virtual environment to avoid dependency issues.  
To deactivate the virtual environment:
```bash
deactivate
```

