import transformers
import torch
import os

# Set the model ID
model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

# Create the text generation pipeline
pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

# Define the Idea Sandbox podcast system message
system_message = """
You are an Idea Sandbox podcast advisor, whose mission is to promote the power of ideas as the foundation for societal progress and personal fulfillment. You believe that while legislative efforts are necessary, the spread of enlightened ideas can shape our values and inspire change far beyond what laws alone can achieve.

Your role is to engage in discussions that challenge the status quo, inspire personal growth, and highlight the incredible potential for human flourishing when we prioritize ideas over injunctions. You will speak with a thoughtful, intellectual tone, and focus on exploring the limitless possibilities that come from thinking critically, living intentionally, and fostering a culture that values ideas as the catalysts for authentic, sustainable progress.
"""

# Define the user message
user_message = "Can you tell me more abour Oron Catts"

# Create the message history
messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": user_message},
]

# Generate the Idea Sandbox podcast response
outputs = pipeline(
    messages,
    max_new_tokens=256,
    do_sample=True,
    top_p=0.9,
    top_k=50,
    num_return_sequences=1,
    eos_token_id=None,
    pad_token_id=0,
)

# Get the model object from the pipeline
model = pipeline.model

# Print out information about the model
print(f"Model class: {type(model)}")
print(f"Model name: {model.name_or_path}")

# If the model has a 'config' attribute, it often contains the path
if hasattr(model, 'config'):
    print(f"Config path: {model.config.name_or_path}")

# Check the Transformers cache directory
cache_dir = transformers.utils.TRANSFORMERS_CACHE
print(f"Transformers cache directory: {cache_dir}")

# List files in the model's cache directory
model_cache_dir = os.path.join(cache_dir, model_id.replace('/', '--'))
if os.path.exists(model_cache_dir):
    print(f"Files in model cache directory:")
    for root, dirs, files in os.walk(model_cache_dir):
        for file in files:
            print(os.path.join(root, file))
else:
    print(f"Model cache directory not found: {model_cache_dir}")

# If the model has a 'state_dict' method, we can check its keys
if hasattr(model, 'state_dict'):
    print("Model state dict keys:")
    for key in model.state_dict().keys():
        print(key)