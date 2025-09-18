from models import db, Secret, Log
from encryption import decrypt_secret
from config import BACKUP_PATH
import json

def format_timestamp(value):
    day = value.day
    suffix = 'th' if 11 <= day % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f"{day}{suffix} {value.strftime('%B, %Y')}"

def format_timestamp_with_time(value):
    day = value.day
    suffix = 'th' if 11 <= day % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    date_part = f"{day}{suffix} {value.strftime('%B, %Y')}"
    time_part = value.strftime('%I:%M %p').lstrip('0')
    return f"{date_part} - {time_part}"

def add_log(action, secret=None):
    log_entry = Log(
        action=action,
        secret_id=secret.id if secret else None,
        category=secret.category if secret else None,
        label=secret.label if secret else None
    )
    db.session.add(log_entry)
    db.session.commit()

def save_backup():
    backup_data = []
    for s in Secret.query.all():
        backup_data.append({
            "id": s.id,
            "category": s.category,
            "label": s.label,
            "tag": s.tag,
            "data": s.data
        })
    with open(BACKUP_PATH, "w") as f:
        json.dump(backup_data, f, indent=2)

def load_backup(master_password):
    if not BACKUP_PATH.exists():
        return
    with open(BACKUP_PATH, "r") as f:
        backup_data = json.load(f)
    for item in backup_data:
        if Secret.query.filter_by(id=item["id"]).first():
            continue
        try:
            decrypt_secret(item["data"], master_password)
        except Exception:
            continue
        new_secret = Secret(
            id=item["id"],
            category=item["category"],
            label=item["label"],
            tag=item["tag"],
            data=item["data"]
        )
        db.session.add(new_secret)
    db.session.commit()