from tavilyBrosRiffnSearcher import process_search_results
import anthropic
import config
import os

# Set up the environment variables for API keys
os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY

# Define the bullet points for research
input_text = """"
The European Enlightenment had a significant impact on shaming culture. The emphasis on reason, individualism, and personal autonomy led to a shift from shaming as a means of social control to more nuanced forms of correction and critique.”,
Power asymmetry plays a significant role in shaming and critiquing. In many societies, those in positions of power use shaming as a means of maintaining control over marginalized groups. This can be seen in the way that racial and ethnic minorities are often shamed and stigmatized for their cultural practices or identities.”,
In contemporary culture, social media has become a platform for public shaming, where individuals can be vilified and ostracized for their actions or opinions. This has led to a culture of outrage and moral posturing, where shaming is used as a means of asserting moral superiority.”,
In many Indigenous cultures, shaming is not a common practice. Instead, they use storytelling, ridicule, and teasing to correct behavior. For example, in some Native American communities, individuals who misbehave are teased and ridiculed in front of the community, but this is done in a lighthearted manner to correct behavior rather than to shame.”,
In some African cultures, shaming is used as a last resort, and only when all other methods of correction have failed. For instance, in some Yoruba communities, shaming is used to correct behavior, but it's done in a way that's respectful and focused on rehabilitation rather than punishment.”,
In some European cultures, shaming was historically used as a means of social control. During the Middle Ages, public shaming was a common practice, where individuals who committed crimes or broke social norms were humiliated in public. This practice was later abolished, but the legacy of shaming as a means of control continues to influence modern European cultures.”,
""".split("\n\n")

if __name__ == '__main__':
    # Process each bullet point to generate search queries
    search_queries = []
    for bullet_point in input_text:
        print(bullet_point)
        result = process_search_results(bullet_point)
        if result is not None:
            search_queries.append(result)


    # Perform searches using Tavily Search
    search_results = []
    for query in search_queries:
        result = process_search_results(query)
        search_results.append(result)
        print("I'm in the next step")
        print(result)
    # Concatenate the search results into a single string
    search_summary = "\n".join(search_results)

    # Set up the Anthropic client
    anthropic_client = anthropic.Anthropic(
        api_key=config.ANTHROPIC_API_KEY,
    )

    # Define the prompt for Anthropic
    prompt = f"""
    As a knowledgeable podcast researcher, your task is to analyze the provided search results and extract key insights, background information, and thought-provoking ideas related to the topic of "Gaming, holding, and chewing out in Indian cultural settings, examining cultural norms of discipline and communication in Indian society and beyond".

    Your goal is to distill the information gathered from the search results and present it in a structured and concise manner, focusing on the most relevant and interesting aspects that can fuel an engaging podcast discussion. Consider the following guidelines when processing the search results:

    1. Identify the main themes, patterns, and cultural nuances that emerge from the search results.
    2. Highlight key historical events, societal trends, and influential figures related to the topic.
    3. Extract thought-provoking quotes, anecdotes, or examples that can spark interesting conversations.
    4. Provide necessary context and background information to help the podcast host and listeners better understand the subject matter.
    5. Suggest potential discussion points, questions, or angles that the podcast host can explore during the episode.

    Here are the search results to analyze:
    {chr(10).join(search_queries)}

    Please process the search results and generate a summary of the most relevant insights if possible, but if necessary expand on topics that require indepth considersation, background information, and discussion points. The output should serve as a valuable resource for the podcast host to refer to while preparing for and conducting the episode.
    """

    response = anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=2000,
        temperature=0.8,
        system="You are a knowledgeable podcast researcher with a keen eye for distilling insights from search results and providing valuable background information for engaging podcast discussions.",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Extract the generated script from the response
    script = response.content[0].text
    topic_words = input_text[0].split()[:2]  # Take the first two words from the first bullet point
    topic_file_name = "_".join(topic_words)
    # Save the generated script to a file
    output_file = f"/Users/rajeevkumar/Documents/TISB Stuff/brosRiffnScripts/{topic_file_name}_podcast_script.txt"
    with open(output_file, "w") as file:
        file.write(script)

    print(f"Generated script saved to: {output_file}")