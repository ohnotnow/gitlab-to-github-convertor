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

<extra-notes-on-github-variable-contexts>

## Context availability

Different contexts are available throughout a workflow run. For example, the secrets context may only be used at certain places within a job.

In addition, some functions may only be used in certain places. For example, the hashFiles function is not available everywhere.

The following table lists the restrictions on where each context and special function can be used within a workflow. The listed contexts are only available for the given workflow key, and may not be used anywhere else. Unless listed below, a function can be used anywhere.


## Workflow Key Context and Special Functions

- **run-name**
  - Context: `github, inputs, vars`
  - Special functions: None

- **concurrency**
  - Context: `github, inputs, vars`
  - Special functions: None

- **env**
  - Context: `github, secrets, inputs, vars`
  - Special functions: None

- **jobs.<job_id>.concurrency**
  - Context: `github, needs, strategy, matrix, inputs, vars`
  - Special functions: None

- **jobs.<job_id>.container**
  - Context: `github, needs, strategy, matrix, vars, inputs`
  - Special functions: None

- **jobs.<job_id>.container.credentials**
  - Context: `github, needs, strategy, matrix, env, vars, secrets, inputs`
  - Special functions: None

- **jobs.<job_id>.container.env.<env_id>**
  - Context: `github, needs, strategy, matrix, job, runner, env, vars, secrets, inputs`
  - Special functions: None

- **jobs.<job_id>.container.image**
  - Context: `github, needs, strategy, matrix, vars, inputs`
  - Special functions: None

- **jobs.<job_id>.continue-on-error**
  - Context: `github, needs, strategy, vars, matrix, inputs`
  - Special functions: None

- **jobs.<job_id>.defaults.run**
  - Context: `github, needs, strategy, matrix, env, vars, inputs`
  - Special functions: None

- **jobs.<job_id>.env**
  - Context: `github, needs, strategy, matrix, vars, secrets, inputs`
  - Special functions: None

- **jobs.<job_id>.environment**
  - Context: `github, needs, strategy, matrix, vars, inputs`
  - Special functions: None

- **jobs.<job_id>.environment.url**
  - Context: `github, needs, strategy, matrix, job, runner, env, vars, steps, inputs`
  - Special functions: None

- **jobs.<job_id>.if**
  - Context: `github, needs, vars, inputs`
  - Special functions: `always, cancelled, success, failure`

- **jobs.<job_id>.name**
  - Context: `github, needs, strategy, matrix, vars, inputs`
  - Special functions: None

- **jobs.<job_id>.outputs.<output_id>**
  - Context: `github, needs, strategy, matrix, job, runner, env, vars, secrets, steps, inputs`
  - Special functions: None

- **jobs.<job_id>.runs-on**
  - Context: `github, needs, strategy, matrix, vars, inputs`
  - Special functions: None

- **jobs.<job_id>.secrets.<secrets_id>**
  - Context: `github, needs, strategy, matrix, secrets, inputs, vars`
  - Special functions: None

- **jobs.<job_id>.services**
  - Context: `github, needs, strategy, matrix, vars, inputs`
  - Special functions: None

- **jobs.<job_id>.services.<service_id>.credentials**
  - Context: `github, needs, strategy, matrix, env, vars, secrets, inputs`
  - Special functions: None

- **jobs.<job_id>.services.<service_id>.env.<env_id>**
  - Context: `github, needs, strategy, matrix, job, runner, env, vars, secrets, inputs`
  - Special functions: None

- **jobs.<job_id>.steps.continue-on-error**
  - Context: `github, needs, strategy, matrix, job, runner, env, vars, secrets, steps, inputs`
  - Special functions: `hashFiles`

- **jobs.<job_id>.steps.env**
  - Context: `github, needs, strategy, matrix, job, runner, env, vars, secrets, steps, inputs`
  - Special functions: `hashFiles`

- **jobs.<job_id>.steps.if**
  - Context: `github, needs, strategy, matrix, job, runner, env, vars, steps, inputs`
  - Special functions: `always, cancelled, success, failure, hashFiles`

- **jobs.<job_id>.steps.name**
  - Context: `github, needs, strategy, matrix, job, runner, env, vars, secrets, steps, inputs`
  - Special functions: `hashFiles`

- **jobs.<job_id>.steps.run**
  - Context: `github, needs, strategy, matrix, job, runner, env, vars, secrets, steps, inputs`
  - Special functions: `hashFiles`

- **jobs.<job_id>.steps.timeout-minutes**
  - Context: `github, needs, strategy, matrix, job, runner, env, vars, secrets, steps, inputs`
  - Special functions: `hashFiles`

- **jobs.<job_id>.steps.with**
  - Context: `github, needs, strategy, matrix, job, runner, env, vars, secrets, steps, inputs`
  - Special functions: `hashFiles`

- **jobs.<job_id>.steps.working-directory**
  - Context: `github, needs, strategy, matrix, job, runner, env, vars, secrets, steps, inputs`
  - Special functions: `hashFiles`

- **jobs.<job_id>.strategy**
  - Context: `github, needs, vars, inputs`
  - Special functions: None

- **jobs.<job_id>.timeout-minutes**
  - Context: `github, needs, strategy, matrix, vars, inputs`
  - Special functions: None

- **jobs.<job_id>.with.<with_id>**
  - Context: `github, needs, strategy, matrix, inputs, vars`
  - Special functions: None

- **on.workflow_call.inputs.<inputs_id>.default**
  - Context: `github, inputs, vars`
  - Special functions: None

- **on.workflow_call.outputs.<output_id>.value**
  - Context: `github, jobs, vars, inputs`
  - Special functions: None


</extra-notes-on-github-variable-contexts>
