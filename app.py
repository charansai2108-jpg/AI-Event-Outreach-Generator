from flask import Flask, render_template, request
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Gemini API Setup
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# # Gemini Model
# model = genai.GenerativeModel("gemini-1.5-flash")

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Generate and Send Email
@app.route('/generate', methods=['POST'])
def generate():

    name = request.form['name']
    email = request.form['email']
    event = request.form['event']

    prompt = f"""
    Write a professional invitation email.

    Recipient Name: {name}

    Event: {event}

    Include:
    - Subject line
    - Greeting
    - Invitation message
    - Professional closing

    Sign off as:
    Charan Sai
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    generated_email = response.choices[0].message.content

    return render_template(
        'result.html',
        email_content=generated_email
    )

# Run App
if __name__ == '__main__':
    app.run(debug=True)