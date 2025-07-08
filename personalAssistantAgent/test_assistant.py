#!/usr/bin/env python3
"""
Personal Assistant Test Script
=============================

Quick test script to demonstrate the personal assistant functionality.
"""

import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from personal_assistant_system import PersonalAssistantWorkflow
from streaming_assistant import StreamingPersonalAssistant

def test_basic_workflow():
    """Test the basic 3-agent workflow"""
    print("🧪 Testing Basic Personal Assistant Workflow")
    print("=" * 60)
    
    workflow = PersonalAssistantWorkflow()
    
    # Test cases for different project lanes
    test_cases = [
        "I just finished recording episode 45 of the podcast and need to schedule the editing",
        "Had a great mentor session with the accelerator startup about their AI architecture",
        "Need to update the Podcast Bots AI feature roadmap based on user feedback",
        "Working on a personal project to learn more about blockchain technology"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n🎯 Test Case {i}: {test_input}")
        print("-" * 40)
        
        try:
            result = workflow.process_speech_input(test_input)
            print(f"✅ Processed successfully!")
            print(f"Session ID: {result['session_id']}")
            print(f"Timestamp: {result['timestamp']}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

async def test_streaming_workflow():
    """Test the streaming workflow"""
    print("🎬 Testing Streaming Personal Assistant")
    print("=" * 60)
    
    assistant = StreamingPersonalAssistant()
    
    test_input = "I need to schedule a podcast recording session with the guest we discussed last week"
    
    print(f"🎤 Input: {test_input}")
    print("-" * 40)
    
    try:
        async for message in assistant.process_speech_stream(test_input):
            if message.type == 'agent_start':
                print(f"\n🚀 {message.content}")
            elif message.type == 'agent_thinking':
                print(f"💭 {message.content}")
            elif message.type == 'agent_response':
                print(f"\n📝 **{message.agent}**:")
                print(f"{message.content}")
            elif message.type == 'task_complete':
                print(f"\n✅ {message.content}")
            elif message.type == 'error':
                print(f"\n❌ {message.content}")
    
    except Exception as e:
        print(f"❌ Streaming error: {e}")

def show_system_info():
    """Show information about the system"""
    print("🤖 Personal Assistant Agent System")
    print("=" * 60)
    print("This system consists of 3 specialized agents:")
    print()
    print("1. 🎤 Personal Assistant (Gatekeeper)")
    print("   - Conversational interface")
    print("   - Understands your 4 project lanes")
    print("   - Refines ideas through dialogue")
    print()
    print("2. 🔍 Research & Classification Specialist")
    print("   - Deep research using search tools")
    print("   - Creates unique work IDs")
    print("   - Classifies into project lanes")
    print()
    print("3. ⚡ Execution Agent")
    print("   - Creates calendar events")
    print("   - Updates checklists")
    print("   - Executes real-world actions")
    print()
    print("📂 Project Lanes:")
    print("   • Podcasting - Content creation & publishing")
    print("   • Distillery Lab - Accelerator & consulting")
    print("   • Podcast Bots AI - Startup development")
    print("   • Miscellaneous - Everything else")
    print()

def main():
    """Main test function"""
    show_system_info()
    
    print("Choose a test mode:")
    print("1. Basic workflow test (non-streaming)")
    print("2. Streaming workflow test")
    print("3. Interactive streaming console")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n" + "=" * 60)
        test_basic_workflow()
    elif choice == "2":
        print("\n" + "=" * 60)
        asyncio.run(test_streaming_workflow())
    elif choice == "3":
        print("\n" + "=" * 60)
        from streaming_assistant import run_streaming_console
        asyncio.run(run_streaming_console())
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
