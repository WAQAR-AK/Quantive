from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv # Uncomment in a real app
 import google.generativeai as genai # Uncomment in a real app

app = Flask(__name__)

# --- Placeholder for loading API Key securely ---
#In a real application, you would load your API key from environment variables
#'' using a library like python-dotenv.
 load_dotenv() # Uncomment in a real app
 GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Uncomment in a real app

 if not GEMINI_API_KEY: # Uncomment in a real app
     raise ValueError("GEMINI_API_KEY not found in environment variables") # Uncomment in a real app

# --- Placeholder for configuring the Gemini API ---
 genai.configure(api_key=GEMINI_API_KEY) # Uncomment in a real app
 model = genai.GenerativeModel('gemini-pro') # Uncomment and choose your model

# --- Placeholder for a dummy response ---
 This list simulates the response you would get from the Gemini API
# based on the prompt and input data. Replace with actual API call logic.
DUMMY_GENERATED_QUESTIONS = [
    {"text": "Describe your experience with Python programming.", "type": "textarea"},
    {"text": "What is your highest level of education?", "type": "text"},
    {"text": "Rate your ability to work effectively in a team (1-5).", "type": "number"},
    {"text": "Please list any relevant certifications you hold.", "type": "text"},
    {"text": "How do you handle constructive criticism?", "type": "textarea"},
    {"text": "Which of the following best describes your communication style?", "type": "radio", "options": ["Direct", "Indirect", "Detailed", "Concise"]},
    {"text": "Check the areas where you have professional experience:", "type": "checkbox", "options": ["Frontend Development", "Backend Development", "Database Management", "Cloud Computing"]},
    {"text": "Provide a link to your online portfolio or GitHub profile.", "type": "text"},
]


@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    """
    Receives form data and parameters, constructs a prompt for Gemini,
    and returns generated questions.
    """
    data = request.json

    form_title = data.get('title', '')
    instructions = data.get('instructions', '')
    parameters = data.get('parameters', []) # This is the array of {name, percentage}

    print(f"Received data for generation:")
    print(f"Title: {form_title}")
    print(f"Instructions: {instructions}")
    print(f"Parameters: {parameters}")

    # --- Prompt Construction Logic ---
    # This is where you build the prompt string for the Gemini API.
    # You need to format the title, instructions, and parameters clearly.
    # The prompt should guide Gemini to generate questions based on weightage
    # and request a specific output format (like JSON).

    parameter_list_str = "\n".join([f"- {p['name']}: {p['percentage']}% importance" for p in parameters])

    prompt = f"""
    Generate form questions for a hiring process based on the following criteria:

    **Form Title:** {form_title}
    **Special Instructions:** {instructions if instructions else 'None'}
    **Key Skills/Parameters and their importance weightage:**
    {parameter_list_str if parameter_list_str else 'No specific parameters provided.'}

    Generate at least 7 questions.
    Ensure the number and focus of the questions are proportional to the importance weightages of the parameters provided. For example, if 'Work Experience' has a high percentage, generate more questions related to work history and past projects. If 'Communication Skill' is 0%, generate no questions about communication.
    For each question, provide a suggested answer type from the following list: 'text', 'textarea', 'number', 'email', 'date', 'file', 'radio', 'checkbox'.
    If the type is 'radio' or 'checkbox', suggest a few relevant options.

    Format the output as a JSON array of objects, where each object has the keys 'text' (string), 'type' (string), and optionally 'options' (array of strings for radio/checkbox types).
    """

    print("\nConstructed Prompt:")
    print(prompt)

    # --- Gemini API Call (Commented Out) ---
    # In a real application, you would uncomment this section and make the API call.
    # try:
    #     response = model.generate_content(prompt)
    #     # Assuming the response contains a text field with the JSON string
    #     generated_questions_json_str = response.text
    #     # Parse the JSON string into a Python list/dictionary
    #     import json
    #     generated_questions = json.loads(generated_questions_json_str)
    #     print("\nGemini API Response (Parsed):")
    #     print(generated_questions)
    # except Exception as e:
    #     print(f"Error calling Gemini API: {e}")
    #     # Return an error response to the frontend
    #     return jsonify({"error": "Failed to generate questions from AI."}), 500

    # --- Return Dummy Response (for now) ---
    # Replace this with the actual 'generated_questions' variable
    # after implementing the Gemini API call.
    return jsonify(DUMMY_GENERATED_QUESTIONS)

if __name__ == '__main__':
    # To run this backend placeholder:
    # 1. Save it as backend_placeholder.py
    # 2. Make sure you have Flask installed (`pip install Flask`)
    # 3. Run from your terminal: `python backend_placeholder.py`
    # This will start a simple web server on http://127.0.0.1:5000/
    # Your frontend fetch call should target this URL.
    app.run(debug=True)
