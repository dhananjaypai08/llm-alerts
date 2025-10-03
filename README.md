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
        uses: dhananjaypai08/llm-alert@v1
        with:
          source: "openai"
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `source` | LLM provider to check | Yes | `openai` |
| `api_key` | API key for the provider | No | Uses `OPENAI_API_KEY` env var |

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

### With Custom Notifications

```yaml
### With Custom Notifications

```yaml
- name: Check for LLM updates
  id: llm-check
  uses: dhananjaypai/llm-version-alert@v1
  with:
    source: "openai"
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}

- name: Send Slack notification
  if: steps.llm-check.outputs.version_changed == 'true'
  run: |
    curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"🚨 New model detected: ${{ steps.llm-check.outputs.model_detected }}"}' \
      ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Multiple Providers

```yaml
- name: Check OpenAI
  uses: dhananjaypai/llm-version-alert@v1
  with:
    source: "openai"
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}

# Add more providers as they become available
```
```

### Multiple Providers

```yaml
- name: Check OpenAI
  uses: dhananjaypai/llm-version-alert@v1
  with:
    source: "openai"
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

# Add more providers as they become available
```

## 🔐 Setup

1. **Get an OpenAI API Key**: Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. **Add to GitHub Secrets**: Go to your repo → Settings → Secrets → Actions → New repository secret
   - Name: `OPENAI_API_KEY`
   - Value: Your API key
3. **Create workflow file**: Add the YAML above to `.github/workflows/llm-monitor.yml`

## 🏗️ How It Works

1. Fetches the latest models from the provider's API
2. Identifies the newest model based on creation timestamp
3. Compares with previously detected version (stored in workspace)
4. Sends GitHub Actions notice if a new model is found
5. Updates the stored version for next run

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