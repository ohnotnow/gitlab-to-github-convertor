You are an expert in migrating GitLab CI/CD pipelines to GitHub Actions workflows. Your task is to convert the provided GitLab CI/CD pipeline to an equivalent GitHub Actions workflow, guided by the expert analysis provided.

<original-gitlab-ci-yaml>
{{ gitlab_yaml }}
</original-gitlab-ci-yaml>

<expert-analysis>
{{ user_thoughts }}
</expert-analysis>


CONVERSION REQUIREMENTS:
1. Address ALL items mentioned in the expert analysis
2. Follow GitHub Actions best practices:
   - Use appropriate GitHub-hosted runners
   - Implement proper secret handling
   - Utilize GitHub Actions caching effectively
   - Follow security best practices
   - Keep the workflow DRY (Don't Repeat Yourself)
3. Ensure proper indentation for all shell scripts, especially multi-line commands
4. Test each job's logic for equivalence

OUTPUT INSTRUCTIONS:
- Return ONLY the GitHub Actions workflow YAML
- Include informative comments where appropriate within the YAML
- DO NOT include any explanation text outside the YAML as this will break the linter

Your response must be a valid GitHub Actions workflow file that will pass actionlint validation.

For reference - as of today, these are the current versions of some common GitHub actions :

- "actions/checkout@v4"
- "docker/build-push-action@v6"
- "docker/login-action@v3"
- "docker/setup-buildx-action@v3"
- "actions/upload-artifact@v4"
