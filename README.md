# AI Portfolio

A Django portfolio site with project pages, an embedded CampusSkillSwap project, and an interactive LangChain chatbot powered by Google Gemini.

## Run Locally

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
.\.venv\Scripts\python.exe manage.py runserver
```

Then open http://127.0.0.1:8000/.

## Environment Variables

Create `LangChainProject1/.env` locally or set these variables in your deployment host:

- `GEMINI_API_KEY`: Google Gemini API key for the LangChain chatbot.
- `DJANGO_SECRET_KEY`: Secret key for Django production deployments.
- `DJANGO_DEBUG`: Use `False` in production.
- `DJANGO_ALLOWED_HOSTS`: Comma-separated allowed hosts, for example `.onrender.com`.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: Comma-separated trusted origins, for example `https://*.onrender.com`.

Never commit `.env` files or API keys.

## Render Deployment

Use Render's **Web Service** option.

This repo includes `.python-version` set to Python 3.14 for consistent Render builds.

Build command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

Start command:

```bash
gunicorn config.wsgi:application
```

Set `GEMINI_API_KEY` in Render's Environment tab. The included `render.yaml` can generate `DJANGO_SECRET_KEY` automatically for blueprint deploys.

## Pages

- Home: `/`
- About: `/about/`
- Projects: `/projects/`
- Project detail: `/projects/<project-slug>/`
- LangChain chatbot: `/projects/langchain-chatbot/app/`
- Skills: `/skills/`
- Resume: `/resume/`
- Contact: `/contact/`
