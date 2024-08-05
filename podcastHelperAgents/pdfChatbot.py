import PyPDF2
import anthropic
import os
import sys
import time
from voice_recognition import VoiceRecognition

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Set environment variables
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

class PDFChatbot:
    def __init__(self, pdf_path):
        self.text = extract_text_from_pdf(pdf_path)
        self.client = anthropic.Anthropic()
        self.system_prompt = (
            "You are an AI assistant tasked with answering questions about a specific PDF document. "
            "The content of the PDF has been provided to you. Please use this information to answer "
            "user questions accurately and concisely."
        )
        self.conversation_history = [
            {
                "role": "user",
                "content": f"Here's the content of the PDF:\n\n{self.text[:10000]}\n\nPlease use this information to answer my questions. If you need more context, let me know."
            },
            {
                "role": "assistant",
                "content": "I understand. I've processed the first part of the PDF content you provided. I'm ready to answer any questions you have about it. What would you like to know? If you need information from later parts of the document, please let me know."
            }
        ]
        self.voice_recognition = VoiceRecognition()

    def answer_question(self, question):
        self.conversation_history.append({"role": "user", "content": question})
        
        max_retries = 5
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=1000,
                    temperature=0.9,
                    system=self.system_prompt,
                    messages=self.conversation_history[-5:]  # Only send the last 5 messages
                )
                answer = response.content[0].text
                self.conversation_history.append({"role": "assistant", "content": answer})
                return answer
            except anthropic.RateLimitError as e:
                if attempt == max_retries - 1:
                    raise e
                delay = base_delay * (2 ** attempt)
                print(f"Rate limit reached. Retrying in {delay} seconds...")
                time.sleep(delay)

    def voice_chat(self):
        print("Voice chat mode activated. Speak your questions.")
        print("After speaking, press Enter to submit your question or type 'r' and press Enter to re-record.")
        print("Say 'quit' to exit voice chat mode.")
        
        for question in self.voice_recognition.get_voice_input():
            print(f"\nRecognized: {question}")
            user_input = input("Press Enter to submit, 'r' to re-record, or type to modify: ").strip().lower()
            
            if user_input == 'r':
                print("Re-recording... Speak your question again.")
                continue
            elif user_input:
                question = user_input  # Use the typed input instead
            
            if question.lower() == 'quit':
                print("Exiting voice chat mode.")
                break
            
            try:
                answer = self.answer_question(question)
                print(f"\nAI: {answer}")
            except anthropic.RateLimitError:
                print("Rate limit exceeded. Please wait a moment before asking another question.")
                time.sleep(60)  # Wait for 60 seconds before allowing another question


def main():
    print("Available microphones:")
    VoiceRecognition.list_microphones()
    # mic_index = input("Enter the index of the microphone you want to use (or press Enter for default): ")
    mic_index = 1
    # pdf_path = input("Enter the path to your PDF file: ")
    pdf_path = '/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Oron Catts/oronCattsFullBookV2.pdf'
    chatbot = PDFChatbot(pdf_path)
    
    if mic_index:
        chatbot.voice_recognition = VoiceRecognition(microphone_index=int(mic_index))
    
    print("PDF loaded. You can now ask questions about its content.")
    print("Type 'voice' to switch to voice input mode, or 'quit' to exit the chat.")

    while True:
        user_input = input("\nYou: ").lower()
        if user_input == 'quit':
            break
        elif user_input == 'voice':
            chatbot.voice_chat()
        else:
            answer = chatbot.answer_question(user_input)
            print(f"\nAI: {answer}")

if __name__ == "__main__":
    main()