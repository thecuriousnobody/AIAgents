import os
# Change this line:
from topic_selector import select_topics, create_topic_selector_agent, create_topic_selection_task
from news_fetcher import fetch_news, create_news_fetcher_agent, create_news_fetching_task
from article_writer import write_articles, create_article_writer_agent, create_article_writing_task
from layout_designer import design_layout, create_layout_designer_agent, create_layout_design_task
from email_sender import send_emails, create_email_sender_agent, create_email_sending_task
from newspaper_formatter import format_newspaper, create_newspaper_formatter_agent, create_newspaper_formatting_task


def main():
    print("Starting AI Newspaper Generation Process")

    # Topic Selection
    topic_agent = create_topic_selector_agent()
    topic_task = create_topic_selection_task()
    selected_topics = select_topics(topic_agent, topic_task)

    # News Fetching
    news_agent = create_news_fetcher_agent()
    news_task = create_news_fetching_task(selected_topics)
    fetched_news = fetch_news(news_agent, news_task)

    # Article Writing
    writer_agent = create_article_writer_agent()
    writing_task = create_article_writing_task(fetched_news)
    written_articles = write_articles(writer_agent, writing_task)

    # Layout Design
    designer_agent = create_layout_designer_agent()
    design_task = create_layout_design_task(written_articles)
    newspaper_layout = design_layout(designer_agent, design_task)

    # Format and generate the HTML newspaper
    formatter_agent = create_newspaper_formatter_agent()
    formatting_task = create_newspaper_formatting_task(newspaper_layout)
    formatted_newspaper = format_newspaper(formatter_agent, formatting_task)

    # Email Sending
    email_agent = create_email_sender_agent()
    email_task = create_email_sending_task(formatted_newspaper)
    email_result = send_emails(email_agent, email_task)

    print("AI Newspaper Generation Process Complete!")


if __name__ == "__main__":
    main()