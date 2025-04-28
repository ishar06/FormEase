
# 📋 Full Plan for Building **FormEase** (in 3 Days)

## 🛠 Technology Stack (with reasons)

| Functionality        | Libraries/Frameworks      | Why Use Them? |
|----------------------|----------------------------|---------------|
| Core Web App         | Django                     | Quick backend development, powerful ORM, easy admin panel. |
| AI Integration       | Ollama Python SDK          | Run LLMs locally for private, fast AI responses. |
| File Handling (PDF, DOCX, PPTX) | PyMuPDF (fitz), python-docx, python-pptx | Fast parsing of documents. |
| Frontend             | HTML5 + Bootstrap5         | Rapid UI development, responsive, professional look. |
| Forms Handling       | Django Forms               | Easy form building and validation. |
| Asynchronous Tasks (optional) | Celery + Redis | For heavy LLM queries (optional if time). |
| User Authentication (optional) | Django Auth | Ready-made login/signup system if needed. |
| Reminder Notifications (bonus) | Django-Q (Optional) | Background task scheduler for reminders. |

---

# 🗓 3-Day Plan (4–5 Hours/Day)

---

## ✅ **Day 1: Setup + PDF Summary + Form Filling Assistant**

### ⏳ 0–1 Hour: Project Setup
- Set up virtual environment
- Install Django, Ollama, fitz (PyMuPDF), python-docx, python-pptx

  ```bash
  pip install django ollama pymupdf python-docx python-pptx
  ```

- Start Django project:

  ```bash
  django-admin startproject formease
  cd formease
  python manage.py startapp core
  ```

- Basic settings: Add 'core' to `INSTALLED_APPS`, set up static files, configure media files (for file uploads).

---
  
### ⏳ 1–3 Hour: PDF Summary Feature

- Frontend:
  - Create a simple page where users upload PDFs.

- Backend:
  - Read the uploaded PDF using PyMuPDF.
  - Extract all text.
  - Send extracted text to Ollama to **summarize** using a prompt like:  
    `"Summarize the following text in bullet points: <text>"`

  Example backend function:
  ```python
  import fitz
  from ollama import Client

  def summarize_pdf(file_path):
      doc = fitz.open(file_path)
      text = ""
      for page in doc:
          text += page.get_text()

      client = Client()
      summary = client.chat("llama3", messages=[{"role": "user", "content": f"Summarize: {text}"}])
      return summary['message']['content']
  ```

---
  
### ⏳ 3–5 Hour: Form Filling Assistant

- Frontend:
  - Create a page with a basic form: Name, Email, Address, etc.

- Backend:
  - Allow users to upload a text file or give text input.
  - Use Ollama to parse data.
    - Example prompt: `"Extract name, email, address from the following: <text>"`
  - Autofill Django form fields based on extracted info.

---
  
## ✅ **Day 2: Q&A over Files + Resume Builder**

### ⏳ 0–2 Hour: Q&A Over PDFs, DOCs, PPTs

- Frontend:
  - Upload file + input box for questions.

- Backend:
  - Use python-docx, python-pptx, and pymupdf to extract text depending on file type.
  - When user asks a question, send prompt to Ollama:

    ```
    Based on the following document, answer: <Question>  
    Document: <Extracted Text>
    ```

- Return answer to frontend.

---

### ⏳ 2–5 Hour: Resume/CV Builder

- Frontend:
  - Simple multi-step form to collect:
    - Personal Info
    - Education
    - Experience
    - Skills

- Backend:
  - When user submits, **send structured input to Ollama**:
  
    ```
    Create a professional resume using the following details: <User Info>
    ```

- Ollama generates text.
- Optional: Generate PDF (using xhtml2pdf or ReportLab).

  Example libraries:
  ```bash
  pip install xhtml2pdf
  ```

- Allow users to download the generated resume.

---

## ✅ **Day 3: To-Do List + Polishing + Final Testing**

### ⏳ 0–2 Hour: To-Do List & Reminder Assistant

