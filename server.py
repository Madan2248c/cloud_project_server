from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
from scraper import NewsScraper
import threading
import time
import bcrypt

cred = credentials.Certificate('./config/firebase.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cloudcomputing-4555d-default-rtdb.firebaseio.com'
})

app = Flask(__name__)

url = 'https://www.ndtv.com/'

last_updated = None  # Track the last update timestamp

def scrape_and_update_headlines():
    global last_updated
    while True:
        try:
            news_scraper = NewsScraper(url)
            headlines = news_scraper.get_headlines()
            print(f"Scraped {len(headlines)} headlines")
            print(headlines)

            headlines_ref = db.reference('/headlines')
            headlines_ref.set(headlines)

            # Update the last_updated timestamp
            last_updated = time.ctime()
            print(f"Headlines updated at {last_updated}")
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
    print(email, password)
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    users_ref = db.reference('/users')
    users = users_ref.get()

    if users:
        for user_id, user_data in users.items():
            if user_data.get('email') == email:
                print("je")
                stored_hashed_password = user_data.get('password')
                print(bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')))
                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
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

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_user_ref = users_ref.push()
    new_user_ref.set({
        "email": email,
        "password": hashed_password.decode('utf-8')  # Decode to store as a string
    })

    return jsonify({"message": "Signup successful", "user_id": new_user_ref.key}), 201

@app.route('/headlines', methods=['GET'])
def get_headlines():
    headlines_ref = db.reference('/headlines')
    headlines = headlines_ref.get()

    if headlines:
        return jsonify(headlines), 200

    return jsonify({"error": "No headlines found"}), 404

@app.route('/last_updated', methods=['GET'])
def get_last_updated():
    global last_updated
    if last_updated:
        return jsonify({"last_updated": last_updated}), 200
    return jsonify({"error": "Headlines have not been updated yet"}), 404

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
    # app.run(port=3000)
