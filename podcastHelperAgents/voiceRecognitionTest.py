from voice_recognition import VoiceRecognition

def test_voice_recognition():
    print("Available microphones:")
    VoiceRecognition.list_microphones()
    
    mic_index = input("Enter the index of the microphone you want to use (or press Enter for default): ")
    if mic_index:
        vr = VoiceRecognition(microphone_index=int(mic_index))
    else:
        vr = VoiceRecognition()
    
    print("This is a test of the conversation-like voice recognition system.")
    print("Start speaking when prompted. The system will transcribe after 3 seconds of silence.")
    print("The conversation will continue until you say 'exit' or press Ctrl+C to stop.")

    try:
        for transcription in vr.get_voice_input():
            print(f"\nFinal Transcription: {transcription}")
            if "exit" in transcription.lower():
                print("Exiting...")
                break
    except KeyboardInterrupt:
        print("\nStopped by user.")

if __name__ == "__main__":
    test_voice_recognition()