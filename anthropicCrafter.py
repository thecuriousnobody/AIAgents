import re
import os
from openai import OpenAI
from podcastShortlisterAgent import topic
from tavilySearchProto import process_guest
from guest_processing import extract_guest_info
import anthropic

# input_text = """
# 1. Dr. Nandita Chaudhary, University of Delhi - Dr. Chaudhary is a Professor of Psychology at the University of Delhi and has published extensively on shame, guilt, and moral emotions in Indian cultural context. Her work explores the role of shame in Indian society and its implications on mental health. Contact: [nandita.chaudhary@du.ac.in](mailto:nandita.chaudhary@du.ac.in)
# """
input_text = """
1. Dr. Uma Chakravarti - A historian and gender studies scholar who has written extensively on caste, gender, and communalism in India. She can be reached at [umachakravarti@gmail.com](mailto:umachakravarti@gmail.com).
2. Dr. Pratiksha Baxi - A sociologist and legal scholar who has researched and written on gender, law, and violence in India. She can be reached at [pratikshabaxi@gmail.com](mailto:pratikshabaxi@gmail.com).
3. Mr. Amitava Kumar - An author and journalist who has written on identity, migration, and culture. He can be reached at [akumar@hamilton.edu](mailto:akumar@hamilton.edu).
4. Dr. Nivedita Menon - A political theorist and gender studies scholar who has written on nationalism, secularism, and feminist politics in India. She can be reached at [nivedita.menon@gmail.com](mailto:nivedita.menon@gmail.com).
5. Dr. Shohini Ghosh - A media scholar and documentary filmmaker who has worked on gender, sexuality, and censorship in India. She can be reached at [shohini.ghosh@gmail.com](mailto:shohini.ghosh@gmail.com).
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

# def extract_guest_info(guest_entry):
#     # Extract the name
#     name_match = re.search(r'^(.*?)\s*[-–]', guest_entry)
#     if not name_match:
#         name_match = re.search(r'^(.*?),', guest_entry)
#     name = name_match.group(1).strip() if name_match else ''
#
#     # Extract the description
#     description_match = re.search(r'[-–,]\s*(.*?)\s*$', guest_entry)
#     description = description_match.group(1).strip() if description_match else ''
#
#     # Extract the contact information
#     contact_match = re.search(r'\[(.*?)\]\((.*?)\)', description)
#     if contact_match:
#         contact_info = contact_match.group(1).strip()
#         contact_url = contact_match.group(2).strip()
#         description = description.replace(contact_match.group(0), '').strip()
#     else:
#         contact_info = ""
#         contact_url = ""
#
#     return name, description, contact_info, contact_url

# Format the guest list
formatted_guest_list = format_guest_list(input_text)
print(formatted_guest_list)

# Process the guest list
guest_list = []
for guest_entry in formatted_guest_list.strip().split("\n"):
    if guest_entry.strip() and not guest_entry.startswith("guest_list = \"\"\""):
        name, description, contact_info = extract_guest_info(guest_entry)
        if name:
            guest_info = {
                'name': name,
                'description': description,
                'contact_info': contact_info,
            }
            guest_list.append(guest_info)


formatted_guest_list = format_guest_list(input_text)
print(formatted_guest_list)
# guests = [guest.strip() for guest in guest_list.split("\n") if guest.strip()]
# guests = [guest.strip() for guest in formatted_guest_list.strip().split("\n") if guest.strip() and not guest.startswith("guest_list = \"\"\"")]

for guest in guest_list:
    print(guest)

host_info = {
    "name": "Rajeev Kumar",
    "email": "theideasandboxpodcast@gmail.com",
    "website": "https://theideasandboxpodcast.com/",
    "whatsapp": "+13096797200"
}

client = anthropic.Anthropic(
    api_key="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",
)
model = "claude-3-sonnet-20240229"


# Process each guest
# Process each guest
for guest in guest_list:
    print("Processing guest:", guest)
    tavily_summary = process_guest(guest)
    # Extract the guest name using regex
    name_match = re.search(r"(Dr\.|Mr\.|Ms\.) (.*?) -", guest['name'])
    if name_match:
        title = name_match.group(1).strip()
        guest_name = name_match.group(2).strip()
    else:
        guest_name = guest['name']

    # Extract the guest description
    guest_description = guest['description']

    # Extract the guest contact information
    guest_contact_info = guest['contact_info']
    # guest_contact_url = guest['contact_url']

    # Extract the guest email using regex
    email_match = re.search(r"can be reached at \. (.*@.*)", guest_description)
    if email_match:
        guest_email = email_match.group(1)
    else:
        guest_email = guest_contact_info

    # Extract the guest Twitter handle using regex
    twitter_match = re.search(r"Twitter handle, @(.*?)[\)\.]", guest_description)
    if twitter_match:
        guest_twitter = twitter_match.group(1)
    else:
        guest_twitter = ""

    # Extract the guest website using regex
    # website_match = re.search(r"Website: (.*)", guest['contact_info'])
    # if website_match:
    #     guest_website = website_match.group(1)
    # else:
    #     guest_website = ""


    if twitter_match:
        contact_type = "Twitter"
        contact_info = twitter_match.group(1)
    elif email_match:
        contact_type = "Email"
        contact_info = email_match.group(1)
    # elif website_match:
    #     contact_type = "Website"
    #     contact_info = website_match.group(1)
    else:
        contact_type = "Unknown"
        contact_info = "N/A"

    # from tavilySearchProto import tavily_summary
    prompt = f"Consider the following context about {guest_name}'s work and contributions:\n{tavily_summary}\n\n"
    prompt += f"Given this context, dive into {guest_name}'s work and contributions, seeking out the essence of their research, publications, or insights that resonate with the theme of {topic}. Identify the core philosophy and mission that drive their work, and consider how it ties into the larger conversation around {topic} and the potential implications for the subject matter.\n\n"
    prompt += f"Write a heartfelt and personalized email from {host_info['name']} to invite {guest_name} to be a guest on the Idea Sandbox podcast. Adopt a warm, genuine, and conversational tone that reflects {host_info['name']}'s own voice and personality. Express {host_info['name']}'s sincere admiration for {guest_name}'s work using language that feels natural and authentic to {host_info['name']}, such as 'As I dove into your work, I was struck by the profound insights you bring to these critical topics.' Highlight how their expertise aligns with the podcast's mission and how their unique perspective could enrich the discussion. Craft the email in a way that feels like a personal message from one person to another, focusing on the key points that will resonate with {guest_name} on a human level. Avoid sounding too formal or automated, and instead aim for a tone that is engaging, enthusiastic, and true to {host_info['name']}'s personality. Include {host_info['name']}'s contact information: Email: {host_info['email']}, Website: {host_info['website']}, WhatsApp: {host_info['whatsapp']}."

    message = client.messages.create(
            model=model,
            max_tokens=1000,
            temperature=0.0,
            system="You are an artificial intelligence assistant and you need to "
                   "engage in a helpful, detailed, polite conversation with a user.",
            messages=[
                {
                    "role": "user",
                    "content": (
                        prompt
                    ),
                },
            ]
        )

    # Extract the text content from the message
    text_content = message.content[0].text

    # Split the text content into lines and remove empty lines
    lines = [line.strip() for line in text_content.split('\n') if line.strip()]

    # Join the lines back together with a single newline character
    email_content = '\n'.join(lines)

    # email_content = response.choices[0].message.content
    email_content = re.sub(r'^Here\'s a draft email:\n', '', email_content, flags=re.MULTILINE)
    print(f"Email for {guest_name}:")
    print(email_content)
    print("\n")

    # Create the email subject
    email_subject = f"Invitation to be a guest on the Idea Sandbox podcast - {topic}"

    # Format the email content with contact information and subject
    formatted_email_content = f"Email Address: {guest_email}\n"
    formatted_email_content += f"Social Media Handle: {twitter_match}\n\n"
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

    with open(file_path, "w") as file:
        file.write(formatted_email_content)

    print(f"Final email saved to: {file_path}\n")