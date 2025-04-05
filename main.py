import argparse
import re
from agents.base_agent import BaseAgent
from agents.planner import PlanningAgent
from agents.implementing import ImplementationAgent
from agents.validator import ValidationAgent
from agents.quick_fix import QuickFixAgent
from agents.debug import DebugAgent
from agents.docs import DocumentationSummarizer
from datetime import datetime

def main(gitlab_yaml: str, max_attempts: int = 3, debug: bool = False):
    total_cost = 0
    print("- Getting implementation plan")
    planner = PlanningAgent()
    plan, cost = planner.run(gitlab_yaml=gitlab_yaml)
    if debug:
        print(f"## Planning (cost: US${cost})\n{plan}")
    total_cost += cost
    attempts = 0
    passes = False
    previous_implementation = ""
    output_basename = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_results = []
    worker_agent = ImplementationAgent()
    docs_agent = DocumentationSummarizer()
    docs = []
    error_guidence = ""
    while not passes and attempts < max_attempts:
        error_message = ""
        attempts += 1
        print(f"- Implementing (attempt {attempts})")
        implementation, cost = worker_agent.run(gitlab_yaml=gitlab_yaml, user_thoughts=plan + error_guidence, error_message=error_message, previous_attempt=previous_implementation)
        quick_fix_agent = QuickFixAgent()
        implementation = quick_fix_agent.run(implementation)
        if debug:
            print(f"## Implementation (cost: US${cost})\n{implementation}")
        total_cost += cost
        output_filename = f"{output_basename}_{attempts}.yml"
        with open(output_filename, "w") as f:
            f.write(implementation)
            print(f"  - Output written to {output_filename}")
        validation_agent = ValidationAgent()
        exit_code, stdout, stderr = validation_agent.run(implementation)
        if debug:
            print(f"Validation exit code:\n{exit_code}")
            print(f"Validation stdout:\n{stdout}")
            print(f"Validation stderr:\n{stderr}")

        if exit_code == True:
            print("## Validation passed")
            passes = True
            error_message = ""
            output_results.append({
                "attempt": attempts,
                "output_filename": output_filename,
                "validation_errors": 0
            })
        else:
            # count the number of lines in stdout which start with "../" (which is how actionlint reports errors)
            lines = stdout.split("\n")
            validation_errors = [line for line in lines if line.startswith("../")]
            print(f"## Validation failed ({len(validation_errors)} errors)")
            output_results.append({
                "attempt": attempts,
                "output_filename": output_filename,
                "validation_errors": len(validation_errors)
            })
            # strip out lots of cruft from the error message to save on tokens
            cleaned_lines = [
                re.sub(r'^.*?(\d+:\d+:)', r'\1', line)
                for line in stdout.splitlines()
            ]
            error_message = "\n".join(cleaned_lines)
            if debug:
                print(error_message)
            previous_implementation = implementation
            docs = docs_agent.process_errors(error_message, implementation, docs)
            error_guidence = ""
            for doc in docs:
                error_guidence += f"## {doc['error']} - {doc['url']}\n{doc['summary']}\n\n"
                print(error_guidence)
            worker_agent = DebugAgent()

    print(f"## Total cost: US${total_cost}")
    output_filename = f"{output_basename}_final.yml"
    with open(output_filename, "w") as f:
        f.write(implementation)
        print(f"Output written to {output_filename}")
    if exit_code != True:
        print(f"## Validation failed after {attempts} attempts")
    # sort the output results by validation_errors - ascending
    output_results.sort(key=lambda x: x["validation_errors"])
    print(f"## Output results:")
    for result in output_results:
        print(f"  - {result['output_filename']} ({result['validation_errors']} errors)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gitlab-yaml", type=str, required=True, help="Path to the GitLab CI/CD YAML file")
    parser.add_argument("--max-attempts", type=int, default=3, help="Maximum number of attempts to make")
    parser.add_argument("--debug", action="store_true", default=False, help="Enable debug mode")
    args = parser.parse_args()
    with open(args.gitlab_yaml, "r") as f:
        gitlab_contents = f.read()
    main(gitlab_contents, args.max_attempts, args.debug)
