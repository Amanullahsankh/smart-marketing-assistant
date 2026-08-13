import logging
from ai_utils import generate_ai_response
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

def filter_icp(our_services_text, client_summary):
    """
    Uses LLM to strictly determine if the target client matches our ICP.
    Returns True if fit, False if not.
    """
    if isinstance(client_summary, dict):
        summary_str = client_summary.get("summary", str(client_summary))
    else:
        summary_str = str(client_summary)
        
    prompt = f"""
You are an expert B2B sales development representative qualifying leads.

OUR SERVICES:
{our_services_text}

TARGET COMPANY PROFILE:
{summary_str}

TASK:
Analyze if the Target Company can directly and realistically benefit from Our Services.
Reject irrelevant leads strictly. For example:
- Reject Banks unless there is a clear fintech/data use case.
- Reject Healthcare/Hospitals unless there is a clear data/AI/tech use case.
- Reject random industries where our services provide no immediate tech value.

Respond strictly with "YES" if they are a strong fit, or "NO" if they are not a fit.
Do not explain your reasoning. Just output YES or NO.
"""
    try:
        response = generate_ai_response(
            prompt=prompt,
            model="llama-3.1-8b-instant",
            max_tokens=10,
            temperature=0.1,
            system_prompt="You are a strict lead qualifier. Output only YES or NO."
        )
        return "YES" in response.upper()
    except Exception as e:
        logger.error(f"ICP filtering failed: {e}")
        return True # Default to True on failure so we don't drop leads unnecessarily

def generate_email(our_name, our_url, our_services_text, client_data, client_summary):
    client_name = client_data.get("title", "the client")

    if isinstance(client_summary, dict):
        summary_str = client_summary.get("summary", str(client_summary))
    else:
        summary_str = str(client_summary)

    prompt = f"""
You are an elite, highly-paid B2B copywriter. Your goal is to write a hyper-personalized, high-converting outreach email.

STEP 6: EMAIL GENERATION (ADVANCED)

INPUT DATA:
Our Company: {our_name} ({our_url})
Our Services: {our_services_text}

Target Client: {client_name}
Target Client Profile: {summary_str}

STRICT INSTRUCTIONS:
1. Context First: Differentiate the Target Company's specific industry based on their profile.
2. Pinpoint Pain: Identify ONE specific, painful problem they realistically face in that industry.
3. Map Solution: Map Our Services directly to solving that exact pain point.
4. Concrete Value: Provide ONE clear, practical benefit (not generic).
5. Length limit: 120-180 words max.

REQUIRED EMAIL STRUCTURE:
1. Personalized Opening: Mention their specific company name and industry context immediately.
2. ONE Specific Pain Point: Bring up the industry-specific problem explicitly.
3. Solution Mapping: Explain exactly how our tech/services solve it.
4. Clear Benefit: State the practical outcome.
5. Simple CTA: A soft, low-friction question to gauge interest (e.g., "Open to a brief chat next week?").

FORBIDDEN WORDS & PHRASES (DO NOT USE THESE EVER):
- "optimize operations"
- "drive growth"
- "enhance efficiency"
- "synergy"
- "I came across your company"
- "Hope this email finds you well"
- "streamline processes"

VARIABILITY & TONE:
Must feel human-written. Do not sound like a standard AI template. 
Vary your opening line. Keep it concise.

Format your reply exactly as:
Subject: [Short, highly specific subject line relevant to their industry]
Body:
[Email body here]
"""
    try:
        content = generate_ai_response(
            prompt=prompt,
            model="llama-3.3-70b-versatile",
            max_tokens=350,
            temperature=0.5,
            system_prompt="You are a professional B2B marketing email copywriter."
        )

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