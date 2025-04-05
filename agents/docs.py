import re
import requests
from bs4 import BeautifulSoup
from litellm import completion
from jinja2 import Environment, FileSystemLoader, select_autoescape

class DocumentationSummarizer:
    """
    A class to process lint errors:
      - For each error with a URL, check if a summary already exists.
      - If not, fetch the documentation content and use an LLM to generate a summary
        using the error message as context.
      - Returns a list of dictionaries for each error with its URL, error message, and summary.
    """

    def __init__(self):
        # Cache to store summaries keyed by (url, error_message)
        self.cache = {}
        self.env = Environment(
            loader=FileSystemLoader("prompts"),
            autoescape=select_autoescape()
        )

    def fetch_content(self, url: str) -> str:
        """
        Fetches and extracts text content from the given URL using requests and BeautifulSoup.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Ensure we catch HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text(separator='\n', strip=True)
        except Exception as e:
            return f"Error fetching content: {str(e)}"

    def summarize(self, error_message: str, content: str, implementation: str) -> str:
        """
        Stub function to simulate a call to a smaller LLM.
        Replace this with your actual LLM call to generate a summary based on the error_message and content.
        """
        template = self.env.get_template("docs_summary.md")
        prompt = template.render(error_message=error_message, page_content=content, workflow_yaml=implementation)
        response = completion(
            model="o3-mini",
            reasoning_effort="high",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
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

        # Regex to extract error messages and associated URLs.
        pattern = r'^\d+:\d+:\s+(.*?)\s+see\s+(https?://[^\s]+)'
        error_details = re.findall(pattern, lint_errors, re.MULTILINE)

        results = []
        for error_message, url in error_details:
            error_message = error_message.strip()
            key = (url, error_message)

            if key not in self.cache:
                content = self.fetch_content(url)
                summary = self.summarize(error_message, content, implementation)
                self.cache[key] = summary
            else:
                summary = self.cache[key]

            results.append({
                "url": url,
                "error": error_message,
                "summary": summary
            })

        return results

# Example usage:
if __name__ == "__main__":
    lint_errors = """42:18: context "env" is not allowed here. available contexts are "github", "inputs", "matrix", "needs", "strategy", "vars". see https://docs.github.com/en/actions/learn-github-actions/contexts#context-availability for more details [expression]
       |
    42 |       image: ${{ env.QA_IMAGE_NAME }}
       |                  ^~~~~~~~~~~~~~~~~
    80:18: context "secrets" is not allowed here. available contexts are "github", "inputs", "matrix", "needs", "strategy", "vars". see https://docs.github.com/en/actions/learn-github-actions/contexts#context-availability for more details [expression]
       |
    80 |       image: ${{ secrets.CI_REGISTRY }}/${{ github.repository }}:qa-${{ github.sha }}
       |                  ^~~~~~~~~~~~~~~~~~~
    97:18: context "secrets" is not allowed here. available contexts are "github", "inputs", "matrix", "needs", "strategy", "vars". see https://docs.github.com/en/actions/learn-github-actions/contexts#context-availability for more details [expression]
       |
    97 |       image: ${{ secrets.CI_REGISTRY }}/${{ github.repository }}:qa-${{ github.sha }}
       |                  ^~~~~~~~~~~~~~~~~~~
    111:18: context "secrets" is not allowed here. available contexts are "github", "inputs", "matrix", "needs", "strategy", "vars". see https://docs.github.com/en/actions/learn-github-actions/contexts#context-availability for more details [expression]"""

    doc_sum = DocumentationSummarizer()
    processed_errors = doc_sum.process_errors(lint_errors)

    # Print the result for each error
    for item in processed_errors:
        print(item)
