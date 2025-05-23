import os
import re
import markdown2
from typing import Dict, Optional

class PodcastOutreachEmailGenerator:
    def __init__(self, input_file: str):
        """
        Initialize the email generator with a markdown file of podcast hosts
        
        :param input_file: Path to the markdown file containing podcast host information
        """
        self.input_file = input_file
        self.podcasts = self._parse_markdown()

    def _parse_markdown(self) -> Dict[str, Dict]:
        """
        Parse the markdown file and extract podcast information
        
        :return: Dictionary of podcasts with their details
        """
        with open(self.input_file, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        
        # Split content by podcast tiers
        tiers = {
            'small': r'## Small Podcasts \(0-1000 subscribers\)',
            'medium': r'## Medium Podcasts \(1000-10,000 subscribers\)',
            'large': r'## Large Podcasts \(10,000\+ subscribers\)'
        }
        
        podcasts = {}
        for tier, tier_header in tiers.items():
            tier_content = re.search(f'{tier_header}(.*?)(?=##|$)', markdown_content, re.DOTALL)
            if tier_content:
                tier_podcasts = self._extract_podcasts(tier_content.group(1), tier)
                podcasts.update(tier_podcasts)
        
        return podcasts

    def _extract_podcasts(self, tier_content: str, tier: str) -> Dict[str, Dict]:
        """
        Extract individual podcast details from tier content
        
        :param tier_content: Markdown content for a specific tier
        :param tier: Podcast tier (small/medium/large)
        :return: Dictionary of podcasts in this tier
        """
        podcast_matches = re.finditer(r'### \d+\. \*\*(.*?)\*\*\n((?:- \*\*.*?\*\*: .*\n)+)', tier_content, re.DOTALL)
        
        podcasts = {}
        for match in podcast_matches:
            podcast_name = match.group(1)
            details_block = match.group(2)
            
            podcast_details = {}
            for detail_line in details_block.split('\n'):
                if detail_line.strip():
                    key, value = re.match(r'- \*\*(.*?)\*\*: (.*)', detail_line).groups()
                    podcast_details[key.lower().replace(' ', '_')] = value
            
            podcast_details['tier'] = tier
            podcasts[podcast_name] = podcast_details
        
        return podcasts

    def generate_emails(self, output_dir: str = 'podcast_outreach_emails'):
        """
        Generate personalized emails for podcasts with verified email addresses
        
        :param output_dir: Directory to save generated emails
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for podcast_name, podcast_details in self.podcasts.items():
            # Skip if no verified email
            if not podcast_details.get('verified_email_address') or 'not verified' in podcast_details.get('verified_email_address', '').lower():
                continue
            
            email_content = self._craft_email(podcast_name, podcast_details)
            
            # Sanitize filename
            safe_filename = re.sub(r'[^\w\-_\. ]', '_', podcast_name)
            email_file_path = os.path.join(output_dir, f'{safe_filename}_outreach_email.txt')
            
            with open(email_file_path, 'w', encoding='utf-8') as email_file:
                email_file.write(email_content)
            
            print(f"Generated email for {podcast_name}")

    def _craft_email(self, podcast_name: str, podcast_details: Dict) -> str:
        """
        Craft a personalized email based on podcast tier and context
        
        :param podcast_name: Name of the podcast
        :param podcast_details: Dictionary of podcast details
        :return: Personalized email content
        """
        host_name = podcast_details.get('host_name', 'Podcast Host')
        email = podcast_details.get('verified_email_address', '')
        contact_notes = podcast_details.get('notes_on_contact_approach', '')
        tier = podcast_details.get('tier', 'small')
        
        # Base email template
        email_template = f"""Subject: Revolutionize Your Podcast Growth with Podcast Bots

Dear {host_name},

I hope this email finds you well. I'm reaching out from Podcast Bots, an innovative AI-powered platform designed to transform how podcasters discover and connect with guests.

"""
        
        # Tier-specific messaging
        if tier == 'small':
            email_template += f"""As a fellow creator in the {podcast_name} space, we understand the challenges of growing a podcast audience. Our AI-driven platform is specifically designed to help emerging podcasts like yours break through the noise.

Our system analyzes 300+ data points to match you with guests that will:
• Elevate your content quality
• Attract new listeners
• Expand your podcast's reach

"""
        elif tier == 'medium':
            email_template += f"""We've been following {podcast_name} and are impressed by your growth trajectory. Our AI-powered guest matching system is designed to take podcasts like yours to the next level.

With Podcast Bots, you'll:
• Discover guests with laser-focused relevance
• Optimize your guest selection strategy
• Accelerate your podcast's growth potential

"""
        else:  # large tier
            email_template += f"""As a successful podcast in the {podcast_name} space, we recognize the importance of continual innovation and audience expansion.

Podcast Bots offers:
• Advanced guest discovery across diverse domains
• AI-driven insights for content diversification
• Strategies to explore new audience segments

"""
        
        # Contextual personalization
        if contact_notes:
            email_template += f"""We were particularly intrigued by your focus on {contact_notes}. Our platform is designed to help creators like you find guests that deeply resonate with your unique mission.

"""
        
        # Closing and call-to-action
        email_template += f"""We're currently selecting beta testers for Podcast Bots, and we believe {podcast_name} would be an incredible partner in shaping the future of podcast guest discovery.

Would you be interested in a quick 15-minute demo to see how we can supercharge your podcast's potential?

Best regards,
The Podcast Bots Team

P.S. Reply to this email or book a demo at [Your Booking Link]
"""
        
        return email_template

def main():
    # Example usage
    input_file = input("Enter the path to the podcast hosts markdown file: ")
    generator = PodcastOutreachEmailGenerator(input_file)
    generator.generate_emails()

if __name__ == '__main__':
    main()
