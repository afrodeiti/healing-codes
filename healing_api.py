from flask import Flask, request, jsonify
import re
import threading
import time
from rapidfuzz import process, fuzz
import hashlib

app = Flask(__name__)

# Load healing codes from TXT file only
def load_healing_codes_from_txt():
    codes = []
    try:
        current_category = None
        with open("healing_codes.txt", "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                # Identify category headers
                if line.isupper() and len(line.split()) < 10:
                    current_category = line
                    continue

                # Match "CODE - MEANING" format
                if re.match(r'^\d[\d\s]+ - .+', line):
                    code, meaning = line.split("-", 1)
                    code = code.strip()
                    meaning = meaning.strip()
                    keywords = re.findall(r'\b\w+\b', meaning.lower())
                    if current_category:
                        keywords.append(current_category.lower())
                    codes.append({
                        "code": code,
                        "meaning": meaning,
                        "keywords": keywords
                    })
    except Exception as e:
        print(f"❌ Failed to load healing codes: {e}")
    return codes

healing_codes = load_healing_codes_from_txt()
all_keywords = list(set(keyword for entry in healing_codes for keyword in entry["keywords"]))

@app.route('/get-healing-code', methods=['POST'])
def get_healing_code():
    data = request.json
    issue = data.get("issue", "").lower()
    limit = data.get("limit", None)

    print(f"🔍 Searching for issue: {issue}")
    unique_codes = {}

    # Exact match first
    for entry in healing_codes:
        if issue in entry["keywords"]:
            unique_codes[entry["code"]] = entry

    # Fuzzy match only if no exact
    if not unique_codes:
        best_match, score = process.extractOne(issue, all_keywords, scorer=fuzz.partial_ratio)
        print(f"🌀 Fuzzy match: {best_match} (score {score})")
        if score >= 92:
            for entry in healing_codes:
                if best_match in entry["keywords"]:
                    unique_codes[entry["code"]] = entry

    # Filter safe code formats (e.g. no made-up short strings)
    matched_codes = [
        entry for entry in unique_codes.values()
        if re.match(r'^\d[\d\s]{6,}$', entry["code"])
    ]

    if matched_codes:
        if limit and isinstance(limit, int):
            matched_codes = matched_codes[:limit]
        return jsonify([
            {"code": entry["code"], "meaning": entry["meaning"]}
            for entry in matched_codes
        ])

    return jsonify({"message": "No healing code found for this issue."})

# INTENTION BROADCASTING
@app.route('/run-intention', methods=['POST'])
def run_intention():
    data = request.json
    intention = data.get("intention", "").strip()
    duration = int(data.get("duration", 60))
    frequency = float(data.get("frequency", 0))
    boost = bool(data.get("boost", False))
    multiplier = int(data.get("multiplier", 1))

    if not intention:
        return jsonify({"success": False, "message": "No intention provided."}), 400

    def sha512(message):
        return hashlib.sha512(message.encode("utf-8")).hexdigest().upper()

    def repeater():
        start = time.time()
        total_iterations = 0
        interval = (1 / frequency) if frequency > 0 else 0.001

        while time.time() - start < duration:
            text_to_hash = intention
            if boost:
                text_to_hash = sha512(f"{text_to_hash}:{intention}")
            _ = sha512(text_to_hash)
            total_iterations += multiplier
            time.sleep(interval)

        print(f"✅ Finished repeating: {intention} ({total_iterations} iterations)")

    threading.Thread(target=repeater).start()

    return jsonify({
        "success": True,
        "message": f"Intention is now running for {duration} seconds.",
        "intention": intention,
        "frequency": frequency,
        "boost": boost,
        "multiplier": multiplier
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
