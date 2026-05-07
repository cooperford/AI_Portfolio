from django.http import Http404
from django.shortcuts import render

from .langchain_chatbot import ChatbotUnavailableError, ask_chatbot

PROJECTS = [
    {
        'slug': 'n8n-multi-agent-system',
        'title': 'n8n Multi-Agent System',
        'summary': 'Built a multi-agent system in n8n Cloud using drag-and-drop nodes.',
        'description': 'Built a multi-agent system in n8n Cloud using drag-and-drop nodes. The Orchestrator workflow calls four agent workflows (Intake, Pricing, Scheduling, Comms) and returns a final business-ready output.',
        'technologies': ['n8n Cloud', 'Automation', 'Multi-agent workflows', 'Google Sheets', 'Gmail'],
        'image': 'portfolio/img/n8n-project.png',
    },
    {
        'slug': 'ai-video-creation',
        'title': 'AI Video Creation',
        'summary': 'Recreated a famous movie scene with a twist using Nano Banana.',
        'description': 'Recreated a famous movie scene with a twist using Nano Banana. Used multiple well structured prompts to get exactly what I wanted from the tool.',
        'technologies': ['Nano Banana', 'Prompt engineering', 'AI video', 'Creative AI'],
        'video': 'portfolio/video/video-ai-project.mp4',
    },
    {
        'slug': 'campus-skill-swap',
        'title': 'CampusSkillSwap',
        'summary': 'Built a Django marketplace where students can post skills, browse peer offerings, book sessions, and leave reviews.',
        'description': 'CampusSkillSwap is a student-focused skill exchange platform built with Django. The app lets users create accounts, post skills they can teach, search and filter available skills, request bookings, manage incoming requests, maintain profiles, and leave ratings and reviews to build trust across the campus community.',
        'technologies': ['Django', 'Python', 'SQLite', 'Bootstrap 5', 'Crispy Forms', 'HTML', 'CSS'],
        'preview_label': 'Django Marketplace App',
        'source_url': 'https://github.com/cooperford/CampusSkillSwap',
        'live_preview_url': 'http://127.0.0.1:8001/',
        'highlights': [
            'User registration, login, logout, and profile management.',
            'Skill posting CRUD with categories, pricing, availability, and contact preferences.',
            'Search and category filtering for browsing available skills.',
            'Booking request workflow with pending, approved, rejected, completed, and cancelled statuses.',
            'Review and rating system with duplicate-review protection.',
        ],
    },
    {
        'slug': 'langchain-chatbot',
        'title': 'LangChain AI Chatbot',
        'summary': 'Built a Gemini-powered LangChain assistant that answers user questions with concise, professional responses.',
        'description': 'Used LangChain framework to build my own chatbot powered by Google Gemini in Python.',
        'technologies': ['Python', 'Django', 'LangChain', 'Google Gemini', 'Generative AI'],
        'preview_label': 'Interactive LangChain Chatbot',
        'app_url_name': 'portfolio:langchain_chatbot',
        'highlights': [
            'Wraps the original LangChain agent in a reusable Django service.',
            'Keeps a short chat history in the visitor session for conversational context.',
            'Handles missing API keys or dependencies with a clear setup message instead of a crash.',
            'Provides a browser-based interface so anyone visiting the site can use the project.',
        ],
    },
]

SKILLS = [
    'Microsoft Excel',
    'Python',
    'Python-based web scraping',
    'Data analysis',
    'Research support',
    'Tableau',
    'R',
    'UI Path',
    'Written reporting',
    'Peer tutoring',
    'Communication',
    'Problem solving',
]


def home(request):
    return render(request, 'portfolio/home.html', {'featured_projects': PROJECTS[:2]})


def about(request):
    return render(request, 'portfolio/about.html')


def projects(request):
    return render(request, 'portfolio/projects.html', {'projects': PROJECTS})


def project_detail(request, slug):
    project = next((project for project in PROJECTS if project['slug'] == slug), None)

    if project is None:
        raise Http404('Project not found')

    return render(request, 'portfolio/project_detail.html', {'project': project})


def langchain_chatbot(request):
    history = request.session.get('langchain_chat_history', [])
    error = None

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        if user_message:
            try:
                reply = ask_chatbot(history, user_message)
            except ChatbotUnavailableError as exc:
                error = str(exc)
            except Exception:
                error = 'The chatbot could not answer right now. Please try again in a moment.'
            else:
                history = history + [
                    {'role': 'user', 'content': user_message},
                    {'role': 'assistant', 'content': reply},
                ]
                history = history[-12:]
                request.session['langchain_chat_history'] = history
                request.session.modified = True

    if request.GET.get('reset') == '1':
        history = []
        request.session['langchain_chat_history'] = history
        request.session.modified = True

    return render(
        request,
        'portfolio/langchain_chatbot.html',
        {
            'history': history,
            'error': error,
        },
    )


def skills(request):
    return render(request, 'portfolio/skills.html', {'skills': SKILLS})


def resume(request):
    return render(request, 'portfolio/resume.html')


def contact(request):
    return render(request, 'portfolio/contact.html')
