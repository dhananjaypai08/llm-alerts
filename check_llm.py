import sys, requests, os
from dotenv import load_dotenv
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

    state_file = os.path.join(os.environ["GITHUB_WORKSPACE"], ".llm_latest")

    previous = None
    if os.path.exists(state_file):
        with open(state_file) as f:
            previous = f.read().strip()

    if latest != previous:
        print(f"::notice title=LLM Update::New {source} model detected: {latest}")
        print(f"::set-output name=model_detected::{latest}")
        print(f"::set-output name=version_changed::true")
        with open(state_file, "w") as f:
            f.write(latest)
        # Optionally: fail the job to force visibility
        # sys.exit(1)
    else:
        print(f"Already up to date: {latest}")
        print(f"::set-output name=model_detected::{latest}")
        print(f"::set-output name=version_changed::false")
