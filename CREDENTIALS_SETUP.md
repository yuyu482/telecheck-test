# Google Cloud認証情報の設定ガイド

## 🔧 Google Cloud Consoleでの設定手順

### 1. プロジェクトの作成・選択
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成、または既存のプロジェクトを選択

### 2. APIの有効化
以下のAPIを有効化してください：
- **Google Sheets API**
- **Google Drive API**

### 3. サービスアカウントの作成
1. **IAM と管理** → **サービス アカウント**
2. **サービス アカウントを作成**をクリック
3. サービスアカウント名を入力（例：`teleapo-checker`）
4. **作成して続行**をクリック

### 4. 権限の設定
以下の権限を付与：
- **編集者** または **Google Sheets API** の権限

### 5. 認証キーの生成
1. 作成したサービスアカウントをクリック
2. **キー**タブに移動
3. **鍵を追加** → **新しい鍵を作成**
4. **JSON**を選択してダウンロード

## 🔒 ローカル環境での設定

### 1. 認証ファイルの配置
```bash
# プロジェクトルートに配置
mv ~/Downloads/your-project-xxxxx.json /path/to/teleapo_mvp/credentials.json
```

### 2. スプレッドシートの共有
1. Google Sheetsで「テレアポチェックシート」を作成
2. サービスアカウントのメールアドレスと共有
3. **編集者**権限を付与

### 3. 安全性の確認
```bash
# .gitignoreに含まれていることを確認
cat .gitignore | grep credentials.json

# ファイル権限を制限
chmod 600 credentials.json
```

## 🌐 Streamlit Shareでの設定

### Secretsの設定例
```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
YOUR_ACTUAL_PRIVATE_KEY_CONTENT
-----END PRIVATE KEY-----
"""
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
universe_domain = "googleapis.com"
```

## ⚠️ セキュリティ注意点

### ❌ やってはいけないこと
- `credentials.json`をGitにコミット
- 認証情報をコードに直接記述
- 認証ファイルをメールで送信
- 公開フォルダに保存

### ✅ 推奨事項
- `.gitignore`で除外
- ファイル権限を`600`に設定
- 定期的なキーローテーション
- 最小権限の原則を適用

## 🔍 トラブルシューティング

### エラー: "credentials.json not found"
1. ファイルがプロジェクトルートにあるか確認
2. ファイル名が正確か確認（`credentials.json`）
3. 権限エラーの場合は`chmod 600`を実行

### エラー: "Permission denied"
1. サービスアカウントにGoogle Sheets APIの権限があるか確認
2. スプレッドシートがサービスアカウントと共有されているか確認
3. 編集者権限が付与されているか確認 