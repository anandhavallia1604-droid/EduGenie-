from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from explanation_module import explain_topic
from learning_path import get_learning_recommendations
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text


# =========================================================
# EduGenie FastAPI Application
# =========================================================

app = FastAPI(
    title="EduGenie",
    description="Google Gemini powered learning assistant",
    version="1.0.0",
)


# =========================================================
# Static Files & Templates
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

templates = Jinja2Templates(
    directory="templates"
)


# =========================================================
# Request Models
# =========================================================

class TextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=20000,
    )


class TopicRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )


class QuizRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=20000,
    )


# =========================================================
# Home Page
# =========================================================

@app.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        },
    )


# =========================================================
# Health Check
# =========================================================

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "EduGenie",
    }


# =========================================================
# Q&A
# =========================================================

@app.post("/qa")
async def qa(request: TextRequest):

    try:

        answer = answer_question(
            request.text
        )

        return {
            "answer": answer
        }

    except Exception as exc:

        # Print detailed error in terminal
        print("\n")
        print("=" * 60)
        print("EDUGENIE Q&A ERROR")
        print("=" * 60)
        print("Error type:", type(exc).__name__)
        print("Error message:", str(exc))
        print("=" * 60)
        print("\n")

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# Explain Concept
# =========================================================

@app.post("/explain")
async def explain(request: TopicRequest):

    try:

        explanation = explain_topic(
            request.topic
        )

        return {
            "topic": request.topic,
            "explanation": explanation,
        }

    except Exception as exc:

        print("\n")
        print("=" * 60)
        print("EDUGENIE EXPLANATION ERROR")
        print("=" * 60)
        print("Error type:", type(exc).__name__)
        print("Error message:", str(exc))
        print("=" * 60)
        print("\n")

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# Summarization
# =========================================================

@app.post("/summarize")
async def summarize(request: TextRequest):

    try:

        summary = summarize_text(
            request.text
        )

        return {
            "summary": summary
        }

    except Exception as exc:

        print("\n")
        print("=" * 60)
        print("EDUGENIE SUMMARY ERROR")
        print("=" * 60)
        print("Error type:", type(exc).__name__)
        print("Error message:", str(exc))
        print("=" * 60)
        print("\n")

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# Quiz Generation
# =========================================================

@app.post("/quiz")
async def quiz(request: QuizRequest):

    try:

        quiz_data = generate_quiz(
            request.text
        )

        return {
            "quiz": quiz_data
        }

    except Exception as exc:

        print("\n")
        print("=" * 60)
        print("EDUGENIE QUIZ ERROR")
        print("=" * 60)
        print("Error type:", type(exc).__name__)
        print("Error message:", str(exc))
        print("=" * 60)
        print("\n")

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# Learning Recommendations
# =========================================================

@app.post("/learn/recommendations")
async def recommendations(
    request: TopicRequest
):

    try:

        recommendation = (
            get_learning_recommendations(
                request.topic
            )
        )

        return {
            "topic": request.topic,
            "recommendation": recommendation,
        }

    except Exception as exc:

        print("\n")
        print("=" * 60)
        print("EDUGENIE LEARNING PATH ERROR")
        print("=" * 60)
        print("Error type:", type(exc).__name__)
        print("Error message:", str(exc))
        print("=" * 60)
        print("\n")

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# Value Error Handler
# =========================================================

@app.exception_handler(ValueError)
async def value_error_handler(
    request: Request,
    exc: ValueError,
):

    return await _json_error(
        400,
        str(exc),
    )


# =========================================================
# JSON Error Helper
# =========================================================

async def _json_error(
    status_code: int,
    message: str,
):

    return JSONResponse(
        status_code=status_code,
        content={
            "error": message
        },
    )


# =========================================================
# Run Application
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
    