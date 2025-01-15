from googletrans import Translator

def test_translation():
    translator = Translator()
    
    # Test translation from English to Spanish
    text = "Hello, how are you?"
    translation = translator.translate(text, dest='es')
    print(f"Original text: {text}")
    print(f"Translated text: {translation.text}")
    print(f"Detected source language: {translation.src}")

if __name__ == "__main__":
    test_translation()
