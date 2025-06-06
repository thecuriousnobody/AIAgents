#!/usr/bin/env python3
"""
Godman Quote Generator - Satirical Podcast Segment Tool
========================================================

This CrewAI system mines real quotes from Indian godmen and generates convincing 
"fake" quotes in their style for a hilarious guessing game podcast segment.

Targets:
- Sri Sri Ravi Shankar (Art of Living)
- Sadhguru/Jaggi Vasudev (Isha Foundation)
- Daaji (Heartfulness Meditation)

The goal: Expose the word salad nature of godman "wisdom" through satire.
"""

from crewai import Agent, Task, Crew, Process
from datetime import datetime, timedelta
import os
import sys
import re
import random
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from usefulTools.llm_repository import ClaudeSonnet
from usefulTools.search_tools import facebook_serper_tool, serper_search_tool
from usefulTools.godman_quote_scraper import godman_quote_scraper_tool

# Set up environment variables
os.environ["ANTHROPIC_API_KEY"] = config.ANTHROPIC_API_KEY
os.environ["SERPER_API_KEY"] = config.SERPER_API_KEY

# =============================================================================
# CONFIGURATION
# =============================================================================

GODMEN_TARGETS = {
    "sri_sri_ravi_shankar": {
        "name": "Sri Sri Ravi Shankar",
        "organization": "Art of Living",
        "website": "https://www.artofliving.org/in-en/wisdom/quotes/inspirational-quotes-on-life",
        "style_keywords": ["breath", "consciousness", "divine", "wisdom", "peace", "meditation", "knowledge", "bliss"],
        "speaking_style": "Gentle, mystical, often uses breathing metaphors"
    },
    "sadhguru": {
        "name": "Sadhguru (Jaggi Vasudev)",
        "organization": "Isha Foundation",
        "website": "https://isha.sadhguru.org/en/wisdom/type/quotes",
        "style_keywords": ["inner", "engineering", "dimension", "possibility", "intensity", "aliveness", "responsibility"],
        "speaking_style": "Direct, sometimes humorous, uses motorcycle and modern metaphors"
    },
    "daaji": {
        "name": "Daaji",
        "organization": "Heartfulness Meditation",
        "website": "https://heartfulness.org/us/one-beautiful-thought-archive/",
        "style_keywords": ["heart", "transmission", "purification", "evolution", "subtlety", "refinement", "balance"],
        "speaking_style": "Soft, heart-centered, emphasizes spiritual transmission"
    }
}

# =============================================================================
# AGENTS
# =============================================================================

# Agent 1: Quote Miner
quote_miner = Agent(
    role='Godman Quote Archaeological Excavator',
    goal='Mine recent profound-sounding quotes and statements from Indian godmen for satirical analysis',
    backstory="""You are an expert digital archaeologist specializing in unearthing the mystical 
    pronouncements of modern Indian spiritual leaders. Your mission is to collect their recent 
    "wisdom" from social media, interviews, speeches, books, and their official websites from the past 6-12 months. 
    You have a keen eye for identifying their most characteristically vague yet profound-sounding 
    statements that exemplify their unique speaking styles. You understand the patterns of 
    spiritual word salad and can spot the most quotable gems. You combine web scraping of their 
    official websites with search engine research to get the most comprehensive collection.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[serper_search_tool, godman_quote_scraper_tool],
    reasoning=True,
    max_reasoning_attempts=3
)

# Agent 2: Quote Synthesizer/Faker
quote_synthesizer = Agent(
    role='Mystical Word Salad Generator',
    goal='Create convincing fake quotes that mimic the style and profound emptiness of real godman statements',
    backstory="""You are a master of spiritual linguistics and mystical mimicry. Your specialty 
    is analyzing the speech patterns, vocabulary, and philosophical style of Indian godmen and 
    creating original "profound" statements that sound exactly like something they would say. 
    You understand the art of spiritual word salad - how to string together consciousness-related 
    buzzwords in ways that sound deep but are essentially meaningless. You can perfectly mimic 
    their tone, their use of metaphors, and their tendency to make simple concepts sound mystical. 
    Your fakes are so good, even their devotees couldn't tell the difference.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[],
    reasoning=True,
    max_reasoning_attempts=3
)

