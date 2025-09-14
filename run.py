import logging
logging.basicConfig(level=logging.DEBUG)
print(">>> run.py gestart <<<")

from app import create_app

app = create_app()

if __name__ == "__main__":
    print(">>> Flask app starten <<<")
    app.run(debug=True, host="127.0.0.1", port=5000)
