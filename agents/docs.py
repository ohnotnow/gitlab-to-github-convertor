import re
import requests
from bs4 import BeautifulSoup
from litellm import completion
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader, select_autoescape
import logging
import os

logger = logging.getLogger('gl2gh')

class DocumentationSummarizer:
    """
    A class to process lint errors:
      - For each error with a URL, check if a summary already exists.
      - If not, fetch the documentation content and use an LLM to generate a summary
        using the error message as context.
      - Returns a list of dictionaries for each error with its URL, error message, and summary.
    """

    def __init__(self, model_name: str = "o3-mini", provider: str = "openai"):
        # Cache to store summaries keyed by (url, error_message)
        self.cache = {}
        self.env = Environment(
            loader=FileSystemLoader("prompts"),
            autoescape=select_autoescape()
        )
        self.model_name = model_name
        self.provider = provider

    def fetch_content(self, url: str) -> str:
        """
        Fetches and extracts text content from the given URL using requests and BeautifulSoup.
        """
        try:
            logger.debug(f"Fetching content from {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Ensure we catch HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text(separator='\n', strip=True)
        except Exception as e:
            logger.error(f"Error fetching content: {str(e)}")
            return f"Error fetching content: {str(e)}"

    def summarize(self, error_message: str, content: str, implementation: str) -> str:
        template = self.env.get_template("docs_summary.md")
        prompt = template.render(error_message=error_message, page_content=content, workflow_yaml=implementation)
        if self.provider == "openai":
            logger.debug(f"Summarizing docs content with OpenAI")
            response = completion(
                model=self.model_name,
                reasoning_effort="high",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
        elif self.provider == "openrouter":
            logger.debug(f"Summarizing docs content with OpenRouter")
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )
            response = client.chat.completions.create(
                model=f"openrouter/{self.model_name}",
                messages=[{"role": "user", "content": prompt}],
            )
        else:
            raise ValueError(f"Invalid provider: {self.provider}")

        logger.debug(f"Summarized docs content: {response.choices[0].message.content}")
        return response.choices[0].message.content

    def process_errors(self, lint_errors: str, implementation: str, docs: list) -> list:
        """
        Processes the lint errors, checking for existing summaries, fetching content, and summarizing as needed.

        Args:
            lint_errors (str): A string containing multiple lint errors.

        Returns:
            list: A list of dictionaries, each with keys "url", "error", and "summary".
        """
        # seed any previous docs in the cache
        for doc in docs:
            self.cache[(doc["url"], doc["error"])] = doc["summary"]

        logger.debug(f"Lint errors: {lint_errors}")
        logger.debug("-" * 100)
        # Regex to extract error messages and associated URLs.
        pattern = r'^\d+:\d+:\s+(.*?)\s+see\s+(https?://[^\s]+)'
        error_details = re.findall(pattern, lint_errors, re.MULTILINE)
        logger.debug(f"Error details: {error_details}")
        logger.debug("-" * 100)
        # make error_details unique
        error_details = list(set(error_details))
        logger.debug(f"Unique error details: {error_details}")
        logger.debug("-" * 100)

        results = []
        for error_message, url in error_details:
            error_message = error_message.strip()
            if not url.startswith("https://"):
                temp = url
                url = error_message
                error_message = temp
            key = (url, error_message)

            if key not in self.cache:
                logger.debug(f"- Getting new docs summary for {url}")
                content = self.fetch_content(url)
                summary = self.summarize(error_message, content, implementation)
                self.cache[key] = summary
            else:
                logger.debug(f"- Using cached summary for {url}")
                summary = self.cache[key]
            results.append({
                "url": url,
                "error": error_message,
                "summary": summary
            })
            docs.append({
                "url": url,
                "error": error_message,
                "summary": summary
            })

        return results, docs
