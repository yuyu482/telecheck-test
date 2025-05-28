"""
Google Sheetsとの連携を行うモジュール
"""

import os
import json
import streamlit as st
import gspread
from gspread import Cell
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

def init_google_sheets():
    """Google Sheets クライアントを初期化"""
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        credentials_path = os.path.join(current_dir, "credentials.json")
        
        if os.path.exists(credentials_path):
            try:
                with open(credentials_path, 'r', encoding='utf-8') as f:
                    credentials_data = json.load(f)
                
                credentials = Credentials.from_service_account_file(
                    credentials_path,
                    scopes=[
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"
                    ]
                )
            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                  ❌ 認証ファイルエラー: {str(e)}
                </div>
                """, unsafe_allow_html=True)
                st.stop()

        elif hasattr(st, 'secrets') and "gcp_service_account" in st.secrets:
            credentials_info = st.secrets["gcp_service_account"]
            credentials = Credentials.from_service_account_info(
                credentials_info,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
            )
        else:
            st.markdown("""
            <div class="error-box">
              ❌ Google Sheets認証情報が見つかりません。credentials.jsonファイルを配置してください。
            </div>
            """, unsafe_allow_html=True)
            st.stop()

        try:
            gc = gspread.authorize(credentials)
            
            # スプレッドシートの存在確認
            try:
                spreadsheet = gc.open("テレアポチェックシート")
                worksheet = spreadsheet.worksheet("Difyテスト")
                return gc
            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                  ❌ スプレッドシートへのアクセスエラー: {str(e)}
                </div>
                """, unsafe_allow_html=True)
                st.stop()

        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
              ❌ Google Sheets認証エラー: {str(e)}
            </div>
            """, unsafe_allow_html=True)
            st.stop()

    except Exception as e:
        st.markdown(f"""
        <div class="error-box">
          ❌ Google Sheets初期化エラー: {str(e)}
        </div>
        """, unsafe_allow_html=True)
        st.stop()

def write_to_sheets(gc, transcript_text, filename):
    """Google Sheetsに文字起こし結果を書き込む"""
    try:
        status_msg = st.empty()
        status_msg.markdown("""
        <div class="info-box">
          🔄 Google Sheetsにデータを保存中...
        </div>
        """, unsafe_allow_html=True)
        
        # スプレッドシートを開く
        spreadsheet = gc.open("テレアポチェックシート")
        worksheet = spreadsheet.worksheet("Difyテスト")
        
        # 最終行の次の行を取得
        next_row = len(worksheet.get_all_values()) + 1
        
        # データを書き込む
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cells = [
            Cell(row=next_row, col=1, value=transcript_text),  # A列: 文字起こしテキスト
            Cell(row=next_row, col=2, value=filename),         # B列: ファイル名
            Cell(row=next_row, col=3, value=now)               # C列: 処理日時
        ]
        
        worksheet.update_cells(cells)
        
        # 完了後は表示をクリア
        status_msg.empty()
        return True
    except Exception as e:
        st.markdown(f"""
        <div class="error-box">
          ❌ スプレッドシートへの書き込みに失敗しました: {str(e)}
        </div>
        """, unsafe_allow_html=True)
        return False

def get_target_rows(gc, max_rows=50):
    """品質チェック対象の行を取得"""
    try:
        status_msg = st.empty()
        status_msg.markdown("""
        <div class="info-box">
          🔍 品質チェック対象データを取得中...
        </div>
        """, unsafe_allow_html=True)
        
        spreadsheet = gc.open("テレアポチェックシート")
        worksheet = spreadsheet.worksheet("Difyテスト")
        
        # すべての値を取得
        all_values = worksheet.get_all_values()
        
        # ヘッダー行をスキップ
        header_row = all_values[0] if all_values else []
        data_rows = all_values[1:] if len(all_values) > 1 else []
        
        # 処理対象の行を抽出
        target_rows = []
        for i, row in enumerate(data_rows, start=2):  # ヘッダー行をスキップして2行目から
            if len(row) >= 1 and row[0].strip() and (len(row) < 4 or not row[3].strip()):
                # テキストがあり、チェック結果がまだない行
                target_rows.append((i, row))
                if len(target_rows) >= max_rows:
                    break
        
        # 完了後は表示をクリア
        status_msg.empty()
        
        return header_row, target_rows
    except Exception as e:
        st.markdown(f"""
        <div class="error-box">
          ❌ スプレッドシートからのデータ取得に失敗しました: {str(e)}
        </div>
        """, unsafe_allow_html=True)
        return [], []

def update_quality_check_results(worksheet, header_map, results_batch):
    """品質チェック結果をスプレッドシートに一括更新"""
    try:
        cells_to_update = []
        
        for row_index, results in results_batch:
            try:
                # JSONから各カラムの値を取得
                results_dict = json.loads(results)
                
                # ヘッダーマップに基づいて各列にデータを配置
                for header_text, col_index in header_map.items():
                    if header_text in results_dict:
                        value = results_dict[header_text]
                        # リスト型の場合は文字列に変換
                        if isinstance(value, list):
                            value = ", ".join(value)
                        cells_to_update.append(Cell(row=row_index, col=col_index, value=value))
                
                # 処理完了フラグを追加
                cells_to_update.append(Cell(row=row_index, col=4, value="完了"))
                
            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                  ❌ 行 {row_index} の処理中にエラー: {str(e)}
                </div>
                """, unsafe_allow_html=True)
        
        if cells_to_update:
            worksheet.update_cells(cells_to_update)
            return True
        
        return False
    except Exception as e:
        st.markdown(f"""
        <div class="error-box">
          ❌ 品質チェック結果の更新に失敗しました: {str(e)}
        </div>
        """, unsafe_allow_html=True)
        return False 