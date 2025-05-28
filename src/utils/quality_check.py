"""
品質チェックのワークフローを実装するモジュール
"""

import streamlit as st
import json
import time
from src.prompts.system_prompts import SYSTEM_PROMPTS

def node_replace(input_text, checker_str, client):
    """固有名詞を置換するノード"""
    prompt = SYSTEM_PROMPTS['replace'].format(checker=checker_str)
    return client.chat_with_retry(client, prompt, input_text)

def node_speaker_separation(text_fixed, client):
    """話者分離を行うノード"""
    prompt = SYSTEM_PROMPTS['speaker']
    return client.chat_with_retry(client, prompt, text_fixed)

def node_company_check(text_fixed, checker_str, client):
    """会社名・担当者名の確認を行うノード"""
    prompt = SYSTEM_PROMPTS['company_check'].format(checker=checker_str)
    return client.chat_with_retry(client, prompt, text_fixed, expect_json=True)

def node_approach_check(text_fixed, client):
    """アプローチの確認を行うノード"""
    prompt = SYSTEM_PROMPTS['approach_check']
    return client.chat_with_retry(client, prompt, text_fixed)

def node_longcall(text_fixed, client):
    """ロングコールの確認を行うノード"""
    prompt = SYSTEM_PROMPTS['longcall']
    return client.chat_with_retry(client, prompt, text_fixed)

def node_customer_react(text_fixed, client):
    """お客様の反応を確認するノード"""
    prompt = SYSTEM_PROMPTS['customer_react']
    return client.chat_with_retry(client, prompt, text_fixed)

def node_manner(text_fixed, client):
    """マナーの確認を行うノード"""
    prompt = SYSTEM_PROMPTS['manner']
    return client.chat_with_retry(client, prompt, text_fixed)

def node_concat(*args):
    """ノードの結果を連結するノード"""
    return "\n\n".join([a for a in args if a])

def node_to_json(concatenated, client):
    """結果をJSONに変換するノード"""
    prompt = SYSTEM_PROMPTS['to_json']
    return client.chat_with_retry(client, prompt, concatenated, expect_json=True)

def run_workflow(raw_transcript, checker_str, client):
    """品質チェックのワークフローを実行"""
    try:
        workflow_progress = st.progress(0)
        status_text = st.empty()
        
        # 1. 固有名詞の置換
        status_text.markdown("**ステップ 1/6**: 固有名詞の置換")
        text_fixed = node_replace(raw_transcript, checker_str, client)
        if not text_fixed:
            return None
        workflow_progress.progress(1/6)

        # 2. 話者分離
        status_text.markdown("**ステップ 2/6**: 話者分離")
        text_separated = node_speaker_separation(text_fixed, client)
        if not text_separated:
            return None
        workflow_progress.progress(2/6)

        # 3. 各種チェック項目の実行
        status_text.markdown("**ステップ 3/6**: 会社名・担当者名の確認")
        company_check = node_company_check(text_separated, checker_str, client)
        workflow_progress.progress(3/6)
        
        status_text.markdown("**ステップ 4/6**: アプローチ・顧客反応・マナーチェック")
        approach_check = node_approach_check(text_separated, client)
        longcall = node_longcall(text_separated, client)
        customer_react = node_customer_react(text_separated, client)
        manner = node_manner(text_separated, client)
        workflow_progress.progress(4/6)

        # 4. 結果の連結
        status_text.markdown("**ステップ 5/6**: 結果の連結")
        concatenated = node_concat(company_check, approach_check, longcall, customer_react, manner)
        workflow_progress.progress(5/6)

        # 5. JSONに変換
        status_text.markdown("**ステップ 6/6**: JSON形式に変換")
        result_json = node_to_json(concatenated, client)
        workflow_progress.progress(1.0)
        
        # 完了表示をクリア
        status_text.empty()
        workflow_progress.empty()
        
        return result_json

    except Exception as e:
        st.markdown(f"""
        <div class="error-box">
          ❌ ワークフロー実行エラー: {str(e)}
        </div>
        """, unsafe_allow_html=True)
        return None

