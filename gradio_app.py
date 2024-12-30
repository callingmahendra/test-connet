import gradio as gr
from ai_assistant import AI_Assistant

assistant = AI_Assistant()

def add_company(company_name):
    assistant.add_company(company_name)
    return f"Company {company_name} added."

def subscribe_news(company_name):
    assistant.subscribe_news(company_name)
    return f"Subscribed to news for {company_name}."

def create_sentiment_view(company_name):
    sentiment = assistant.create_sentiment_view(company_name)
    return sentiment if sentiment else f"No sentiment view available for {company_name}."

def get_sentiment_view(company_name):
    sentiment = assistant.get_sentiment_view(company_name)
    return sentiment if sentiment else f"No sentiment view available for {company_name}."

with gr.Blocks() as demo:
    with gr.Row():
        company_name_input = gr.Textbox(label="Company Name")
        add_company_button = gr.Button("Add Company")
        subscribe_news_button = gr.Button("Subscribe News")
        create_sentiment_button = gr.Button("Create Sentiment View")
        get_sentiment_button = gr.Button("Get Sentiment View")
    
    add_company_output = gr.Textbox(label="Add Company Output")
    subscribe_news_output = gr.Textbox(label="Subscribe News Output")
    create_sentiment_output = gr.Textbox(label="Create Sentiment View Output")
    get_sentiment_output = gr.Textbox(label="Get Sentiment View Output")
    
    add_company_button.click(add_company, inputs=company_name_input, outputs=add_company_output)
    subscribe_news_button.click(subscribe_news, inputs=company_name_input, outputs=subscribe_news_output)
    create_sentiment_button.click(create_sentiment_view, inputs=company_name_input, outputs=create_sentiment_output)
    get_sentiment_button.click(get_sentiment_view, inputs=company_name_input, outputs=get_sentiment_output)

demo.launch()
