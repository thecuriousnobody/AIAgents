import re

def extract_guest_info(guest_entry):
    name_match = re.search(r'^(.*?)\s*-', guest_entry)
    description_match = re.search(r'-\s*(.*?)\s*$', guest_entry)
    contact_match = re.search(r'\s*(.*?)\s*$', guest_entry)

    name = name_match.group(1).strip() if name_match else ''
    description = description_match.group(1).strip() if description_match else ''
    contact = contact_match.group(1).strip() if contact_match else ''

    return name, description, contact

def process_guest_list(input_text):
    guest_list = []
    for guest_entry in input_text.strip().split("\n"):
        if guest_entry.strip() and not guest_entry.startswith("guest_list = \"\"\""):
            name, description, contact = extract_guest_info(guest_entry)
            if name:
                guest_info = {
                    'name': name,
                    'description': description,
                    'contact': contact
                }
                guest_list.append(guest_info)
    return guest_list