def run_quality_check_batch(gc, client, checker_str, progress_bar, status_text, max_rows=50, batch_size=10):
    """バッチ処理で品質チェックを実行"""
    from src.api.sheets_client import get_target_rows, update_quality_check_results
    
    try:
        # 処理対象の行を取得
        header_row, target_rows = get_target_rows(gc, max_rows)
        
        if not target_rows:
            st.markdown('<div class="info-box">処理対象のデータがありません</div>', unsafe_allow_html=True)
            return
        
        # ヘッダーマップを作成
        header_map = {}
        for i, header in enumerate(header_row, start=1):
            if header.strip():
                header_map[header.strip()] = i
        
        # 進捗バーの初期化
        progress_bar.progress(0)
        status_text.markdown(f"<p style='text-align: center; font-weight: 500;'>0/{len(target_rows)} 処理中...</p>", unsafe_allow_html=True)
        
        # メトリクス表示用
        metrics_cols = st.columns(2)
        with metrics_cols[0]:
            processed_metric = st.empty()
            processed_metric.markdown(f"""
            <div class="metric-card">
              <h3>✅ 処理済み</h3>
              <p>0/{len(target_rows)}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with metrics_cols[1]:
            success_metric = st.empty()
            success_metric.markdown(f"""
            <div class="metric-card">
              <h3>🎯 成功率</h3>
              <p>0%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # バッチ単位で処理
        results_batch = []
        total_processed = 0
        total_success = 0
        total_errors = 0
        
        for i, (row_index, row) in enumerate(target_rows):
            try:
                # 1列目のテキストを取得
                raw_transcript = row[0] if row else ""
                
                if not raw_transcript:
                    continue
                
                # ファイル名の取得（利用可能な場合）
                filename = row[1] if len(row) > 1 else f"行 {row_index}"
                
                # 現在処理中のファイル名を表示
                current_file = st.empty()
                current_file.markdown(f"""
                <div style="text-align: center; padding: 0.5rem; background-color: rgba(40,40,40,0.7); border-radius: 5px; margin: 1rem 0;">
                  <p style="margin: 0; font-weight: 500;">🔍 現在処理中: {filename}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 品質チェックワークフローを実行
                result_json = run_workflow(raw_transcript, checker_str, client)
                
                if result_json:
                    results_batch.append((row_index, result_json))
                    total_success += 1
                else:
                    total_errors += 1
                
                # 現在処理中の表示をクリア
                current_file.empty()
                
                # バッチサイズに達したらスプレッドシートを更新
                if len(results_batch) >= batch_size or i == len(target_rows) - 1:
                    if results_batch:
                        batch_status = st.empty()
                        batch_status.markdown(f"""
                        <div class="info-box">
                          ⏳ Googleスプレッドシートを更新中...
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # スプレッドシートを開く
                        spreadsheet = gc.open("テレアポチェックシート")
                        worksheet = spreadsheet.worksheet("Difyテスト")
                        
                        # 結果をスプレッドシートに書き込み
                        update_success = update_quality_check_results(worksheet, header_map, results_batch)
                        batch_status.empty()
                        
                        total_processed += len(results_batch)
                        results_batch = []
                
                # 進捗とメトリクスを更新
                progress = (i + 1) / len(target_rows)
                progress_bar.progress(progress)
                status_text.markdown(f"<p style='text-align: center; font-weight: 500;'>{i+1}/{len(target_rows)} 処理中...</p>", unsafe_allow_html=True)
                
                processed_metric.markdown(f"""
                <div class="metric-card">
                  <h3>✅ 処理済み</h3>
                  <p>{i+1}/{len(target_rows)}</p>
                </div>
                """, unsafe_allow_html=True)
                
                success_rate = int((total_success / (i+1)) * 100)
                success_metric.markdown(f"""
                <div class="metric-card">
                  <h3>🎯 成功率</h3>
                  <p>{success_rate}%</p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                  ❌ 行 {row_index} の処理中にエラー: {str(e)}
                </div>
                """, unsafe_allow_html=True)
                total_errors += 1
        
        # 完了メッセージ
        if total_processed > 0:
            st.markdown(f"""
            <div class="success-box" style="text-align: center; padding: 1rem;">
              ✅ 処理完了: {total_processed}/{len(target_rows)} 件の品質チェックが完了しました
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box" style="text-align: center; padding: 1rem;">
              ⚠️ 処理完了しましたが、更新されたデータはありませんでした
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.markdown(f"""
        <div class="error-box">
          ❌ バッチ処理エラー: {str(e)}
        </div>
        """, unsafe_allow_html=True) 