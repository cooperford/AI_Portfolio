from django.test import TestCase
from django.urls import reverse


class PortfolioPageTests(TestCase):
    def test_main_pages_load(self):
        urls = [
            reverse('portfolio:home'),
            reverse('portfolio:about'),
            reverse('portfolio:projects'),
            reverse('portfolio:skills'),
            reverse('portfolio:resume'),
            reverse('portfolio:contact'),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_project_detail_page_loads(self):
        response = self.client.get(reverse('portfolio:project_detail', args=['n8n-multi-agent-system']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'n8n Multi-Agent System')

    def test_video_project_detail_page_loads(self):
        response = self.client.get(reverse('portfolio:project_detail', args=['ai-video-creation']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Video Creation')

    def test_campus_skill_swap_project_detail_page_loads(self):
        response = self.client.get(reverse('portfolio:project_detail', args=['campus-skill-swap']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CampusSkillSwap')

    def test_langchain_chatbot_project_detail_page_loads(self):
        response = self.client.get(reverse('portfolio:project_detail', args=['langchain-chatbot']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'LangChain AI Chatbot')
        self.assertContains(response, reverse('portfolio:langchain_chatbot'))

    def test_langchain_chatbot_app_page_loads(self):
        response = self.client.get(reverse('portfolio:langchain_chatbot'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ask a question')

    def test_missing_project_detail_returns_404(self):
        response = self.client.get(reverse('portfolio:project_detail', args=['missing-project']))

        self.assertEqual(response.status_code, 404)