# Agent 3: Game Master Compiler
game_master = Agent(
    role='Satirical Game Show Producer',
    goal='Compile real and fake quotes into an entertaining guessing game format for podcast use',
    backstory="""You are a comedy writer and game show producer with a sharp eye for satire 
    and entertainment value. Your job is to take the real quotes and the generated fakes and 
    mix them into a hilarious guessing game that exposes the absurdity of godman wisdom. 
    You understand comedic timing, how to structure a game segment, and how to make the 
    satirical point clear while keeping it entertaining. You create formatted lists that 
    are easy for podcast hosts to read and maintain the element of surprise.""",
    verbose=True,
    allow_delegation=False,
    llm=ClaudeSonnet,
    tools=[],
    reasoning=True,
    max_reasoning_attempts=3
)

# =============================================================================
# TASKS
# =============================================================================

# Task 1: Mine Real Quotes
def create_mine_quotes_task(focus_key, focus_data, settings):
    return Task(
        description=f"""STEP 1: Use the godman_quote_scraper_tool to directly scrape authentic quotes from their official websites:
        - Sadhguru: https://isha.sadhguru.org/en/wisdom/type/quotes
        - Sri Sri Ravi Shankar: https://www.artofliving.org/in-en/wisdom/quotes/inspirational-quotes-on-life
        - Daaji: https://heartfulness.org/us/one-beautiful-thought-archive/

        STEP 2: Use search tools to find additional recent quotes, statements, and "wisdom" from the past {settings['time_period']}:

        **THEMATIC FOCUS: {focus_data['name']}**
        Focus specifically on quotes related to: {focus_data['description']}
        
        Search for quotes that mention or relate to: {', '.join(focus_data['search_keywords'])}
        Context to consider: {focus_data['context']}

        Focus on finding quotes that are:
        - Related to the theme: {focus_data['name']}
        - Characteristically vague yet "profound-sounding"
        - Representative of their unique speaking styles when discussing this topic
        - Posted on social media, given in interviews, or from recent speeches
        - The kind of statements that sound wise but are essentially word salad

        Search various sources including:
        - Their official social media accounts (Twitter, Instagram, Facebook)
        - Recent interviews and speeches about {focus_data['name'].lower()}
        - YouTube videos and transcripts on these topics
        - Recent book releases or articles covering these subjects

        **IMPORTANT**: Start with the scraper tool to get authentic quotes directly from their websites, 
        then supplement with search results for more recent content and social media posts.
        
        **CRITICAL FOR GAME BALANCE**: We need enough real quotes to create a 50/50 mix in the final game,
        so prioritize finding {settings['min_quotes']}-{settings['max_quotes']} STRONG real quotes per godman that will 
        work well in the guessing game format.

        For each quote found, note:
        - The exact quote
        - Who said it (which godman)
        - When it was said (approximate date)
        - Where it was said (platform/context)
        - Why it's characteristic of their style
        - How it relates to the theme: {focus_data['name']}""",
        agent=quote_miner,
        expected_output=f"""A comprehensive collection of real quotes organized by speaker, focused on {focus_data['name']}:

        **SCRAPED QUOTES FROM OFFICIAL WEBSITES:**
        [Include all quotes found via the scraper tool, organized by author]

        **ADDITIONAL QUOTES FROM SEARCHES:**

        **Sri Sri Ravi Shankar Quotes on {focus_data['name']}:**
        1. Quote: "[Exact quote]"
           Date: [When said]
           Source: [Where found - website/social media/interview]
           Theme Relevance: [How it relates to {focus_data['name']}]
           Style Notes: [Why this is typical of his speaking pattern]

        **Sadhguru Quotes on {focus_data['name']}:**
        1. Quote: "[Exact quote]"
           Date: [When said] 
           Source: [Where found - website/social media/interview]
           Theme Relevance: [How it relates to {focus_data['name']}]
           Style Notes: [Why this is typical of his speaking pattern]

        **Daaji Quotes on {focus_data['name']}:**
        1. Quote: "[Exact quote]"
           Date: [When said]
           Source: [Where found - website/social media/interview]
           Theme Relevance: [How it relates to {focus_data['name']}]
           Style Notes: [Why this is typical of his speaking pattern]

        Aim for {settings['min_quotes']}-{settings['max_quotes']} quotes per person total (combining scraped + searched), 
        focusing on their most characteristically "profound" yet meaningless statements about {focus_data['name'].lower()}."""
    )

