import argparse
import re
from agents.base_agent import BaseAgent
from agents.planner import PlanningAgent
from agents.implementing import ImplementationAgent
from agents.validator import ValidationAgent
from agents.quick_fix import QuickFixAgent
from datetime import datetime

def main(gitlab_yaml: str, max_attempts: int = 3):
    total_cost = 0
    planner = PlanningAgent()
    plan, cost = planner.run(gitlab_yaml=gitlab_yaml)
    print(f"## Planning (cost: US${cost})\n{plan}")
    total_cost += cost
    attempts = 0
    passes = False
    previous_implementation = ""
    while not passes and attempts < max_attempts:
        error_message = ""
        attempts += 1
        implementation_agent = ImplementationAgent()
        implementation, cost = implementation_agent.run(gitlab_yaml=gitlab_yaml, user_thoughts=plan, error_message=error_message, previous_attempt=previous_implementation)
        quick_fix_agent = QuickFixAgent()
        implementation = quick_fix_agent.run(implementation)
        print(f"## Implementation (cost: US${cost})\n{implementation}")
        total_cost += cost
        validation_agent = ValidationAgent()
        exit_code, stdout, stderr = validation_agent.run(implementation)
        print(f"Validation exit code:\n{exit_code}")
        print(f"Validation stdout:\n{stdout}")
        print(f"Validation stderr:\n{stderr}")

        if exit_code == True:
            print("## Validation passed")
            passes = True
        else:
            print("## Validation failed")
            # use a regex to remove extraneous text from the error message of the rough form :
            # ../../../../../var/folders/c5/tc46xpnx2gg53l57q8nlyy340000gn/T/tmpisvkcogx:{number}:{number}
            # leaving the numbers in the replacement
            error_message = re.sub(r'^../../.+:(\d+:\d+)', r'\1', stdout)
            previous_implementation = implementation

    print(f"## Total cost: US${total_cost}")
    output_filename = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yml"
    with open(output_filename, "w") as f:
        f.write(implementation)
        print(f"Output written to {output_filename}")
    if exit_code != True:
        print("## Validation failed after 3 attempts")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gitlab-yaml", type=str, required=True, help="Path to the GitLab CI/CD YAML file")
    parser.add_argument("--max-attempts", type=int, default=3, help="Maximum number of attempts to make")
    args = parser.parse_args()
    with open(args.gitlab_yaml, "r") as f:
        gitlab_contents = f.read()
    main(gitlab_contents, args.max_attempts)
