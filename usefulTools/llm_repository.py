from langchain_anthropic import ChatAnthropic

ClaudeSonnet = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    max_tokens = 8192,
    temperature=0.6
)

ClaudeHaiku = ChatAnthropic(
    model="claude-3-haiku-20240307",
    max_tokens = 8192,
    temperature=0.6
)


ClaudeOpus = ChatAnthropic(
    model="claude-3-opus-20240229",
    max_tokens = 8192,
    temperature=0.6
)