from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles 
from fastapi.templating import Jinja2Templates
import shutil
import os
from datetime import datetime

import resend

from pdf_utils import extract_text_from_pdf, generate_optimized_pdf, generate_cover_letter_pdf
from llm_refiner import refine_resume, generate_cover_letter

app = FastAPI(title="ResumeFlow")

# Serve static files (favicon, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")


# ====================== PAGES ======================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/features", response_class=HTMLResponse)
def features(request: Request):
    return templates.TemplateResponse("features.html", {"request": request})

@app.get("/how-it-works", response_class=HTMLResponse)
def how_it_works(request: Request):
    return templates.TemplateResponse("how-it-works.html", {"request": request})

@app.get("/pricing", response_class=HTMLResponse)
def pricing(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})

@app.get("/blog", response_class=HTMLResponse)
def blog(request: Request):
    return templates.TemplateResponse("blog.html", {"request": request})

@app.get("/support", response_class=HTMLResponse)
def support(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})


# ====================== CONTACT FORM ======================
@app.post("/send-message")
async def send_message(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    try:
        resend.api_key = os.getenv("RESEND_API_KEY")
        
        if not resend.api_key:
            return {"status": "error", "msg": "Email service not configured yet."}

        html_content = f"""
        <h2>New Contact Form Submission</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Message:</strong></p>
        <p style="background:#f9f9f9; padding:15px; border-left:4px solid #f38181;">
            {message.replace(chr(10), '<br>')}
        </p>
        <hr>
        <p style="color:#666; font-size:0.9em;">Sent from ResuMy Support Form</p>
        """

        r = resend.Emails.send({
            "from": "ResuMy <noreply@resend.dev>",
            "to": os.getenv("EMAIL_TO", "your-email@gmail.com"),
            "subject": f"New Message from {name}",
            "html": html_content,
            "reply_to": email
        })

        print(f"✅ Email sent successfully via Resend from {name} ({email})")
        return {"status": "success", "msg": "Thank you! Your message has been sent. We'll reply soon."}

    except Exception as e:
        print("❌ Resend error:", str(e))
        return {"status": "error", "msg": "Sorry, we couldn't send your message right now. Please try again."}


# ====================== AI ROUTES ======================
@app.post("/optimize/")
async def optimize_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(None)
):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = os.path.join(UPLOAD_DIR, f"input_{ts}.pdf")

    with open(input_path, "wb") as f:
        shutil.copyfileobj(resume.file, f)

    resume_text = extract_text_from_pdf(input_path)
    improved_text = refine_resume(resume_text, job_description)

    output_path = os.path.join(OUTPUT_DIR, f"optimized_{ts}.pdf")
    generate_optimized_pdf(improved_text, output_path)

    return FileResponse(output_path, filename="optimized_resume.pdf")


@app.post("/generate-cover/")
async def generate_cover(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = os.path.join(UPLOAD_DIR, f"cover_{ts}.pdf")

    with open(input_path, "wb") as f:
        shutil.copyfileobj(resume.file, f)

    resume_text = extract_text_from_pdf(input_path)
    cover_text = generate_cover_letter(resume_text, job_description)

    output_path = os.path.join(OUTPUT_DIR, f"cover_{ts}.pdf")
    generate_cover_letter_pdf(cover_text, output_path)

    return FileResponse(output_path, filename="cover_letter.pdf")
