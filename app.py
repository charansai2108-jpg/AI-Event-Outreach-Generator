from flask import Flask, render_template, request
from groq import Groq
from dotenv import load_dotenv
import resend
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# API Keys
groq_api_key = os.getenv("GROQ_API_KEY")
resend.api_key = os.getenv("RESEND_API_KEY")

# Groq Client
client = Groq(
    api_key=groq_api_key
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():

    # Form Data
    name = request.form["name"]
    email = request.form["email"]

    event_type = request.form["event_type"]
    event_title = request.form["event_title"]
    venue = request.form["venue"]
    date = request.form["date"]
    notes = request.form["notes"]
    sender = request.form["sender"]

    # AI Prompt
    prompt = f"""
Write a professional invitation email.

Recipient Name: {name}

Event Type: {event_type}
Event Title: {event_title}
Venue: {venue}
Date: {date}

Additional Notes:
{notes}

Requirements:
- Include subject line
- Include greeting
- Mention event title
- Mention venue
- Mention date
- Mention additional notes
- Professional closing
- Sign off using sender name: {sender}

Generate only the email body.
"""

    try:

        # Generate Email using Groq
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

        # Send Email using Resend
        try:

            resend.Emails.send(
                {
                    "from": "onboarding@resend.dev",
                    "to": [email],
                    "subject": f"Invitation: {event_title}",
                    "html": generated_email.replace("\n", "<br>")
                }
            )

            status = f"Email sent successfully to {email}"

        except Exception as email_error:

            status = f"Email sending failed: {str(email_error)}"

    except Exception as ai_error:

        generated_email = "Failed to generate email."
        status = f"AI Error: {str(ai_error)}"

    return render_template(
        "result.html",
        email_content=generated_email,
        status=status
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )