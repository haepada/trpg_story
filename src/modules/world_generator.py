"""
세계관 생성 및 관리를 담당하는 모듈
"""
from modules.ai_service import generate_gemini_text

def generate_world_description(theme):
    """
    선택한 테마에 기반한 세계관 생성 - 개선된 버전
    
    Args:
        theme (str): 세계관 테마
        
    Returns:
        str: 생성된 세계관 설명
    """
    prompt = f"""
    당신은 TRPG 게임 마스터입니다. '{theme}' 테마의 몰입감 있는 세계를 한국어로 만들어주세요.
    다음 구조에 따라 체계적으로 세계관을 구축해주세요:

    # 1. 기본 골격 수립
    ## 핵심 테마와 분위기
    - '{theme}'의 특성이 뚜렷하게 드러나는 세계의 중심 이념이나 분위기
    
    ## 세계의 독창적 규칙
    - 이 세계만의 특별한 물리법칙이나 마법/기술 체계
    
    # 2. 구조적 요소
    ## 주요 지역 (3~5개)
    - 각 지역의 특성과 분위기
    
    ## 주요 세력 (2~3개)
    - 세력 간의 관계와 갈등 구조
    
    # 3. 현재 상황
    ## 중심 갈등 
    - 플레이어가 직면하게 될 세계의 주요 문제나 갈등
    
    ## 잠재적 위협
    - 세계를 위협하는 요소나 임박한 위기
    
    # 4. 플레이어 개입 지점
    - 플레이어가 이 세계에서 영향력을 행사할 수 있는 방법
    - 탐험 가능한 비밀이나 수수께끼

    모든 문장은 반드시 완성된 형태로 작성하세요. 중간에 문장이 끊기지 않도록 해주세요.
    전체 내용은 약 400-500단어로 작성해주세요.
    """
    
    return generate_gemini_text(prompt, 800)

def master_answer_question(question, world_desc, theme):
    """
    세계관에 대한 질문에 마스터가 답변 - 개선된 버전
    
    Args:
        question (str): 플레이어의 질문
        world_desc (str): 세계관 설명
        theme (str): 세계관 테마
        
    Returns:
        str: 마스터의 답변
    """
    try:
        prompt = f"""
        당신은 TRPG 게임 마스터입니다. 플레이어가 '{theme}' 테마의 다음 세계에 대해 질문했습니다:
        
        세계 설명:
        {world_desc[:500]}...
        
        플레이어 질문:
        {question}
        
        ## 응답 지침:
        1. 게임 마스터로서 이 질문에 대한 답변을 한국어로 작성해주세요.
        2. 세계관을 풍부하게 하면서 플레이어의 상상력을 자극하는 답변을 제공하세요.
        3. 플레이어가 알 수 없는 신비한 요소를 한두 가지 남겨두세요.
        4. 질문에 관련된 세계의 역사, 전설, 소문 등을 포함하세요.
        5. 150단어 이내로 간결하게 답변하세요.
        
        모든 문장은 완결된 형태로 작성하세요.
        """
        
        return generate_gemini_text(prompt, 400)
    except Exception as e:
        from config.constants import BACKUP_RESPONSES
        return BACKUP_RESPONSES["question"]  # 백업 응답 반환

def generate_world_expansion(world_description, theme, expansion_topic):
    """
    세계관을 특정 주제로 확장하는 함수
    
    Args:
        world_description (str): 기존 세계관 설명
        theme (str): 세계관 테마
        expansion_topic (str): 확장할 주제
        
    Returns:
        str: 확장된 세계관 내용
    """
    prompt = f"""
    당신은 TRPG 게임 마스터입니다. 다음 세계관 설명을 이어서 작성해주세요.
    이전 세계관 내용을 기반으로 "{expansion_topic}" 측면을 더 상세히 확장해주세요.
    
    테마: {theme}
    현재 세계관 설명의 일부:
    {world_description[:500]}...
    
    ## 확장 지침:
    1. 선택한 주제({expansion_topic})에 초점을 맞추어 세계관을 확장하세요.
    2. 플레이어가 탐험하거나 상호작용할 수 있는 구체적인 요소를 추가하세요.
    3. 이전 내용과 일관성을 유지하면서 세계를 더 풍부하게 만드세요.
    4. 비밀, 갈등, 또는 미스터리 요소를 하나 이상 포함하세요.
    5. 200-300단어 내외로 작성하세요.
    6. 단락을 나누어 가독성을 높이세요.
    
    모든 문장은 완결된 형태로 작성하세요.
    """
    
    return generate_gemini_text(prompt, 500)

def master_answer_game_question(question, theme, location, world_description):
    """
    게임 중 질문에 마스터가 답변
    
    Args:
        question (str): 플레이어의 질문
        theme (str): 세계관 테마
        location (str): 현재 위치
        world_description (str): 세계관 설명
        
    Returns:
        str: 마스터의 답변
    """
    prompt = f"""
    당신은 TRPG 게임 마스터입니다. 플레이어가 게임 중에 다음과 같은 질문을 했습니다:
    
    {question}
    
    ## 게임 정보
    세계 테마: {theme}
    현재 위치: {location}
    세계 설명: {world_description[:300]}...
    
    ## 응답 지침
    1. 게임의 흐름을 유지하되, 플레이어에게 유용한 정보를 제공하세요.
    2. 세계관의 신비함과 일관성을 유지하세요.
    3. 필요하다면 플레이어의 캐릭터가 알지 못하는 정보는 "소문에 따르면..." 또는 "전설에 의하면..."과 같은 형식으로 제공하세요.
    4. 직접적인 답변보다는 플레이어가 스스로 발견하고 탐험할 수 있는 힌트를 제공하세요.
    5. 150단어 이내로 답변하세요.
    6. 모든 문장은 완결된 형태로 작성하세요.
    """
    
    return generate_gemini_text(prompt, 400)