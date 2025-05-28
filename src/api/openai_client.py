"""
OpenAI APIとの通信を行うクライアントモジュール
"""

import os
from openai import OpenAI
import streamlit as st
import time

def init_openai_client():
    """OpenAI クライアントを初期化"""
    try:
        # 環境変数からAPIキーを取得
        api_key = os.getenv("OPENAI_API_KEY")
        
        # 環境変数にない場合はStreamlitのシークレットから取得（複数のパターンに対応）
        if not api_key and hasattr(st, 'secrets'):
            # パターン1: openai.api_key の形式
            if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
                api_key = st.secrets["openai"]["api_key"]
            # パターン2: OPENAI_API_KEY の形式
            elif "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
            # パターン3: api_keys.openai の形式
            elif "api_keys" in st.secrets and "openai" in st.secrets["api_keys"]:
                api_key = st.secrets["api_keys"]["openai"]
        
        if not api_key:
            st.markdown("""
            <div class="error-box">
              ❌ OpenAI APIキーが設定されていません。
              <br>・ローカル環境: .envファイルにOPENAI_API_KEYを設定
              <br>・Streamlit Share: シークレット設定で以下のいずれかの形式で設定してください
              <br>　1. openai.api_key
              <br>　2. OPENAI_API_KEY
              <br>　3. api_keys.openai
            </div>
            """, unsafe_allow_html=True)
            st.stop()

        # デバッグ情報を表示
        st.write(f"DEBUG: APIキーの長さ: {len(api_key) if api_key else 0}")
        
        try:
            # OpenAIクライアントの初期化（必要最小限のパラメータのみ）
            client = OpenAI(
                api_key=api_key,
                # timeout=60,  # 必要に応じてタイムアウトを設定
            )
            
            # 簡単な接続テスト（models.listは重いのでより軽いテストに変更）
            try:
                # より軽量なテスト：短いチャット応答で接続確認
                test_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1,
                    temperature=0
                )
                
                # 成功メッセージ
                st.success("✅ OpenAI APIに正常に接続しました")
                return client
                
            except Exception as connection_error:
                # 接続テストが失敗した場合でも、クライアント自体は返す
                # （実際の使用時にエラーハンドリングする）
                st.warning(f"⚠️ 接続テストは失敗しましたが、クライアントを作成しました: {str(connection_error)}")
                return client
                
        except TypeError as type_error:
            # TypeError が発生した場合（proxiesパラメータなど）
            if "unexpected keyword argument" in str(type_error):
                st.markdown(f"""
                <div class="error-box">
                  ❌ OpenAI SDK のバージョン問題が発生しています。
                  <br>エラー: {str(type_error)}
                  <br><br>解決方法:
                  <br>1. OpenAI SDKを最新版に更新: pip install --upgrade openai
                  <br>2. requirements.txtで openai==1.16.0 以上を指定
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="error-box">
                  ❌ OpenAI クライアント初期化エラー: {str(type_error)}
                </div>
                """, unsafe_allow_html=True)
            
            st.write(f"DEBUG: エラータイプ: {type(type_error)}")
            st.write(f"DEBUG: エラー詳細: {str(type_error)}")
            st.stop()
            
        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
              ❌ OpenAI API接続エラー: {str(e)}
            </div>
            """, unsafe_allow_html=True)
            st.write(f"DEBUG: エラータイプ: {type(e)}")
            st.write(f"DEBUG: エラー詳細: {str(e)}")
            st.stop()

    except Exception as e:
        st.markdown(f"""
        <div class="error-box">
          ❌ OpenAI クライアントの初期化エラー: {str(e)}
        </div>
        """, unsafe_allow_html=True)
        st.write(f"DEBUG: エラータイプ: {type(e)}")
        st.write(f"DEBUG: エラー詳細: {str(e)}")
        st.stop()

def chat_with_retry(client, system_prompt, user_prompt, temperature=0.0, expect_json=False, model="gpt-4o-mini", max_retries=3):
    """OpenAI Chat APIを使用してプロンプトの応答を取得（リトライ機能付き）"""
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            retry_count += 1
            if retry_count == max_retries:
                st.markdown(f"""
                <div class="error-box">
                  ❌ APIリクエストに失敗しました（{max_retries}回試行）: {str(e)}
                </div>
                """, unsafe_allow_html=True)
                return None
            st.markdown(f"""
            <div class="warning-box">
              ⚠️ APIリクエストに失敗しました。リトライします ({retry_count}/{max_retries})...
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)  # リトライ前に少し待機

def transcribe_audio(audio_file, client):
    """音声ファイルを文字起こし"""
    import tempfile

    tmp_file_path = None
    try:
        # 処理ステータス表示
        status_msg = st.empty()
        status_msg.markdown("""
        <div class="info-box">
          🎤 音声ファイルを文字起こし中です。これには数分かかる場合があります...
        </div>
        """, unsafe_allow_html=True)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(audio_file.getvalue())
            tmp_file_path = tmp_file.name
        
        with open(tmp_file_path, "rb") as audio:
            try:
                transcript = client.audio.transcriptions.create(
                    file=audio,
                    model="whisper-1",
                    language="ja",
                    response_format="text"
                )
                
                # 完了表示をクリア
                status_msg.empty()
                return transcript
            except Exception as e:
                status_msg.markdown(f"""
                <div class="error-box">
                  ❌ 文字起こし処理に失敗しました: {str(e)}
                </div>
                """, unsafe_allow_html=True)
                st.write(f"DEBUG: 文字起こしエラー詳細: {str(e)}")
                return None
    finally:
        # 一時ファイルの削除
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)