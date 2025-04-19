from agents.base_agent import BaseAgent

class ImplementationAgent(BaseAgent):
    prompt_file: str = "implementation.md"

    def __init__(self, model_name: str = "gpt-4.1", provider: str = "openai"):
        super().__init__(*args, **kwargs)

