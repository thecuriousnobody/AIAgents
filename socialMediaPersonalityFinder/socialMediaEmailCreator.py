from tavilySocialMediaPersonalitySearcher import process_search_results
import anthropic
import config
import os

# Set up the environment variables for API keys
os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY

host_info = {
    "name": "Rajeev Kumar",
    "email": "theideasandboxpodcast@gmail.com",
    "website": "tisb.world",
    "whatsapp": "3096797200"
}

def find_potential_guests(niche_topics):
    potential_guests = []
    for topic in niche_topics:
        search_query = f"Individuals or groups working on {topic}, including those with low or no social media presence"
        search_results = process_search_results(search_query)
        for result in search_results:
            potential_guests.append(result)
    return potential_guests

def verify_guest_existence(potential_guests):
    verified_guests = []
    for guest in potential_guests:
        search_query = f"{guest['name']} {guest['affiliation']} {guest['work']}"
        search_results = process_search_results(search_query)
        if search_results:
            verified_guests.append(guest)
    return verified_guests

def generate_email_template(guest, niche_topic):
    anthropic_client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )
    prompt = f"""
    You are an AI assistant tasked with generating a compelling email template to invite {guest['name']} to appear as a guest on a podcast or provide a comment for a blog post or video.

    {guest['name']} is affiliated with {guest['affiliation']} and works on {guest['work']} related to the niche topic of {niche_topic}.

    The podcast host is {host_info['name']}, and their contact information is as follows:
    Email: {host_info['email']}
    Website: {host_info['website']}
    WhatsApp: {host_info['whatsapp']}

    Craft an email that:
    1. Introduces the podcast host and the purpose of the podcast or blog/video.
    2. Highlights the guest's expertise and how it aligns with the niche topic.
    3. Expresses genuine interest in the guest's work and the value their insights could bring to the audience.
    4. Politely requests the guest's participation in the podcast or a comment for the blog/video.
    5. Provides clear next steps and contact information for further communication.

    Please generate a compelling and concise email template that has a high likelihood of receiving a positive response from the guest.
    """
    response = anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        temperature=0.7,
        system="You are an AI assistant tasked with generating compelling email templates to invite guests to appear on a podcast or provide comments for a blog post or video.",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    email_template = response.content[0].text
    return email_template

# Rest of the code remains the same

    # Extract the generated script from the response
    script = response.content[0].text
    topic_words = input_text[0].split()[:2]  # Take the first two words from the first bullet point
    topic_file_name = "_".join(topic_words)
    # Save the generated script to a file
    output_file = f"/Users/rajeevkumar/Documents/TISB Stuff/brosRiffnScripts/{topic_file_name}_podcast_script.txt"
    with open(output_file, "w") as file:
        file.write(script)

    print(f"Generated script saved to: {output_file}")