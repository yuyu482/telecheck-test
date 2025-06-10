"""
AssemblyAI APIクライアント - 話者分離機能付き文字起こし
"""

import os
import assemblyai as aai
import streamlit as st
import tempfile
import time
from typing import Dict, List, Optional
from src.config import config


def init_assemblyai_client():
    """AssemblyAI クライアントを初期化"""
    try:
        if not config.assemblyai_api_key:
            st.markdown("""
            <div class="error-box">
            ❌ AssemblyAI APIキーが設定されていません。
            <br>・ローカル環境: .envファイルにASSEMBLYAI_API_KEYを設定
            <br>・Streamlit Share: シークレット設定で以下のいずれかの形式で設定してください
            <br>　1. assemblyai.api_key
            <br>　2. ASSEMBLYAI_API_KEY
            <br>　3. api_keys.assemblyai
            </div>
            """, unsafe_allow_html=True)
            st.stop()
        
        # AssemblyAI設定
        aai.settings.api_key = config.assemblyai_api_key
        
        # 接続テスト
        try:
            transcriber = aai.Transcriber()
            st.success("✅ AssemblyAI APIに正常に接続しました")
            return transcriber
        except Exception as connection_error:
            st.warning(f"⚠️ 接続テストは失敗しましたが、クライアントを作成しました: {str(connection_error)}")
            return aai.Transcriber()
            
    except Exception as e:
        st.markdown(f"""
        <div class="error-box">
        ❌ AssemblyAI クライアントの初期化エラー: {str(e)}
        </div>
        """, unsafe_allow_html=True)
        st.stop()


def transcribe_with_speaker_diarization(audio_file, transcriber) -> Optional[Dict]:
    """音声ファイルを話者分離付きで文字起こし"""
    tmp_file_path = None
    
    try:
        # ファイルサイズ情報取得
        file_info = config.get_file_size_info(audio_file.size)
        
        # 処理ステータス表示
        status_msg = st.empty()
        
        if file_info["is_very_large"]:
            status_msg.markdown(f"""
            <div class="warning-box">
            🎤 大容量ファイル({file_info["size_mb"]:.1f}MB)の話者分離付き文字起こし中です。
            <br>処理には10分以上かかる場合があります...
            </div>
            """, unsafe_allow_html=True)
        else:
            status_msg.markdown("""
            <div class="info-box">
            🎤 話者分離付き文字起こし中です。これには数分かかる場合があります...
            </div>
            """, unsafe_allow_html=True)
        
        # 一時ファイル作成
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(audio_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # AssemblyAI設定
        transcript_config = aai.TranscriptionConfig(
            speaker_labels=True,
            speakers_expected=config.default_speakers_expected,
            language_code=config.default_language
        )
        
        # 文字起こし実行
        transcript = transcriber.transcribe(tmp_file_path, config=transcript_config)
        
        # エラーチェック
        if transcript.status == aai.TranscriptStatus.error:
            status_msg.markdown(f"""
            <div class="error-box">
            ❌ 文字起こし処理に失敗しました: {transcript.error}
            </div>
            """, unsafe_allow_html=True)
            return None
        
        # 完了表示をクリア
        status_msg.empty()
        
        # 結果を構造化して返す
        result = {
            "full_text": transcript.text,
            "utterances": transcript.utterances,
            "speakers": _extract_speakers(transcript.utterances),
            "raw_transcript": transcript,
            "file_info": file_info
        }
        
        return result
        
    except Exception as e:
        if 'status_msg' in locals():
            status_msg.markdown(f"""
            <div class="error-box">
            ❌ 文字起こし処理に失敗しました: {str(e)}
            </div>
            """, unsafe_allow_html=True)
        return None
        
    finally:
        # 一時ファイルの削除
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


def _extract_speakers(utterances) -> Dict[str, List[str]]:
    """話者別に発言を整理"""
    speakers = {}
    
    for utterance in utterances:
        speaker = utterance.speaker
        if speaker not in speakers:
            speakers[speaker] = []
        speakers[speaker].append(utterance.text)
    
    return speakers


def format_transcript_with_speakers(transcript_result: Dict, teleapo_speaker: str) -> str:
    """話者分離結果をフォーマット（Google Sheets保存用）"""
    if not transcript_result or not transcript_result.get("utterances"):
        return "文字起こし結果が取得できませんでした。"
    
    # ファイル情報
    file_info = transcript_result.get("file_info", {})
    size_info = f"（ファイルサイズ: {file_info.get('size_mb', 0):.1f}MB）" if file_info else ""
    
    # 全体の会話部分
    full_conversation = f"=== 全体の会話 {size_info} ===\n"
    for utterance in transcript_result["utterances"]:
        full_conversation += f"[{utterance.speaker}] {utterance.text}\n"
    
    # テレアポ担当者の発言のみ
    teleapo_only = f"\n=== テレアポ担当者の発言のみ ({teleapo_speaker}) ===\n"
    teleapo_statements = []
    
    for utterance in transcript_result["utterances"]:
        if utterance.speaker == teleapo_speaker:
            teleapo_statements.append(utterance.text)
    
    teleapo_only += "\n".join(teleapo_statements)
    
    return full_conversation + teleapo_only


def get_teleapo_speaker_content(transcript_result: Dict, teleapo_speaker: str) -> str:
    """テレアポ担当者の発言のみを取得（品質チェック用）"""
    if not transcript_result or not transcript_result.get("utterances"):
        return ""
    
    teleapo_statements = []
    for utterance in transcript_result["utterances"]:
        if utterance.speaker == teleapo_speaker:
            teleapo_statements.append(utterance.text)
    
    return "\n".join(teleapo_statements) 