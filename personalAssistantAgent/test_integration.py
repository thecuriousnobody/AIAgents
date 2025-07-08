#!/usr/bin/env python3
"""
Integration Test for Complete Personal Assistant Workflow
========================================================

This tests the complete end-to-end workflow:
Speech → Conversation → Processing → Results
"""

import asyncio
import json
from conversational_assistant import StreamingPersonalAssistant
from personal_assistant_system import PersonalAssistantWorkflow

async def test_complete_workflow():
    """Test the complete workflow from speech to results"""
    
    print("🧪 Testing Complete Personal Assistant Workflow")
    print("=" * 60)
    
    # Initialize components
    streaming_assistant = StreamingPersonalAssistant()
    full_workflow = PersonalAssistantWorkflow()
    
    # Simulate speech input
    speech_inputs = [
        "I just finished editing podcast episode 45 and need to schedule publication for next Tuesday",
        "Yes, it's for the main podcast series",
        "The guest was talking about AI in healthcare", 
        "Please go ahead and process this"
    ]
    
    print("🎤 Simulating speech inputs:")
    for i, speech in enumerate(speech_inputs, 1):
        print(f"   {i}. '{speech}'")
    
    # Start conversation
    session_id = await streaming_assistant.start_conversation(speech_inputs[0])
    print(f"\n🆔 Started conversation session: {session_id}")
    
    # Continue conversation
    for speech in speech_inputs[1:]:
        print(f"\n👤 User: {speech}")
        print("🤖 Assistant: ", end="")
        
        # Simulate streaming response
        response_text = ""
        async for chunk in streaming_assistant.continue_conversation(session_id, speech):
            if chunk.startswith("data: "):
                data = json.loads(chunk[6:])
                if data['type'] == 'token':
                    response_text += data['content']
                    print(data['content'], end='', flush=True)
                elif data['type'] == 'complete':
                    print(f"\n   [Session: {data['session_id']}]")
    
    # Check if ready for processing
    if streaming_assistant.is_ready_for_processing(session_id):
        print(f"\n✅ Conversation ready for processing!")
        
        # Get refined input
        refined_input = streaming_assistant.get_refined_input_for_next_agents(session_id)
        print(f"\n📋 Refined input summary:")
        print(f"   Topic: {refined_input.get('identified_topic', 'Unknown')}")
        print(f"   Lane: {refined_input.get('suggested_lane', 'Unknown')}")
        print(f"   Confidence: {refined_input.get('confidence_score', 0):.2f}")
        
        # Process through full workflow
        print(f"\n🔄 Processing through Research & Execution agents...")
        result = full_workflow.process_speech_input(refined_input['original_input'])
        
        print(f"\n🎉 Processing complete!")
        print(f"   Session ID: {result['session_id']}")
        print(f"   Timestamp: {result['timestamp']}")
        print(f"   Results saved to sessions folder")
        
    else:
        print(f"\n⏳ Conversation not ready for processing yet")
    
    print(f"\n✅ Complete workflow test finished!")

async def test_quick_conversation():
    """Quick test of just the conversational interface"""
    
    print("🗣️  Quick Conversation Test")
    print("=" * 40)
    
    assistant = StreamingPersonalAssistant()
    
    # Start conversation
    session_id = await assistant.start_conversation(
        "I need to update my Podcast Bots AI startup metrics dashboard"
    )
    
    print(f"Session: {session_id}")
    
    # Continue with follow-up
    print("\n🤖 Assistant response:")
    async for chunk in assistant.continue_conversation(
        session_id, 
        "Yes, I want to track user growth and feature adoption rates"
    ):
        if chunk.startswith("data: "):
            data = json.loads(chunk[6:])
            if data['type'] == 'token':
                print(data['content'], end='', flush=True)
    
    print(f"\n\n✅ Quick test complete!")

if __name__ == "__main__":
    print("🎯 Personal Assistant Integration Tests")
    print("\nChoose test:")
    print("1. Complete workflow (speech → conversation → processing)")
    print("2. Quick conversation test") 
    print("3. Exit")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        asyncio.run(test_complete_workflow())
    elif choice == "2":
        asyncio.run(test_quick_conversation())
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")
