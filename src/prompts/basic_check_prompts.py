"""
基本的な品質チェック用プロンプト定義（リファクタリング版）
"""

def _create_base_prompt(check_item_name: str):
    """
    指定されたチェック項目に基づいて、プロンプトの共通ベース部分を生成します。
    ベストプラクティスからの情報取得とフォールバック処理を含みます。
    """
    try:
        from src.quality_check.best_practices import get_all_principles, get_judgment_instruction
        principles = get_all_principles()
        judgment_guide = get_judgment_instruction(check_item_name)
    except ImportError:
        # フォールバック：ベストプラクティス未利用版
        principles = ""
        judgment_guide = ""
    
    return (
        'あなたは「SFIDA X（スフィーダクロス）」のテレアポチェックを行うプロフェッショナルです。\n\n'
        f'{principles}\n\n'
        f'{judgment_guide}\n\n'
        '以下に示す会話記録とチェックすべきルールに基づいて、テレアポが問題なく実施されているかを判定してください。\n\n'
        '入力された会話記録は既にAssemblyAIによって話者分離済みです。\n'
        '[テレアポ担当者] で始まる発言がテレアポ担当者、[顧客] で始まる発言が顧客の発言です。\n\n'
    )

def _get_company_name_check_prompt():
    """社名・担当者名チェック用プロンプト（遅延ロード）"""
    base_prompt = _create_base_prompt("社名や担当者名を名乗らない")
    
    specific_rules = (
        '問題があった場合は「問題あり」とし、具体的に何が問題だったかを「報告」欄に書いてください。問題がなければ「問題なし」としてください。\n\n'
        'チェックすべき内容\n\n'
        '#社名と担当者名を名乗っているか\n'
        '社名：「SFIDA X」または「スフィーダクロス」\n'
        '担当者名：以下のいずれか\n'
        '（{checker}）\n'
        '両方（社名・担当者名）が名乗られていない場合は「問題あり」。名字だけでも問題ありません。\n\n'
        '**重要な判定基準**\n'
        '• 問題なし：社名（SFIDA X または スフィーダクロス）と担当者名（姓のみ可）の両方を名乗っている\n'
        '• 問題あり：社名または担当者名のいずれかが欠けている\n\n'
        '#アウトプット形式\n'
        '以下のフォーマットに従って回答してください。セミコロン以降を埋めてください。\n'
        '**重要**: 判定は必ず「問題なし」または「問題あり」のいずれかを記載してください。\n\n'
        '1. テレアポ担当者名(④) : \n'
        '2. 社名や担当者名を名乗らない : \n'
        '判定: 問題あり or 問題なし\n'
        '「報告」欄には、問題があった場合のみ詳細を記述してください。\n'
        '問題がない場合は「報告 : なし」としてください。'
    )
    return base_prompt + specific_rules

def _get_longcall_check_prompt():
    """ロングコールチェック用プロンプト（遅延ロード）"""
    base_prompt = _create_base_prompt("ロングコール")
    
    specific_rules = (
        '以下に示す会話記録のチェックルールに基づいて、テレアポが問題なく実施されているか、お客様の反応に問題がなかったかを判定してください。\n\n'
        '#チェックルール\n'
        '1. ロングコール\n\n'
        '会話記録に「電話が鳴る」という記述がある場合、この回数をカウントしてください。記述がない場合は、「問題なし」で良いです。\n'
        'これは電話のコールを表しています。「電話が鳴る」が7回以上繰り返された場合は、問題ありです。ロングコールに当たります。\n\n'
        '**重要な判定基準**\n'
        '• 問題なし：「電話が鳴る」記述が6回以下、または記述がない\n'
        '• 問題あり：「電話が鳴る」記述が7回以上\n'
        '• 理由：7回以上のコールは相手に不快感を与え、迷惑行為と判断される\n\n'
        '#アウトプット形式\n'
        '下記のテンプレートを使い、各ルールごとに判定を行ってください。\n'
        '「問題あり」または「問題なし」を必ず明記し、問題がある場合のみ「報告」欄に詳細を書いてください。\n'
        '**重要**: 判定は必ず「問題なし」または「問題あり」のいずれかを記載してください。\n\n'
        '▪️ロングコール\n'
        '判定 : 問題なし or 問題あり\n'
        '報告 : '
    )
    return base_prompt + specific_rules

def get_basic_prompt(prompt_name: str):
    """基本プロンプトを取得（遅延ロード）"""
    prompts = {
        'company_name_check': _get_company_name_check_prompt,
        'longcall_check': _get_longcall_check_prompt
    }
    
    if prompt_name in prompts:
        return prompts[prompt_name]()
    return f"プロンプト '{prompt_name}' は見つかりません。"

# 後方互換性のため、辞書形式もサポート
class _BasicCheckPromptsDict:
    """基本チェックプロンプト辞書クラス（遅延ロード対応）"""
    
    def __getitem__(self, key):
        return get_basic_prompt(key)
    
    def __contains__(self, key):
        return key in ['company_name_check', 'longcall_check']
    
    def get(self, key, default=None):
        try:
            return self[key]
        except:
            return default
    
    def keys(self):
        return ['company_name_check', 'longcall_check']

BASIC_CHECK_PROMPTS = _BasicCheckPromptsDict() 