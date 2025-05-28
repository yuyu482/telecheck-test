"""
品質チェックのコアワークフローを実装するモジュール（Dify互換版）
"""

import streamlit as st
import json
from src.prompts.system_prompts import SYSTEM_PROMPTS
from src.api.openai_client import chat_with_retry

def node_replace(input_text, checker_str, client):
    """固有名詞を置換するノード（Dify互換）"""
    prompt = SYSTEM_PROMPTS['replace'].format(checker=checker_str)
    return chat_with_retry(client, prompt, input_text)

def node_speaker_separation(text_fixed, client):
    """話者分離を行うノード（Dify互換）"""
    prompt = SYSTEM_PROMPTS['speaker']
    return chat_with_retry(client, prompt, text_fixed, expect_json=True)

def node_company_name_check(text_separated, checker_str, client):
    """社名・担当者名の確認を行うノード（Dify互換）"""
    prompt = SYSTEM_PROMPTS['company_name_check'].format(checker=checker_str)
    return chat_with_retry(client, prompt, text_separated)

def node_teleapo_response_check(text_separated, client):
    """テレアポ担当者の対応チェックを行うノード（Dify互換）"""
    prompt = SYSTEM_PROMPTS['teleapo_response_check']
    return chat_with_retry(client, prompt, text_separated)

def node_longcall_check(text_separated, client):
    """ロングコールチェックを行うノード（Dify互換）"""
    prompt = SYSTEM_PROMPTS['longcall_check']
    return chat_with_retry(client, prompt, text_separated)

def node_customer_reaction_check(text_separated, client):
    """お客様の反応チェックを行うノード（Dify互換）"""
    prompt = SYSTEM_PROMPTS['customer_reaction_check']
    return chat_with_retry(client, prompt, text_separated)

def node_manner_check(text_separated, client):
    """心構え・マナーチェックを行うノード（Dify互換）"""
    prompt = SYSTEM_PROMPTS['manner_check']
    return chat_with_retry(client, prompt, text_separated)

def node_concat(company_name_check, teleapo_response_check, longcall_check, customer_reaction_check, manner_check):
    """各チェック結果を連結するノード（Dify互換）"""
    return (
        f"{company_name_check}\n\n"
        f"{teleapo_response_check}\n\n"
        f"{longcall_check}\n\n"
        f"{customer_reaction_check}\n\n"
        f"{manner_check}"
    )

def node_to_json(concatenated, client):
    """結果をJSONに変換するノード（Dify互換）"""
    prompt = SYSTEM_PROMPTS['to_json']
    full_prompt = f"{prompt}\n\n#インプット内容\n{concatenated}"
    return chat_with_retry(client, full_prompt, "", expect_json=True)

