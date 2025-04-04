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

        return github_yaml
