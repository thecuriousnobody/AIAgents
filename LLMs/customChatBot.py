import tkinter as tk
from transformers import pipeline

# Load the Llama 3.1 language model
model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
chatbot = pipeline("text-generation", model=model_id, device_map="auto")

class IdeaSandboxChatbot(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set window title and size
        self.title("Idea Sandbox Chatbot")
        self.geometry("800x600")

        # Create the chat history and input area
        self.chat_history = tk.Text(self, height=20, width=80, state="disabled")
        self.chat_history.grid(row=0, column=0, padx=10, pady=10)

        self.input_frame = tk.Frame(self)
        self.input_frame.grid(row=1, column=0, padx=10, pady=10)

        self.input_field = tk.Entry(self.input_frame, width=60)
        self.input_field.pack(side=tk.LEFT, padx=5)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5)

        # Bind the Enter key to the send_message function
        self.input_field.bind("<Return>", lambda event: self.send_message())

    def send_message(self):
        user_input = self.input_field.get()
        if user_input.strip():
            self.chat_history.configure(state="normal")
            self.chat_history.insert(tk.END, f"User: {user_input}\n")
            self.chat_history.configure(state="disabled")

            # Generate the chatbot response
            chatbot_response = chatbot([{"role": "user", "content": user_input}])[0]["generated_text"]
            self.chat_history.configure(state="normal")
            self.chat_history.insert(tk.END, f"Chatbot: {chatbot_response}\n")
            self.chat_history.configure(state="disabled")

            self.input_field.delete(0, tk.END)

if __name__ == "__main__":
    app = IdeaSandboxChatbot()
    app.mainloop()