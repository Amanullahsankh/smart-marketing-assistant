import logging
from groq import Groq
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()
ai_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_email(our_name, our_url, our_services_text, client_data, client_summary):
    client_name = client_data.get("title", "the client")

    if isinstance(client_summary, dict):
        summary_str = client_summary.get("summary", str(client_summary))
    else:
        summary_str = str(client_summary)

    prompt = f"""
You are a professional B2B marketing email copywriter.

Write a personalized, formal but friendly outreach email with:
- A clear, catchy subject line.
- A professional and engaging email body (max 8 lines).
- A soft Call-To-Action at the end (like scheduling a quick call).

Details:
Our Company: {our_name} ({our_url})
Our Key Services:
{our_services_text}

Target Client: {client_name}
Client Summary:
{summary_str}

Format your reply as:
Subject: <short subject line>
Body:
<email body text>
"""
    try:
        response = ai_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        content = response.choices[0].message.content.strip()

        subject = ""
        body = ""

        if "Subject:" in content and "Body:" in content:
            parts = content.split("Body:", 1)
            subject = parts[0].replace("Subject:", "").strip()
            body = parts[1].strip()
        else:
            lines = content.split("\n", 1)
            subject = lines[0].replace("Subject:", "").strip()
            body = lines[1].strip() if len(lines) > 1 else content

        return {"subject": subject, "body": body}

    except Exception:
        logger.exception("Email generation failed for %s", client_name)
        return {
            "subject": f"Collaboration Opportunity with {our_name}",
            "body": (
                f"Dear {client_name},\n\n"
                f"We at {our_name} specialize in AI-driven solutions "
                "that help businesses grow.\n\n"
                "We would love to explore a potential collaboration.\n"
                "Would you be open to a short call this week?\n\n"
                f"Best Regards,\n{our_name} Team"
            )
        }