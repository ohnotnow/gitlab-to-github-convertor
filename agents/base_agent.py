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

    def get_full_model_name(self) -> str:
        return f"{self.provider}/{self.model_name}"

    def run(self, **kwargs) -> tuple[str, float]:
        prompt = self.get_prompt(**kwargs)
        logger.debug(f"Running agent with provider={self.provider}")
        logger.debug(f"Prompt:\n{prompt}")

        full_model_name = self.get_full_model_name()
        logger.debug(f"Using model: {full_model_name}")

        response, cost = self.get_openrouter_response(prompt)

        logger.debug(f"LLM response (first 200 chars): {response[:200]}")
        logger.debug(f"Cost for response: US${cost}")
        return response, cost

    def get_openrouter_response(self, prompt: str) -> tuple[str, float]:
        logger.debug("Calling OpenRouter API")
        full_model_name = self.get_full_model_name()
        logger.debug(f"Using model: {full_model_name}")
        litellm.drop_params = True
        try:
            response = completion(
                model=full_model_name,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            raise e
        cost = response._hidden_params.get("response_cost", 0.0)
        if not cost:
            # sometimes litellm returns None for cost - so we catch that
            cost = 0.0
        logger.debug(f"OpenRouter cost: US${cost}")
        return response.choices[0].message.content, cost
