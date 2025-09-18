from app import init_db
from app import app
import threading
import webview

HOST = "127.0.0.1"
PORT = 5000

def start_flask():
    init_db()
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    webview.create_window(
        title="Solace Vault",
        url=f"http://{HOST}:{PORT}/",
        width=1000,
        height=800,
        resizable=True
    )

    webview.start()