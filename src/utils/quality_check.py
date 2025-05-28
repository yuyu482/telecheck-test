"""
品質チェックのコアワークフローを実装するモジュール
"""

import streamlit as st
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