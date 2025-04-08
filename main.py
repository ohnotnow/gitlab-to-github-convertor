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


def main(gitlab_yaml: str, max_attempts: int = 3, debug_file: str | None = None, provider: str = "openrouter", model: str = "openrouter/quasar-alpha"):
    setup_logging(debug_file)

    total_cost = 0
    logger.info(f"Using model: {model} ({provider})")
    logger.info("Getting implementation plan")
    planner = PlanningAgent(model_name=model, provider=provider)
    plan, cost = planner.run(gitlab_yaml=gitlab_yaml)
    logger.debug(f"## Planning (cost: US${cost})\n{plan}")
    total_cost += cost

    attempts = 0
    passes = False
    previous_implementation = ""
    output_basename = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_results = []
    worker_agent = ImplementationAgent(model_name=model, provider=provider)
    docs_agent = DocumentationSummarizer(model_name=model, provider=provider)
    docs = []
    error_guidence = ""
    error_message = ""

    while not passes and attempts < max_attempts:
        attempts += 1
        logger.info(f"Implementing (attempt {attempts})")
        logger.debug(f"Error message: {error_message}")
        implementation, cost = worker_agent.run(
            gitlab_yaml=gitlab_yaml,
            user_thoughts=plan,
            error_message=error_message,
            error_guidence=error_guidence,
            previous_attempt=previous_implementation
        )
        quick_fix_agent = QuickFixAgent()
        implementation = quick_fix_agent.run(implementation)

        logger.debug(f"## Implementation (cost: US${cost})\n{implementation}")
        total_cost += cost

        output_filename = f"{output_basename}_{attempts}.yml"
        with open(output_filename, "w") as f:
            f.write(implementation)
            logger.info(f"Output written to {output_filename}")

        validation_agent = ValidationAgent()
        exit_code, stdout, stderr = validation_agent.run(implementation)
        logger.debug(f"Validation exit code:\n{exit_code}")
        logger.debug(f"Validation stdout:\n{stdout}")
        logger.debug(f"Validation stderr:\n{stderr}")

        if exit_code is True:
            logger.info("Validation passed")
            passes = True
            error_message = ""
            output_results.append({
                "attempt": attempts,
                "output_filename": output_filename,
                "validation_errors": 0
            })
        else:
            lines = stdout.split("\n")
            validation_errors = [line for line in lines if line.startswith("../")]
            logger.info(f"Validation failed ({len(validation_errors)} errors)")
            output_results.append({
                "attempt": attempts,
                "output_filename": output_filename,
                "validation_errors": len(validation_errors)
            })

            cleaned_lines = [
                re.sub(r'^.*?(\d+:\d+:)', r'\1', line)
                for line in stdout.splitlines()
            ]
            error_message = "\n".join(cleaned_lines)
            logger.debug(f"Raw error message: {error_message}")
            logger.debug("-" * 100)
            previous_implementation = implementation
            logger.info("Looking up docs for errors")
            applicable_docs, docs = docs_agent.process_errors(error_message, implementation, docs)
            logger.debug(f"Returned {len(applicable_docs)} applicable docs and {len(docs)} total docs")
            if len(applicable_docs) > 0:
                error_guidence = ""
                for doc in applicable_docs:
                    error_guidence += f"## {doc['error']} - {doc['url']}\n{doc['summary']}\n\n"
            else:
                logger.debug(f"No applicable docs found")
            logger.info("Analyzing errors")
            analysis_agent = ErrorAnalysisAgent(model_name=model, provider=provider)
            error_guidence, cost = analysis_agent.run(
                error_message=error_message,
                implementation=implementation,
                error_guidence=error_guidence
            )
            total_cost += cost
            logger.debug(f"Error guidence: {error_guidence}")
            logger.debug("-" * 100)
            if not isinstance(worker_agent, DebugAgent):
                logger.debug(f"Switching to debug agent")
                worker_agent = DebugAgent(model_name=model, provider=provider)

    logger.info(f"Total cost: US${total_cost}")
    output_filename = f"{output_basename}_final.yml"
    with open(output_filename, "w") as f:
        f.write(implementation)
        logger.info(f"Output written to {output_filename}")


    output_results.sort(key=lambda x: x["validation_errors"])
    logger.info("Output results:")
    for result in output_results:
        logger.info(f"  - {result['output_filename']} ({result['validation_errors']} errors)")

    if exit_code is not True:
        logger.info(f"Validation failed after {attempts} attempts")
        exit(1)
    else:
        logger.info("Validation passed")
        exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gitlab-yaml", type=str, required=True, help="Path to the GitLab CI/CD YAML file")
    parser.add_argument("--max-attempts", type=int, default=3, help="Maximum number of attempts to make")
    parser.add_argument("--debug-file", type=str, help="Path to a file for detailed debug logging")
    parser.add_argument("--provider", type=str, default=os.getenv("LLM_PROVIDER", "openrouter"), help="LLM provider to use")
    parser.add_argument("--model", type=str, default=os.getenv("LLM_MODEL", "openrouter/quasar-alpha"), help="LLM model to use")
    args = parser.parse_args()

    with open(args.gitlab_yaml, "r") as f:
        gitlab_contents = f.read()

    main(gitlab_contents, args.max_attempts, args.debug_file, args.provider, args.model)
