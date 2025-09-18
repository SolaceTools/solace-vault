from pathlib import Path

DATA_DIR = Path.home() / ".SOLiD_Vault"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "vault.db"
BACKUP_PATH = DATA_DIR / "backup.json"