import os
import config
from groq import Groq
os.environ["GROQ_API_KEY"] =config.GROQ_API_KEY

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "what are the theories behind how the grand canyon was formed",
        }
    ],
    # model="mixtral-8x7b-32768",
    model = "gemma-7b-it"
)

print(chat_completion.choices[0].message.content)