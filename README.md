# AI Assistant for Wealth Managers

This AI assistant helps wealth managers to survey company information. It maintains a list of companies for research, subscribes to the latest news, and creates a sentiment view on how the company is perceived in terms of investor sentiments.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/callingmahendra/test-connet.git
    cd test-connet
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Create an instance of the AI assistant:
    ```python
    from ai_assistant import AI_Assistant

    api_key = "your_openai_api_key"
    assistant = AI_Assistant(api_key)
    ```

2. Add a company to the research list:
    ```python
    assistant.add_company("Company Name")
    ```

3. Subscribe to the latest news for a company:
    ```python
    assistant.subscribe_news("Company Name", "Latest news article")
    ```

4. Create a sentiment view for a company:
    ```python
    sentiment = assistant.create_sentiment_view("Company Name")
    print(sentiment)
    ```

5. Get the sentiment view for a company:
    ```python
    sentiment = assistant.get_sentiment_view("Company Name")
    print(sentiment)
    ```
