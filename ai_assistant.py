from openai import OpenAI
import requests
from datetime import datetime, timedelta
import os 

class AI_Assistant:
    def __init__(self):
        self.companies = []
        self.news_subscriptions = {}
        self.sentiment_views = {}
        self.client = OpenAI(
                        base_url="https://models.inference.ai.azure.com",
                        api_key=os.environ["GITHUB_TOKEN"]
                    )

    def add_company(self, company_name):
        if company_name not in self.companies:
            self.companies.append(company_name)
            self.news_subscriptions[company_name] = []
            self.sentiment_views[company_name] = None

    def subscribe_news(self, company_name):
        if company_name in self.companies:
            news = self.fetch_latest_news(company_name)
            self.news_subscriptions[company_name].extend(news)

    def fetch_latest_news(self, company_name):
        api_key = os.environ.get("NEWS_API_KEY")
        if not api_key:
            raise ValueError("NEWS_API_KEY environment variable not set")
        
        url = f"https://newsapi.org/v2/everything?q={company_name}&apiKey={api_key}"
        response = requests.get(url)
        
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            return [article["title"] for article in articles]
        else:
            return []

    def create_sentiment_view(self, company_name):
        if company_name in self.companies:
            news = self.news_subscriptions[company_name]
            if news:               
                response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analysis model and helping Wealth Advisors to analyze the sentiment of the news articles.",
                    },
                    {
                        "role": "user",
                        "content": f"Analyze the sentiment of the following news articles: {news}"
                    }
                ],
                model="gpt-4o",
                temperature=1,
                max_tokens=4096,
                top_p=1
                )
                sentiment = response.choices[0].message.content
                self.sentiment_views[company_name] = sentiment
                return sentiment
        return None

    def get_sentiment_view(self, company_name):
        if company_name in self.companies:
            return self.sentiment_views[company_name]
        return None