def run_workflow(raw_transcript, checker_str, client):
    """品質チェックのワークフローを実行（Dify互換版）"""
    try:
        workflow_progress = st.progress(0)
        status_text = st.empty()
        
        # 入力検証
        if not raw_transcript or not raw_transcript.strip():
            st.warning("入力テキストが空です")
            return None
        
        # 1. 固有名詞の置換
        status_text.markdown("**ステップ 1/9**: 固有名詞の置換")
        text_fixed = node_replace(raw_transcript, checker_str, client)
        if not text_fixed or not text_fixed.strip():
            st.warning("ステップ1: 固有名詞の置換でエラーが発生しました")
            return None
        workflow_progress.progress(1/9)

        # 2. 話者分離
        status_text.markdown("**ステップ 2/9**: 話者分離")
        text_separated = node_speaker_separation(text_fixed, client)
        if not text_separated or not text_separated.strip():
            st.warning("ステップ2: 話者分離でエラーが発生しました")
            return None
        workflow_progress.progress(2/9)

        # 3. 社名・担当者名チェック
        status_text.markdown("**ステップ 3/9**: 社名・担当者名チェック")
        company_name_check = node_company_name_check(text_separated, checker_str, client)
        if not company_name_check:
            company_name_check = "チェック失敗"
        workflow_progress.progress(3/9)
        
        # 4. テレアポ担当者対応チェック
        status_text.markdown("**ステップ 4/9**: テレアポ担当者対応チェック")
        teleapo_response_check = node_teleapo_response_check(text_separated, client)
        if not teleapo_response_check:
            teleapo_response_check = "チェック失敗"
        workflow_progress.progress(4/9)
            
        # 5. ロングコールチェック
        status_text.markdown("**ステップ 5/9**: ロングコールチェック")
        longcall_check = node_longcall_check(text_separated, client)
        if not longcall_check:
            longcall_check = "チェック失敗"
        workflow_progress.progress(5/9)
            
        # 6. お客様反応チェック
        status_text.markdown("**ステップ 6/9**: お客様反応チェック")
        customer_reaction_check = node_customer_reaction_check(text_separated, client)
        if not customer_reaction_check:
            customer_reaction_check = "チェック失敗"
        workflow_progress.progress(6/9)
            
        # 7. 心構え・マナーチェック
        status_text.markdown("**ステップ 7/9**: 心構え・マナーチェック")
        manner_check = node_manner_check(text_separated, client)
        if not manner_check:
            manner_check = "チェック失敗"
        workflow_progress.progress(7/9)

        # 8. 結果の連結
        status_text.markdown("**ステップ 8/9**: 結果の連結")
        concatenated = node_concat(company_name_check, teleapo_response_check, longcall_check, customer_reaction_check, manner_check)
        workflow_progress.progress(8/9)

        # 9. JSONに変換
        status_text.markdown("**ステップ 9/9**: JSON形式に変換")
        result_json = node_to_json(concatenated, client)
        
        # JSON変換結果の検証
        if result_json:
            result_json = result_json.strip()
            # JSON形式でない場合は、手動でJSONを作成
            if not (result_json.startswith('{') and result_json.endswith('}')):
                st.warning("JSON変換に失敗したため、手動でJSONを作成します")
                fallback_json = create_fallback_json(
                    company_name_check, teleapo_response_check, longcall_check, 
                    customer_reaction_check, manner_check
                )
                result_json = json.dumps(fallback_json, ensure_ascii=False, indent=2)
        else:
            # API呼び出し失敗時のフォールバック
            st.warning("JSON変換APIが失敗したため、フォールバックJSONを使用します")
            fallback_json = create_fallback_json(
                company_name_check, teleapo_response_check, longcall_check, 
                customer_reaction_check, manner_check
            )
            result_json = json.dumps(fallback_json, ensure_ascii=False, indent=2)
        
        workflow_progress.progress(1.0)
        
        # 完了表示をクリア
        status_text.empty()
        workflow_progress.empty()
        
        return result_json
        
    except Exception as e:
        st.error(f"ワークフロー実行エラー: {str(e)}")
        # 完全なエラー時のフォールバック
        fallback_json = {
            "テレアポ担当者名": "処理エラー",
            "報告まとめ": [f"処理エラー: {str(e)}"],
            "社名や担当者名を名乗らない": "処理エラー",
            "アプローチで販売店名、ソフト名の先出し": "処理エラー",
            "同業他社の悪口等": "処理エラー",
            "運転中や電車内でも無理やり続ける": "処理エラー",
            "2回断られても食い下がる": "処理エラー",
            "暴言・悪口・脅迫・逆上": "処理エラー",
            "情報漏洩": "処理エラー",
            "共犯（教唆・幇助）": "処理エラー",
            "通話対応（無言電話／ガチャ切り）": "処理エラー",
            "呼び方": "処理エラー",
            "ロングコール": "処理エラー",
            "ガチャ切りされた△": "処理エラー",
            "当社の電話お断り": "処理エラー",
            "しつこい・何度も電話がある": "処理エラー",
            "お客様専用電話番号と言われる": "処理エラー",
            "口調を注意された": "処理エラー",
            "怒らせた": "処理エラー",
            "暴言を受けた": "処理エラー",
            "通報する": "処理エラー",
            "営業お断り": "処理エラー",
            "事務員に対して代表者のことを「社長」「オーナー」「代表」": "処理エラー",
            "一人称が「僕」「自分」「俺」": "処理エラー",
            "「弊社」のことを「うち」「僕ら」と言う": "処理エラー",
            "謝罪が「すみません」「ごめんなさい」": "処理エラー",
            "口調や態度が失礼": "処理エラー",
            "会話が成り立っていない": "処理エラー",
            "残債の「下取り」「買い取り」トーク": "処理エラー",
            "嘘・真偽不明": "処理エラー",
            "その他問題": "処理エラー"
        }
        return json.dumps(fallback_json, ensure_ascii=False, indent=2)

