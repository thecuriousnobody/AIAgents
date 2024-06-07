import anthropic
from podcastShortlisterAgent import topic
import config

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=config.PERPLEXITY_API_KEY,
)
host_info = {
    "name": "Rajeev Kumar",
    "email": "theideasandboxpodcast@gmail.com",
    "website": "https://theideasandboxpodcast.com/",
    "whatsapp": "+13096797200"
}
guest_name = "Dr. Nandita Chaudhary"
prompt = f"Before crafting the email, dive into {guest_name}'s work and contributions, seeking out the essence of their research, publications, or insights that resonate with the theme of {topic}. Identify the core philosophy and mission that drive their work, and consider how it ties into the larger conversation around {topic}.\n\nWrite a heartfelt and personalized email from {host_info['name']} to invite {guest_name} to be a guest on the Idea Sandbox podcast. Adopt a warm, genuine tone that reflects {host_info['name']}'s own voice and sensibility, as if reaching out to a kindred spirit. Express a deep appreciation for {guest_name}'s unique perspective on {topic}, drawing from the fundamental insights you gleaned from your research. Highlight how their expertise aligns with the podcast's mission of exploring ideas that foster thriving societies, and how their work challenges prevailing notions around shame, chewing out, and othering. Emphasize the potential for a rich, nuanced discussion that delves into the heart of the matter. Craft the email in a way that feels authentic and engaging, focusing on the key points that will resonate with {guest_name} on a personal level. Include {host_info['name']}'s contact information: Email: {host_info['email']}, Website: {host_info['website']}, WhatsApp: {host_info['whatsapp']}."

# model = 'claude-3-opus-20240229'
model = 'claude-3-haiku-20240307'
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
formatted_text = '\n'.join(lines)

print(formatted_text)

