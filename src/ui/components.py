"""
Streamlit UIコンポーネント - 簡潔バージョン
"""

import streamlit as st
from src.ui.styles import ALL_STYLES


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
    
    uploaded_file = st.file_uploader(
        "mp3ファイルを選択してください（最大25MB）",
        type=['mp3'],
        help="テレアポの録音データをアップロードしてください"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    return uploaded_file


def render_quality_check_section():
    """品質チェックセクションを表示"""
    st.markdown('<div class="section-container quality-check-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 品質チェック設定")
    
    # 担当者選択
    checker_options = ["担当者A", "担当者B", "担当者C", "担当者D", "その他"]
    selected_checkers = []
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        for i, option in enumerate(checker_options[:2]):
            if st.checkbox(option, key=f"checker_{i}"):
                selected_checkers.append(option)
    
    with col2:
        for i, option in enumerate(checker_options[2:4], start=2):
            if st.checkbox(option, key=f"checker_{i}"):
                selected_checkers.append(option)
    
    with col3:
        if st.checkbox(checker_options[4], key="checker_4"):
            other_checker = st.text_input("担当者名を入力", key="other_checker_name")
            if other_checker:
                selected_checkers.append(other_checker)
    
    # バッチサイズ設定
    batch_size = st.slider("バッチサイズ", min_value=1, max_value=20, value=10, 
                          help="一度に処理する件数")
    
    st.markdown('</div>', unsafe_allow_html=True)
    return selected_checkers, batch_size


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
      <p>© 2024 テレアポ品質チェックシステム - Version 1.2.0</p>
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