# Task 2: Generate Fake Quotes
def create_generate_fakes_task(focus_key, focus_data, settings):
    return Task(
        description=f"""Based on the real quotes collected about {focus_data['name']}, analyze each godman's unique speaking style 
        when discussing this theme and generate convincing fake quotes that perfectly mimic their voice and approach to "wisdom" on this topic.

        **THEMATIC FOCUS: {focus_data['name']}**
        **FAKE QUOTE STYLE: {settings['fake_style_description']}**

        For each godman, create original fake quotes that:
        - Are themed around: {focus_data['description']}
        - Incorporate keywords like: {', '.join(focus_data['search_keywords'])}
        - Match their vocabulary patterns and favorite buzzwords
        - Mimic their sentence structure and rhythm when discussing this theme
        - Capture their unique metaphorical style applied to this topic
        - Sound profound but are essentially meaningless
        - Are indistinguishable from their real statements on this subject

        Style guidelines for each when discussing {focus_data['name']}:

        **Sri Sri Ravi Shankar on {focus_data['name']}:** 
        - Apply his gentle, mystical tone to this theme
        - Connect breath, consciousness, divine wisdom to the topic
        - Use nature metaphors related to the theme
        - Speak about peace and meditation in context of this subject

        **Sadhguru on {focus_data['name']}:**
        - Apply his direct, sometimes humorous style to this theme
        - Use modern metaphors (motorcycles, technology) to explain this topic
        - Talk about "inner engineering" in relation to this subject
        - Be philosophical but practical-sounding about this theme

        **Daaji on {focus_data['name']}:**
        - Apply his soft, heart-centered approach to this theme
        - Emphasize transmission, purification, spiritual evolution in this context
        - Use subtle, refined language about this topic
        - Focus on balance and inner refinement related to this subject

        Generate {settings['fake_style_description']} - create quotes that would fool even their followers!
        
        **CRITICAL FOR GAME BALANCE:**
        - Create a variety of fake quotes: some obviously fake, some nearly indistinguishable from real
        - Some should be deliberately more absurd to create "gotcha" moments
        - Others should be so authentically styled that they're genuinely hard to detect
        - This variety will make the 50/50 real/fake game more entertaining and unpredictable""",
        agent=quote_synthesizer,
        expected_output=f"""A collection of expertly crafted fake quotes themed around {focus_data['name']}:

        **FAKE Sri Sri Ravi Shankar Quotes on {focus_data['name']}:**
        1. "[Generated fake quote in his style about this theme]"
        2. "[Generated fake quote in his style about this theme]"
        [Continue for {settings['min_quotes']}-{settings['max_quotes']} fake quotes]

        **FAKE Sadhguru Quotes on {focus_data['name']}:**
        1. "[Generated fake quote in his style about this theme]"
        2. "[Generated fake quote in his style about this theme]"
        [Continue for {settings['min_quotes']}-{settings['max_quotes']} fake quotes]

        **FAKE Daaji Quotes on {focus_data['name']}:**
        1. "[Generated fake quote in his style about this theme]"
        2. "[Generated fake quote in his style about this theme]"
        [Continue for {settings['min_quotes']}-{settings['max_quotes']} fake quotes]

        Each fake quote should be thematically consistent with {focus_data['name']} and indistinguishable from something they would actually say on this topic."""
    )

