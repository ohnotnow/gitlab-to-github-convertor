import logging
import os
import requests
from jinja2 import Environment, FileSystemLoader, select_autoescape
import litellm
from litellm import completion
from openai import OpenAI

logger = logging.getLogger('gl2gh')

class BaseAgent:
    prompt_file: str = "changeme.md"

    def __init__(self, model_name: str = "o3-mini", provider: str = "openai"):
        self.model_name = model_name
        self.provider = provider
        self.env = Environment(
            loader=FileSystemLoader("prompts"),
            autoescape=select_autoescape()
        )
        logger.debug(f"Initialized BaseAgent with model={self.model_name}, provider={self.provider}")

    def get_prompt(self, **kwargs) -> str:
        template = self.env.get_template(self.prompt_file)
        rendered = template.render(**kwargs)
        logger.debug(f"Rendered prompt from {self.prompt_file}:\n{rendered}")  # log only first 500 chars
        return rendered

    def run(self, **kwargs) -> tuple[str, float]:
        prompt = self.get_prompt(**kwargs)
        logger.debug(f"Running agent with provider={self.provider}")
        logger.debug(f"Prompt:\n{prompt}")

        if self.provider == "openai":
            response, cost = self.get_openai_response(prompt)
        else:
            response, cost = self.get_openrouter_response(prompt)

        logger.debug(f"LLM response (first 200 chars): {response[:200]}")
        logger.debug(f"Cost for response: US${cost}")
        return response, cost

    def get_openrouter_response(self, prompt: str) -> tuple[str, float]:
        logger.debug("Calling OpenRouter API")
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        response = client.chat.completions.create(
            model=f"openrouter/{self.model_name}",
            messages=[{"role": "user", "content": prompt}],
        )

        # Temporarily hardcoded cost
        cost = 0
        logger.debug("Using placeholder cost=0 for OpenRouter — replace with actual cost once available.")
        return response.choices[0].message.content, cost

    def get_openai_response(self, prompt: str) -> tuple[str, float]:
        logger.debug("Calling OpenAI via LiteLLM")
        litellm.drop_params = True
        response = completion(
            model=self.model_name,
            reasoning_effort="high",
            messages=[{"role": "user", "content": prompt}],
        )
        cost = response._hidden_params.get("response_cost", 0.0)
        logger.debug(f"LiteLLM cost: US${cost}")
        return response.choices[0].message.content, cost
