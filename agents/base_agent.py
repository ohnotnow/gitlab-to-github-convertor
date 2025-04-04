from litellm import completion
from jinja2 import Environment, FileSystemLoader, select_autoescape

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
        print(prompt)
        response = completion(
            model=self.model_name,
            reasoning_effort="high",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content, response._hidden_params["response_cost"]
