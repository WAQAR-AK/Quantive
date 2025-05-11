# server.py
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv # To load environment variables from .env
import google.generativeai as genai # Gemini API library
import json # To parse the JSON response from Gemini

# Load environment variables from .env file
# In Glitch, this reads from the .env secrets managed in the UI
load_dotenv()

app = Flask(__name__)

# --- Configure the Gemini API ---
# Load the API key from environment variables
# Use os.getenv to read the variable named GEMINI_API_KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    # If the API key is not found, print an error and return a server error response
    print("Error: GEMINI_API_KEY not found in environment variables.")
    # In a real application, you might want more robust error handling here.
    # For Glitch, ensure you've added the key in the .env secrets UI.
    # We'll add a check in the route handler as well.


# Configure the generative AI model (only if API key is available)
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Choose a suitable model. 'gemini-pro' is a good general-purpose model.
        # You might explore other models depending on your needs.
        # Check model availability and capabilities in the Gemini API documentation.
        model = genai.GenerativeModel('gemini-pro')
        print("Gemini model configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini model: {e}")
        model = None # Set model to None if configuration fails


@app.route('/')
def index():
    """Basic route to confirm the backend is running."""
    return "AI Form Builder Backend is running!"

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    """
    Receives form data and parameters from the frontend,
    constructs a prompt for Gemini, calls the API,
    and returns the generated questions.
    """
    # Check if the Gemini model was configured successfully
    if not model:
        print("Gemini API not configured. Cannot generate questions.")
        return jsonify({"error": "AI service is not available. Please check backend configuration."}), 503 # Service Unavailable

    try:
        data = request.json

        form_title = data.get('title', '')
        instructions = data.get('instructions', '')
        parameters = data.get('parameters', []) # This is the array of {name, percentage}

        print(f"Received data for generation:")
        print(f"Title: {form_title}")
        print(f"Instructions: {instructions}")
        print(f"Parameters: {parameters}")

        # --- Prompt Construction Logic ---
        # This prompt is designed to guide Gemini to generate questions
        # based on the provided title, instructions, and parameters,
        # considering the weightage and outputting in a specific JSON format.

        parameter_list_str = "\n".join([f"- {p['name']}: {p['percentage']}% importance" for p in parameters])

        # Determine minimum number of questions. Default to 7 if not specified in instructions.
        # This is a basic attempt to parse instructions. More complex parsing might be needed.
        min_questions = 7
        import re
        match = re.search(r'generate\s+(\d+)\s+questions', instructions, re.IGNORECASE)
        if match:
            try:
                min_questions = int(match.group(1))
                print(f"Found minimum questions in instructions: {min_questions}")
            except ValueError:
                print("Could not parse number of questions from instructions, defaulting to 7.")
                min_questions = 7 # Fallback if parsing fails


        prompt = f"""
        You are an AI assistant that generates questions for a form, specifically for hiring or applications.
        Generate form questions based on the following criteria and priorities:

        **Form Title:** {form_title}
        **Special Instructions:** {instructions if instructions else 'None provided.'}
        **Key Skills/Parameters and their importance weightage (Total weightage is 100%):**
        {parameter_list_str if parameter_list_str else 'No specific parameters provided. Generate general questions relevant to the title and instructions.'}

        Generate exactly {min_questions} questions, or more if needed to cover the parameters adequately.
        Ensure the number and focus of the questions are proportional to the importance weightages of the parameters provided. For example, if 'Work Experience' has a 50% weightage, approximately half of the generated questions should focus on work history, past projects, roles, etc. If a parameter has 0% weightage, generate no questions related to that parameter.

        For each question, provide a suggested answer type from the following list: 'text', 'textarea', 'number', 'email', 'date', 'file', 'radio', 'checkbox'.
        If the suggested type is 'radio' or 'checkbox', provide a reasonable list of relevant options as an array of strings.

        Format the output strictly as a JSON array of objects. Each object must have the following keys:
        - 'text': The question text (string).
        - 'type': The suggested answer type (string from the allowed list).
        - 'options': An array of strings (only required for 'radio' and 'checkbox' types). If the type is not 'radio' or 'checkbox', this key should be omitted or be an empty array.

        Example JSON format:
        [
          {{
            "text": "What is your full name?",
            "type": "text"
          }},
          {{
            "text": "Describe your previous work experience.",
            "type": "textarea"
          }},
          {{
            "text": "What is your preferred contact email?",
            "type": "email"
          }},
           {{
            "text": "Which programming languages are you proficient in?",
            "type": "checkbox",
            "options": ["Python", "JavaScript", "Java"]
          }}
        ]
        Ensure the output is valid JSON and contains only the array of question objects. Do not include any introductory or concluding text outside the JSON array.
        """

        print("\nConstructed Prompt:")
        print(prompt)

        # --- Call the Gemini API ---
        # The model.generate_content method sends the prompt to Gemini.
        # We expect the response to contain the generated JSON string in the 'text' attribute.
        response = model.generate_content(prompt)

        # Assuming the response text contains the JSON string
        # Use strip() to remove potential leading/trailing whitespace or markdown ticks
        generated_questions_json_str = response.text.strip()

        # Clean up potential markdown formatting around JSON (e.g., ```json ... ```)
        if generated_questions_json_str.startswith('```json'):
            generated_questions_json_str = generated_questions_json_str[len('```json'):].strip()
        if generated_questions_json_str.endswith('```'):
            generated_questions_json_str = generated_questions_json_str[:-len('```')].strip()


        # Attempt to parse the JSON string
        generated_questions = json.loads(generated_questions_json_str)

        print("\nGemini API Response (Parsed):")
        print(generated_questions)

        # Return the parsed questions as a JSON response to the frontend
        return jsonify(generated_questions)

    except json.JSONDecodeError as e:
        # Handle cases where Gemini's response is not valid JSON
        print(f"JSON parsing error: {e}")
        # Attempt to print the raw response text if available
        raw_response_text = "N/A"
        if 'response' in locals() and hasattr(response, 'text'):
             raw_response_text = response.text
        print(f"Raw response text: {raw_response_text}")
        return jsonify({"error": f"Failed to parse AI response. The AI did not return valid JSON. Raw response: {raw_response_text}"}), 500
    except Exception as e:
        # Handle other potential errors during the process
        print(f"An error occurred: {e}")
        return jsonify({"error": f"An error occurred during question generation: {e}"}), 500

if __name__ == '__main__':
    # Glitch typically runs your server automatically based on project setup.
    # If you need to run manually in the console, use:
    # python server.py
    # The host='0.0.0.0' makes the server accessible externally, which is needed on Glitch.
    # debug=True is useful for development to see errors, but set to False for production.
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)
