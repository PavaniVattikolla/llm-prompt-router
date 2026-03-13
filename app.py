from flask import Flask, request, jsonify
import openai
import json
import os
from prompts import SYSTEM_PROMPTS, CLASSIFIER_PROMPT

app = Flask(__name__)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_intent(message: str) -> dict:
    """
    Classifies the user's intent from their message.
    
    Args:
        message (str): The user's input message
        
    Returns:
        dict: A JSON object with structure:
        {
            "intent": "string",      # e.g., "code", "data", "writing", "career", "unclear"
            "confidence": float      # 0.0 to 1.0, representing certainty
        }
    """
    prompt = CLASSIFIER_PROMPT.format(user_message=message)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0
        )
        content = response.choices[0].message.content.strip()
        # Try to parse JSON
        result = json.loads(content)
        # Validate structure
        if ("intent" in result and "confidence" in result and 
            isinstance(result["confidence"], (int, float)) and 
            result["intent"] in ["code", "data", "writing", "career", "unclear"]):
            return result
        else:
            return {"intent": "unclear", "confidence": 0.0}
    except Exception as e:
        print(f"Error in classification: {e}")
        return {"intent": "unclear", "confidence": 0.0}

def route_and_respond(message: str, intent: dict) -> str:
    """
    Routes the message to the appropriate expert persona based on intent.
    
    Args:
        message (str): The original user message
        intent (dict): The classified intent dict with "intent" and "confidence" keys
        
    Returns:
        str: The final generated response from the selected expert persona
    """
    intent_label = intent["intent"]
    confidence = intent["confidence"]
    
    if intent_label == "unclear":
        response = SYSTEM_PROMPTS["unclear"]
    else:
        system_prompt = SYSTEM_PROMPTS[intent_label]
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=1000,
                temperature=0.7
            ).choices[0].message.content.strip()
        except Exception as e:
            response = f"Error generating response: {e}"
    
    # Log the interaction
    log_interaction(intent_label, confidence, message, response)
    return response

def log_interaction(intent, confidence, user_message, final_response):
    log_entry = {
        "intent": intent,
        "confidence": confidence,
        "user_message": user_message,
        "final_response": final_response
    }
    with open("route_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

@app.route('/route', methods=['POST'])
def route():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' in request"}), 400
    
    message = data['message']
    intent = classify_intent(message)
    response = route_and_respond(message, intent)
    return jsonify({"response": response, "intent": intent})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)