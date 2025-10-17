import sys, requests, os, json, textwrap
from dotenv import load_dotenv

# Only load .env file if it exists (for local development)
if os.path.exists('.env'):
    load_dotenv()

def check_openai():
    # You can only query `models` list (and they don’t publish changelogs).
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("::error::OPENAI_API_KEY not set")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {key}"}
    resp = requests.get("https://api.openai.com/v1/models", headers=headers)
    if resp.status_code != 200:
        print(f"::error::Failed to fetch models: {resp.text}")
        sys.exit(1)

    models = resp.json().get("data", [])
    candidates = [m for m in models if m["id"].startswith("gpt-4")]
    if not candidates:
        print("::warning::No GPT-4 models found")
        return None

    candidates.sort(key=lambda m: m.get("created", 0), reverse=True)
    latest = candidates[0]["id"]
    return latest

def gh_summary_append(markdown: str):
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a") as f:
            f.write(markdown + "\n")

def gh_set_output(name: str, value: str):
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"{name}={value}\n")
    else:
        print(f"::set-output name={name}::{value}")  # legacy fallback

def create_or_update_issue(repo: str, token: str, title: str, body: str):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    issues_url = f"https://api.github.com/repos/{repo}/issues"
    # Search existing open issues with same title
    params = {"state": "open", "per_page": 50}
    resp = requests.get(issues_url, headers=headers, params=params)
    if resp.status_code == 200:
        for issue in resp.json():
            if issue.get("title") == title:
                issue_url = issue["url"]
                update = requests.patch(issue_url, headers=headers, json={"body": body})
                if update.status_code >= 300:
                    print(f"::warning::Failed to update issue: {update.text}")
                else:
                    print(f"Updated issue #{issue['number']}")
                return
    else:
        print(f"::warning::Unable to list issues: {resp.text}")
    # Create new issue
    create = requests.post(issues_url, headers=headers, json={"title": title, "body": body})
    if create.status_code >= 300:
        print(f"::warning::Failed to create issue: {create.text}")
    else:
        num = create.json().get("number")
        print(f"Created issue #{num}")

def write_manifest(path: str, model_id: str):
    if not path:
        return
    try:
        with open(path, "w") as f:
            f.write(model_id + "\n")
    except Exception as e:
        print(f"::warning::Failed to write manifest file {path}: {e}")

if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else "openai"
    latest = None

    if source == "openai":
        latest = check_openai()
    else:
        print(f"::error::Unsupported source: {source}")
        sys.exit(1)

    if not latest:
        sys.exit(0)

    workspace = os.environ.get("GITHUB_WORKSPACE", os.getcwd())
    state_file = os.path.join(workspace, ".llm_latest")

    previous = None
    if os.path.exists(state_file):
        with open(state_file) as f:
            previous = f.read().strip()

    notify_mode = os.environ.get("NOTIFY_MODE", "none").lower()
    manifest_file = os.environ.get("MANIFEST_FILE", "")
    repo = os.environ.get("GITHUB_REPOSITORY")
    gh_token = os.environ.get("GITHUB_TOKEN")

    if latest != previous:
        print(f"::notice title=LLM Update::New {source} model detected: {latest}")
        gh_set_output("model_detected", latest)
        gh_set_output("version_changed", "true")
        with open(state_file, "w") as f:
            f.write(latest)
        write_manifest(os.path.join(workspace, manifest_file) if manifest_file else "", latest)

        summary_md = textwrap.dedent(f"""
        ### 🚨 New LLM Model Detected

        Provider: **{source}**  
        Latest: `{latest}`  
        Previous: `{previous or '—'}`  

        This was detected automatically by the LLM Version Alert action.
        """)
        gh_summary_append(summary_md)

        if notify_mode == "issue" and repo and gh_token:
            issue_title = f"LLM Update: {source} -> {latest}"
            issue_body = summary_md + "\n\n> Automated notification. Close this issue to acknowledge."
            create_or_update_issue(repo, gh_token, issue_title, issue_body)
        if notify_mode == "fail":
            print("::error::Failing job because notify=fail and a new model was detected")
            sys.exit(1)
    else:
        print(f"Already up to date: {latest}")
        gh_set_output("model_detected", latest)
        gh_set_output("version_changed", "false")
