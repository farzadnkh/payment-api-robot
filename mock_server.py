"""Mock server for payment API – serves testdata JSON files by scenario.

Usage:
    python mock_server.py

Endpoint:
    GET /payment/?CellNumber=<string>&scenario=s1|s2|...|s8
"""
import json
from pathlib import Path

from flask import Flask, request, jsonify

app = Flask(__name__)
# Use absolute path so it works no matter where you run: python mock_server.py
TESTDATA = Path(__file__).resolve().parent / "testdata"
SCENARIO_FILES = {
    "s1": "happy_path.json",
    "s2": "bnpl_blocked.json",
    "s3": "insufficient_credit.json",
    "s4": "non_active_option.json",
    "s5": "multiple_default.json",
    "s6": "missing_field.json",
    "s7": "wrong_type.json",
    "s8": "non_success.json",
}


@app.route("/health")
def health():
    """Simple check that this server is running."""
    return jsonify({"status": "ok"})


@app.route("/payment/", methods=["GET"])
def payment():
    scenario = request.args.get("scenario", "s1")
    print(f"[mock_server] request scenario={scenario}", flush=True)
    if scenario == "s9":
        data = {"status": 500, "payment_methods": []}
        return jsonify(data), 500
    if scenario == "s_r3":
        data = {
            "status": 200,
            "payment_methods": [
                {
                    "id": 2,
                    "type": "online",
                    "title": "Online wallet misconfig",
                    "is_clickable": True,
                    "is_wallet": True,
                }
            ],
        }
        return jsonify(data)
    filename = SCENARIO_FILES.get(scenario)
    if not filename:
        return jsonify({"error": f"Unknown scenario: {scenario}"}), 400
    path = TESTDATA / filename
    path_str = str(path)
    if not path.exists():
        err = {"error": f"File not found: {filename}", "path": path_str}
        print(f"[mock_server] {err}", flush=True)
        return jsonify(err), 500
    try:
        with open(path_str, encoding="utf-8") as f:
            data = json.load(f)
        print(f"[mock_server] OK scenario={scenario} -> {filename}", flush=True)
        return jsonify(data)
    except Exception as e:
        err = {"error": str(e), "path": path_str}
        print(f"[mock_server] {err}", flush=True)
        return jsonify(err), 500


if __name__ == "__main__":
    print(f"[mock_server] TESTDATA = {TESTDATA}")
    print(f"[mock_server] exists: {TESTDATA.exists()}, files: {list(TESTDATA.glob('*.json')) if TESTDATA.exists() else 'N/A'}")
    app.run(host="0.0.0.0", port=8080)
