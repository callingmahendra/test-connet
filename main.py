from ai_assistant import AI_Assistant

api_key = "your_openai_api_key"
assistant = AI_Assistant(api_key)

# Add companies to the research list
assistant.add_company("Infosys")

# Subscribe to the latest news for the companies
assistant.subscribe_news("Infosys")
# Create sentiment views for the companies
sentiment_a = assistant.create_sentiment_view("Infosys")

# Print the sentiment views
print(f"Sentiment for Infosys: {sentiment_a}")
