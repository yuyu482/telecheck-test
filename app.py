"""
テレアポ文字起こし・品質チェックシステム
"""

import os
import sys
import traceback
import streamlit as st
from dotenv import load_dotenv
from src.ui.main_app import main

# アプリケーションのバージョン
VERSION = "1.2.0"

# アプリケーションのメイン処理
def run_app():
# 環境変数の読み込み
load_dotenv()

    try:
        # メインアプリケーションの実行
        main()
    except Exception as e:
        # エラーハンドリング
        st.markdown(f"""
        <div class="error-box" style="margin-top: 2rem;">
          <h3>⚠️ エラーが発生しました</h3>
          <p>{str(e)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 詳細なエラー情報を表示（開発者向け）
        with st.expander("詳細なエラー情報（開発者向け）"):
            st.code(traceback.format_exc())
            
        # ヘルプ情報
        st.markdown("""
        <div class="info-box" style="margin-top: 1rem;">
          <h3>🛠️ トラブルシューティング</h3>
          <ul>
            <li>API接続エラーの場合: <code>.env</code> ファイルのAPIキーを確認してください</li>
            <li>Google Sheetsエラーの場合: <code>credentials.json</code> が正しく設定されているか確認してください</li>
            <li>アップロードエラーの場合: ファイルサイズと形式を確認してください（mp3形式、25MB以下）</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    run_app()