- Models:
  - Create a `Task` model: `title`, `description`, `due_date`, `completed`.

- Views:
  - CRUD operations: Add task, mark as complete, delete task.

- AI:
  - Accept natural language tasks like:  
    `"Remind me to submit project tomorrow at 5 PM."`
  - Ollama parses into structured fields.

    ```
    Extract task title, date, and time from: <input>
    ```

- Bonus: Set up Django-Q for actual reminders (optional).

---

### ⏳ 2–5 Hour: Final Touches

- UI polishing using Bootstrap
- Test all flows:
  - PDF upload
  - Q&A
  - Resume Builder
  - Form Autofill
  - To-Do Task creation

- Deploy locally or on Render/Heroku (if extra time).
- Record small demos for LinkedIn posts/hackathon.

---

# 🧠 Priorities to Stick to Plan
- **Focus on 1 feature at a time** — finish before jumping.
- **Always test small code pieces immediately.**
- **Hardcode prompts to Ollama first; optimize later.**
- **Frontend can be minimal. Backend must work smoothly.**

---

# 🔥 Summary of Feature Activation Steps
| Feature                   | When Activated  |
|----------------------------|-----------------|
| Basic Django app setup     | Day 1, Hour 1    |
| PDF Summarizer             | Day 1, Hour 3    |
| Form Filling               | Day 1, Hour 5    |
| Q&A System                 | Day 2, Hour 2    |
| Resume Builder             | Day 2, Hour 5    |
| To-Do List Assistant       | Day 3, Hour 2    |
| Final Testing and Polish   | Day 3, Hour 5    |

---

# 🛠 Team GitHub Workflow (Best Practice)

## 1. Everyone Clones the Repo (Once)

Each team member should run:

```bash
git clone https://github.com/yourorg/your-repo-name.git
```

> You now have a local copy of the repository.

---

## 2. Always Create Your Own Branch for Features

Before starting any new feature or fixing a bug:

```bash
git checkout -b feature/your-feature-name
```

**Example:**

```bash
git checkout -b feature/login-page
```

🚫 **Never work directly on the `main` branch!**

🔥 **Golden Rule:**  
`1 feature = 1 branch`

---

## 3. Work on Your Branch

- Write code  
- Add files  
- Test locally  

---

## 4. Stage and Commit Your Work

```bash
git add .
git commit -m "Added login page UI"
```

✅ Make **small**, **meaningful** commits!

---

## 5. Before Pushing, Always Pull Latest `main`

### Step 1: Switch to `main` and pull the latest changes

```bash
git checkout main
git pull origin main
```

### Step 2: Go back to your feature branch and merge `main`

```bash
git checkout feature/your-feature-name
git merge main
```

✅ This ensures your branch is up-to-date with the team's work.

---

## 6. Push Your Feature Branch to GitHub

```bash
git push origin feature/your-feature-name
```

---

## 7. Create a Pull Request (PR)

1. Go to GitHub.
2. Create a **New Pull Request**:  
   `feature/your-feature-name ➔ main`
3. Request review from teammates.
4. Once approved, **merge** it into `main`.

🛡️ **Protect the `main` branch**: Only merge via Pull Requests — never push directly!

---

## 📈 Team Working Cycle Looks Like This:

```
Everyone ➜ Creates their own branch  
         ➜ Works individually  
         ➜ Pushes their branch  
         ➜ Creates Pull Request  
         ➜ Team reviews  
         ➜ Merge to main
```

---

## ⚡ Very Important Things

| Rule                            | Why                                |
|---------------------------------|-------------------------------------|
| Always Pull Before You Start    | Avoid conflicts                     |
| Always Work on Your Own Branch  | Parallel work possible              |
| Small Commits                   | Easy to debug later                 |
| Pull Request + Code Review      | Better quality and teamwork         |
| Do Not Push Directly to `main`  | Protect the main code               |
```

Would you like me to save this as a downloadable `.md` file for you?

