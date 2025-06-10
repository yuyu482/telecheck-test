# 📞 テレアポ文字起こし・品質チェックシステム v2.0

AssemblyAI API による話者分離機能付きの文字起こしシステムです。
テレアポの録音データを自動的に文字起こしし、話者を分離してテレアポ担当者の発言を特定します。

## 🌟 主な機能

### 🎤 話者分離文字起こし
- **AssemblyAI API** による高精度な話者分離
- **自動テレアポ担当者判定** - 発言内容から担当者を自動識別
- **大容量ファイル対応** - 最大2GB（2,048MB）まで対応
- **複数ファイル一括処理** - 同時に複数ファイルの処理が可能

### 🔍 品質チェック
- **OpenAI GPT-4o-mini** による文字起こし品質の自動チェック
- **カスタム担当者設定** - 複数担当者の品質評価に対応
- **バッチ処理** - 大量データの効率的な処理

### 📊 データ管理
- **Google Sheets連携** - 結果の自動保存・管理
- **話者別集計** - テレアポ担当者の発言のみを抽出
- **ファイル情報追跡** - サイズ、処理時間等の詳細記録

## 🏗️ アーキテクチャ

### ファイル構造
```
src/
├── config.py                 # 🔧 アプリケーション設定管理
├── api/
│   ├── assemblyai_client.py   # 🎤 AssemblyAI API（文字起こし・話者分離）
│   ├── openai_client.py       # 🤖 OpenAI API（品質チェック専用）
│   └── sheets_client.py       # 📊 Google Sheets API
├── ui/
│   ├── main_app.py           # 🖥️ メインアプリケーション
│   ├── components.py         # 🧩 UIコンポーネント
│   └── styles.py             # 🎨 スタイル定義
└── utils/
    ├── speaker_detection.py   # 🔍 テレアポ担当者自動判定
    ├── quality_check.py       # ✅ 品質チェックロジック
    └── batch_processor.py     # ⚡ バッチ処理エンジン
```

### 技術スタック
- **Frontend**: Streamlit
- **音声処理**: AssemblyAI API
- **AI分析**: OpenAI GPT-4o-mini
- **データ保存**: Google Sheets API
- **言語**: Python 3.9+

## 🚀 セットアップ

### 1. 環境準備
```bash
# リポジトリクローン
git clone <repository-url>
cd telecheck-system

# 仮想環境作成・有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt
```

### 2. API キー設定

#### ローカル環境
`.env` ファイルを作成：
```env
# AssemblyAI API（話者分離文字起こし用）
ASSEMBLYAI_API_KEY=your-assemblyai-api-key

# OpenAI API（品質チェック用）
OPENAI_API_KEY=your-openai-api-key
```

#### Streamlit Cloud環境
Secrets設定で以下のいずれかの形式で設定：

**方式1: 階層化設定**
```toml
[assemblyai]
api_key = "your-assemblyai-api-key"

[openai]
api_key = "your-openai-api-key"
```

**方式2: フラット設定**
```toml
ASSEMBLYAI_API_KEY = "your-assemblyai-api-key"
OPENAI_API_KEY = "your-openai-api-key"
```

### 3. Google Sheets認証設定
詳細は [CREDENTIALS_SETUP.md](CREDENTIALS_SETUP.md) を参照

### 4. アプリケーション起動
```bash
streamlit run app.py
```

## 🔧 設定・カスタマイズ

### ファイルサイズ制限の変更
`.streamlit/config.toml` で調整可能：
```toml
[server]
maxUploadSize = 2048  # MB単位
```

### 話者判定ルールのカスタマイズ
`src/utils/speaker_detection.py` で判定ロジックを調整：
- キーワード重み
- 発言量による判定
- 最初話者ボーナス

### アプリケーション設定
`src/config.py` で各種設定を変更：
- ファイルサイズ制限
- 処理並行数
- バッチサイズ

## 📋 使用方法

### 話者分離文字起こし
1. **音声ファイルアップロード** - mp3ファイルを選択
2. **自動処理実行** - 話者分離と担当者判定を実行
3. **結果確認** - 話者別発言数と判定結果を確認
4. **Google Sheets保存** - フォーマット済み結果を自動保存

### 品質チェック
1. **担当者設定** - カンマ区切りで担当者名を入力
2. **処理設定** - 最大処理行数を指定
3. **バッチ実行** - Google Sheetsデータの品質チェック実行

## 🔍 ファイルサイズ対応

### サイズ制限
- **最大ファイルサイズ**: 2GB（2,048MB）
- **推奨ファイルサイズ**: 500MB以下
- **複数ファイル**: 同時アップロード可能（推奨10ファイル以下）

### パフォーマンス
| ファイルサイズ | 処理時間目安 | 推奨事項 |
|-------------|------------|----------|
| ～100MB     | 1-3分      | 標準処理 |
| 100-500MB   | 3-8分      | 推奨範囲 |
| 500MB-1GB   | 8-15分     | 注意が必要 |
| 1GB-2GB     | 15分以上    | 安定した環境必須 |

## 🛠️ トラブルシューティング

### よくある問題

#### 1. アップロードエラー
- **原因**: ファイルサイズ制限超過
- **解決**: `.streamlit/config.toml`の設定確認

#### 2. メモリエラー
- **原因**: 大容量ファイルまたは同時処理数過多
- **解決**: ファイル分割またはバッチサイズ削減

#### 3. API接続エラー
- **原因**: APIキー設定ミス
- **解決**: 環境変数またはSecrets設定確認

#### 4. 話者判定精度
- **原因**: 音声品質またはキーワード設定
- **解決**: `speaker_detection.py`の判定ルール調整

### ログ・デバッグ
- 処理状況はStreamlit画面でリアルタイム表示
- エラー詳細は画面上に表示
- 設定状況は起動時に自動チェック

## 📈 バージョン履歴

### v2.0.0（リファクタリング版）
- 🎯 AssemblyAI専用化（Whisper API削除）
- 🔧 設定管理統一化
- 📁 ファイル構造最適化
- 🚀 パフォーマンス向上
- 💾 最大2GBファイル対応

### v1.2.0
- 話者分離機能追加
- 複数API対応

### v1.0.0
- 基本文字起こし機能

## 🤝 開発・貢献

### 開発環境
```bash
# 開発依存関係インストール
pip install -r requirements-dev.txt

# コード品質チェック
flake8 src/
black src/

# テスト実行
pytest tests/
```

### 貢献方法
1. Forkしてfeatureブランチ作成
2. 変更実装とテスト追加
3. Pull Request作成

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照

## 🆘 サポート

- **技術的な質問**: GitHubのIssuesを使用
- **バグ報告**: Issues テンプレートに従って報告
- **機能要望**: Discussionsで提案

---

**© 2024 テレアポ品質チェックシステム - Version 2.0.0**
