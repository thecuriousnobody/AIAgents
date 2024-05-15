import re
import os
from openai import OpenAI
from podcastShortlisterAgent import topic

# Example usage
input_text = """
1. Dr. Nandita Chaudhary, University of Delhi - Dr. Chaudhary is a Professor of Psychology at the University of Delhi and has published extensively on shame, guilt, and moral emotions in Indian cultural context. Her work explores the role of shame in Indian society and its implications on mental health. Contact: [nandita.chaudhary@du.ac.in](mailto:nandita.chaudhary@du.ac.in)
"""

def format_guest_list(input_text):
    lines = input_text.strip().split("\n")
    formatted_lines = []

    for line in lines:
        if line.strip() and not line.startswith("guest_list = \"\"\""):
            # Extract the name and description
            match = re.match(r'\d+\.\s*(.*?)\s*-\s*(.*)', line)
            if match:
                name = match.group(1).strip()
                description = match.group(2).strip()

                # Extract the contact information
                contact_match = re.search(r'\[(.*?)\]\((.*?)\)', description)
                if contact_match:
                    contact_info = contact_match.group(1).strip()
                    contact_url = contact_match.group(2).strip()
                    description = description.replace(contact_match.group(0), '').strip()
                else:
                    contact_info = ""
                    contact_url = ""

                # Create the formatted line
                formatted_line = f"{name} - {description}"
                if contact_info:
                    formatted_line += f" {contact_info}"

                formatted_lines.append(formatted_line)

    return "guest_list = \"\"\"\n" + "\n".join(formatted_lines) + "\n\"\"\""


formatted_guest_list = format_guest_list(input_text)
print(formatted_guest_list)
# guests = [guest.strip() for guest in guest_list.split("\n") if guest.strip()]
guests = [guest.strip() for guest in formatted_guest_list.strip().split("\n") if guest.strip() and not guest.startswith("guest_list = \"\"\"")]

for guest in guests:
    print(guest)

host_info = {
    "name": "Rajeev Kumar",
    "email": "theideasandboxpodcast@gmail.com",
    "website": "https://theideasandboxpodcast.com/",
    "whatsapp": "+13096797200"
}

