from flask import Flask, render_template, request
from groq import Groq
from dotenv import load_dotenv

import os
import smtplib
from email.mime.text import MIMEText

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get API Keys
groq_api_key = os.getenv("GROQ_API_KEY")
email_user = os.getenv("EMAIL_USER")
email_password = os.getenv("EMAIL_PASSWORD")

# Initialize Groq Client
client = Groq(api_key=groq_api_key)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():

    # Get form data
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

    # Generate Email
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

    # Send Email via Gmail SMTP
    try:

        msg = MIMEText(generated_email)

        msg["Subject"] = f"Invitation: {event_title}"
        msg["From"] = email_user
        msg["To"] = email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(
            email_user,
            email_password
        )

        server.sendmail(
            email_user,
            email,
            msg.as_string()
        )

        server.quit()

        status = f"Email sent successfully to {email}"

    except Exception as e:

        status = f"Email sending failed: {str(e)}"

    return render_template(
        "result.html",
        email_content=generated_email,
        status=status
    )


if __name__ == "__main__":
    app.run(debug=True)