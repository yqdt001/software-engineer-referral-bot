from flask import Flask, request, jsonify
import requests
import re
from typing import Dict, Any

app = Flask(__name__)

JAN_AI_ENDPOINT = "http://localhost:1337/v1/chat/completions"


def clean_resume_text(text: str) -> str:
    """
    Clean and normalize resume text by removing extra whitespace,
    special characters, and formatting artifacts.
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common resume artifacts
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)  # Zero-width characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Non-ASCII characters (optional)
    
    # Remove extra newlines and spaces
    text = text.strip()
    
    return text


def create_scoring_prompt(resume_text: str) -> str:
    """
    Create a prompt for the AI to score technical skills from the resume.
    """
    prompt = f"""Please analyze the following resume and provide a technical skill assessment.

Resume:
{resume_text}

Please evaluate:
1. Programming languages and proficiency levels
2. Frameworks and libraries used
3. Technical tools and technologies
4. Years of experience with key technologies
5. Overall technical score (1-10)

Provide the assessment in JSON format with the following structure:
{{
    "programming_languages": [{{"name": "Python", "proficiency": "Advanced", "years": 5}}],
    "frameworks": [{{"name": "Flask", "proficiency": "Intermediate"}}],
    "tools": ["Git", "Docker", "AWS"],
    "technical_score": 8,
    "summary": "Brief summary of technical capabilities"
}}"""
    return prompt


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook endpoint to receive Make.com POST payloads.
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        # Extract resume text from payload
        resume_text = data.get('resume_text') or data.get('resume') or data.get('text')
        
        if not resume_text:
            return jsonify({"error": "No resume text found in payload"}), 400
        
        # Clean the resume text
        cleaned_text = clean_resume_text(resume_text)
        
        # Create scoring prompt
        prompt = create_scoring_prompt(cleaned_text)
        
        # Prepare request to Jan AI
        jan_payload = {
            "model": "qwen2_5-coder-7b-instruct-q4_k_m",  # Adjust based on your Jan AI model
            "messages": [
                {
                    "role": "system",
                    "content": "You are a technical recruiter skilled at evaluating software engineering resumes."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        # Forward to Jan AI endpoint
        response = requests.post(
            JAN_AI_ENDPOINT,
            json=jan_payload,
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        
        if response.status_code == 200:
            jan_response = response.json()
            return jsonify({
                "status": "success",
                "cleaned_resume_length": len(cleaned_text),
                "ai_response": jan_response
            }), 200
        else:
            return jsonify({
                "error": "Jan AI request failed",
                "status_code": response.status_code,
                "response": response.text
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request to Jan AI timed out"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Could not connect to Jan AI endpoint"}), 503
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/health', methods=['GET']) def health_check(): return {"status": "ok", "message": "Bridge is healthy"}, 200


if __name__ == '__main__':
    print("Starting Flask bridge server on port 5000...")
    print(f"Forwarding requests to Jan AI at {JAN_AI_ENDPOINT}")
    app.run(host='0.0.0.0', port=5000, debug=True)
