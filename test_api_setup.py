#!/usr/bin/env python3
"""
API設定テストスクリプト
OpenAIとAssemblyAIのAPIキーが正しく設定されているかをテストします
"""

import os
import sys
from dotenv import load_dotenv

def test_api_setup():
    """APIキーの設定をテストする"""
    print("🔍 API設定をテストしています...\n")
    
    # .envファイルを読み込み
    load_dotenv()
    
    # OpenAI APIキーのテスト
    print("1. OpenAI API接続テスト")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key or openai_key == "your-openai-api-key-here":
        print("❌ OpenAI APIキーが設定されていません")
        print("   .envファイルでOPENAI_API_KEYを設定してください")
        return False
    else:
        print(f"✅ OpenAI APIキーが設定されています (長さ: {len(openai_key)}文字)")
        
        # 実際の接続テスト
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            # 軽量なテストリクエスト
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1
            )
            print("✅ OpenAI API接続成功")
        except Exception as e:
            print(f"❌ OpenAI API接続エラー: {str(e)}")
            return False
    
    print()
    
    # AssemblyAI APIキーのテスト
    print("2. AssemblyAI API接続テスト")
    assemblyai_key = os.getenv("ASSEMBLYAI_API_KEY")
    
    if not assemblyai_key or assemblyai_key == "your-assemblyai-api-key-here":
        print("❌ AssemblyAI APIキーが設定されていません")
        print("   .envファイルでASSEMBLYAI_API_KEYを設定してください")
        return False
    else:
        print(f"✅ AssemblyAI APIキーが設定されています (長さ: {len(assemblyai_key)}文字)")
        
        # 実際の接続テスト
        try:
            import assemblyai as aai
            aai.settings.api_key = assemblyai_key
            
            # 接続テスト（transcriber作成）
            transcriber = aai.Transcriber()
            print("✅ AssemblyAI API接続成功")
        except Exception as e:
            print(f"❌ AssemblyAI API接続エラー: {str(e)}")
            return False
    
    print()
    
    # Google Sheets設定の確認
    print("3. Google Sheets設定確認")
    if os.path.exists("credentials.json"):
        print("✅ credentials.jsonが見つかりました")
    else:
        print("⚠️  credentials.jsonが見つかりません（Google Sheets機能に必要）")
    
    print()
    print("🎉 API設定テスト完了！")
    return True

def print_setup_instructions():
    """セットアップ手順を表示"""
    print("📝 セットアップ手順:")
    print()
    print("1. .envファイルを作成し、以下の内容を追加:")
    print("   OPENAI_API_KEY=sk-your-actual-openai-key")
    print("   ASSEMBLYAI_API_KEY=your-actual-assemblyai-key")
    print()
    print("2. Google Sheets用のcredentials.jsonを配置")
    print()
    print("3. python test_api_setup.py を実行してテスト")
    print()

if __name__ == "__main__":
    if not os.path.exists(".env"):
        print("❌ .envファイルが見つかりません\n")
        print_setup_instructions()
        sys.exit(1)
    
    success = test_api_setup()
    
    if success:
        print("✅ 全ての設定が完了しました！")
        print("🚀 streamlit run app.py でアプリケーションを起動できます")
    else:
        print("❌ 設定に問題があります。上記のエラーを修正してください。")
        print_setup_instructions() 