for guest in guests:
    print("Processing guest:", guest)

    # Extract the guest name using regex
    name_match = re.search(r"(Dr\.|Mr\.|Ms\.) (.*?) -", guest)
    if name_match:
        guest_name = name_match.group(2)
    else:
        print(f"Skipping guest: {guest}")
        continue

    # Extract the contact information using regex
    contact_match = re.search(r"can be reached at \. (.*@.*)", guest)
    if contact_match:
        email_address = contact_match.group(1)
    else:
        email_address = "N/A"

    social_media_match = re.search(r"Twitter: @(.*)", guest)
    if social_media_match:
        social_media_handle = social_media_match.group(1)
    else:
        social_media_handle = "N/A"

    # Extract the contact information using regex
    twitter_match = re.search(r"Twitter: \[@(.*?)\]", guest)
    email_match = re.search(r"Email: \[(.*?)\]", guest)
    website_match = re.search(r"Website: <(.*?)>", guest)

    if twitter_match:
        contact_type = "Twitter"
        contact_info = twitter_match.group(1)
    elif email_match:
        contact_type = "Email"
        contact_info = email_match.group(1)
    elif website_match:
        contact_type = "Website"
        contact_info = website_match.group(1)
    else:
        contact_type = "Unknown"
        contact_info = "N/A"

    # prompt = f"Before creating the email, conduct a focused search on {guest_name}'s work and contributions, specifically looking for any research, publications, or insights that connect to the topic of {topic}. Identify a particular aspect of their work that resonates with this theme and briefly mention how it ties into the larger conversation around {topic}.\n\nCraft a thoughtful and personalized email from {host_info['name']} to invite {guest_name} to be a guest on the Idea Sandbox podcast. Write in a warm and genuine tone, as if {host_info['name']} is reaching out to a respected colleague. Express {host_info['name']}'s sincere interest in {guest_name}'s unique perspective on {topic}, drawing from the specific insight you discovered in your research. Highlight how {guest_name}'s expertise aligns with the podcast's mission of exploring ideas that foster thriving societies and how their work challenges prevailing notions around shame, chewing out, and othering. Emphasize the potential for a nuanced and impactful discussion that goes beyond surface-level discourse. Keep the email concise and engaging, focusing on the key points that will resonate with {guest_name}. Include {host_info['name']}'s contact information: Email: {host_info['email']}, Website: {host_info['website']}, WhatsApp: {host_info['whatsapp']}."
    prompt = f"Before crafting the email, dive into {guest_name}'s work and contributions, seeking out the essence of their research, publications, or insights that resonate with the theme of {topic}. Identify the core philosophy and mission that drive their work, and consider how it ties into the larger conversation around {topic}.\n\nWrite a heartfelt and personalized email from {host_info['name']} to invite {guest_name} to be a guest on the Idea Sandbox podcast. Adopt a warm, genuine tone that reflects {host_info['name']}'s own voice and sensibility, as if reaching out to a kindred spirit. Express a deep appreciation for {guest_name}'s unique perspective on {topic}, drawing from the fundamental insights you gleaned from your research. Highlight how their expertise aligns with the podcast's mission of exploring ideas that foster thriving societies, and how their work challenges prevailing notions around shame, chewing out, and othering. Emphasize the potential for a rich, nuanced discussion that delves into the heart of the matter. Craft the email in a way that feels authentic and engaging, focusing on the key points that will resonate with {guest_name} on a personal level. Include {host_info['name']}'s contact information: Email: {host_info['email']}, Website: {host_info['website']}, WhatsApp: {host_info['whatsapp']}."
    model = "llama-3-70b-instruct"
    messages = [
        {
            "role": "system",
            "content": (
                "You are an artificial intelligence assistant and you need to "
                "engage in a helpful, detailed, polite conversation with a user."
            ),
        },
        {
            "role": "user",
            "content": (
                prompt
            ),
        },
    ]

    client = OpenAI(api_key='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',
                    base_url="https://api.perplexity.ai")

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    email_content = response.choices[0].message.content
    email_content = re.sub(r'^Here\'s a draft email:\n', '', email_content, flags=re.MULTILINE)
    print(f"Email for {guest_name}:")
    print(email_content)
    print("\n")

    # Create the email subject
    email_subject = f"Invitation to be a guest on the Idea Sandbox podcast - {topic}"

    # Format the email content with contact information and subject
    formatted_email_content = f"Email Address: {email_address}\n"
    formatted_email_content += f"Social Media Handle: {social_media_handle}\n\n"
    formatted_email_content += f"Subject: {email_subject}\n\n"
    formatted_email_content += email_content

    first_word = topic.split()[0]
    first_word = re.sub(r'[^a-zA-Z0-9]', '', first_word)
    guest_name = re.sub(r'[^a-zA-Z0-9\s]', '', guest_name)
    guest_name = re.sub(r'\s+', '_', guest_name)

    # Truncate the guest name if it's too long
    max_name_length = 20
    guest_name = guest_name[:max_name_length]

    # Save the final email to a file in the specified folder
    folder_path = "/Users/rajeevkumar/Documents/TISB Stuff/guestPrep"
    file_name = f"{first_word}_{guest_name}_email.txt"
    file_path = os.path.join(folder_path, file_name)

    # Remove the unnecessary line from the email content
    email_content = re.sub(
        r'^Here is a compelling and personalized email from Rajeev Kumar to invite .* to be a guest on the Idea Sandbox podcast:\n',
        '', email_content, flags=re.MULTILINE)

    # Create a more succinct email subject
    email_subject = f"Invitation to the Idea Sandbox Podcast"

    # Remove any existing subject lines from the email content
    email_content = re.sub(r'^Subject:.*\n', '', email_content, flags=re.MULTILINE)

    # Format the email content with contact information and subject
    formatted_email_content = f"Email Address: {email_address}\n"
    formatted_email_content += f"Social Media Handle: {social_media_handle}\n\n"
    formatted_email_content += f"Subject: {email_subject}\n\n"
    formatted_email_content += email_content

    with open(file_path, "w") as file:
        file.write(formatted_email_content)

    print(f"Final email saved to: {file_path}\n")