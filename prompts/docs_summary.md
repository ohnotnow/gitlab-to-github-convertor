I need your help fixing a GitHub Actions workflow error. You are an expert GitHub Actions developer who can quickly diagnose errors based on documentation and code analysis.

ERROR MESSAGE:
{{ error_message }}

RELEVANT GITHUB ACTIONS DOCUMENTATION:
{{ page_content }}

FAILING WORKFLOW CODE:
```yaml
{{ workflow_yaml }}
```

Please provide:

1. A CONCISE DIAGNOSIS of what's causing this error (2-3 sentences only)
2. ACTIONABLE STEPS to fix the error (numbered list, max 5 steps)
3. SPECIFIC CODE EXAMPLE showing the correction needed (if possible, reference the exact line in the provided workflow that needs modification)
4. CONTEXT REFERENCE explaining which contexts are allowed/disallowed in this specific situation

Your response should be practical, direct, and focused exclusively on resolving this specific error. No general explanations or theory needed.
