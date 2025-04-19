import argparse
import logging
import os
import re
from datetime import datetime
from agents.planner import PlanningAgent
from agents.implementing import ImplementationAgent
from agents.validator import ValidationAgent
from agents.quick_fix import QuickFixAgent
from agents.debug import DebugAgent
from agents.docs import DocumentationSummarizer
from agents.error_analyst import ErrorAnalysisAgent
from agents.quality import QualityAgent
logger = logging.getLogger("gl2gh")


def setup_logging(debug_filename: str | None):
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file handler for debug output
    if debug_filename:
        file_handler = logging.FileHandler(debug_filename)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if os.getenv("LOG_ERRORS"):
        error_handler = logging.StreamHandler()
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

class GitLabToGitHubConverter:
    def __init__(self, gitlab_yaml: str, max_attempts: int = 3, debug_file: str | None = None,
                 provider: str = "openrouter", model: str = "openrouter/quasar-alpha", thorough: bool = False):
        self.gitlab_yaml = gitlab_yaml
        self.max_attempts = max_attempts
        self.provider = provider
        self.model = model
        self.thorough = thorough
        self.total_cost = 0
        self.output_basename = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_results = []

        setup_logging(debug_file)
        logger.info(f"Using model: {model} ({provider})")

        # Initialize agents
        self.planner = PlanningAgent(model_name=model, provider=provider)
        self.worker_agent = ImplementationAgent(model_name=model, provider=provider)
        self.docs_agent = DocumentationSummarizer(model_name=model, provider=provider)
        self.validation_agent = ValidationAgent()
        self.quick_fix_agent = QuickFixAgent()
        self.quality_agent = QualityAgent()

    def create_implementation_plan(self):
        """Generate a plan for implementation using the planning agent"""
        logger.info("Getting implementation plan")
        plan, cost = self.planner.run(gitlab_yaml=self.gitlab_yaml)
        logger.debug(f"## Planning (cost: US${cost})\n{plan}")
        self.total_cost += cost
        return plan

    def implement_solution(self, plan: str, error_message: str = "",
                           error_guidance: str = "", previous_implementation: str = ""):
        """Generate an implementation based on the plan and any error feedback"""
        implementation, cost = self.worker_agent.run(
            gitlab_yaml=self.gitlab_yaml,
            user_thoughts=plan,
            error_message=error_message,
            error_guidence=error_guidance,
            previous_attempt=previous_implementation
        )
        implementation = self.quick_fix_agent.run(implementation)

        logger.debug(f"## Implementation (cost: US${cost})\n{implementation}")
        self.total_cost += cost

        return implementation

    def save_implementation(self, implementation: str, attempt: int, is_final: bool = False):
        """Save the implementation to a file"""
        output_filename = f"{self.output_basename}_final.yml" if is_final else f"{self.output_basename}_{attempt}.yml"
        with open(output_filename, "w") as f:
            f.write(implementation)
            logger.info(f"Output written to {output_filename}")
        return output_filename

    def save_quality_check(self, quality_check: str):
        """Save the quality check to a file"""
        output_filename = f"{self.output_basename}_quality_check.md"
        with open(output_filename, "w") as f:
            f.write(quality_check)
            logger.info(f"Quality check written to {output_filename}")
        return output_filename

    def validate_implementation(self, implementation: str, attempt: int):
        """Validate the implementation and record results"""
        exit_code, stdout, stderr = self.validation_agent.run(implementation)

        logger.debug(f"Validation exit code:\n{exit_code}")
        logger.debug(f"Validation stdout:\n{stdout}")
        logger.debug(f"Validation stderr:\n{stderr}")

        if exit_code is True:
            logger.info("Validation passed")
            self.output_results.append({
                "attempt": attempt,
                "output_filename": f"{self.output_basename}_{attempt}.yml",
                "validation_errors": 0
            })
            return True, "", ""
        else:
            lines = stdout.split("\n")
            validation_errors = [line for line in lines if line.startswith("../")]
            logger.info(f"Validation failed ({len(validation_errors)} errors)")

            self.output_results.append({
                "attempt": attempt,
                "output_filename": f"{self.output_basename}_{attempt}.yml",
                "validation_errors": len(validation_errors)
            })

            cleaned_lines = [
                re.sub(r'^.*?(\d+:\d+:)', r'\1', line)
                for line in stdout.splitlines()
            ]
            error_message = "\n".join(cleaned_lines)
            logger.debug(f"Raw error message: {error_message}")

            return False, error_message, stdout

    def process_errors(self, error_message: str, implementation: str, docs: list):
        """Process errors and retrieve relevant documentation"""
        logger.info("Looking up docs for errors")
        applicable_docs, updated_docs = self.docs_agent.process_errors(error_message, implementation, docs)

        logger.debug(f"Returned {len(applicable_docs)} applicable docs and {len(updated_docs)} total docs")

        error_guidance = ""
        if applicable_docs:
            for doc in applicable_docs:
                error_guidance += f"## {doc['error']} - {doc['url']}\n{doc['summary']}\n\n"
        else:
            logger.debug("No applicable docs found")

        # Analyze errors for additional guidance
        logger.info("Analyzing errors")
        analysis_agent = ErrorAnalysisAgent(model_name=self.model, provider=self.provider)
        error_guidance, cost = analysis_agent.run(
            error_message=error_message,
            implementation=implementation,
            error_guidence=error_guidance
        )
        self.total_cost += cost
        logger.debug(f"Error guidance: {error_guidance}")

        return error_guidance, updated_docs

    def switch_to_debug_agent_if_needed(self):
        """Switch to debug agent if not already using it"""
        if not isinstance(self.worker_agent, DebugAgent):
            logger.debug("Switching to debug agent")
            self.worker_agent = DebugAgent(model_name=self.model, provider=self.provider)

    def display_results(self):
        """Display the results of all attempts"""
        self.output_results.sort(key=lambda x: x["validation_errors"])
        logger.info("Output results:")
        for result in self.output_results:
            logger.info(f"  - {result['output_filename']} ({result['validation_errors']} errors)")

    def quality_check_passed(self, quality_check: str):
        """Check if the quality check passed"""
        lines = quality_check.lower().split("\n")
        for line in lines:
            if "verdict" in line and "pass" in line:
                return True
        return False

    def run(self):
        """Main execution flow of the converter"""
        # Create implementation plan
        plan = self.create_implementation_plan()

        # Implementation and validation loop
        attempts = 0
        passes = False
        quality_check_passed = False
        previous_implementation = ""
        error_message = ""
        error_guidance = ""
        quality_check = ""
        docs = []

        while not passes and not (quality_check_passed and self.thorough) and attempts < self.max_attempts:
            attempts += 1
            logger.info(f"Implementing (attempt {attempts})")
            logger.debug(f"Error message: {error_message}")

            # Generate implementation
            implementation = self.implement_solution(
                plan, error_message, error_guidance, previous_implementation
            )

            # Save current implementation
            self.save_implementation(implementation, attempts)

            # Validate implementation
            passes, error_message, stdout = self.validate_implementation(implementation, attempts)

            if not passes:
                previous_implementation = implementation
                error_guidance, docs = self.process_errors(error_message, implementation, docs)
                self.switch_to_debug_agent_if_needed()
            else:
                # Quality check
                quality_check, cost = self.quality_agent.run(gitlab_yaml=self.gitlab_yaml, github_yaml=implementation)
                self.total_cost += cost
                logger.debug(f"Quality check: {quality_check}")
                quality_check_passed = self.quality_check_passed(quality_check)
                if quality_check_passed:
                    logger.info("Quality check passed")
                else:
                    logger.info("Quality check failed")
                    if self.thorough:
                        logger.info("Regenerating GitHub YAML")
                        previous_implementation = implementation
                        error_guidance = quality_check
                        self.switch_to_debug_agent_if_needed()

        # Save final output
        self.save_implementation(implementation, attempts, is_final=True)
        self.save_quality_check(quality_check)

        # Display results
        logger.info(f"Total cost: US${self.total_cost}")
        self.display_results()

        return 0 if passes else 1


