import gradio as gr
import requests
import json , os
from datetime import datetime, timedelta
import numpy as np
from newsapi import NewsApiClient
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone,ServerlessSpec
from openai import OpenAI
import hashlib

# Replace with your actual API keys and environment
OPENAI_API_KEY = os.environ['GITHUB_TOKEN']
NEWS_API_KEY = os.environ['NEWS_API_KEY']
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
PINECONE_ENVIRONMENT = 'DEV'
PINECONE_INDEX_NAME = "company-news"

newsapi = NewsApiClient(api_key=NEWS_API_KEY)
model = SentenceTransformer('all-mpnet-base-v2')
pinecone = Pinecone(
        api_key=PINECONE_API_KEY
    )

client = OpenAI(
                        base_url="https://models.inference.ai.azure.com",
                        api_key=OPENAI_API_KEY
                    )
if PINECONE_INDEX_NAME not in pinecone.list_indexes().names():
    pinecone.create_index(PINECONE_INDEX_NAME, dimension=768, spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    ))
index = pinecone.Index(PINECONE_INDEX_NAME)

def get_news(company, days=15):
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)
    try:
        all_articles = newsapi.get_everything(q=company,
                                              from_param=from_date.strftime('%Y-%m-%d'),
                                              to=to_date.strftime('%Y-%m-%d'),
                                              language='en',
                                              sort_by='relevancy',
                                              page_size=1)
        articles = []
        if all_articles['status'] == 'ok':
            for article in all_articles['articles']:
                articles.append({
                    "title": article['title'],
                    "text": article['description'] if article['description'] else article['content'] if article['content'] else "No description/content available",
                    "date": article['publishedAt'][:10]
                })
        else:
            print(f"News API Error: {all_articles['message']}")
            return []
        return articles
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def embed_text(text):
    return model.encode(text).tolist()

def upsert_news_to_pinecone(company, news):
    vectors = []
    for article in news:
        embedding = embed_text(article['text'])
        metadata = {
            "title": article['title'],
            "date": article['date'],
            "company": company,
            "hashtags": article.get("hashtags", [])
        }
        vectors.append((str(hash(article['title']+article["date"])), embedding, metadata))
    if vectors:
        index.upsert(vectors=vectors)

def search_news(query, top_k=5):
    query_embedding = embed_text(query)
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return results

def analyze_sentiment(text):

    response = client.chat.completions.create(
                model="gpt-4o",
                temperature=1,
                max_tokens=4096,
                top_p=1,
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis and hashtag generation expert. \
                     Provide a sentiment score between -1 and 1, a short explanation, and 3-5 relevant hashtags (without the # character) in JSON format. \
                     Sample response: {\"score\": 0.5, \"explanation\": \"This text is very positive.\", \"hashtags\": [\"happy\", \"joyful\", \"excited\"]}"},
                    {"role": "user", "content": f"Analyze the following text: '{text}'."}
                ],
            )
    sentiment_response = response.choices[0].message.content
    try:
        sentiment_data = json.loads(sentiment_response)
        score = sentiment_data.get("score", np.nan)
        if score < -1:
            score = -1
        if score > 1:
            score = 1
        explanation = sentiment_data.get("explanation", "")
        hashtags = sentiment_data.get("hashtags", [])
    except json.JSONDecodeError:
        print(f"Could not decode JSON from: {sentiment_response}")
        score = np.nan
        explanation = ""
        hashtags = []

    return score, explanation, hashtags
def process_company(company):
    news = get_news(company)
    if not news:
        return np.nan, "Could not fetch news for this company.", [], []

    all_text = " ".join([item['text'] for item in news])
    if not all_text:
        return np.nan, "No text available for sentiment analysis", [], []
    score, explanation, hashtags = analyze_sentiment(all_text)
    for article in news:
        article["hashtags"] = hashtags
    upsert_news_to_pinecone(company, news)
    return score, explanation, hashtags, news

def search_and_display(query):
    search_results = search_news(query)
    formatted_results = []
    if search_results and search_results['matches']:
        for match in search_results['matches']:
            metadata = match['metadata']
            formatted_results.append(f"**{metadata['title']}** ({metadata['date']}):\n{match['score']}\n")
    else:
        formatted_results.append("No results found.")
    return "\n".join(formatted_results)

def display_filtered_news(filtered_news):
    display_string = ""
    if filtered_news:
        for item in filtered_news:
            display_string += f"**{item['company']}: {item['article']['title']}**\n"
            display_string += f"{item['article']['text']}\n"
            display_string += f"Hashtags: {', '.join(['#' + h for h in item['article']['hashtags']])}\n\n"
    else:
        display_string = "No news found with this hashtag."
    return display_string

def main(company1):
    all_results = {}
    companies = [company1]
    for company in companies:
        if company:
            score, explanation, hashtags, news = process_company(company)
            all_results[company] = {"score": score, "explanation": explanation, "hashtags": hashtags, "news": news}
    return all_results

iface = gr.Interface(
    fn=main,
    inputs=[
        gr.Textbox(label="Company 1")
    ],
    outputs=gr.JSON(label="Sentiment Analysis Results"),
    title="Company Sentiment Analyzer",
    description="Analyzes overall sentiment of combined news for given companies using OpenAI.",
)

search_interface = gr.Interface(
    fn=search_and_display,
    inputs=gr.Textbox(label="Search News"),
    outputs=gr.Markdown(label="Search Results"),
    title="News Search",
    description="Search for news articles in the vector database.",
)



demo = gr.TabbedInterface([iface, search_interface], ["Sentiment Analysis", "News Search"])

if __name__ == "__main__":
    demo.launch()
