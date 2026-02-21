import os
import re
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

client = InferenceClient(model=MODEL, token=HF_TOKEN)


def clean_text(text: str) -> str:
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'^\s*[-•*]\s*', '• ', text, flags=re.MULTILINE)
    text = text.replace('�', '')
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def refine_resume(resume_text: str, job_description: str | None = None) -> str:
    print("\n=== LLM STARTED ===")
    
    system = "You are a professional resume editor. Improve wording, use strong action verbs, make concise. Return clean text only. Use • for bullets. No markdown."

    user = f"""JOB DESCRIPTION (guide wording only):
{job_description or "None"}

ORIGINAL RESUME:
{resume_text[:7000]}

Rewrite the resume professionally. Keep all facts. Use clear sections and • bullets."""

    try:
        resp = client.chat_completion(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=1600,
            temperature=0.2
        )
        raw = resp.choices[0].message.content.strip()
        print("RAW LLM OUTPUT:\n", raw[:800])
        
        cleaned = clean_text(raw)
        print("=== LLM FINISHED ===\n")
        return cleaned
    except Exception as e:
        print("LLM ERROR:", e)
        return resume_text


def generate_cover_letter(resume_text: str, job_description: str, user_name: str = "Ken Kaibe") -> str:
    system = "Write a professional cover letter (320-420 words). Use only facts from resume. First person."
    user = f"""Job: {job_description}

Resume: {resume_text[:6000]}

Name: {user_name}

Write the full cover letter. Return only the text."""

    try:
        resp = client.chat_completion(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=1100,
            temperature=0.35
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print("Cover letter error:", e)
        return "Dear Hiring Manager,\n\nI am writing to apply...\n\nBest regards,\nKen Kaibe"