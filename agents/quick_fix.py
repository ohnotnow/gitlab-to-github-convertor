import re

class QuickFixAgent():
    """
    Class to fix some common issues with the LLM implementation.
    """
    def run(self, github_yaml: str) -> str:
        github_yaml = github_yaml.replace("```yaml", "").replace("```", "")
        github_yaml = github_yaml.replace("actions/checkout@v3", "actions/checkout@v4")
        github_yaml = github_yaml.replace("docker/build-push-action@v4", "docker/build-push-action@v6")
        github_yaml = github_yaml.replace("docker/login-action@v2", "docker/login-action@v3")
        github_yaml = github_yaml.replace("docker/setup-buildx-action@v2", "docker/setup-buildx-action@v3")
        github_yaml = github_yaml.replace("actions/upload-artifact@v3", "actions/upload-artifact@v4")
        github_yaml = self.fix_heredoc_indentation(github_yaml)
        return github_yaml


    def fix_heredoc_indentation(self, yaml_text: str) -> str:
        """
        Fixes the indentation of heredoc closing delimiters in a YAML shell string.
        For each heredoc block (e.g. a line containing <<'EOF' or <<EOF),
        it will search for the closing delimiter in subsequent lines and adjust its
        indentation to match that of the heredoc start line.

        (It's a very common issue with LLM generated YAML files where they get the alignment wrong.)

        Returns the corrected YAML text.
        """
        # Regex to detect a heredoc start.
        heredoc_start_re = re.compile(
            r'^(?P<indent>\s*).*<<\s*["\']?(?P<delimiter>\w+)["\']?\s*$'
        )

        # Split YAML into lines for processing.
        lines = yaml_text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            start_match = heredoc_start_re.match(line)
            if start_match:
                expected_indent = start_match.group("indent")
                delimiter = start_match.group("delimiter")
                # Build a regex for the closing delimiter line.
                # The closing line should only contain optional whitespace and the delimiter.
                closing_re = re.compile(r'^(?P<indent>\s*)' + re.escape(delimiter) + r'\s*$')
                # Look for the closing delimiter in the subsequent lines.
                j = i + 1
                while j < len(lines):
                    closing_line = lines[j]
                    if closing_re.match(closing_line):
                        # If the current indentation does not match the expected indentation,
                        # replace the line with the properly indented closing delimiter.
                        if not closing_line.startswith(expected_indent):
                            lines[j] = expected_indent + delimiter
                        break
                    j += 1
            i += 1
        return "\n".join(lines)
