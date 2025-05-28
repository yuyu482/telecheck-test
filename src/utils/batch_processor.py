"""
バッチ処理用のワークフロー管理モジュール
"""

import streamlit as st
import time
from src.utils.quality_check import run_workflow
from src.api.sheets_client import get_target_rows, update_quality_check_results


def run_quality_check_batch(gc, client, checker_str, progress_bar, status_text, max_rows=50, batch_size=10):
    """バッチ処理で品質チェックを実行"""
    try:
        # 処理対象の行を取得
        header_row, target_rows = get_target_rows(gc, max_rows)
        
        if not target_rows:
            st.markdown('<div class="info-box">処理対象のデータがありません</div>', unsafe_allow_html=True)
            return
        
        # ヘッダーマップを作成
        header_map = _create_header_map(header_row)
        
        # 進捗表示の初期化
        _initialize_progress_display(progress_bar, status_text, len(target_rows))
        
        # メトリクス表示
        metrics_containers = _setup_metrics_display(len(target_rows))
        
        # バッチ処理実行
        _process_batch(
            target_rows, checker_str, client, gc, 
            batch_size, progress_bar, status_text, metrics_containers
        )
        
    except Exception as e:
        st.error(f"バッチ処理エラー: {str(e)}")


def _create_header_map(header_row):
    """ヘッダーマップを作成"""
    header_map = {}
    for i, header in enumerate(header_row, start=1):
        if header.strip():
            header_map[header.strip()] = i
    return header_map


def _initialize_progress_display(progress_bar, status_text, total_rows):
    """進捗表示を初期化"""
    progress_bar.progress(0)
    status_text.markdown(
        f"<p style='text-align: center; font-weight: 500;'>0/{total_rows} 処理中...</p>", 
        unsafe_allow_html=True
    )


def _setup_metrics_display(total_rows):
    """メトリクス表示エリアを設定"""
    metrics_cols = st.columns(2)
    
    with metrics_cols[0]:
        processed_metric = st.empty()
        processed_metric.markdown(f"""
        <div class="metric-card">
          <h3>✅ 処理済み</h3>
          <p>0/{total_rows}</p>
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
    
    return {
        'processed': processed_metric,
        'success': success_metric
    }


def _process_batch(target_rows, checker_str, client, gc, batch_size, 
                  progress_bar, status_text, metrics_containers):
    """実際のバッチ処理を実行"""
    results_batch = []
    total_processed = 0
    total_success = 0
    
    for i, (row_index, row) in enumerate(target_rows):
        try:
            # テキストとファイル名を取得
            raw_transcript = row[0] if row else ""
            if not raw_transcript:
                continue
                
            filename = row[1] if len(row) > 1 else f"行 {row_index}"
            
            # 現在処理中のファイル表示
            current_file = _show_current_processing(filename)
            
            # 品質チェックワークフロー実行
            result_json = run_workflow(raw_transcript, checker_str, client)
            
            if result_json:
                results_batch.append((row_index, result_json))
                total_success += 1
            
            # 現在処理中の表示をクリア
            current_file.empty()
            total_processed += 1
            
            # メトリクス更新
            _update_metrics(metrics_containers, total_processed, total_success, len(target_rows))
            
            # バッチサイズに達した場合、または最後の処理の場合にスプレッドシート更新
            if len(results_batch) >= batch_size or i == len(target_rows) - 1:
                if results_batch:
                    _update_spreadsheet_batch(gc, results_batch)
                    results_batch = []
            
            # 進捗更新
            progress = (i + 1) / len(target_rows)
            progress_bar.progress(progress)
            status_text.markdown(
                f"<p style='text-align: center; font-weight: 500;'>{i + 1}/{len(target_rows)} 処理完了</p>", 
                unsafe_allow_html=True
            )
            
        except Exception as e:
            st.error(f"行 {row_index} の処理エラー: {str(e)}")
            continue


def _show_current_processing(filename):
    """現在処理中のファイル名を表示"""
    current_file = st.empty()
    current_file.markdown(f"""
    <div style="text-align: center; padding: 0.5rem; background-color: rgba(40,40,40,0.7); border-radius: 5px; margin: 1rem 0;">
      <p style="margin: 0; font-weight: 500;">🔍 現在処理中: {filename}</p>
    </div>
    """, unsafe_allow_html=True)
    return current_file


def _update_metrics(metrics_containers, processed, success, total):
    """メトリクス表示を更新"""
    success_rate = (success / processed * 100) if processed > 0 else 0
    
    metrics_containers['processed'].markdown(f"""
    <div class="metric-card">
      <h3>✅ 処理済み</h3>
      <p>{processed}/{total}</p>
    </div>
    """, unsafe_allow_html=True)
    
    metrics_containers['success'].markdown(f"""
    <div class="metric-card">
      <h3>🎯 成功率</h3>
      <p>{success_rate:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)


def _update_spreadsheet_batch(gc, results_batch):
    """バッチ単位でスプレッドシートを更新"""
    batch_status = st.empty()
    batch_status.markdown("""
    <div class="info-box">
      ⏳ Googleスプレッドシートを更新中...
    </div>
    """, unsafe_allow_html=True)
    
    try:
        spreadsheet = gc.open("テレアポチェックシート")
        update_quality_check_results(spreadsheet, results_batch)
        time.sleep(1)  # API制限を避けるための待機
        batch_status.empty()
    except Exception as e:
        batch_status.markdown(f"""
        <div class="error-box">
          ❌ スプレッドシート更新エラー: {str(e)}
        </div>
        """, unsafe_allow_html=True)
        time.sleep(2)
        batch_status.empty() 