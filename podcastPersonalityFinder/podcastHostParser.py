import re
import json

class PodcastHostParser:
    def __init__(self, file_path):
        """
        Initialize the parser with a file path
        
        :param file_path: Path to the text file containing podcast host information
        """
        self.file_path = file_path
        self.podcasts = {
            'small': [],
            'medium': [],
            'large': []
        }

    def _clean_text(self, text):
        """
        Clean and normalize text
        
        :param text: Input text
        :return: Cleaned text
        """
        return text.strip().replace('\n', ' ')

    def parse(self):
        """
        Parse the podcast host information file
        
        :return: Dictionary of parsed podcasts by tier
        """
        with open(self.file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Detect current tier
        current_tier = None
        tier_patterns = {
            'small': r'Small Podcasts \(0-1,000 subscribers\)',
            'medium': r'Medium Podcasts \(1,000-10,000 subscribers\)',
            'large': r'Large Podcasts \(10,000\+ subscribers\)'
        }

        # Split content into podcast entries
        podcast_entries = re.split(r'\n\s*\d+\.', content)
        
        for entry in podcast_entries[1:]:  # Skip first empty split
            # Determine current tier
            for tier, pattern in tier_patterns.items():
                if re.search(pattern, entry, re.IGNORECASE):
                    current_tier = tier
                    break

            if not current_tier:
                continue

            # Extract podcast name (first line)
            name_match = re.search(r'^(.+?)(?=\n-)', entry, re.DOTALL)
            if not name_match:
                continue
            podcast_name = self._clean_text(name_match.group(1))

            # Extract hosts
            hosts_match = re.search(r'- Hosts?:\s*(.+?)(?=\n-)', entry, re.DOTALL)
            hosts = self._clean_text(hosts_match.group(1)) if hosts_match else 'Unknown'

            # Extract verified email addresses
            emails_match = re.search(r'- Verified Email Addresses?:\s*(.+?)(?=\n-)', entry, re.DOTALL)
            emails = self._clean_text(emails_match.group(1)) if emails_match else 'No email found'

            # Extract alternative contact methods
            contacts_match = re.search(r'- Alternative Contact Methods:\s*(.+?)(?=\n-)', entry, re.DOTALL)
            alternative_contacts = self._clean_text(contacts_match.group(1)) if contacts_match else 'No alternative contacts'

            # Extract contact approach notes
            notes_match = re.search(r'- Notes on Contact Approach:\s*(.+?)(?=$)', entry, re.DOTALL)
            contact_notes = self._clean_text(notes_match.group(1)) if notes_match else 'No specific notes'

            # Create podcast entry
            podcast_entry = {
                'name': podcast_name,
                'hosts': hosts,
                'verified_emails': emails,
                'alternative_contacts': alternative_contacts,
                'contact_notes': contact_notes
            }

            # Add to appropriate tier
            self.podcasts[current_tier].append(podcast_entry)

        return self.podcasts

    def save_to_json(self, output_path='podcast_hosts.json'):
        """
        Save parsed podcasts to a JSON file
        
        :param output_path: Path to save JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(self.podcasts, file, indent=2)

def main():
    # Example usage
    input_file = input("Enter the path to the podcast hosts text file: ")
    parser = PodcastHostParser(input_file)
    
    # Parse podcasts
    parsed_podcasts = parser.parse()
    
    # Print parsed podcasts
    for tier, podcasts in parsed_podcasts.items():
        print(f"\n{tier.capitalize()} Podcasts:")
        for podcast in podcasts:
            print(f"- {podcast['name']}")
    
    # Optional: Save to JSON
    save_option = input("\nDo you want to save the parsed podcasts to a JSON file? (yes/no): ").lower()
    if save_option in ['yes', 'y']:
        parser.save_to_json()
        print("Podcasts saved to podcast_hosts.json")

if __name__ == '__main__':
    main()