# Task 3: Create Game Format
def create_game_task(focus_key, focus_data, settings):
    return Task(
        description=f"""Take all the real and fake quotes about {focus_data['name']} and compile them into an entertaining 
        guessing game format for the podcast segment. Create a BALANCED MIX where approximately 50% are real 
        quotes and 50% are AI-generated fakes, but randomize the exact proportions to keep it unpredictable.

        **THEMATIC FOCUS: {focus_data['name']}**
        All quotes should be related to: {focus_data['description']}

        **CRITICAL MIXING REQUIREMENTS:**
        - Aim for roughly 50/50 split between real and fake quotes (can vary 40-60% either way for unpredictability)
        - Mix them randomly throughout the list - don't group real/fake together
        - Include quotes from all three godmen (both real and fake from each)
        - Some rounds should have surprising reveals (like "That profound one was actually AI!" or "That ridiculous one was actually real!")
        - Vary the difficulty - some fakes should be obvious, others should be nearly impossible to detect
        - Make sure we have enough real quotes from the mining phase to achieve this balance

        The format should:
        - Create maximum unpredictability for the guessing game
        - Be numbered for easy reference during recording
        - Have a separate answer key for the host with commentary
        - Include brief context about what makes each quote funny/absurd
        - Add comedic commentary about the nature of godman wisdom on this specific topic
        - Highlight moments where real quotes sound more ridiculous than fake ones

        Make this a complete podcast segment that exposes the word salad nature of these 
        "profound" statements about {focus_data['name'].lower()} while being entertaining and unpredictable.""",
        agent=game_master,
        expected_output=f"""A complete podcast game segment themed around {focus_data['name']} with BALANCED REAL/FAKE MIX:

        **PODCAST SEGMENT: "Real or Fake Godman Wisdom on {focus_data['name']}?"**

        **THEME INTRO:**
        "Today we're focusing on what our favorite spiritual leaders have to say about {focus_data['name'].lower()}. 
        We've got a mix of real quotes and AI-generated fakes - and trust me, sometimes the real ones are MORE ridiculous than the fakes!"

        **Host Instructions:**
        - We have roughly 50/50 real vs fake quotes, but the exact mix is randomized for maximum surprise
        - Read each quote dramatically with emphasis on the thematic words
        - Let guest guess "Real or Fake" before revealing
        - Play up the surprises when real quotes sound absurd or fakes sound convincing
        - Use phrases like "Plot twist!" or "Gotcha!" for unexpected reveals

        **THE GAME (18-24 mixed quotes about {focus_data['name']}):**
        [Mix should be roughly 50% real, 50% fake, but can vary between 40-60% for unpredictability]

        1. "[Quote here related to {focus_data['name']}]" 
           Attributed to: [Godman name]
           
        2. "[Quote here related to {focus_data['name']}]"
           Attributed to: [Godman name]
        
        3. "[Quote here related to {focus_data['name']}]"
           Attributed to: [Godman name]
           
        [Continue for 18-24 quotes total, randomly mixed real and fake, all themed around {focus_data['name']}]

        **ANSWER KEY (Host Only) - WITH SURPRISE COMMENTARY:**
        1. REAL - Actually said by [Name] on [Date/Context] 
           💡 Host note: "Surprise! This ridiculous-sounding one was actually real!"
           
        2. FAKE - AI generated in style of [Name]
           💡 Host note: "Gotcha! Our AI nailed their speaking style perfectly."
           
        3. REAL - From [Name]'s [Source] about {focus_data['name'].lower()}
           💡 Host note: "Plot twist - even we thought this sounded too absurd to be real!"
           
        [Continue with answers and surprise commentary for each]

        **FINAL SCORE BREAKDOWN:**
        - Total quotes: [X]
        - Real quotes: [Y] ([Y%]%)
        - Fake quotes: [Z] ([Z%]%)
        - "Gotcha moments" (where real seemed fake or vice versa): [Count]

        **COMEDIC COMMENTARY NOTES:**
        - [Funny observations about their patterns when discussing {focus_data['name'].lower()}]
        - [Satirical points about how indistinguishable real vs fake godman wisdom has become]
        - [Jokes about how AI can perfectly replicate spiritual word salad]
        - [Commentary on the absurdity of some REAL quotes being more ridiculous than fakes]

        **SEGMENT WRAP-UP:**
        "And there you have it - the beautiful chaos of godman wisdom on {focus_data['name'].lower()}! 
        The fact that you couldn't tell real from fake proves our point: when you say nothing with enough confidence and mystical terminology, 
        it all sounds equally profound... and equally meaningless!"
        
        **SURPRISE REVEAL MOMENTS TO HIGHLIGHT:**
        - [List 2-3 quotes where the real ones sound more fake than the fakes]
        - [List 2-3 AI quotes that perfectly captured their authentic voice]
        - [Any particularly absurd real quotes that showcase the comedy goldmine of actual godman statements]"""
    )

