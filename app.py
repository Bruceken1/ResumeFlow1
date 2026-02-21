from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
import os
from datetime import datetime

from pdf_utils import extract_text_from_pdf, generate_optimized_pdf, generate_cover_letter_pdf
from llm_refiner import refine_resume, generate_cover_letter

app = FastAPI(title="ResumeFlow")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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