def main(gitlab_yaml: str, max_attempts: int = 3, debug_file: str | None = None,
         provider: str = "openrouter", model: str = "openrouter/quasar-alpha", thorough: bool = False):
    """Main entry point for the script"""
    converter = GitLabToGitHubConverter(
        gitlab_yaml=gitlab_yaml,
        max_attempts=max_attempts,
        debug_file=debug_file,
        provider=provider,
        model=model,
        thorough=thorough
    )

    exit_code = converter.run()
    exit(exit_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gitlab-yaml", type=str, required=True, help="Path to the GitLab CI/CD YAML file")
    parser.add_argument("--max-attempts", type=int, default=3, help="Maximum number of attempts to make")
    parser.add_argument("--debug-file", type=str, required=False, help="Path to a file for detailed debug logging")
    parser.add_argument("--provider", type=str, required=False, default=os.getenv("LLM_PROVIDER", "openrouter"), help="LLM provider to use")
    parser.add_argument("--model", type=str, required=False, default=os.getenv("LLM_MODEL", "openai/o4-mini"), help="LLM model to use")
    parser.add_argument("--thorough", action="store_true", required=False, default=False, help="Regenerate the GitHub YAML if the quality check fails")
    args = parser.parse_args()

    with open(args.gitlab_yaml, "r") as f:
        gitlab_contents = f.read()

    main(gitlab_contents, args.max_attempts, args.debug_file, args.provider, args.model, args.thorough)
