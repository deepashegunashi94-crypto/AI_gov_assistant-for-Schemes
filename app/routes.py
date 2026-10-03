import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def create_app():

    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/chat", methods=["POST"])
    def chat():

        try:
            data = request.get_json()

            message = data.get("message", "").strip()
            language = data.get("language", "en")

            if not message:
                return jsonify({
                    "response": "Please enter a message."
                }), 400

            language_names = {
                "en": "English",
                "hi": "Hindi",
                "kn": "Kannada"
            }

            selected_language = language_names.get(
                language,
                "English"
            )

            system_prompt = f"""
You are a professional Government Services AI Assistant.

Your purpose is to help users with:

- Government jobs
- Government schemes
- Scholarships
- Government benefits
- Eligibility information
- Required documents
- Application procedures
- Official government portals

The user selected {selected_language}.

Rules:

1. Reply in {selected_language}.
2. Speak naturally and conversationally.
3. Do not make the user fill out a large form.
4. Ask questions naturally when information is needed.
5. Be friendly, clear and professional.
6. Keep answers easy to understand.
7. Do not invent government schemes or eligibility rules.
8. Do not invent application links.
9. For information that requires current official verification,
   clearly tell the user that official government sources should
   be checked.
10. Personalize responses using information the user provides.
"""

            completion = client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],

                temperature=0.3,
                max_tokens=700
            )

            answer = completion.choices[0].message.content

            return jsonify({
                "response": answer
            })

        except Exception as e:

            print("ERROR:", e)

            return jsonify({
                "response":
                    "Sorry, something went wrong. "
                    "Please try again."
            }), 500

    return app