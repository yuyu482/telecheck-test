# 🏠 ローカル開発環境セットアップガイド

## 📋 概要
このガイドでは、テレアポMVPシステムをローカル環境で動作させるための設定方法を説明します。

## 🔧 必要な設定ファイル

### 1. `.env`ファイル（環境変数）
```bash
# 1. サンプルファイルをコピー
cp .env.example .env

# 2. エディタで編集
# OpenAI API キーを実際の値に変更
OPENAI_API_KEY=sk-your-actual-openai-api-key
```

### 2. `credentials.json`ファイル（Google Cloud認証情報）
```bash
# Google Cloud Consoleから取得したサービスアカウントキーファイル
# プロジェクトルートに配置
mv ~/Downloads/your-project-12345-abcdef123456.json ./credentials.json

# セキュリティのためアクセス権限を制限
chmod 600 credentials.json
```

## ⚠️ **重要な注意事項**

### ❌ **絶対にGitにコミットしてはいけないファイル**
- `.env` - OpenAI APIキーなど機密情報を含む
- `credentials.json` - Google Cloud認証情報

### ✅ **自動的に除外される仕組み**
`.gitignore`で以下のファイルが除外設定済み：
```gitignore
# 環境変数ファイル
.env

# Google Cloud認証情報
credentials.json
```

## 🚀 セットアップ手順

### Step 1: リポジトリクローン
```bash
git clone [your-repository-url]
cd teleapo_mvp
```

### Step 2: 仮想環境作成
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate     # Windows
```

### Step 3: 依存関係インストール
```bash
pip install -r requirements.txt
```

### Step 4: 環境変数設定
```bash
# 1. サンプルファイルをコピー
cp .env.example .env

# 2. .envファイルを編集（実際の値に変更）
nano .env  # または好きなエディタで編集
```

### Step 5: Google Cloud認証設定
```bash
# 1. credentials.jsonをプロジェクトルートに配置
# 2. アクセス権限を制限
chmod 600 credentials.json

# 3. ファイルの存在確認
ls -la credentials.json
```

### Step 6: アプリケーション起動
```bash
streamlit run app.py
```

## 🔍 設定確認

### 環境変数チェック
```python
# Python REPLで確認
import os
from dotenv import load_dotenv

load_dotenv()
print("OpenAI API Key設定:", "✅" if os.getenv("OPENAI_API_KEY") else "❌")
```

### Google Cloud認証チェック
```python
# 認証ファイルの確認
import os
print("Credentials file:", "✅" if os.path.exists("credentials.json") else "❌")
```

## 🚨 トラブルシューティング

### よくある問題

#### 1. OpenAI APIキーエラー
```
Error: OpenAI API key not found
```
**解決方法:**
- `.env`ファイルのAPIキーを確認
- APIキーの形式：`sk-...`で始まる
- quotesは不要

#### 2. Google Cloud認証エラー
```
Error: Could not automatically determine credentials
```
**解決方法:**
- `credentials.json`がプロジェクトルートにあるか確認
- ファイルの権限設定確認：`chmod 600 credentials.json`
- JSONファイルの形式確認

#### 3. パッケージインポートエラー
```
ModuleNotFoundError: No module named 'xxx'
```
**解決方法:**
```bash
# 仮想環境がアクティブか確認
which python
# または
python -m pip list

# 依存関係再インストール
pip install -r requirements.txt
```

## 📁 ディレクトリ構造
```
teleapo_mvp/
├── .env                    # ⚠️  Git除外 - 環境変数
├── .env.example           # ✅  サンプルファイル
├── credentials.json        # ⚠️  Git除外 - Google認証
├── credentials.json.example # ✅  サンプルファイル
├── app.py                 # メインアプリケーション
├── requirements.txt       # Python依存関係
├── .gitignore            # Git除外設定
└── src/                  # ソースコード
    ├── ui/
    ├── utils/
    └── services/
```

## 🔐 セキュリティベストプラクティス

1. **APIキー管理**
   - 定期的にローテーション
   - 不要なアクセス権限は付与しない
   - プロジェクト専用のキーを使用

2. **認証ファイル**
   - アクセス権限を最小限に制限
   - バックアップは暗号化
   - 共有は避ける

3. **バージョン管理**
   - 機密ファイルは絶対にコミットしない
   - `.gitignore`の定期チェック
   - コミット前の確認習慣

## 💡 ヒント

### 開発効率化
```bash
# 環境変数確認用alias
alias check-env='python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(\"OpenAI:\", \"✅\" if os.getenv(\"OPENAI_API_KEY\") else \"❌\"); print(\"Credentials:\", \"✅\" if os.path.exists(\"credentials.json\") else \"❌\")"'

# Streamlit起動用alias
alias run-teleapo='streamlit run app.py'
```

### VSCode設定
`.vscode/settings.json`（オプション）:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "files.exclude": {
        ".env": true,
        "credentials.json": true
    }
}
``` 