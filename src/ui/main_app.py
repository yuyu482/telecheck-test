"""
メインアプリケーションロジック - 話者分離機能統一版
"""

import streamlit as st
from src.ui.components import (
    setup_page, 
    render_header, 
    render_upload_section, 
    render_quality_check_section,
    render_footer,
    show_success_message,
    show_error_message,
    show_info_message
)
from src.api.openai_client import init_openai_client
from src.api.assemblyai_client import (
    init_assemblyai_client, 
    transcribe_with_speaker_diarization, 
    format_transcript_with_speakers, 
    get_teleapo_speaker_content
)
from src.api.sheets_client import init_google_sheets, write_to_sheets
from src.utils.batch_processor import run_quality_check_batch
from src.utils.speaker_detection import detect_teleapo_speaker
from src.config import config


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
    tab1, tab2 = st.tabs(["🎤 話者分離文字起こし", "🔍 品質チェック"])
    
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
            assemblyai_client = init_assemblyai_client()
            sheets_client = init_google_sheets()
            return {
                'openai': openai_client,
                'assemblyai': assemblyai_client,
                'sheets': sheets_client
            }
        except Exception as e:
            st.error(f"API初期化エラー: {str(e)}")
            return {'openai': None, 'assemblyai': None, 'sheets': None}


def _handle_transcription_tab(clients):
    """話者分離文字起こしタブの処理"""
    st.subheader("🎙️ 話者分離機能付き文字起こし")
    
    st.markdown("""
    <div class="info-box">
    この機能では、AssemblyAI APIを使用して音声ファイルを文字起こしし、
    話者を自動的に分離してテレアポ担当者の発言を特定します。
    </div>
    """, unsafe_allow_html=True)
    
    # 音声アップロードセクション
    uploaded_files = render_upload_section()
    
    # 処理ボタン
    if uploaded_files:
        process_button = st.button("🎤 話者分離文字起こし開始", type="primary", use_container_width=True)
        
        if process_button:
            _process_transcription_files(uploaded_files, clients)
    else:
        st.button("🎤 話者分離文字起こし開始", type="primary", use_container_width=True, disabled=True)
        show_info_message("音声ファイルを選択してください")


def _process_transcription_files(uploaded_files, clients):
    """アップロードされたファイルの文字起こし処理"""
    total_files = len(uploaded_files)
    processed_files = 0
    error_files = 0

    # プログレスバーの初期化
    overall_progress = st.progress(0.0)
    
    for i, uploaded_file in enumerate(uploaded_files):
        file_info = config.get_file_size_info(uploaded_file.size)
        
        with st.spinner(f"🎤 {uploaded_file.name} ({file_info['size_mb']:.1f}MB) を処理中... ({i+1}/{total_files})"):
            try:
                # 大きなファイルの場合は追加の警告
                if file_info["is_very_large"]:
                    st.info(f"🕐 大容量ファイル({file_info['size_mb']:.1f}MB)のため、処理に10分以上かかる場合があります")
                
                # 話者分離付き文字起こし
                transcript_result = transcribe_with_speaker_diarization(uploaded_file, clients['assemblyai'])
                
                if transcript_result:
                    # テレアポ担当者を自動判定
                    try:
                        teleapo_speaker = detect_teleapo_speaker(transcript_result)
                        if not teleapo_speaker:
                            teleapo_speaker = "A"  # デフォルト値
                    except Exception as speaker_error:
                        st.warning(f"⚠️ 話者判定でエラーが発生しました: {str(speaker_error)}")
                        teleapo_speaker = "A"  # デフォルト値
                    
                    # フォーマット済み文字起こし
                    try:
                        formatted_transcript = format_transcript_with_speakers(transcript_result, teleapo_speaker)
                    except Exception as format_error:
                        st.warning(f"⚠️ フォーマット処理でエラーが発生しました: {str(format_error)}")
                        # フォールバック：基本的な文字起こし結果を使用
                        formatted_transcript = transcript_result.get("full_text", "文字起こし結果を取得できませんでした。")
                    
                    # 結果表示
                    _display_transcription_result(uploaded_file, file_info, transcript_result, teleapo_speaker)
                    
                    # Google Sheetsに保存
                    try:
                        write_to_sheets(clients['sheets'], formatted_transcript, uploaded_file.name)
                        show_success_message(f"{uploaded_file.name} ({file_info['size_mb']:.1f}MB) の処理完了")
                        processed_files += 1
                    except Exception as sheets_error:
                        st.error(f"Google Sheetsへの保存に失敗しました: {str(sheets_error)}")
                        st.info("文字起こしは完了していますが、保存できませんでした。")
                        processed_files += 1  # 文字起こし自体は成功
                else:
                    show_error_message(f"{uploaded_file.name} ({file_info['size_mb']:.1f}MB) の文字起こしに失敗しました")
                    error_files += 1
                    
            except Exception as e:
                show_error_message(f"{uploaded_file.name} の処理中にエラーが発生しました: {str(e)}")
                error_files += 1
        
        # 全体進捗の更新
        overall_progress.progress((i + 1) / total_files)

    # 全体処理完了メッセージ
    _display_processing_summary(processed_files, error_files)


def _display_transcription_result(uploaded_file, file_info, transcript_result, teleapo_speaker):
    """文字起こし結果の表示"""
    st.success(f"✅ {uploaded_file.name} ({file_info['size_mb']:.1f}MB) の話者分離付き文字起こしが完了")
    st.info(f"📊 テレアポ担当者として判定: {teleapo_speaker}")
    
    # 話者別発言数の表示
    try:
        speakers = transcript_result.get("speakers", {})
        if speakers:
            st.markdown("**📊 話者別発言数:**")
            cols = st.columns(len(speakers))
            for i, (speaker, statements) in enumerate(speakers.items()):
                marker = "🎯" if speaker == teleapo_speaker else "👤"
                statement_count = len(statements) if isinstance(statements, list) else 0
                with cols[i]:
                    st.metric(f"{marker} {speaker}", f"{statement_count}発言")
        else:
            st.write("📊 話者分離情報は利用できません")
    except Exception as display_error:
        st.write(f"表示エラー: {str(display_error)}")


def _display_processing_summary(processed_files, error_files):
    """処理結果サマリーの表示"""
    if processed_files > 0:
        show_success_message(f"{processed_files}件のファイル処理が完了しました。")
    if error_files > 0:
        show_error_message(f"{error_files}件のファイル処理中にエラーが発生しました。")
    if processed_files == 0 and error_files == 0:
        show_info_message("処理対象のファイルがありませんでした。")


def _handle_quality_check_tab(clients):
    """品質チェックタブの処理"""
    # 品質チェック設定セクション
    selected_checkers = render_quality_check_section()
    
    # 処理設定
    col1, col2 = st.columns(2)
    with col1:
        max_rows = st.number_input(
            "最大処理行数", 
            min_value=1, 
            max_value=config.max_processing_rows, 
            value=50
        )
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
                    batch_size=config.default_batch_size
                )
            
            show_success_message("品質チェックが完了しました")
            
        except Exception as e:
            show_error_message(f"品質チェック中にエラーが発生しました: {str(e)}")
        finally:
            # 進捗表示をクリア
            progress_bar.empty()
            status_text.empty() 