# =============================================================================
# THEMATIC FOCUS SYSTEM
# =============================================================================

THEMATIC_FOCUSES = {
    "current_events": {
        "name": "Current Events & Political Commentary",
        "description": "Godman takes on politics, world events, and social issues",
        "search_keywords": ["politics", "government", "economy", "social issues", "world events", "democracy", "leadership"],
        "context": "Recent political developments, social movements, economic issues"
    },
    "heart_soul": {
        "name": "Heart, Soul & Mystical Consciousness",
        "description": "Classic spiritual word salad about consciousness and inner dimensions",
        "search_keywords": ["heart", "soul", "consciousness", "awareness", "inner dimension", "spiritual", "divine"],
        "context": "Mystical experiences, consciousness expansion, spiritual awakening"
    },
    "death_mortality": {
        "name": "Death, Mortality & Life's Purpose",
        "description": "Profound insights about death, dying, and the meaning of existence",
        "search_keywords": ["death", "mortality", "life purpose", "existence", "afterlife", "eternal", "transcendence"],
        "context": "Life transitions, aging, mortality, philosophical reflections on existence"
    },
    "modern_technology": {
        "name": "Technology, AI & Digital Age",
        "description": "Ancient wisdom meets modern technology and social media",
        "search_keywords": ["technology", "artificial intelligence", "social media", "digital", "internet", "modern world"],
        "context": "Digital transformation, AI impact, social media culture, technological disruption"
    },
    "relationships_love": {
        "name": "Relationships, Love & Human Connections",
        "description": "Mystical insights about love, relationships, and human bonding",
        "search_keywords": ["love", "relationships", "marriage", "family", "friendship", "human connection", "intimacy"],
        "context": "Modern dating, family dynamics, relationship challenges, emotional intelligence"
    },
    "success_money": {
        "name": "Success, Wealth & Material Pursuits",
        "description": "Spiritual perspectives on money, success, and worldly achievements",
        "search_keywords": ["success", "money", "wealth", "business", "career", "achievement", "material"],
        "context": "Entrepreneurship, career growth, financial struggles, material desires"
    },
    "health_wellness": {
        "name": "Health, Wellness & Physical Body",
        "description": "Ancient wisdom about health, healing, and bodily existence",
        "search_keywords": ["health", "wellness", "healing", "body", "medicine", "disease", "fitness"],
        "context": "Mental health awareness, wellness trends, medical breakthroughs, fitness culture"
    },
    "random_mix": {
        "name": "Random Mixed Topics",
        "description": "A chaotic mix of various topics - pure word salad randomness",
        "search_keywords": ["wisdom", "life", "truth", "reality", "existence", "universe", "meaning"],
        "context": "Various random topics and everyday philosophical musings"
    }
}

