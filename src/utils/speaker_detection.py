"""
テレアポ担当者自動判定ロジック
システム開発者が変更可能な設定ベースの判定システム
"""

import re
from typing import Dict, List, Optional

class TeleapoSpeakerDetector:
    """テレアポ担当者判定クラス"""
    
    def __init__(self):
        # 判定ルールの設定（開発者が変更可能）
        self.detection_rules = {
            # 会社名・自己紹介キーワード
            "company_keywords": [
                "会社", "株式会社", "有限会社", "と申します", "と言います",
                "営業", "担当", "部署", "本日は", "お忙しい中"
            ],
            
            # 商品・サービス紹介キーワード
            "sales_keywords": [
                "ご紹介", "サービス", "商品", "プラン", "料金", "価格",
                "お得", "キャンペーン", "無料", "体験", "導入"
            ],
            
            # 顧客対応キーワード
            "customer_service_keywords": [
                "いかがでしょうか", "ご質問", "ご相談", "ご検討", 
                "資料", "説明", "デモ", "お話"
            ],
            
            # 顧客の反応キーワード（これらが多い話者は顧客と判定）
            "customer_response_keywords": [
                "はい", "そうですね", "わかりました", "なるほど",
                "興味があります", "検討します", "質問があります"
            ],
            
            # 重み設定
            "weights": {
                "company_keywords": 3.0,
                "sales_keywords": 2.5,
                "customer_service_keywords": 2.0,
                "customer_response_keywords": -2.0,  # マイナス重みで顧客判定
                "first_speaker_bonus": 1.5  # 最初の話者ボーナス
            },
            
            # 発言量による判定
            "speech_ratio_threshold": 0.6,  # 60%以上発言している場合はテレアポ担当者の可能性が高い
        }
    
    def detect_teleapo_speaker(self, transcript_result: Dict) -> str:
        """テレアポ担当者を自動判定"""
        utterances = transcript_result.get("utterances", [])
        if not utterances:
            return "A"  # デフォルト
        
        # 話者別スコア計算
        speaker_scores = {}
        speaker_word_counts = {}
        first_speaker = utterances[0].speaker if utterances else None
        
        for utterance in utterances:
            speaker = utterance.speaker
            text = utterance.text
            
            if speaker not in speaker_scores:
                speaker_scores[speaker] = 0
                speaker_word_counts[speaker] = 0
            
            # 単語数カウント
            speaker_word_counts[speaker] += len(text.split())
            
            # キーワードベースのスコア計算
            speaker_scores[speaker] += self._calculate_keyword_score(text)
            
            # 最初の話者ボーナス
            if speaker == first_speaker:
                first_speaker_bonus = self.detection_rules["weights"].get("first_speaker_bonus", 1.5)
                speaker_scores[speaker] += first_speaker_bonus
        
        # 発言量による調整
        total_words = sum(speaker_word_counts.values())
        for speaker in speaker_word_counts:
            speech_ratio = speaker_word_counts[speaker] / total_words if total_words > 0 else 0
            speech_threshold = self.detection_rules.get("speech_ratio_threshold", 0.6)
            if speech_ratio >= speech_threshold:
                speaker_scores[speaker] += 2.0
        
        # 最高スコアの話者をテレアポ担当者として判定
        if speaker_scores:
            teleapo_speaker = max(speaker_scores.keys(), key=lambda x: speaker_scores[x])
            return teleapo_speaker
        else:
            return "A"  # デフォルト
    
    def _calculate_keyword_score(self, text: str) -> float:
        """テキストのキーワードスコアを計算"""
        score = 0
        text_lower = text.lower()
        
        for category, keywords in self.detection_rules.items():
            if category == "weights" or category.endswith("_threshold"):
                continue
                
            weight = self.detection_rules["weights"].get(category, 1.0)
            
            if isinstance(keywords, list):
                for keyword in keywords:
                    if keyword in text_lower:
                        score += weight
        
        return score
    
    def get_detection_summary(self, transcript_result: Dict) -> Dict:
        """判定根拠のサマリーを返す（デバッグ用）"""
        utterances = transcript_result.get("utterances", [])
        summary = {
            "speakers": {},
            "detection_logic": self.detection_rules
        }
        
        for utterance in utterances:
            speaker = utterance.speaker
            if speaker not in summary["speakers"]:
                summary["speakers"][speaker] = {
                    "total_words": 0,
                    "keyword_matches": [],
                    "score": 0
                }
            
            summary["speakers"][speaker]["total_words"] += len(utterance.text.split())
            summary["speakers"][speaker]["score"] += self._calculate_keyword_score(utterance.text)
        
        return summary

# シングルトンインスタンス
detector = TeleapoSpeakerDetector()

def detect_teleapo_speaker(transcript_result: Dict) -> str:
    """テレアポ担当者を自動判定（外部インターフェース）"""
    return detector.detect_teleapo_speaker(transcript_result)

def get_detection_summary(transcript_result: Dict) -> Dict:
    """判定根拠のサマリーを返す（外部インターフェース）"""
    return detector.get_detection_summary(transcript_result)

def update_detection_rules(new_rules: Dict):
    """判定ルールを更新（開発者用）"""
    detector.detection_rules.update(new_rules) 