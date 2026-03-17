from flask import Flask, request, jsonify
from dotenv import load_dotenv
from groq import Groq
import json
import os
from prompts import SYSTEM_PROMPTS

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

client = Groq(api_key=api_key.strip())

print("Groq API Key loaded:", api_key[:5] + "...")

app = Flask(__name__)

VALID_INTENTS = ["code", "data", "writing", "career", "unclear"]

# 🔥 Strong classifier prompt
CLASSIFIER_PROMPT = """
You are an intent classifier.

Classify the user's message into one of these:
code, data, writing, career, unclear

Return ONLY valid JSON:
{"intent": "code", "confidence": 0.95}

No explanations. No code. Only JSON.
"""

# ✅ Intent Classification
def classify_intent(message: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": CLASSIFIER_PROMPT},
                {"role": "user", "content": message}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content.strip()
        print("MODEL RESPONSE:", content)

        result = json.loads(content)

        intent = result.get("intent", "unclear")
        confidence = result.get("confidence", 0.0)

        if intent not in VALID_INTENTS:
            return {"intent": "unclear", "confidence": 0.0}

        return {"intent": intent, "confidence": confidence}

    except Exception as e:
        print("Classification Error:", e)
        return {"intent": "unclear", "confidence": 0.0}


# ✅ Routing + Clean Output
def route_and_respond(message: str, intent: dict) -> str:
    intent_label = intent["intent"]

    if intent_label == "unclear":
        return "Are you asking for help with coding, data analysis, writing, or career advice?"

    system_prompt = SYSTEM_PROMPTS[intent_label]

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7
        )

        output = completion.choices[0].message.content.strip()

        # 🔥 Remove markdown formatting
        output = output.replace("```python", "").replace("```", "").strip()

        return output

    except Exception as e:
        return f"Error generating response: {e}"


@app.route('/route', methods=['POST'])
def route():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message'"}), 400

    message = data["message"]

    intent = classify_intent(message)
    response = route_and_respond(message, intent)

    return jsonify({
        "intent": intent,
        "response": response
    })


if __name__ == "__main__":
    print("Starting LLM Prompt Router (Groq)...")
    app.run(host="0.0.0.0", port=5000, debug=True)