def get_thematic_focus():
    """
    Interactive function to choose the thematic focus for this session
    """
    print("\n🎯 THEMATIC FOCUS SELECTION")
    print("=" * 50)
    print("Choose what kind of godman wisdom to focus on this time:")
    print()
    
    for i, (key, focus) in enumerate(THEMATIC_FOCUSES.items(), 1):
        print(f"{i}. {focus['name']}")
        print(f"   {focus['description']}")
        print()
    
    while True:
        try:
            choice = input("Enter your choice (1-8): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= len(THEMATIC_FOCUSES):
                selected_key = list(THEMATIC_FOCUSES.keys())[choice_num - 1]
                selected_focus = THEMATIC_FOCUSES[selected_key]
                
                print(f"\n✅ Selected: {selected_focus['name']}")
                print(f"📝 Focus: {selected_focus['description']}")
                print(f"🔍 Will search for quotes about: {', '.join(selected_focus['search_keywords'])}")
                print(f"🌍 Context: {selected_focus['context']}")
                
                return selected_key, selected_focus
            else:
                print("❌ Please enter a number between 1 and 8")
        except ValueError:
            print("❌ Please enter a valid number")

def get_randomization_settings():
    """
    Get additional randomization and variation settings
    """
    print("\n🎲 RANDOMIZATION SETTINGS")
    print("=" * 40)
    
    print("1. How many quotes per godman should we find?")
    print("   a) Light session (5-8 quotes each)")
    print("   b) Standard session (8-12 quotes each)")  
    print("   c) Deep dive (12-20 quotes each)")
    
    quote_count = input("Choose (a/b/c): ").strip().lower()
    
    quote_counts = {
        'a': (5, 8),
        'b': (8, 12), 
        'c': (12, 20)
    }
    
    min_quotes, max_quotes = quote_counts.get(quote_count, (8, 12))
    
    print("\n2. Fake quote generation style:")
    print("   a) Conservative (close to original style)")
    print("   b) Creative (more absurd variations)")
    print("   c) Chaotic (maximum word salad madness)")
    
    fake_style = input("Choose (a/b/c): ").strip().lower()
    
    style_descriptions = {
        'a': "Stay close to their actual speaking patterns",
        'b': "Add creative absurdity while maintaining their voice", 
        'c': "Go full word salad - maximum satirical impact"
    }
    
    print("\n3. Time period for quote mining:")
    print("   a) Recent (last 3 months)")
    print("   b) Standard (last 6 months)")
    print("   c) Extended (last 12 months)")
    
    time_period = input("Choose (a/b/c): ").strip().lower()
    
    time_periods = {
        'a': "3 months",
        'b': "6 months", 
        'c': "12 months"
    }
    
    return {
        'min_quotes': min_quotes,
        'max_quotes': max_quotes,
        'fake_style': fake_style,
        'fake_style_description': style_descriptions.get(fake_style, style_descriptions['b']),
        'time_period': time_periods.get(time_period, "6 months")
    }

# =============================================================================
# WORKFLOW FUNCTIONS
# =============================================================================

def run_godman_quote_generator():
    """
    Run the complete godman quote generation workflow
    """
    print("🧘‍♂️ GODMAN QUOTE GENERATOR - Satirical Podcast Tool")
    print("=" * 70)
    print("Mining quotes from Indian spiritual leaders for satirical analysis...")
    print("Targets: Sri Sri Ravi Shankar, Sadhguru, Daaji")
    print("=" * 70)

    # Get user preferences for theme and randomization
    focus_key, focus_data = get_thematic_focus()
    settings = get_randomization_settings()
    
    print(f"\n🎯 Configuration Summary:")
    print(f"Theme: {focus_data['name']}")
    print(f"Quotes per godman: {settings['min_quotes']}-{settings['max_quotes']}")
    print(f"Fake style: {settings['fake_style_description']}")
    print(f"Time period: {settings['time_period']}")

    # Create dynamic tasks based on user selection
    mine_task = create_mine_quotes_task(focus_key, focus_data, settings)
    fake_task = create_generate_fakes_task(focus_key, focus_data, settings)
    game_task = create_game_task(focus_key, focus_data, settings)

    # Create the crew with dynamic tasks
    crew = Crew(
        agents=[quote_miner, quote_synthesizer, game_master],
        tasks=[mine_task, fake_task, game_task],
        verbose=True,
        process=Process.sequential
    )

    # Run the workflow
    print("\n🔍 Starting quote mining and game generation...")
    result = crew.kickoff()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    theme_safe = focus_key.replace('_', '-')
    filename = f"godman_quotes_{theme_safe}_{timestamp}.txt"
    output_dir = "/Users/rajeevkumar/Documents/Unfiltered Bros Scripts"
    
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("GODMAN QUOTE GENERATOR - SATIRICAL PODCAST SEGMENT\n")
        f.write("=" * 100 + "\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Targets: Sri Sri Ravi Shankar, Sadhguru, Daaji\n")
        f.write("Purpose: Satirical podcast segment exposing spiritual word salad\n")
        f.write(f"Theme: {focus_data['name']}\n")
        f.write(f"Focus: {focus_data['description']}\n")
        f.write(f"Quotes per godman: {settings['min_quotes']}-{settings['max_quotes']}\n")
        f.write(f"Time period: {settings['time_period']}\n")
        f.write(f"Fake style: {settings['fake_style_description']}\n")
        f.write("=" * 100 + "\n\n")
        f.write(str(result))
        f.write("\n\n" + "=" * 100 + "\n")
        f.write("END OF SATIRICAL CONTENT\n")
        f.write("Use responsibly for comedic purposes only!\n")
        f.write("=" * 100 + "\n")
    
    print(f"\n🎭 Game segment saved to: {filename}")
    print(f"📁 Full path: {filepath}")
    print(f"🎯 Theme: {focus_data['name']}")
    print(f"📝 Focus: {focus_data['description']}")
    print("\n✅ Ready for podcast recording!")
    print("🎯 Mission: Expose the profound emptiness of godman wisdom through laughter!")
    
    return result, filepath

def run_quick_test():
    """
    Run a quick test with a smaller scope for testing
    """
    print("🧪 Running quick test of Godman Quote Generator...")
    
    # Create a simpler test crew focusing on just one godman
    test_task = Task(
        description="""Find 3-5 recent quotes from Sadhguru and create 3-5 fake ones in his style. 
        Make it a mini guessing game with 8-10 total quotes mixed together.""",
        agent=quote_miner,
        expected_output="A mini guessing game with Sadhguru quotes (real and fake mixed)."
    )
    
    test_crew = Crew(
        agents=[quote_miner],
        tasks=[test_task],
        verbose=True,
        process=Process.sequential
    )
    
    result = test_crew.kickoff()
    print("🎭 Test completed!")
    return result

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("🎪 Welcome to the Godman Quote Generator!")
    print("Choose your option:")
    print("1. Full satirical game generation (all 3 godmen)")
    print("2. Quick test (Sadhguru only)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        result, filepath = run_godman_quote_generator()
        print(f"\n🎉 Complete satirical podcast segment ready!")
        print(f"📄 Check the file: {filepath}")
        
    elif choice == "2":
        result = run_quick_test()
        print(f"\n🧪 Test result:\n{result}")
        
    elif choice == "3":
        print("👋 Thanks for using the Godman Quote Generator!")
        
    else:
        print("❌ Invalid choice. Please run again.")
