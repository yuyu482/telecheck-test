"""
Streamlit UIコンポーネント
"""

import streamlit as st
from src.ui.styles import ALL_STYLES
from src.config import config


def setup_page():
    """ページの基本設定とスタイルを適用"""
    st.set_page_config(
        page_title="テレアポ文字起こし・品質チェックシステム",
        page_icon="📞",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 統合されたスタイルを適用
    st.markdown(ALL_STYLES, unsafe_allow_html=True)


def render_header():
    """メインヘッダーを表示"""
    st.markdown("""
    <div class="main-header">
      📞 テレアポ文字起こし・品質チェックシステム
    </div>
    """, unsafe_allow_html=True)


def render_upload_section():
    """ファイルアップロードセクションを表示"""
    st.markdown('<div class="section-container upload-section">', unsafe_allow_html=True)
    st.markdown("### 📁 音声ファイルアップロード")
    
    uploaded_files = st.file_uploader(
        f"mp3ファイルを選択してください（最大{config.max_file_size_mb}MB）",
        type=['mp3'],
        help="テレアポの録音データをアップロードしてください。大きなファイルの場合、アップロードに時間がかかることがあります。",
        accept_multiple_files=True
    )
    
    # ファイルサイズ制限についての詳細情報を表示
    st.markdown(f"""
    <div class="info-box">
    📋 <strong>アップロード制限について</strong><br>
    • 1ファイルあたり最大{config.max_file_size_mb}MB（{config.max_file_size_mb/1024:.1f}GB）まで対応<br>
    • 複数ファイルの同時アップロード可能（推奨: {config.max_concurrent_files}ファイル以下）<br>
    • 推奨サイズ: {config.recommended_file_size_mb}MB以下（安定した処理のため）<br>
    • {config.recommended_file_size_mb}MB以上のファイルでは処理に時間がかかる場合があります
    </div>
    """, unsafe_allow_html=True)
    
    # アップロードされたファイルの情報表示
    if uploaded_files:
        _display_uploaded_files_info(uploaded_files)
    
    st.markdown('</div>', unsafe_allow_html=True)
    return uploaded_files


def _display_uploaded_files_info(uploaded_files):
    """アップロードされたファイルの情報を表示"""
    total_size_mb = sum(file.size for file in uploaded_files) / (1024 * 1024)
    
    st.markdown("#### 📊 アップロードファイル情報")
    
    # 全体サマリー
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("ファイル数", f"{len(uploaded_files)}件")
    with col2:
        st.metric("合計サイズ", f"{total_size_mb:.1f}MB")
    with col3:
        status = "⚠️ 大容量" if total_size_mb > config.recommended_file_size_mb else "✅ 正常"
        st.metric("ステータス", status)
    
    # ファイル別詳細（多すぎる場合は省略）
    if len(uploaded_files) <= 5:
        for i, file in enumerate(uploaded_files):
            file_info = config.get_file_size_info(file.size)
            icon = "⚠️" if file_info["is_large"] else "📁"
            st.write(f"{icon} {file.name}: {file_info['size_mb']:.1f}MB")
    else:
        st.write(f"📁 {len(uploaded_files)}ファイルがアップロード済み（詳細は省略）")
    
    # 警告表示
    if total_size_mb > config.recommended_file_size_mb:
        st.warning(f"⚠️ 合計ファイルサイズが{config.recommended_file_size_mb}MBを超えています。処理に時間がかかる可能性があります。")


def render_quality_check_section():
    """品質チェックセクションを表示"""
    st.markdown('<div class="section-container quality-check-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 品質チェック設定")
    
    # 担当者設定（カンマ区切りのテキスト入力）
    st.markdown("#### 👥 担当者設定")
    
    # Difyで定義されている担当者リスト（参考表示用）
    available_checkers = [
        "野田", "永廣", "猪俣", "渡辺", "工藤", "前川", "田本", "立川", "濱田"
    ]
    
    # 参考として表示
    st.caption(f"参考：登録済み担当者 - {', '.join(available_checkers)}")
    
    # テキスト入力（カンマ区切り）
    checker_input = st.text_input(
        "品質チェックを行う担当者名をカンマ区切りで入力してください",
        value="",
        help="例：田中, 佐藤, 鈴木（カンマ区切りで複数の担当者を入力できます）"
    )
    
    # カンマ区切りの入力を処理
    selected_checkers = []
    if checker_input:
        # カンマで分割して空白を削除
        selected_checkers = [name.strip() for name in checker_input.split(',') if name.strip()]
    
    # 担当者プレビュー表示
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if selected_checkers:
            st.markdown("**✅ 入力された担当者:**")
            # 2列で表示（多数の場合の見やすさを考慮）
            checker_cols = st.columns(3)
            for i, checker in enumerate(selected_checkers):
                with checker_cols[i % 3]:
                    st.markdown(f"　• {checker}")
        else:
            st.info("👆 上記に担当者名をカンマ区切りで入力してください")
    
    with col2:
        if selected_checkers:
            st.metric("入力担当者数", f"{len(selected_checkers)}名")
            if len(selected_checkers) > 5:
                st.warning("担当者数が多いです")
        else:
            st.metric("入力担当者数", "0名")
    
    st.markdown('</div>', unsafe_allow_html=True)
    return selected_checkers


def render_result_section(transcript_text=None):
    """結果表示セクションを表示"""
    st.markdown('<div class="section-container result-section">', unsafe_allow_html=True)
    st.markdown("### 📋 処理結果")
    
    if transcript_text:
        st.text_area("文字起こし結果", transcript_text, height=200, key="transcript_result")
        
        # コピーボタン
        st.markdown(f"""
        <button class="copy-btn" onclick="navigator.clipboard.writeText(`{transcript_text}`)">
          📋 テキストをコピー
        </button>
        """, unsafe_allow_html=True)
    else:
        st.info("音声ファイルをアップロードして文字起こしを開始してください")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_footer():
    """フッターを表示"""
    st.markdown("""
    <div class="footer">
      <p>© 2024 テレアポ品質チェックシステム - Version 2.0.0</p>
    </div>
    """, unsafe_allow_html=True)


def show_success_message(message):
    """成功メッセージを表示"""
    st.markdown(f"""
    <div class="success-box">
      ✅ {message}
    </div>
    """, unsafe_allow_html=True)


def show_error_message(message):
    """エラーメッセージを表示"""
    st.markdown(f"""
    <div class="error-box">
      ❌ {message}
    </div>
    """, unsafe_allow_html=True)


def show_warning_message(message):
    """警告メッセージを表示"""
    st.markdown(f"""
    <div class="warning-box">
      ⚠️ {message}
    </div>
    """, unsafe_allow_html=True)


def show_info_message(message):
    """情報メッセージを表示"""
    st.markdown(f"""
    <div class="info-box">
    ℹ️ {message}
    </div>
    """, unsafe_allow_html=True) 