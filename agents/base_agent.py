from litellm import completion
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

class BaseAgent:
    prompt_file: str = "changeme.md"

    def __init__(self, model_name: str = "openai/o3-mini"):
        self.model_name = model_name
        self.env = Environment(
            loader=FileSystemLoader("prompts"),
            autoescape=select_autoescape()
        )

    def get_prompt(self, **kwargs) -> str:
        template = self.env.get_template(self.prompt_file)
        return template.render(**kwargs)

    def run(self, **kwargs) -> str:
        prompt = self.get_prompt(**kwargs)
        response, cost = self.get_openrouter_response(prompt)
        return response, cost
        response = completion(
            model=self.model_name,
            reasoning_effort="high",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content, response._hidden_params["response_cost"]

    def get_openrouter_response(self, prompt: str) -> str:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        response = client.chat.completions.create(
            model="openrouter/quasar-alpha",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content, 0
