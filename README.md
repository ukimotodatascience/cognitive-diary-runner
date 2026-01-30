# cognitive-diary-runner

日記リポジトリ（`ukimotodatascience/obsidian`）のデータからワードクラウド画像を生成し、
毎日 05:00（JST）に自動更新するためのランナーです。

## 仕組み

- GitHub Actions が毎日 05:00 JST に実行
- 日記リポジトリを checkout
- `scripts/run_wordcloud.py` を実行して `日記/ワードクラウド` に画像を出力
- 生成物を日記リポジトリへコミット・プッシュ

## セットアップ

### 1. Secrets の登録

このリポジトリの **Settings > Secrets and variables > Actions** に以下を追加してください。

| Name | 内容 |
| --- | --- |
| `DIARY_REPO_TOKEN` | `ukimotodatascience/obsidian` へ push できる Personal Access Token |

### 2. ワークフロー

ワークフローは `.github/workflows/daily-wordcloud.yml` に定義されています。

- cron: `0 20 * * *`（UTC）= JST 毎日 05:00
- `workflow_dispatch` で手動実行も可能

## ローカル実行

```bash
python -m venv .venv
source .venv/bin/activate  # Windowsは .venv\\Scripts\\activate
pip install -r requirements.txt

# 実行（例）
DIARY_REPO_PATH=../obsidian \
DIARY_DIR="日記" \
OUTPUT_SUBDIR="ワードクラウド" \
python scripts/run_wordcloud.py
```

## 主なファイル

- `scripts/run_wordcloud.py`: ワードクラウド生成スクリプト
- `requirements.txt`: 依存関係
- `.github/workflows/daily-wordcloud.yml`: 定期実行ワークフロー