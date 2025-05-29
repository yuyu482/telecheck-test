## 主な機能

- **音声ファイル処理**: MP3形式の音声ファイルをアップロード（最大25MB）
- **AI文字起こし**: OpenAI Whisper APIを使用した日本語音声の高精度文字起こし
- **詳細品質チェック**: Difyと同じ26項目の詳細な品質評価
- **データ保存**: 品質チェック結果をGoogle Sheetsに自動保存（30列の詳細データ）
- **ユーザーインターフェース**: Streamlitを使用した直感的なWebインターフェース

## システム要件

- Python 3.11+
- OpenAI API キー
- Google Cloud Platform サービスアカウント
- Google Sheets API アクセス権限

## セットアップ

### 1. Python環境の準備

#### 1.1. 仮想環境の作成
```bash
# 1. 仮想環境の作成
python -m venv venv

# 2. 仮想環境のアクティベート
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 1.2. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 2. Google Cloud Platform設定

#### 2.1. プロジェクトの作成・選択

1. **GCPコンソールにアクセス**
   - [Google Cloud Console](https://console.cloud.google.com/) にアクセス
   - Googleアカウントでログイン

2. **新しいプロジェクトを作成**
   - 上部の「プロジェクトを選択」をクリック
   - 「新しいプロジェクト」をクリック
   - プロジェクト名を入力（例：`teleapo-mvp`）
   - 「作成」をクリック

#### 2.2. 必要なAPIの有効化

⚠️ **重要**: このシステムは Google Sheets API と Google Drive API の **両方** が必要です。

**なぜ Google Drive API が必要なのか？**
- Google Sheets API: スプレッドシートの読み書きに使用
- Google Drive API: スプレッドシートファイルへのアクセス権限管理に使用
- システムが使用するgspreadライブラリは内部的に Google Drive API を使用

1. **Google Sheets API の有効化**
   - 左サイドメニューから「APIとサービス」→「ライブラリ」
   - 検索バーで「Google Sheets API」を検索
   - 「Google Sheets API」をクリック
   - 「有効にする」ボタンをクリック

2. **Google Drive API の有効化** ⚠️ **必須**
   - 同じ「ライブラリ」画面で検索バーで「Google Drive API」を検索
   - 「Google Drive API」をクリック
   - 「有効にする」ボタンをクリック

3. **有効化の確認**
   - 「APIとサービス」→「有効なAPI」から以下の2つが表示されることを確認：
     - ✅ Google Sheets API
     - ✅ Google Drive API

⚠️ **注意**: API有効化後、システムに反映されるまで3-5分かかる場合があります。

#### 2.3. サービスアカウントの作成

1. **サービスアカウント作成**
   - 左サイドメニューから「APIとサービス」→「認証情報」
   - 「認証情報を作成」→「サービスアカウント」をクリック
   - 以下を入力：
     - **サービスアカウント名**: 
     - **サービスアカウントID**: 自動生成される
     - **説明**: `テレアポシステム用サービスアカウント`
   - 「作成して続行」をクリック

2. **ロールの付与**
   - 「ロールを選択」ドロップダウンから以下を選択：
     - `編集者` または `Project Editor`
   - 「続行」をクリック
   - 「完了」をクリック

#### 2.4. サービスアカウントキーの作成・ダウンロード

1. **キーファイルの作成**
   - 作成されたサービスアカウントをクリック
   - 「キー」タブをクリック
   - 「キーを追加」→「新しいキーを作成」
   - 「JSON」を選択
   - 「作成」をクリック

2. **ファイルの保存とプロジェクトへの配置**
   - JSONファイルが自動でダウンロードされます
   - ファイル名は `プロジェクト名-xxxxxxxx.json` のような形式

#### 2.5. credentials.json ファイルの配置

**方法1: PowerShellでファイルをコピー**
```powershell
# ダウンロードフォルダからプロジェクトルートにコピー
copy "$env:USERPROFILE\Downloads\your-project-12345-abcdef.json" "credentials.json"
```

**方法2: 手動でファイルをコピー**
1. ダウンロードフォルダからダウンロードしたJSONファイルを選択
2. プロジェクトルート（`telecheck_mvp`フォルダ）にコピー
3. ファイル名を `credentials.json` に変更

### 3. OpenAI API設定

#### 3.1. OpenAI APIキーの取得

1. [OpenAI API](https://platform.openai.com/api-keys) にアクセス
2. アカウントにログイン
3. 「Create new secret key」をクリック
4. APIキーをコピー（`sk-...` で始まる文字列）

#### 3.2. .env ファイルの作成

プロジェクトルートに `.env` ファイルを作成し、以下の内容を記述：

```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

⚠️ **重要**: `.env` ファイルと `credentials.json` ファイルは機密情報を含むため、Gitにコミットしないでください。これらのファイルは `.gitignore` で除外設定済みです。

