import openai
from langchain import LLMChain, OpenAI, PromptTemplate
import requests
from datetime import datetime, timedelta
import os 
from newsapi import NewsApiClient


class AI_Assistant:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.companies = []
        self.news_subscriptions = {}
        self.sentiment_views = {}
        self.client = OpenAI(
                        base_url="https://models.inference.ai.azure.com",
                        api_key=os.environ["GITHUB_TOKEN"],
                        model = "gpt-4o"
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
       
        newsapi = NewsApiClient(api_key=api_key)

        # /v2/top-headlines
        top_headlines = newsapi.get_top_headlines(q=company_name,
                                                language='en',
                                                country='in')
        print(top_headlines)
        return top_headlines


    def create_sentiment_view(self, company_name):
        if company_name in self.companies:
            news = self.news_subscriptions[company_name]
            if news:
                prompt = PromptTemplate(
                    input_variables=["news"],
                    template="Analyze the sentiment of the following news articles: {news}"
                )
                
                chain = LLMChain(llm=self.client, prompt=prompt)
                sentiment = chain.run(news=news)
                self.sentiment_views[company_name] = sentiment
                return sentiment
        return None

    def get_sentiment_view(self, company_name):
        if company_name in self.companies:
            return self.sentiment_views[company_name]
        return None
