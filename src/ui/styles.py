"""
Streamlit アプリケーションのCSSスタイル定義
"""

# ダークテーマ対応のメインCSS
MAIN_CSS = """
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

/* 特定セクションのスタイル */
.upload-section {
    background: linear-gradient(to bottom, rgba(35,35,35,0.7), rgba(30,30,30,0.7));
    border-left: 5px solid #60b4ff;
}

.quality-check-section {
    background: linear-gradient(to bottom, rgba(35,35,35,0.7), rgba(30,30,30,0.7));
    border-left: 5px solid #4cd964;
}

.result-section {
    background: linear-gradient(to bottom, rgba(35,35,35,0.7), rgba(30,30,30,0.7));
    border-left: 5px solid #bf5af2;
}
</style>
"""

# 通知ボックス用CSS
NOTIFICATION_CSS = """
<style>
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
</style>
"""

# インタラクティブ要素用CSS
INTERACTIVE_CSS = """
<style>
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
</style>
"""

# メトリクスカード用CSS
METRICS_CSS = """
<style>
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

.footer {
    text-align: center;
    color: #aaa;
    font-size: 0.9rem;
    margin-top: 3rem;
    padding: 1rem;
    border-top: 1px solid rgba(70,70,70,0.5);
}
</style>
"""

# 全てのスタイルを統合
ALL_STYLES = MAIN_CSS + NOTIFICATION_CSS + INTERACTIVE_CSS + METRICS_CSS 