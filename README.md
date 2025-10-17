# 🚨 LLM Version Alert

Automatically detect new LLM model releases and get notified in your GitHub workflows. Never miss a new GPT, Claude, or other language model release!

## Features

- **OpenAI GPT Models and others soon**: Automatically detects latest GPT-4 models
- **Zero Setup**: Works out of the box with minimal configuration
- **Stateful**: Remembers previous versions to avoid duplicate alerts

## Quick Start

```yaml
name: LLM Version Monitor
on:
  schedule:
    - cron: "0 9 * * *"  # Check daily at 9 AM
  workflow_dispatch:     # Manual trigger

jobs:
  check-llm-updates:
    runs-on: ubuntu-latest
    steps:
      - name: Check for new LLM models
        uses: dhananjaypai08/llm-alerts@v1
        with:
          source: "openai"
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `source` | LLM provider to check (currently only `openai`) | Yes | `openai` |
| `openai_api_key` | OpenAI API key (or set `OPENAI_API_KEY` env) | Yes | — |
| `notify` | Notification mode: `none`, `issue`, or `fail` | No | `none` |
| `manifest_file` | File to write latest model id into for PR visibility | No | `LATEST_LLM_MODEL.txt` |

## 📤 Outputs

| Output | Description |
|--------|-------------|
| `model_detected` | The latest model ID that was detected |
| `version_changed` | `true` if a new model was found, `false` otherwise |

## 🔧 Supported Providers

- **OpenAI**: GPT-4 models (requires `OPENAI_API_KEY`)
- **Anthropic Claude**: 🚧 Coming soon
- **Google Gemini**: 🚧 Coming soon
- **Meta Llama**: 🚧 Coming soon

## 🛠️ Advanced Usage

### Basic with Outputs

```yaml
- name: Check for LLM updates
  id: llm-check
  uses: dhananjaypai08/llm-alerts@v1
  with:
    source: openai
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}

- name: Use outputs
  run: |
    echo "Model: ${{ steps.llm-check.outputs.model_detected }}"
    echo "Changed: ${{ steps.llm-check.outputs.version_changed }}"
```

### Notification Modes

| Mode | Behavior |
|------|----------|
| `none` | Only sets outputs & summary notice |
| `issue` | Creates or updates an issue titled `LLM Update: openai -> <model>` |
| `fail` | Marks the job failed if a new model is found (use to gate merges) |

Example using issue notifications and manifest file (commit in later step):

```yaml
- name: Check model & open issue
  id: llm-check
  uses: dhananjaypai08/llm-alerts@v1
  with:
    source: openai
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    notify: issue
    manifest_file: LATEST_LLM_MODEL.txt

- name: Commit manifest if changed
  if: steps.llm-check.outputs.version_changed == 'true'
  run: |
    git config user.name 'llm-bot'
    git config user.email 'llm-bot@users.noreply.github.com'
    git add LATEST_LLM_MODEL.txt
    git commit -m "chore: update LLM model to ${{ steps.llm-check.outputs.model_detected }}" || echo "No diff"
```

### Slack Notification Example

```yaml
- name: Check LLM
  id: llm-check
  uses: dhananjaypai08/llm-alerts@v1
  with:
    source: openai
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}

- name: Slack alert
  if: steps.llm-check.outputs.version_changed == 'true'
  run: |
    curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"🚨 New OpenAI model: ${{ steps.llm-check.outputs.model_detected }}"}' \
      ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 🔐 Setup

1. **Get an OpenAI API Key**: Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. **Add to GitHub Secrets**: Go to your repo → Settings → Secrets → Actions → New repository secret
   - Name: `OPENAI_API_KEY`
   - Value: Your API key
3. **Create workflow file**: Add the YAML above to `.github/workflows/llm-monitor.yml`

## 🏗️ How It Works

1. Fetches current OpenAI models list.
2. Picks the newest GPT-4* variant by `created` timestamp.
3. Compares with previously stored value in `.llm_latest`.
4. Writes outputs, summary, optional manifest file.
5. Optional: opens/updates issue or fails job depending on `notify`.

## 🤝 Contributing

Want to add support for more LLM providers? PRs welcome!

1. Fork this repository
2. Add provider support in `check_llm.py`
3. Update the documentation
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🐛 Issues

Found a bug or have a feature request? [Open an issue](https://github.com/dhananjaypai08/llm-alerts/issues)!

## 🧪 Local CI Test with act

A helper script is provided to repeatedly test the workflow locally whenever you modify the action logic.

Prerequisites: Install `act` (macOS/Homebrew):

```bash
brew install act
```

Run the workflow job locally:

```bash
chmod +x scripts/test_ci_with_act.sh
OPENAI_API_KEY=sk-yourkey scripts/test_ci_with_act.sh
```

Notes:
- On Apple Silicon the script auto-adds `--container-architecture linux/amd64`.
- Provide secrets either via environment (`OPENAI_API_KEY=`) or an optional `.secrets` file.
- View job summary for notices about new model versions.