"""
Streamlit UIコンポーネント
"""

import streamlit as st

def setup_page():
    """ページの基本設定を行う"""
    st.set_page_config(
        page_title="テレアポ文字起こし・品質チェックシステム",
        page_icon="📞",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # カスタムCSS
    st.markdown("""
    <style>
    /* 全体のフォントとカラーの設定 - ダークテーマ対応 */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* ヘッダー */
    .main-header {
        text-align: center;
        color: #60b4ff;
        font-weight: 600;
        margin-bottom: 2rem;
        padding: 1rem;
        font-size: 2.5rem;
        background: linear-gradient(90deg, rgba(25,25,25,0.4), rgba(35,35,35,0.7), rgba(25,25,25,0.4));
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* セクション共通スタイル */
    .section-container {
        background-color: rgba(35,35,35,0.7);
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: 1px solid rgba(70,70,70,0.5);
        transition: all 0.3s ease;
    }
    .section-container:hover {
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }
    
    /* アップロードセクション */
    .upload-section {
        background: linear-gradient(to bottom, rgba(35,35,35,0.7), rgba(30,30,30,0.7));
        border-left: 5px solid #60b4ff;
    }
    
    /* 品質チェックセクション */
    .quality-check-section {
        background: linear-gradient(to bottom, rgba(35,35,35,0.7), rgba(30,30,30,0.7));
        border-left: 5px solid #4cd964;
    }
    
    /* 結果セクション */
    .result-section {
        background: linear-gradient(to bottom, rgba(35,35,35,0.7), rgba(30,30,30,0.7));
        border-left: 5px solid #bf5af2;
    }
    
    /* 通知ボックス */
    .success-box {
        background-color: rgba(40,167,69,0.2);
        border-left: 5px solid #28a745;
        color: #bfffca;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .error-box {
        background-color: rgba(220,53,69,0.2);
        border-left: 5px solid #dc3545;
        color: #ffbdc2;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .warning-box {
        background-color: rgba(255,193,7,0.2);
        border-left: 5px solid #ffc107;
        color: #ffe7a0;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .info-box {
        background-color: rgba(23,162,184,0.2);
        border-left: 5px solid #17a2b8;
        color: #a8e5ee;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* ボタンスタイル */
    .stButton > button {
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* テキストエリア */
    .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #444 !important;
        background-color: rgba(30,30,30,0.7) !important;
        color: #ddd !important;
    }
    
    /* プログレスバー */
    .stProgress > div > div {
        background-color: #60b4ff !important;
    }
    
    /* フッター */
    .footer {
        text-align: center;
        color: #aaa;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid rgba(70,70,70,0.5);
    }
    
    /* タブのスタイル */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(40,40,40,0.8) !important;
        border-bottom: 3px solid #60b4ff !important;
    }
    
    /* カードスタイル */
    .metric-card {
        background-color: rgba(40,40,40,0.7);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-card h3 {
        color: #aaa;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .metric-card p {
        color: #eee;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    /* コピーボタン */
    .copy-btn {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: rgba(50,50,50,0.8);
        color: #ddd;
        border-radius: 4px;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        text-decoration: none;
        margin-top: 0.5rem;
        border: 1px solid #444;
        transition: all 0.2s ease;
    }
    .copy-btn:hover {
        background-color: rgba(70,70,70,0.8);
        color: #fff;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """ヘッダーセクションをレンダリング"""
    st.markdown("<h1 class='main-header'>📞 テレアポ文字起こし・品質チェックシステム</h1>", unsafe_allow_html=True)
    
    # システム説明
    with st.expander("📋 システムについて", expanded=False):
        st.markdown("""
        <div style="padding: 1rem; border-radius: 8px; background-color: #f8f9fa;">
        <h3 style="color: #3498db; font-size: 1.2rem;">🌟 このシステムでできること</h3>
        <ul>
          <li>MP3形式の音声ファイルを自動で文字起こし</li>
          <li>AIによる30項目の品質チェック</li>
          <li>結果をGoogle Sheetsに自動保存</li>
          <li>テレアポの品質チェック業務を効率化</li>
        </ul>
        
        <h3 style="color: #3498db; font-size: 1.2rem;">📊 品質チェック項目</h3>
        <ul>
          <li>社名・担当者名の確認（3項目）</li>
          <li>アプローチ手法のチェック（9項目）</li>
          <li>ロングコール判定（1項目）</li>
          <li>顧客反応のチェック（8項目）</li>
          <li>マナーチェック（9項目）</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

def render_upload_section():
    """アップロードセクションをレンダリング"""
    st.markdown("<div class='section-container upload-section'>", unsafe_allow_html=True)
    st.subheader("📤 音声ファイルのアップロード")
    
    uploaded_file = st.file_uploader(
        "mp3形式の音声ファイルをアップロードしてください（最大25MB）",
        type=["mp3"]
    )

    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        
        if file_size_mb > 25:
            st.markdown(f"<div class='error-box'>❌ ファイルサイズが大きすぎます（{file_size_mb:.2f}MB）。25MB以下のファイルを選択してください。</div>", unsafe_allow_html=True)
            uploaded_file = None
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                  <h3>📁 ファイル名</h3>
                  <p>{uploaded_file.name}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                  <h3>📊 ファイルサイズ</h3>
                  <p>{file_size_mb:.2f} MB</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                  <h3>📝 形式</h3>
                  <p>MP3</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="success-box">✅ ファイルが正常にアップロードされました</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_button = st.button("🎤 文字起こし開始", type="primary", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return uploaded_file, process_button

def render_quality_check_section():
    """品質チェックセクションをレンダリング"""
    st.markdown("<div class='section-container quality-check-section'>", unsafe_allow_html=True)
    st.subheader("🔍 一括品質チェック")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 担当者名の入力フィールド
        st.markdown("<p style='font-weight: 500; margin-bottom: 0.5rem;'>チェック対象の担当者名（カンマ区切りで複数入力可能）：</p>", unsafe_allow_html=True)
        
        # デフォルト値を設定
        default_checkers = "渡辺, 野田, 井上, 永広, 浅井, 清水, 田中, 佐藤, 山田, 伊藤"
        
        # セッション状態から担当者名を取得（存在する場合）
        if 'checker_names' in st.session_state:
            default_checkers = st.session_state.checker_names
        
        # テキスト入力フィールド
        checker_str = st.text_area(
            "担当者の名字をカンマ(,)区切りで入力してください",
            value=default_checkers,
            height=100,
            help="例: 山田, 鈴木, 佐藤"
        )
        
        # セッション状態に保存
        st.session_state.checker_names = checker_str
        
        # 入力確認
        if checker_str:
            checker_list = [name.strip() for name in checker_str.split(",") if name.strip()]
            if checker_list:
                st.markdown(f"""
                <div class="info-box">
                  ✓ {len(checker_list)}名の担当者がチェック対象に設定されました
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # 最大行数の設定
        st.markdown("<p style='font-weight: 500; margin-bottom: 0.5rem;'>処理設定：</p>", unsafe_allow_html=True)
        max_rows = st.number_input("最大処理件数", min_value=1, max_value=100, value=10)
        batch_size = st.select_slider("バッチサイズ", options=[1, 5, 10, 20, 50], value=10, 
                                     help="一度に処理する行数。大きいほど早く処理できますが、エラー時の影響も大きくなります。")
        
        # セッション状態に保存
        st.session_state.batch_size = batch_size
    
    # 実行ボタン
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        run_check_button = st.button("🔍 品質チェック実行", type="primary", use_container_width=True)
    
    # 進捗バーとステータステキスト
    st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
    progress_bar = st.progress(0)
    status_text = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return checker_str, max_rows, run_check_button, progress_bar, status_text

def render_result_section(transcript_text=None):
    """結果表示セクションをレンダリング"""
    if transcript_text:
        st.markdown("<div class='section-container result-section'>", unsafe_allow_html=True)
        st.subheader("📝 文字起こし結果")
        
        # 結果サマリー
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
              <h3>🔤 テキスト文字数</h3>
              <p>{len(transcript_text)} 文字</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
              <h3>🕒 ステータス</h3>
              <p>完了</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 折りたたみ可能なテキストエリアで結果を表示
        with st.expander("文字起こしテキスト（クリックして表示）", expanded=True):
            st.text_area(
                "文字起こし結果",
                value=transcript_text,
                height=400,
                key="transcript_result"
            )
            
            # コピーボタン
            st.markdown("""
            <a class="copy-btn" href="#" onclick="
                navigator.clipboard.writeText(document.querySelector('.stTextArea textarea').value);
                this.innerHTML = '✓ コピーしました';
                setTimeout(() => { this.innerHTML = '📋 テキストをクリップボードにコピー'; }, 2000);
                return false;
            ">📋 テキストをクリップボードにコピー</a>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 成功メッセージ
        st.markdown('<div class="success-box">✅ 文字起こしが完了し、Google Sheetsに保存されました！</div>', unsafe_allow_html=True)

def render_footer():
    """フッターをレンダリング"""
    st.markdown("<div class='footer'>", unsafe_allow_html=True)
    st.markdown(
        """
        © 2024 SFIDA X | Powered by OpenAI Whisper & GPT-4o
        """, 
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True) 