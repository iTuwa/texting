import os
import textwrap
from pathlib import Path

from flask import Flask, request, jsonify, render_template
import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

app = Flask(__name__)


NIMS_KNOWLEDGE = textwrap.dedent(
    """
    SCHOOL NAME
    - New Ideal Model Schools (NIMS), Jalingo, Taraba State, Nigeria.

    LOCATION & CONTACT
    - Address: No. 12 Old Pantisawa Road, Jalingo, Taraba State, Nigeria.
    - Email: info@nimschools.org
    - Phone: +234 803 426 1645
    - Official website: https://nimschools.org/
    - Result Portal: https://portal.nimschools.org/

    IDENTITY & MISSION
    - Motto/mission phrases:
      - "Developing lifelong learning through quality education."
      - "For Your Best Education."
    - The school describes itself as one of the best schools in Jalingo Metropolitan Area and the best in Taraba State.

    ACADEMIC STAGES
    - Early Years Foundation Stage (EYFS):
      - Playgroup Lily
      - Pre-Nursery Jasmine
      - Pre-Nursery Tulip
      - Nursery Daisy
      - Nursery Ivy
      - Reception Sage
      - Reception Rose

    - Key Stage 1:
      - Year 1 Cheetah
      - Year 2 Dolphin
      - Year 2 Orca
      - Year 3 Bear

    - Key Stage 2:
      - Year 4 Blue Jays
      - Year 5 Barn Owls
      - Year 6 Zebra

    - Key Stage 3:
      - Year 7 Amber
      - Year 8 Ruby
      - Year 9 Beryl

    - Key Stage 4:
      - Year 10 Jasper
      - Year 11 Onyx
      - Year 12 Topaz

    LEARNING ENVIRONMENT & FACILITIES
    - Vibrant learning environment with engaged students.
    - State-of-the-art facilities and modern classrooms with up-to-date technology.
    - Focus on academic and personal growth.

    EXTRACURRICULAR ACTIVITIES
    - The school emphasizes holistic development through sports and arts.
    - Example activities mentioned:
      - Art gallery
      - Architectural design
      - And many more extracurricular options.

    ADMISSIONS (MERIT-BASED)
    - Admissions are granted purely on merit.
    - Admission for 2025 is advertised as open on the website.

    ADMISSION APPLICATION MODES
    - Online Application:
      - Applicants can submit their application digitally through the secure online portal.
    - Offline Application:
      - Applicants can download a printable admission form (PDF) from the website
        and submit a hard copy at the admissions office.

    ADMISSION PROCESS (TYPICAL STEPS)
    1. Application is reviewed by the school.
    2. Shortlisted applicants sit for a written examination.
    3. Successful candidates proceed to an oral interview.
    4. After a successful interview, the applicant receives an admission letter
       and a unique student ID for use throughout their time at the school.

    ADMISSION FORM SECTIONS
    - Section A: Personal Data.
    - Section B: Parents/Guardians Details.
    - Section C: Current/Previous School.

    KEY STAFF & ROLES (SELECTED)
    - Principal / Head of Schools: Mr. Adebanjo Oluwafemi
      - Over 15 years of experience in education.
      - Background in Mathematics, Statistics, and educational leadership.
      - Experience in both Nigerian and British curricula and Cambridge assessment.

    - Vice Principal Academic: Mrs. Ifeoma Victoria Onwuka
      - Focus on academic excellence, curriculum development, and teacher effectiveness.

    - Vice Principal Special Duties: Mr. David Kennedy
      - Oversees daily operations, resources, and ensures a safe and organized environment.

    - Art Teacher: Mr. Baajon Cyracus Michael
      - Delivers engaging art lessons (drawing, painting, sculpture) and teaches art history and appreciation.

    - Home Room Teachers (examples):
      - Mr. Erul Basil – homeroom teacher responsible for academic and personal development,
        monitoring progress, behavior, and wellbeing.
      - Beatrice Filibus – homeroom teacher and Mathematics teacher for lower secondary,
        mentors Year 8 Ruby students and simplifies complex math concepts.
      - Samir Ishaka – homeroom teacher for Year 9 students, guiding and mentoring them
        academically and morally.

    - ICT Staff and E-Librarian: Samuel Oguche
      - Manages the schools digital resources and e-library.
      - Supports students and teachers with technological tools and e-learning.

    TESTIMONIALS (ALUMNI THEMES)
    - Alumni describe NIMS as:
      - The best school that has impacted them and their generation positively.
      - A place where they truly understood what education is about.
      - A school that made them more brilliant and competitive and guided them academically.

    EVENTS & PLANNERS
    - NIMS celebrates events such as Career Day 2025, highlighting inspiring career paths.
    - The school publishes term planners, for example a "Summer Term 2024/2025 Planner"
      available as a downloadable PDF on the website.

    IMPORTANT LIMITATIONS
    - The website pages reviewed do NOT clearly list tuition/school fees,
      detailed term dates, or full policy documents.
    - For those details, parents/guardians should contact the school directly via
      email or phone for the most up-to-date and accurate information.
    """
)


