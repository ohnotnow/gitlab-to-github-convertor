from subprocess import run
import tempfile

class ValidationAgent():
    def run(self, github_actions_code: str) -> tuple[bool, str, str]:
        # run 'actionlint' on the provided code
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(github_actions_code.encode('utf-8'))
        temp_file.flush()
        # add the -shellcheck flag to the actionlint command
        result = run(['actionlint', '-shellcheck=""', temp_file.name], capture_output=True, text=True)
        temp_file.close()

        return result.returncode == 0, result.stdout, result.stderr
