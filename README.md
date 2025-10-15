# GitHub Issues コピー ツール

## これは何？

このツールは、GitHub（ギットハブ）というサイトにある「Issues」（イシューズ）を、別の場所にコピーするものです。

Issuesとは、プロジェクトのバグやアイデアを書き込むメモのようなものです。このツールを使えば、たくさんのIssuesを一気に別のリポジトリ（プロジェクトの場所）に移動できます。

## 必要なもの

- GitHubのアカウント
- Python（パイソン）というプログラミング言語（パソコンにインストールされていること）
- GitHubのトークン（パスワードのようなもの）

## 使い方

### 1. ローカルで実行する（自分のパソコンで）

パソコンで直接実行する方法です。

#### 準備
1. このリポジトリをダウンロードする
2. Pythonとrequestsライブラリをインストールする

```bash
pip install requests
```

#### 実行
環境変数を設定して、スクリプトを実行します。

```bash
export GITHUB_TOKEN="あなたのトークン"
export SOURCE_OWNER="コピー元のオーナー"
export SOURCE_REPO="コピー元のリポジトリ名"
export DEST_OWNER="コピー先のオーナー"
export DEST_REPO="コピー先のリポジトリ名"
python issues_copy.py
```

### 2. GitHub Actions で実行する（自動で）

GitHubのサーバーで自動実行する方法です。

#### 準備
1. このリポジトリを自分のGitHubにフォークする
2. シークレット（秘密の設定）を設定する：
   - リポジトリのSettings > Secrets and variables > Actions
   - `GITHUB_TOKEN` を追加（自動で設定されているはず）

#### 実行
1. GitHubのリポジトリページを開く
2. Actionsタブをクリック
3. "Copy GitHub Issues" ワークフローを選ぶ
4. "Run workflow" をクリック
5. 入力フォームに以下の情報を入れる：
   - コピー元のオーナー
   - コピー元のリポジトリ名
   - コピー先のオーナー
   - コピー先のリポジトリ名
   - コメントもコピーするかどうか
   - Issueの状態も保持するかどうか
6. "Run workflow" をクリック

#### 何が起こるか
- GitHubのサーバーが自動でPythonスクリプトを実行
- コピー元のIssuesを取得
- コピー先に新しいIssuesを作成
- 完了すると、通知が来る

## 注意点

- コピー先のリポジトリは事前に作成しておく
- トークンにはリポジトリへのアクセス権限が必要
- たくさんのIssuesをコピーすると時間がかかる

## トラブルシューティング

- 404エラーが出たら：リポジトリが存在するか、トークンの権限を確認
- ファイルが見つからない：ファイル名が `issues_copy.py` か確認

## 技術的な詳細

- 言語：Python
- ライブラリ：requests
- API：GitHub REST API

このツールで、プロジェクトのIssues管理が楽になります！