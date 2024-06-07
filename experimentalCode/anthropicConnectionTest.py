import anthropic
import config

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=config.ANTHROPIC_API_KEY,
)

message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    temperature=0.0,
    system="think about this deeply as it pertains to my career as a podcaster, blogger and artis",
    messages=[
        {"role": "user", "content": "Can you give me names of indian researchers who specialize in understanding the godmen culture of india"}
    ]
)

# Split the response into lines and remove any empty lines
# lines = [line.strip() for line in message.content.split("\n") if line.strip()]

# Print the formatted list
# for line in message.content:
#     print(line)

# Extract the text from the response
response_text = message.content[0].text

# Use regex to extract the numbered list items
pattern = r'\d+\.\s+(.+?)\s*(?=\n\d+\.|$)'
matches = re.findall(pattern, response_text, re.DOTALL)

# Print the formatted list
for match in matches:
    print(match.strip())