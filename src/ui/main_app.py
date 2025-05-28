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
    render_footer,
    show_success_message,
    show_error_message
)
from src.api.openai_client import init_openai_client, transcribe_audio
from src.api.sheets_client import init_google_sheets, write_to_sheets
from src.utils.batch_processor import run_quality_check_batch


def main():
    """メインアプリケーション"""
    # ページ設定とスタイル適用
    setup_page()
    
    # ヘッダー
    render_header()
    
    # APIクライアントの初期化
    clients = _initialize_api_clients()
    if not all(clients.values()):
        show_error_message("API接続の初期化に失敗しました。設定を確認してください。")
        return
    
    # タブの設定
    tab1, tab2 = st.tabs(["📝 文字起こし", "🔍 品質チェック"])
    
    with tab1:
        _handle_transcription_tab(clients)
    
    with tab2:
        _handle_quality_check_tab(clients)
    
    # フッター
    render_footer()


def _initialize_api_clients():
    """APIクライアントを初期化"""
    with st.spinner("必要なAPI接続を確立中..."):
        try:
            openai_client = init_openai_client()
            sheets_client = init_google_sheets()
            return {
                'openai': openai_client,
                'sheets': sheets_client
            }
        except Exception as e:
            st.error(f"API初期化エラー: {str(e)}")
            return {'openai': None, 'sheets': None}


def _handle_transcription_tab(clients):
    """文字起こしタブの処理"""
    # 音声アップロードセクション
    uploaded_file = render_upload_section()
    
    # 処理ボタン
    process_button = st.button("🎤 文字起こし開始", type="primary", use_container_width=True)
    
    # 文字起こし処理
    if process_button and uploaded_file is not None:
        with st.spinner("🎤 音声ファイルを文字起こし中..."):
            try:
                # 文字起こし処理
                transcript_text = transcribe_audio(uploaded_file, clients['openai'])
                
                if transcript_text:
                    # 結果表示
                    render_result_section(transcript_text)
                    
                    # Google Sheetsに保存
                    write_to_sheets(clients['sheets'], transcript_text, uploaded_file.name)
                    show_success_message("文字起こしが完了し、Google Sheetsに保存されました")
                else:
                    show_error_message("文字起こしに失敗しました")
                    
            except Exception as e:
                show_error_message(f"処理中にエラーが発生しました: {str(e)}")
    
    elif process_button and uploaded_file is None:
        show_error_message("音声ファイルを選択してください")


def _handle_quality_check_tab(clients):
    """品質チェックタブの処理"""
    # 品質チェック設定セクション
    selected_checkers, batch_size = render_quality_check_section()
    
    # 処理設定
    col1, col2 = st.columns(2)
    with col1:
        max_rows = st.number_input("最大処理行数", min_value=1, max_value=1000, value=50)
    with col2:
        st.metric("選択された担当者", len(selected_checkers))
    
    # 実行ボタン
    run_check_button = st.button("🔍 品質チェック実行", type="primary", use_container_width=True)
    
    # 品質チェック実行
    if run_check_button:
        if not selected_checkers:
            show_error_message("担当者を選択してください")
            return
        
        # 進捗表示エリア
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            checker_str = ", ".join(selected_checkers)
            
            with st.spinner("🔍 品質チェック処理を実行中..."):
                run_quality_check_batch(
                    clients['sheets'], 
                    clients['openai'], 
                    checker_str, 
                    progress_bar, 
                    status_text, 
                    max_rows=max_rows,
                    batch_size=batch_size
                )
            
            show_success_message("品質チェックが完了しました")
            
        except Exception as e:
            show_error_message(f"品質チェック中にエラーが発生しました: {str(e)}")
        finally:
            # 進捗表示をクリア
            progress_bar.empty()
            status_text.empty() 