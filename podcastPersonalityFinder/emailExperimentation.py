from intelligentEmailerClass import EmailCrafter, LLMEmailCrafter

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

email_crafter = EmailCrafter(host_info["name"], host_info["podcast_name"], host_info["mission"], host_info["contact_info"])

guest_info = {
    "name": "Jane Smith",
    "title": "Dr.",
    "work_summary": "your groundbreaking research on quantum computing and its potential applications in solving complex societal issues"
}
email_body = email_crafter.craft_email(guest_info, guest_info["work_summary"])
print(email_body)

# Example usage
host_info = {
    "name": "Rajeev Kumar",
}

podcast_info = {
    "name": "The Idea Sandbox",
    "mission": "Our mission is rooted in the conviction that while legislative efforts are necessary, they are insufficient to usher in a brighter future. We believe that true transformation comes from embracing and promoting enlightenment ideas that encourage us to think deeper, live fully, and engage with the world and each other more meaningfully.",
    "contact_info": "Email: theideasandboxpodcast@gmail.com, Website: https://tisb.world, WhatsApp: +13096797200"
}

llm_model = LLM()  # Placeholder for actual LLM initialization
email_crafter = LLMEmailCrafter(host_info, podcast_info, llm_model)

guest_info = {
    "name": "Dr. Jane Smith",
    "title": "Professor",
    "work_summary": "groundbreaking research on quantum computing and its potential applications in solving complex societal issues"
}

email_body = email_crafter.craft_email(guest_info, guest_info["work_summary"])
print(email_body)