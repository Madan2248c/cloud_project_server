from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
from scraper import NewsScraper
import threading
import time

cred = credentials.Certificate('./config/firebase.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cloudcomputing-4555d-default-rtdb.firebaseio.com'
})

app = Flask(__name__)

url = 'https://www.ndtv.com/'

def scrape_and_update_headlines():
    while True:
        try:
            news_scraper = NewsScraper(url)
            headlines = news_scraper.get_headlines()
            print(f"Scraped {len(headlines)} headlines")
            print(headlines)

            headlines_ref = db.reference('/headlines')
            headlines_ref.set(headlines)

            print(f"Headlines updated at {time.ctime()}")
        except Exception as e:
            print(f"Error updating headlines: {e}")

        time.sleep(3600)

threading.Thread(target=scrape_and_update_headlines, daemon=True).start()

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    users_ref = db.reference('/users')
    users = users_ref.get()

    for user_id, user_data in users.items():
        if user_data.get('email') == email and user_data.get('password') == password:
            return jsonify({"message": "Login successful", "user_id": user_id}), 200

    return jsonify({"error": "Invalid email or password"}), 401

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    users_ref = db.reference('/users')
    users = users_ref.get()

    if users:
        for user_data in users.values():
            if user_data.get('email') == email:
                return jsonify({"error": "Email already exists"}), 400

    new_user_ref = users_ref.push()
    new_user_ref.set({
        "email": email,
        "password": password
    })

    return jsonify({"message": "Signup successful", "user_id": new_user_ref.key}), 201

@app.route('/headlines', methods=['GET'])
def get_headlines():
    headlines_ref = db.reference('/headlines')
    headlines = headlines_ref.get()

    if headlines:
        return jsonify(headlines), 200

    return jsonify({"error": "No headlines found"}), 404

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
