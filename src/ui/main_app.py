"""
メインアプリケーションロジック
"""

import streamlit as st
from src.ui.components import (
    setup_page, 
    render_header, 
    render_upload_section, 
    render_quality_check_section, 
    render_result_section,
    render_footer
)
from src.api.openai_client import init_openai_client, transcribe_audio
from src.api.sheets_client import init_google_sheets, write_to_sheets
from src.utils.quality_check import run_quality_check_batch

def main():
    """メインアプリケーション"""
    # ページ設定
    setup_page()
    
    # ヘッダー
    render_header()
    
    # APIクライアントの初期化（バックグラウンドで実行）
    with st.spinner("必要なAPI接続を確立中..."):
        # OpenAI APIクライアントの初期化
        openai_client = init_openai_client()
        # Google Sheetsクライアントの初期化
        sheets_client = init_google_sheets()
    
    # タブの設定
    tab1, tab2 = st.tabs(["📝 文字起こし", "🔍 品質チェック"])
    
    with tab1:
        # 音声アップロードセクション
        uploaded_file, process_button = render_upload_section()
        
        # 文字起こし処理
        if process_button and uploaded_file is not None:
            with st.spinner("🎤 音声ファイルを文字起こし中..."):
                # 文字起こし処理
                transcript_text = transcribe_audio(uploaded_file, openai_client)
                
                if transcript_text:
                    # 結果表示
                    render_result_section(transcript_text)
                    
                    # Google Sheetsに保存
                    write_to_sheets(sheets_client, transcript_text, uploaded_file.name)
    
    with tab2:
        # 品質チェックセクション
        checker_str, max_rows, run_check_button, progress_bar, status_text = render_quality_check_section()
        
        # 品質チェック実行
        if run_check_button:
            with st.spinner("🔍 品質チェック処理を実行中..."):
                # セッション状態からバッチサイズを取得
                batch_size = st.session_state.get('batch_size', 10)
                
                run_quality_check_batch(
                    sheets_client, 
                    openai_client, 
                    checker_str, 
                    progress_bar, 
                    status_text, 
                    max_rows=max_rows,
                    batch_size=batch_size
                )
    
    # フッター
    render_footer() 