from flask import Flask, request, jsonify
import json
import os
import random
import time

app = Flask(__name__)

# Load existing cards
CARDS_FILE = 'amex_cards.json'
if os.path.exists(CARDS_FILE):
    with open(CARDS_FILE, 'r') as f:
        cards_db = json.load(f)
else:
    cards_db = {}

def find_card(card_number):
    for token, card_info in cards_db.items():
        if card_info['card_number'] == card_number:
            return token, card_info
    return None, None

@app.route('/charge', methods=['POST'])
def charge():
    data = request.json
    print(f"Incoming charge request: {data}")

    card_number = data.get('card_number')
    exp_month = data.get('exp_month')
    exp_year = data.get('exp_year')
    cvv = data.get('cvv')

    if not all([card_number, exp_month, exp_year, cvv]):
        return jsonify({"error": "Missing card details"}), 400

    token, card_info = find_card(card_number)

    if card_info:
        print(f"✅ Found matching card in database. Token: {token}")
        # Simulate approval
        response = {
            "status": "approved",
            "authorization_code": str(random.randint(100000, 999999)),
            "card": {
                "brand": "American Express",
                "last4": card_number[-4:],
                "exp_month": exp_month,
                "exp_year": exp_year
            }
        }
        return jsonify(response)
    else:
        print("❌ Card not found or invalid.")
        return jsonify({"status": "declined", "reason": "Card not found"}), 404

@app.route('/tokenize', methods=['POST'])
def tokenize():
    data = request.json
    card_number = data.get('card_number')

    if not card_number:
        return jsonify({"error": "Card number missing"}), 400

    # Create a fake token
    token = f"tok_{random.randint(10000000,99999999)}"
    cards_db[token] = {
        "card_number": card_number,
        "exp_month": data.get('exp_month'),
        "exp_year": data.get('exp_year'),
        "cvv": data.get('cvv'),
        "name": data.get('name'),
        "address": data.get('address')
    }

    # Save back to file
    with open(CARDS_FILE, 'w') as f:
        json.dump(cards_db, f, indent=4)

    print(f"✅ Tokenized card {card_number} as {token}")
    return jsonify({"token": token})

@app.route('/3ds-challenge', methods=['POST'])
def three_ds_challenge():
    data = request.json
    print(f"Incoming 3DS challenge: {data}")

    # Simulate always passing 3DS
    return jsonify({"3ds_status": "authenticated"})

@app.route('/3ds-fail', methods=['POST'])
def three_ds_fail():
    data = request.json
    print(f"Incoming 3DS fail simulation: {data}")

    return jsonify({"3ds_status": "failed"})

# 🆕 New: Catch-all handler to stop 404 errors
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    print(f"⚡ Caught unknown path: /{path}")
    return jsonify({"status": "ok", "message": "Request captured successfully."}), 200

# ✅ Proper app.run to start server
if __name__ == "__main__":
    print("✅ Starting Amex Proxy Server on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
