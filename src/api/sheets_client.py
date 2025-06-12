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
                # A列にテキストがあり、D列（テレアポ担当者名）がまだ空の行
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
    """品質チェック結果をスプレッドシートに一括更新（Dify互換版）"""
    try:
        cells_to_update = []
        
        # 実際のスプレッドシートの列名に合わせたヘッダーマップを定義
        actual_header_map = {
            # A列「会話記録」、B列「ファイル名」、C列「処理日時」は品質チェック結果では更新しない
            "テレアポ担当者名": 4,  # D列
            "報告まとめ": 5,  # E列
            "社名や担当者名を名乗らない": 6,  # F列
            "アプローチで販売店名、ソフト名の先出し": 7,  # G列
            "同業他社の悪口等": 8,  # H列
            "運転中や電車内でも無理やり続ける": 9,  # I列
            "2回断られても食い下がる": 10,  # J列
            "暴言・悪口・脅迫・逆上": 11,  # K列
            "情報漏洩": 12,  # L列
            "共犯（教唆・幇助）": 13,  # M列
            "通話対応（無言電話／ガチャ切り）": 14,  # N列
            "呼び方": 15,  # O列
            "ロングコール": 16,  # P列
            "ガチャ切りされた△": 17,  # Q列
            "当社の電話お断り": 18,  # R列
            "しつこい・何度も電話がある": 19,  # S列
            "お客様専用電話番号と言われる": 20,  # T列
            "口調を注意された": 21,  # U列
            "怒らせた": 22,  # V列
            "暴言を受けた": 23,  # W列
            "通報する": 24,  # X列
            "営業お断り": 25,  # Y列
            "事務員に対して代表者のことを「社長」「オーナー」「代表」": 26,  # Z列
            "一人称が「僕」「自分」「俺」": 27,  # AA列
            "「弊社」のことを「うち」「僕ら」と言う": 28,  # AB列
            "謝罪が「すみません」「ごめんなさい」": 29,  # AC列
            "口調や態度が失礼": 30,  # AD列
            "会話が成り立っていない": 31,  # AE列
            "残債の「下取り」「買い取り」トーク": 32,  # AF列
            "嘘・真偽不明": 33,  # AG列
            "その他問題": 34,  # AH列
        }
        
        for row_index, results in results_batch:
            try:
                # JSONパースを試行
                if isinstance(results, str):
                    # 空文字列チェック
                    if not results.strip():
                        st.warning(f"行 {row_index}: 空の結果が返されました")
                        continue
                    
                    # JSON形式かどうかを確認
                    results = results.strip()
                    if results.startswith('{') and results.endswith('}'):
                        try:
                            results_dict = json.loads(results)
                        except json.JSONDecodeError as e:
                            st.warning(f"行 {row_index}: JSON解析エラー - {str(e)}")
                            # JSONでない場合は、報告まとめ列にテキストとして保存
                            cells_to_update.append(Cell(row=row_index, col=5, value=results))
                            continue
                    else:
                        # JSON形式でない場合は、報告まとめ列にテキストとして保存
                        st.info(f"行 {row_index}: テキスト形式の結果を報告まとめ列に保存")
                        cells_to_update.append(Cell(row=row_index, col=5, value=results))
                        continue
                else:
                    results_dict = results
                
                # 実際のヘッダーマップに基づいて各列にデータを配置
                for header_text, col_index in actual_header_map.items():
                    if header_text in results_dict:
                        value = results_dict[header_text]
                        # リスト型の場合は文字列に変換
                        if isinstance(value, list):
                            value = ", ".join(str(item) for item in value)
                        cells_to_update.append(Cell(row=row_index, col=col_index, value=str(value)))
                    else:
                        # 該当するデータがない場合は空文字列
                        cells_to_update.append(Cell(row=row_index, col=col_index, value=""))
                
            except Exception as e:
                st.error(f"行 {row_index} の結果処理中にエラー: {str(e)}")
                # エラーの場合も報告まとめ列にエラー情報を記録
                cells_to_update.append(Cell(row=row_index, col=5, value=f"エラー: {str(e)}"))
        
        if cells_to_update:
            try:
                # バッチサイズを制限して更新（Google Sheetsの制限対応）
                batch_size = 100
                for i in range(0, len(cells_to_update), batch_size):
                    batch = cells_to_update[i:i + batch_size]
                    worksheet.update_cells(batch)
                    time.sleep(1)  # API制限対応
                
                st.success(f"✅ {len(results_batch)}件の結果をスプレッドシートに更新しました")
                return True
            except Exception as update_error:
                st.error(f"スプレッドシート更新エラー: {str(update_error)}")
                return False
        else:
            st.warning("更新するデータがありません")
            return False
        
    except Exception as e:
        st.error(f"品質チェック結果の更新に失敗しました: {str(e)}")
        return False 