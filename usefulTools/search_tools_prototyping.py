

import requests

searchAPIKeys = "QDmDPMU2JT3fhZL13q6aD6hk"
from crewai_tools import Tool
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities import GoogleSerperAPIWrapper
ClaudeSonnet = ChatAnthropic(model="claude-3-5-sonnet-20240620")
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

os.environ["SERPER_API_KEY"] = "0a49b8ac6532a531cca6f928e1c5a04bc580e547"


url = "https://www.searchapi.io/api/v1/search"
params = {
  "engine": "google",
  "q": "Oron Catts, Semi Living Tissue",
  "api_key": config.SEARCH_API_KEY
}


response = requests.get(url, params = params)
print(response.text)



# llm = ClaudeSonnet
# search = GoogleSerperAPIWrapper()
# tools = [
#     Tool(
#         name="Intermediate Answer",
#         func=search.run,
#         description="useful for when you need to ask with search"
#     )
# ]


# self_ask_with_search = initialize_agent(tools, llm, agent=AgentType.SELF_ASK_WITH_SEARCH, verbose=True)
# self_ask_with_search.run("Oron Catts, semi-living tissue")

# import http.client
# import json

# conn = http.client.HTTPSConnection("google.serper.dev")
# payload = json.dumps({
#   "q": "Oron Catts, Semi Living Tissue"
# })
# headers = {
#   'X-API-KEY': '0a49b8ac6532a531cca6f928e1c5a04bc580e547',
#   'Content-Type': 'application/json'
# }
# conn.request("POST", "/search", payload, headers)
# res = conn.getresponse()
# data = res.read()
# print(data.decode("utf-8"))