### 4. Google Sheetsの準備

#### 4.1. スプレッドシートの作成

1. [Google Sheets](https://sheets.google.com/) にアクセス
2. 「空白のスプレッドシート」をクリック
3. スプレッドシート名を「テレアポチェックシート」に変更
4. シート名を「Difyテスト」に変更

#### 4.2. サービスアカウントへのアクセス権限付与

1. スプレッドシートの「共有」ボタンをクリック
2. `credentials.json`内の`client_email`（例：`teleapo-service-account@your-project.iam.gserviceaccount.com`）を入力
3. 権限を「編集者」に設定
4. 「送信」をクリック

詳細な設定手順は `CREDENTIALS_SETUP.md` を参照してください。

### 5. Google Sheetsのヘッダー設定

「Difyテスト」シートの1行目に以下のヘッダーを設定：

| A列 | B列 | C列 | D列 | ... | AE列 |
|-----|-----|-----|-----|-----|------|
| ファイル名 | 文字起こし内容 | 処理日時 | テレアポ担当者名 | ... | 処理状況 |

## 使用方法

### 1. アプリケーションの起動

```bash
streamlit run app.py
```

### 2. ブラウザでアクセス

通常は http://localhost:8501 でアクセス可能

### 3. 文字起こし

1. 「📝 文字起こし」タブを選択
2. MP3ファイルをアップロード
3. 「🎤 文字起こし開始」ボタンをクリック

### 4. 品質チェック

1. 「🔍 品質チェック」タブを選択
2. 担当者を選択（複数選択可能）
3. 処理設定を調整
4. 「🔍 品質チェック実行」ボタンをクリック

## 技術スタック

- **フロントエンド**: Streamlit（Pythonベースのウェブアプリフレームワーク）
- **音声処理API**: OpenAI Whisper API（AI音声認識モデル）
- **言語処理API**: OpenAI GPT-4o-mini（品質チェック用）
- **データストレージ**: Google Sheets API（スプレッドシート操作）
- **認証**: Google OAuth2.0（GCPサービスアカウント）
- **言語・環境**: Python 3.11+

## ファイル構成

```
teleapo_mvp/
├── app.py                      # メインアプリケーション
├── requirements.txt            # 依存パッケージリスト
├── .env                        # 環境変数設定ファイル
├── credentials.json            # Google API認証用JSONファイル
├── src/
│   ├── api/
│   │   ├── openai_client.py    # OpenAI API クライアント
│   │   └── sheets_client.py    # Google Sheets API クライアント
│   ├── ui/
│   │   ├── main_app.py         # メインアプリケーションロジック
│   │   ├── components.py       # UIコンポーネント
│   │   └── styles.py           # スタイル定義
│   ├── utils/
│   │   ├── quality_check.py    # 品質チェックワークフロー（Dify互換）
│   │   └── batch_processor.py  # バッチ処理管理
│   └── prompts/
│       └── system_prompts.py   # システムプロンプト（Dify互換）
├── README.md                   # このファイル
├── CREDENTIALS_SETUP.md        # 認証設定手順
└── LOCAL_SETUP.md             # ローカル環境セットアップ手順
```

## Difyとの互換性

このシステムは、Difyで開発された品質チェックワークフローと完全に互換性があります：

- **同じプロンプト**: Difyで使用されているプロンプトを完全再現
- **同じワークフロー**: 固有名詞置換 → 話者分離 → 品質チェック → JSON変換の流れ
- **同じ出力形式**: 30列の詳細なチェック結果をGoogle Sheetsに出力
- **同じ担当者リスト**: Difyで定義された9名の担当者名を使用

## トラブルシューティング

### よくある問題

1. **API接続エラー**: `.env` ファイルのAPIキーを確認
2. **Google Sheetsエラー**: `credentials.json` の設定とアクセス権限を確認
3. **Google Drive API エラー** ⚠️ **頻出**
   ```
   Google Drive API has not been used in project before or it is disabled
   ```
   **解決方法**:
   - Google Cloud Consoleで Google Drive API を有効化
   - エラーメッセージのリンクから直接有効化ページにアクセス可能
   - 有効化後、3-5分待機してから再試行
4. **アップロードエラー**: ファイルサイズ（25MB以下）と形式（MP3）を確認
5. **品質チェックエラー**: 担当者選択と処理対象データの存在を確認

### ログの確認

アプリケーション実行時のコンソール出力でエラー詳細を確認できます。

## ライセンス

© 2024 テレアポ品質チェックシステム - Version 1.2.0（Dify互換版）

## 更新履歴

### v1.2.0（Dify互換版）
- Difyと同じ詳細な品質チェック手法を実装
- 26項目の詳細チェック項目を追加
- 担当者リストをDify互換に更新
- Google Sheets出力を30列の詳細形式に変更
- ワークフローをDifyと完全互換に変更 
