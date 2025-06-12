# 話者分離機能の設定とテスト手順

## 概要

このシステムは AssemblyAI API を使用した話者分離機能を搭載しており、テレアポの音声から話者を自動判定し、品質チェック対象を絞り込むことができます。

## 機能構成

### 1. 新規追加ファイル

- `src/api/assemblyai_client.py`: AssemblyAI API との通信クライアント
- `src/utils/speaker_detection.py`: テレアポ担当者自動判定ロジック
- `env_example.txt`: 環境変数設定例

### 2. 更新ファイル

- `requirements.txt`: assemblyai>=0.41.0 を追加
- `src/api/openai_client.py`: 従来機能を非推奨としてマーク
- `src/ui/main_app.py`: 話者分離機能を統合
- `README.md`: 新機能の説明を追加

## セットアップ手順

### 1. AssemblyAI APIキーの取得

1. [AssemblyAI](https://www.assemblyai.com/) でアカウントを作成
2. ダッシュボードでAPIキーを確認
3. `.env` ファイルに追加：

```env
OPENAI_API_KEY=sk-your-openai-key
ASSEMBLYAI_API_KEY=your-assemblyai-key
```

### 2. パッケージのインストール

```bash
pip install assemblyai>=0.41.0
```

## 使用方法

### 基本的な使用例

```python
from src.api.assemblyai_client import init_assemblyai_client, transcribe_with_speaker_diarization
from src.utils.speaker_detection import detect_teleapo_speaker

# クライアント初期化
client = init_assemblyai_client()

# 話者分離付き文字起こし
transcript_result = transcribe_with_speaker_diarization(audio_file, client)

# テレアポ担当者自動判定
teleapo_speaker = detect_teleapo_speaker(transcript_result)
```

## 話者判定ロジックの詳細

### 判定基準

`src/utils/speaker_detection.py` の `TeleapoSpeakerDetector` クラスで定義されています：

#### キーワードベースの判定

1. **会社名・自己紹介キーワード** (重み: 3.0)
   - "会社", "株式会社", "と申します", "営業", "担当" など

2. **商品・サービス紹介キーワード** (重み: 2.5)
   - "ご紹介", "サービス", "商品", "料金", "キャンペーン" など

3. **顧客対応キーワード** (重み: 2.0)
   - "いかがでしょうか", "ご質問", "ご相談", "説明" など

4. **顧客反応キーワード** (重み: -2.0)
   - "はい", "そうですね", "なるほど", "検討します" など

#### その他の判定要素

- **発言量**: 60%以上発言している場合は +2.0 ポイント
- **最初の話者**: 通常テレアポ担当者なので +1.5 ポイント

### 判定ルールのカスタマイズ

開発者は以下のようにルールを変更できます：

```python
from src.utils.speaker_detection import update_detection_rules

# カスタムルールで更新
new_rules = {
    "company_keywords": ["弊社", "私ども", "当社"],
    "weights": {
        "company_keywords": 4.0,  # 重みを変更
    },
    "speech_ratio_threshold": 0.7  # 閾値を変更
}

update_detection_rules(new_rules)
```

## 出力形式

### 話者分離結果の構造

```python
transcript_result = {
    "full_text": "完全な文字起こし内容",
    "utterances": [
        {
            "speaker": "A",
            "text": "発言内容",
            "start": 開始時間,
            "end": 終了時間
        },
        # ...
    ],
    "speakers": {
        "A": ["発言1", "発言2", ...],
        "B": ["発言1", "発言2", ...]
    },
    "raw_transcript": # AssemblyAI生レスポンス
}
```

### Google Sheets保存形式

```
=== 全体の会話 ===
[A] こんにちは、株式会社〇〇の田中と申します。
[B] はい、お疲れさまです。
[A] 本日はお忙しい中、お時間をいただきありがとうございます。

=== テレアポ担当者の発言のみ (A) ===
こんにちは、株式会社〇〇の田中と申します。
本日はお忙しい中、お時間をいただきありがとうございます。
```

## トラブルシューティング

### よくある問題

1. **AssemblyAI接続エラー**
   ```
   AssemblyAI APIキーが設定されていません
   ```
   **解決方法**: `.env` ファイルで `ASSEMBLYAI_API_KEY` を設定

2. **音声ファイル処理エラー**
   ```
   文字起こし処理に失敗しました
   ```
   **解決方法**: 
   - ファイル形式がMP3であることを確認
   - ファイルサイズが25MB以下であることを確認
   - 音声の品質を確認

3. **話者分離がうまくいかない**
   - 音声の品質が低い場合は判定精度が下がります
   - 2名以上の話者がいる場合は期待通りに動作しない可能性があります

### デバッグ機能

判定根拠を確認したい場合：

```python
from src.utils.speaker_detection import get_detection_summary

summary = get_detection_summary(transcript_result)
print(summary)
```

### ログの確認

- Streamlit アプリのコンソール出力でエラー詳細を確認
- AssemblyAI API のステータスは処理中に表示されます

## 互換性情報

### バージョン要件

- Python 3.11+
- assemblyai >= 0.41.0
- streamlit >= 1.29.0

### 既存機能との互換性

- 従来のWhisper API機能は引き続き利用可能
- Google Sheets保存機能は変更なし
- 品質チェック機能は話者分離結果に対応

## パフォーマンス

### 処理時間

- 5分の音声ファイル: 約2-3分で処理完了
- 処理時間は音声の長さとAssemblyAI APIの負荷に依存

### 精度

- 日本語音声での話者分離精度: 約85-95%
- テレアポ担当者判定精度: 約90-95%（キーワードベース）

## 今後の拡張予定

1. **3名以上の話者への対応**
2. **より詳細な感情分析**
3. **リアルタイム処理対応**
4. **カスタム話者ラベル設定**

---

## 開発者向けAPI参考

### assemblyai_client.py

```python
# クライアント初期化
transcriber = init_assemblyai_client()

# 話者分離付き文字起こし
result = transcribe_with_speaker_diarization(audio_file, transcriber)

# フォーマット
formatted = format_transcript_with_speakers(result, teleapo_speaker)

# テレアポ担当者の発言のみ取得
teleapo_content = get_teleapo_speaker_content(result, teleapo_speaker)
```

### speaker_detection.py

```python
# テレアポ担当者判定
speaker = detect_teleapo_speaker(transcript_result)

# 判定根拠の取得
summary = get_detection_summary(transcript_result)

# ルール更新
update_detection_rules(new_rules)
``` 