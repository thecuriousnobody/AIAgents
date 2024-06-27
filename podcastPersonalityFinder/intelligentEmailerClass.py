import random

class EmailCrafter:
    def __init__(self, host_name, podcast_name, podcast_mission, contact_info):
        self.host_name = host_name
        self.podcast_name = podcast_name
        self.podcast_mission = podcast_mission
        self.contact_info = contact_info

    def craft_email(self, guest_info, guest_work_summary):
        # Structure the email
        greeting = self._create_greeting(guest_info['name'], guest_info['title'])
        introduction = self._create_introduction()
        guest_relevance = self._create_guest_relevance(guest_work_summary)
        invitation = self._create_invitation()
        closing = self._create_closing()

        # Combine all parts
        email_body = f"{greeting}\n\n{introduction}\n\n{guest_relevance}\n\n{invitation}\n\n{closing}"
        return email_body

    def _create_greeting(self, guest_name, guest_title):
        return f"Dear {guest_title} {guest_name},"

    def _create_introduction(self):
        intros = [
            f"I hope this email finds you well. My name is {self.host_name}, and I'm the host of {self.podcast_name}, a platform dedicated to exploring thought-provoking ideas and fostering meaningful conversations.",
            f"I trust this message reaches you in good spirits. I am {self.host_name}, the host of {self.podcast_name}, a podcast committed to harvesting and disseminating ideas across borders for humanity's collective flourishing.",
            f"I hope this message finds you well. My name is {self.host_name}, and I am reaching out to you with great admiration for your work. I am the host of {self.podcast_name}, a platform dedicated to shifting societal conversations towards a more scientific temper and fostering enlightened beliefs."
        ]
        return random.choice(intros)

    def _create_guest_relevance(self, guest_work_summary):
        return f"As I dove into your work, I was struck by {guest_work_summary}. Your expertise and insights align perfectly with the ethos of {self.podcast_name}. {self.podcast_mission}"

    def _create_invitation(self):
        return f"It would be an honor to have you as a guest on the podcast. I believe your voice and insights would resonate deeply with our audience and contribute to a nuanced understanding of these crucial themes."

    def _create_closing(self):
        return f"If you're open to the idea, I'd love to discuss further and find a mutually convenient time for the recording. Please feel free to reach out to me directly at {self.contact_info['email']}, or visit our website at {self.contact_info['website']}. You can also connect with me on WhatsApp at {self.contact_info['whatsapp']}.\n\nThank you for your time and consideration. I look forward to the possibility of engaging in a thought-provoking dialogue with you.\n\nWarm regards,\n{self.host_name}\nHost, {self.podcast_name}"

# Example usage
host_info = {
    "name": "Rajeev Kumar",
    "podcast_name": "The Idea Sandbox",
    "mission": "Our mission is rooted in the conviction that while legislative efforts are necessary, they are insufficient to usher in a brighter future. We believe that true transformation comes from embracing and promoting enlightenment ideas that encourage us to think deeper, live fully, and engage with the world and each other more meaningfully.",
    "contact_info": {
        "email": "theideasandboxpodcast@gmail.com",
        "website": "https://tisb.world",
        "whatsapp": "+13096797200"
    }
}


from some_llm_library import LLM  # Placeholder for actual LLM library

class LLMEmailCrafter:
    def __init__(self, host_info, podcast_info, llm_model):
        self.host_info = host_info
        self.podcast_info = podcast_info
        self.llm = llm_model

    def craft_email(self, guest_info, guest_work_summary):
        prompt = self._create_prompt(guest_info, guest_work_summary)
        email_body = self.llm.generate(prompt)
        return email_body

    def _create_prompt(self, guest_info, guest_work_summary):
        prompt = f"""
        Task: Craft a personalized email inviting a guest to appear on a podcast.

        Host Information:
        - Name: {self.host_info['name']}
        - Podcast: {self.podcast_info['name']}
        - Mission: {self.podcast_info['mission']}

        Guest Information:
        - Name: {guest_info['name']}
        - Title: {guest_info['title']}
        - Work Summary: {guest_work_summary}

        Email Guidelines:
        1. Use a warm, personal tone that reflects the host's passion for ideas and intellectual discourse.
        2. Highlight the guest's work and its relevance to the podcast's mission.
        3. Emphasize the potential for a meaningful, thought-provoking conversation.
        4. Include the podcast's contact information: {self.podcast_info['contact_info']}
        5. Keep the email concise but impactful, around 250-350 words.
        6. Avoid clichés and overly formal language. Aim for authenticity and genuine enthusiasm.
        7. Incorporate elements of the podcast's mission: harvesting ideas, fostering enlightened beliefs, and promoting societal progress through thought.

        Please generate a complete email based on these guidelines.
        """
        return prompt

