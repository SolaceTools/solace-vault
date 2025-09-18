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