SYSTEM_PROMPT = f"""You are the NIMS School Information Bot.
You answer questions ONLY about New Ideal Model Schools (NIMS) in Jalingo, Taraba State, Nigeria.
Use ONLY the information contained in the knowledge base below. Do not invent new facts.
If you are not sure or the answer is not in the knowledge base, say you are not certain
and advise the user to contact the school directly at info@nimschools.org or
+234 803 426 1645.

Knowledge base:
{NIMS_KNOWLEDGE}
"""


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
GROQ_API_BASE = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")


def _fallback_answer(user_message: str) -> str:
    """Simple fallback if no API key is configured or the API call fails.

    This uses a very basic keyword search over the knowledge string and returns
    a short, safe answer instead of failing hard.
    """

    lower_msg = user_message.lower()

    if any(k in lower_msg for k in ["where", "address", "location"]):
        return (
            "New Ideal Model Schools (NIMS) is located at No. 12 Old Pantisawa Road, "
            "Jalingo, Taraba State, Nigeria. You can contact the school via "
            "info@nimschools.org or +234 803 426 1645."
        )

    if "contact" in lower_msg or "phone" in lower_msg or "email" in lower_msg:
        return (
            "You can reach NIMS at info@nimschools.org or by phone on "
            "+234 803 426 1645."
        )

    if "admission" in lower_msg or "apply" in lower_msg:
        return (
            "NIMS admissions are merit-based. You can apply online through the "
            "school's admission portal or offline by downloading and submitting "
            "the admission form at the school. After application review, shortlisted "
            "candidates sit for a written exam and then an oral interview."
        )

    return (
        "I am a demo version running without an AI key. I can only share basic "
        "information about NIMS. For detailed or up-to-date information, please "
        "contact the school via info@nimschools.org or +234 803 426 1645."
    )


def call_llm(messages):
    """Call a chat-completions style LLM API (Groq via OpenAI-compatible endpoint).

    Expects GROQ_API_KEY to be set. If not set or if the request fails, falls back
    to a safe, rule-based answer.
    """

    if not GROQ_API_KEY:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return _fallback_answer(last_user)

    base = (GROQ_API_BASE or "").rstrip("/")
    if base.endswith("/chat/completions"):
        url = base
    else:
        url = f"{base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 512,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        try:
            print("LLM error:", repr(exc))
            if "resp" in locals():
                print("LLM response text:", resp.text)
        except Exception:
            pass
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return _fallback_answer(last_user)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Build messages for the LLM
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # Optional short conversation history (last 10 turns)
    for m in history[-10:]:
        role = m.get("role")
        content = m.get("content")
        if role in ("user", "assistant") and isinstance(content, str):
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})

    reply = call_llm(messages)

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
