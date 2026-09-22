# EduGenie — Google Gemini Powered Learning Assistant

EduGenie is a lightweight AI-powered educational assistant based on the supplied project documentation.

## Features

- Ask academic/general questions
- Explain complex concepts simply
- Generate 3-question MCQ quizzes
- Summarize educational passages
- Generate beginner → intermediate → advanced learning paths
- Responsive HTML/CSS frontend
- FastAPI REST backend
- Gemini API integration
- Optional LaMini-Flan-T5 local explanation model

## Project structure

```text
EduGenie/
├── main.py
├── ai_client.py
├── explanation_module.py
├── qna.py
├── quiz_module.py
├── summary_module.py
├── learning_path.py
├── requirements.txt
├── requirements-local.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── tests/
    └── test_app.py
```

## 1. Install Python

Use Python 3.10 or newer.

Check:

```bash
python --version
```

On Windows, if `python` does not work, try:

```bash
py --version
```

## 2. Open the project in VS Code

Open the `EduGenie` folder.

Then open:

**Terminal → New Terminal**

## 3. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure Gemini

Copy:

```text
.env.example
```

to:

```text
.env
```

Then put your API key in `.env`:

```env
GEMINI_API_KEY=your_real_key_here
GEMINI_MODEL=gemini-3.8-flash
USE_LOCAL_EXPLAINER=false
```

Do not upload `.env` to GitHub.

## 6. Run the application

```bash
uvicorn main:app --reload
```

You should see the server start on:

```text
http://127.0.0.1:8000
```

Open that address in your browser.

## 7. Test the application

### Browser

Try each tab:

1. Ask — `Which is the largest ocean?`
2. Explain — `Explain the Pythagorean theorem for a beginner.`
3. Summarize — paste a paragraph.
4. Quiz — provide a topic/passage.
5. Learn — `Learn SQL from beginner to advanced.`

### API documentation

FastAPI automatically provides:

```text
http://127.0.0.1:8000/docs
```

You can test `/qa`, `/explain`, `/quiz`, `/summarize`, and `/learn/recommendations` from Swagger UI.

### Health check

Open:

```text
http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok","service":"EduGenie"}
```

## 8. Optional local LaMini-Flan-T5 explanation

The supplied documentation describes LaMini-Flan-T5-783M as the local explanation model. Because downloading/loading a transformer model is much heavier than using the cloud API, it is optional in this implementation.

Install:

```bash
pip install -r requirements-local.txt
```

Then change `.env`:

```env
USE_LOCAL_EXPLAINER=true
```

The application will try the local model for `/explain` and fall back to Gemini if the local model cannot load.

## Troubleshooting

### `Gemini API key is not configured`

Check that `.env` exists in the same folder as `main.py` and contains:

```env
GEMINI_API_KEY=...
```

Restart the terminal/server after changing environment variables.

### Model/API errors

Check that the Gemini API key is active and that the model configured in `GEMINI_MODEL` is available to your account.

### Port already in use

Run:

```bash
uvicorn main:app --reload --port 8001
```

Then open:

```text
http://127.0.0.1:8001
```

### PowerShell activation blocked

If Windows PowerShell blocks activation, you can either use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

or configure PowerShell execution policy for your user account according to your organization's policy.

## Security

Treat the Gemini API key like a password. Never put it in frontend JavaScript or commit it to Git.

## Architecture

```text
Browser
   │
   ▼
HTML/CSS/JavaScript
   │
   │ POST JSON
   ▼
FastAPI
   │
   ├── /qa
   ├── /explain
   ├── /quiz
   ├── /summarize
   └── /learn/recommendations
   │
   ▼
Feature modules
   │
   ▼
Google Gemini API
   │
   ▼
AI response
   │
   ▼
Browser result
```
