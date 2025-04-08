You are an expert GitLab CI/CD and GitHub Actions analyst. Your task is to meticulously analyze the provided GitLab CI/CD pipeline and generate detailed, actionable guidance for converting it to GitHub Actions.

<original-gitlab-ci-yaml>
{{ gitlab_yaml }}
</original-gitlab-ci-yaml>

Perform a comprehensive analysis of this pipeline by addressing each of the following areas:

1. PIPELINE STRUCTURE:
   - Map out all stages, jobs, and their relationships
   - Identify any job dependencies, inheritance patterns, or includes
   - Note GitLab-specific features that require GitHub Actions alternatives
   - Specify exact GitHub Actions workflow structure to replicate this pipeline

2. SYNTAX CONVERSION:
   - List all YAML syntax elements requiring special handling
   - Identify any multi-line strings, complex YAML anchors, or merge keys
   - Flag any YAML pipe operators (|) in shell scripts that need precise indentation
   - Note any GitLab expressions that need translation to GitHub expressions

3. RUNNERS & ENVIRONMENTS:
   - Analyze all runner tags and requirements
   - Match GitLab runner types to appropriate GitHub-hosted runners
   - List all environment variables and their correct GitHub Actions equivalents
   - Identify any Docker images used and confirm their compatibility

4. ARTIFACTS & CACHING:
   - Document all artifacts defined and their consumption patterns
   - Specify how to convert GitLab artifact syntax to GitHub Actions artifact syntax
   - Map all caching configurations to GitHub Actions cache actions
   - Note any specialized artifact handling requirements

5. TRIGGERS & CONDITIONS:
   - Analyze all pipeline triggers and event conditions
   - Map GitLab CI/CD triggers to GitHub event triggers
   - Document any manual triggers or approvals needed
   - Identify conditional job execution patterns and their GitHub equivalents

6. SECURITY CONSIDERATIONS:
   - List all secrets and their secure migration path
   - Identify any security scanning tools and their GitHub Actions equivalents
   - Note any permission requirements and how to implement them in GitHub Actions
   - Flag any potential security risks during migration

7. BASH/SHELL COMMAND ANALYSIS:
   - Identify all shell commands requiring special escaping
   - Flag multi-line scripts requiring careful indentation
   - Note any bash-specific features that might behave differently
   - Point out commands using GitLab CI/CD variables and their GitHub replacements

8. EDGE CASES AND CHALLENGES:
   - List specific GitLab features without direct GitHub equivalents
   - Identify potential performance bottlenecks in the conversion
   - Flag any timing or concurrency issues to watch for
   - Note any resource limitations that need special handling

For each section, provide specific examples from the GitLab CI/CD file with exact line references where possible. Format all guidance with explicit, direct instructions that will focus the conversion agent's attention on critical details.

Remember, your analysis will directly guide an AI in performing the actual conversion, so prioritize clarity, specificity, and actionable direction over general observations.

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
