"""
アプリケーション設定管理モジュール
"""

import os
from dataclasses import dataclass
from typing import Optional
import streamlit as st


@dataclass
class AppConfig:
    """アプリケーション設定クラス"""
    
    # API設定
    openai_api_key: Optional[str] = None
    assemblyai_api_key: Optional[str] = None
    
    # ファイル処理設定
    max_file_size_mb: int = 2048  # 2GB
    max_concurrent_files: int = 10
    recommended_file_size_mb: int = 500
    
    # 話者分離設定
    default_speakers_expected: int = 2
    default_language: str = "ja"
    
    # 品質チェック設定
    default_batch_size: int = 5
    max_processing_rows: int = 1000

    def __post_init__(self):
        """設定の初期化後処理"""
        self._load_api_keys()
    
    def _load_api_keys(self):
        """API キーを環境変数またはStreamlitシークレットから読み込み"""
        # OpenAI API Key
        self.openai_api_key = self._get_api_key(
            "OPENAI_API_KEY",
            ["openai.api_key", "OPENAI_API_KEY", "api_keys.openai"]
        )
        
        # AssemblyAI API Key
        self.assemblyai_api_key = self._get_api_key(
            "ASSEMBLYAI_API_KEY", 
            ["assemblyai.api_key", "ASSEMBLYAI_API_KEY", "api_keys.assemblyai"]
        )
    
    def _get_api_key(self, env_name: str, secret_paths: list) -> Optional[str]:
        """環境変数またはStreamlitシークレットからAPIキーを取得"""
        # 環境変数から取得
        api_key = os.getenv(env_name)
        
        # 環境変数にない場合はStreamlitのシークレットから取得
        if not api_key and hasattr(st, 'secrets'):
            for path in secret_paths:
                keys = path.split('.')
                current = st.secrets
                
                try:
                    for key in keys:
                        current = current[key]
                    api_key = current
                    break
                except (KeyError, TypeError):
                    continue
        
        return api_key
    
    def validate_api_keys(self) -> dict:
        """API キーの有効性を検証"""
        results = {
            "openai": bool(self.openai_api_key),
            "assemblyai": bool(self.assemblyai_api_key)
        }
        return results
    
    def get_file_size_info(self, file_size_bytes: int) -> dict:
        """ファイルサイズ情報を取得"""
        size_mb = file_size_bytes / (1024 * 1024)
        
        return {
            "size_mb": size_mb,
            "is_large": size_mb > self.recommended_file_size_mb,
            "is_very_large": size_mb > 1000,
            "is_oversized": size_mb > self.max_file_size_mb
        }


# グローバル設定インスタンス
config = AppConfig() 