def create_fallback_json(company_name_check, teleapo_response_check, longcall_check, customer_reaction_check, manner_check):
    """フォールバックJSONを作成する関数"""
    
    # 担当者名を抽出
    担当者名 = "不明"
    if company_name_check and "テレアポ担当者名" in company_name_check:
        lines = company_name_check.split('\n')
        for line in lines:
            if "テレアポ担当者名" in line and ":" in line:
                担当者名 = line.split(':')[1].strip()
                break
    
    # 各チェック結果から判定を抽出
    def extract_judgments(text, rules):
        judgments = {}
        if not text:
            return {rule: "処理失敗" for rule in rules}
        
        lines = text.split('\n')
        current_rule = None
        
        # デバッグ用：処理するテキストを表示
        print(f"=== 判定抽出デバッグ ===")
        print(f"処理対象テキスト: {text[:200]}...")
        
        for line in lines:
            line = line.strip()
            
            # ルール名の検出（より柔軟に）
            if line.startswith('▪️') or line.startswith('■') or line.startswith('●'):
                current_rule = line.replace('▪️', '').replace('■', '').replace('●', '').strip()
                print(f"ルール検出: {current_rule}")
            
            # 判定の検出（より柔軟に）
            elif current_rule and ('判定' in line or '結果' in line):
                print(f"判定行検出: {line}")
                
                # 問題なし/問題ありの判定（より柔軟に）
                if '問題なし' in line or '問題無し' in line or 'なし' in line:
                    judgments[current_rule] = "問題なし"
                    print(f"→ 問題なし")
                elif '問題あり' in line or '問題有り' in line or 'あり' in line:
                    judgments[current_rule] = "問題あり"
                    print(f"→ 問題あり")
                else:
                    judgments[current_rule] = "判定不明"
                    print(f"→ 判定不明: {line}")
        
        print(f"抽出された判定: {judgments}")
        
        # 不足している項目を補完
        for rule in rules:
            if rule not in judgments:
                judgments[rule] = "処理失敗"
                print(f"補完: {rule} → 処理失敗")
        
        print(f"最終判定結果: {judgments}")
        print("=== デバッグ終了 ===")
        
        return judgments
    
    # 各チェック項目の判定を抽出（実際のスプレッドシート列名に合わせる）
    company_judgments = extract_judgments(company_name_check, ["社名や担当者名を名乗らない"])
    teleapo_judgments = extract_judgments(teleapo_response_check, [
        "アプローチで販売店名、ソフト名の先出し", "同業他社の悪口等", "運転中や電車内でも無理やり続ける",
        "2回断られても食い下がる", "暴言・悪口・脅迫・逆上", "情報漏洩", "共犯（教唆・幇助）",
        "通話対応（無言電話／ガチャ切り）", "呼び方"
    ])
    longcall_judgments = extract_judgments(longcall_check, ["ロングコール"])
    customer_judgments = extract_judgments(customer_reaction_check, [
        "当社の電話お断り", "しつこい・何度も電話がある", "お客様専用電話番号と言われる",
        "口調を注意された", "怒らせた", "暴言を受けた", "通報する", "営業お断り"
    ])
    manner_judgments = extract_judgments(manner_check, [
        "事務員に対して代表者のことを「社長」「オーナー」「代表」", "一人称が「僕」「自分」「俺」",
        "「弊社」のことを「うち」「僕ら」と言う", "謝罪が「すみません」「ごめんなさい」",
        "口調や態度が失礼", "会話が成り立っていない", "残債の「下取り」「買い取り」トーク",
        "嘘・真偽不明", "その他問題"
    ])
    
    # 報告まとめを作成
    報告まとめ = []
    all_texts = [company_name_check, teleapo_response_check, longcall_check, customer_reaction_check, manner_check]
    for text in all_texts:
        if text and "問題あり" in text:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if "報告" in line and ":" in line and i < len(lines) - 1:
                    report = line.split(':', 1)[1].strip()
                    if report and report != "なし" and len(報告まとめ) < 5:
                        報告まとめ.append(report)
    
    if not 報告まとめ:
        報告まとめ = ["特に問題は検出されませんでした"]
    
    # 最終的なJSONを構築（実際のスプレッドシート列名に合わせる）
    result = {
        "テレアポ担当者名": 担当者名,
        "報告まとめ": 報告まとめ,
        "社名や担当者名を名乗らない": company_judgments.get("社名や担当者名を名乗らない", "処理失敗"),
        **teleapo_judgments,
        **longcall_judgments,
        "ガチャ切りされた△": "処理失敗",  # この項目は現在のワークフローにないため
        **customer_judgments,
        **manner_judgments
    }
    
    return result 