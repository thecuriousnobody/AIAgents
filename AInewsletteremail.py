 
import os
from serpapi import GoogleSearch
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

os.environ['SENDER_EMAIL'] = 'vishnuidksomething@gmail.com' #use curious nobody email
os.environ['SENDER_PASSWORD'] = 'xapr xyya voll sfgl' #create app password for email (ask claude how to make one)
os.environ['RECEIVER_EMAIL'] = 'vishnuidksomething@gmail.com' #just example for testing, ask claude how to mass email users(probably loop of this)


def get_news_for_topic(topic, api_key):
    params = {
        "q": topic,
        "tbm": "nws",
        "api_key": api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    news_results = results.get("news_results", [])
    return [
        {
            "title": item["title"],
            "link": item["link"],
            "snippet": item["snippet"]
        }
        for item in news_results[:3]  # Limit to top 3 results
    ]

def generate_newsletter(topics, api_key):
    newsletter = []
    for topic in topics:
        news_items = get_news_for_topic(topic, api_key)
        newsletter.append((topic.capitalize(), news_items))
    return newsletter

def format_newsletter_html(newsletter):
    today = datetime.now()
    html = f"""
    <html>
    <body>
    <h1>AI-Generated Newsletter for {today.strftime('%B %d, %Y')}</h1>
    """
    for topic, news_items in newsletter:
        html += f"<h2>{topic} News:</h2>"
        for item in news_items:
            html += f"""
            <h3>{item['title']}</h3>
            <p>{item['snippet']}</p>
            <a href="{item['link']}">Read more</a>
            <hr>
            """
    html += "</body></html>"
    return html

def send_email(sender_email, sender_password, receiver_email, subject, html_content):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

def main():
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        print("Error: SERPAPI_API_KEY environment variable not set.")
        return

    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL")

    if not all([sender_email, sender_password, receiver_email]):
        print("Error: Email configuration environment variables not set.")
        return

    print("Welcome to the AI Newsletter Generator!")
    topics_input = input("Enter topics for your newsletter (comma-separated): ")
    topics = [topic.strip().lower() for topic in topics_input.split(',')]
    
    newsletter = generate_newsletter(topics, api_key)
    html_newsletter = format_newsletter_html(newsletter)
    
    subject = f"AI-Generated Newsletter for {datetime.now().strftime('%B %d, %Y')}"
    
    try:
        send_email(sender_email, sender_password, receiver_email, subject, html_newsletter)
        print("Newsletter sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

if __name__ == "__main__":
    main()