"""
캐릭터 생성 및 관리를 위한 유틸리티 모듈
"""
import random
import streamlit as st
import re
from modules.ai_service import generate_gemini_text
from modules.item_manager import initialize_inventory
from config.constants import PROFESSION_KEY_STATS, BACKGROUND_TAGS, ABILITY_NAMES

# 직업별 아이콘 맵핑
PROFESSION_ICONS = {
    '마법사': '🧙',
    '전사': '⚔️',
    '도적': '🗡️',
    '성직자': '📿',
    '음유시인': '🎭',
    '연금술사': '⚗️',
    '우주 파일럿': '🚀',
    '사이버 해커': '💻',
    '생체공학자': '🧬',
    '보안 요원': '🛡️',
    '외계종족 전문가': '👽',
    '기계공학자': '⚙️',
    '정보 브로커': '📡',
    '밀수업자': '📦',
    '저항군 요원': '🕵️',
    '엘리트 경비원': '💂',
    '스카운터': '🔭',
    '의료 기술자': '💉'
}

# 종족별 아이콘 맵핑
RACE_ICONS = {
    '인간': '👤',
    '엘프': '🧝',
    '드워프': '🧔',
    '하플링': '🧒',
    '오크': '👹',
    '고블린': '👺',
    '드라코니안': '🐲',
    '안드로이드': '🤖',
    '외계인 하이브리드': '👽',
    '변형 인류': '🧟',
    '네뷸런': '👾',
    '크로노스피어': '⏱️',
    '우주 유목민': '🌠',
    '변이체': '🧬',
    '강화인류': '🦾',
    '생체기계': '🦿',
    '숙주': '🕸️',
    '정신감응자': '🔮',
    '저항자': '✊'
}

# 종족별 능력치 보너스
RACE_BONUSES = {
    '인간': {'모든 능력치': '+1'},
    '엘프': {'DEX': '+2', 'INT': '+1'},
    '드워프': {'CON': '+2', 'STR': '+1'},
    '하플링': {'DEX': '+2', 'CHA': '+1'},
    '오크': {'STR': '+2', 'CON': '+1'},
    '고블린': {'DEX': '+2', 'INT': '+1'},
    '드라코니안': {'STR': '+2', 'CHA': '+1'},
    '안드로이드': {'INT': '+2', 'STR': '+1'},
    '외계인 하이브리드': {'WIS': '+2', 'CHA': '+1'},
    '변형 인류': {'DEX': '+2', 'CON': '+1'},
    '네뷸런': {'INT': '+2', 'WIS': '+1'},
    '크로노스피어': {'INT': '+2', 'DEX': '+1'},
    '우주 유목민': {'CON': '+2', 'WIS': '+1'},
    '변이체': {'CON': '+2', 'STR': '+1'},
    '강화인류': {'STR': '+2', 'DEX': '+1'},
    '생체기계': {'STR': '+1', 'INT': '+2'},
    '숙주': {'CON': '+2', 'WIS': '+1'},
    '정신감응자': {'WIS': '+2', 'CHA': '+1'},
    '저항자': {'DEX': '+1', 'CON': '+2'}
}

# 종족별 특수 능력
RACE_ABILITIES = {
    '인간': '적응력: 하루에 한 번 주사위를 다시 굴릴 수 있습니다.',
    '엘프': '암시야: 어두운 곳에서도 잘 볼 수 있습니다.',
    '드워프': '내구력: 독성에 대한 저항력이 있습니다.',
    '하플링': '행운: 주사위 결과가 1이 나오면 다시 굴릴 수 있습니다.',
    '오크': '끈질김: 체력이 0이 되어도 1턴 더 활동할 수 있습니다.',
    '고블린': '약삭빠름: 은신 판정에 +2 보너스를 받습니다.',
    '드라코니안': '용의 숨결: 불을 내뿜을 수 있습니다.',
    '안드로이드': '계산 능력: 수학적 판정에 +3 보너스를 받습니다.',
    '외계인 하이브리드': '텔레파시: 타인의 마음을 읽을 수 있습니다.',
    '변형 인류': '적응력: 유해한 환경에 저항할 수 있습니다.',
    '네뷸런': '에너지 흡수: 에너지 공격을 흡수할 수 있습니다.',
    '크로노스피어': '시간 감각: 시간 흐름을 느리게 할 수 있습니다.',
    '우주 유목민': '우주 생존: 진공에서도 짧은 시간 살 수 있습니다.',
    '변이체': '재생 능력: 턴마다 체력 1점을 회복합니다.',
    '강화인류': '싸이버 강화: 특정 행동에 보너스를 받습니다.',
    '생체기계': '에너지 저장: 에너지를 저장하고 방출할 수 있습니다.',
    '숙주': '공생: 기생체와 함께 강화된 능력을 사용할 수 있습니다.',
    '정신감응자': '원격 감지: 근처의 생명체를 감지할 수 있습니다.',
    '저항자': '반역: 정신 지배에 대한 저항력이 있습니다.'
}

# 종족별 설명
RACE_DESCRIPTIONS = {
    '인간': '적응력과 다재다능함으로 모든 환경에서 성공할 수 있습니다.',
    '엘프': '우아하고 장수하는 종족으로 예술과 마법에 뛰어납니다.',
    '드워프': '강인하고 끈질긴 종족으로 대장장이 기술과 광산 작업에 능숙합니다.',
    '하플링': '작지만 용감한 종족으로 행운과 민첩성이 뛰어납니다.',
    '오크': '강력하고 야만적인 종족으로 전투에 뛰어납니다.',
    '고블린': '교활하고 약삭빠른 종족으로 생존 능력이 뛰어납니다.',
    '드라코니안': '드래곤의 피를 물려받은 종족으로 원소 저항력이 있습니다.',
    '안드로이드': '인공 지능을 가진 기계 생명체로 논리적 사고에 뛰어납니다.',
    '외계인 하이브리드': '인간과 외계종의 혼혈로 독특한 능력을 가집니다.',
    '변형 인류': '유전자 조작을 통해 진화한 인류로 특수 능력을 가집니다.',
    '네뷸런': '에너지 기반 생명체로 물리적 형태를 변형할 수 있습니다.',
    '크로노스피어': '시간의 흐름을 조작할 수 있는 능력을 가진 존재입니다.',
    '우주 유목민': '우주 공간에서 세대를 거쳐 살아온 인류의 변종입니다.',
    '변이체': '방사능이나 화학물질에 의해 변이된 인간입니다.',
    '강화인류': '기계 장치를 통해 강화된 인간입니다.',
    '생체기계': '생물학적 요소와 기계가 융합된 존재입니다.',
    '숙주': '외계 생물체와 공생 관계를 맺은 인간입니다.',
    '정신감응자': '정신적 능력이 발달한 인간의 진화 형태입니다.',
    '저항자': '억압에 저항하며 생존한 강인한 인류입니다.'
}

# 직업별 주요 능력치
PROFESSION_STATS = {
    '마법사': ['INT', 'WIS'],
    '전사': ['STR', 'CON'],
    '도적': ['DEX', 'CHA'],
    '성직자': ['WIS', 'CHA'],
    '음유시인': ['CHA', 'DEX'],
    '연금술사': ['INT', 'DEX'],
    '우주 파일럿': ['DEX', 'INT'],
    '사이버 해커': ['INT', 'DEX'],
    '생체공학자': ['INT', 'WIS'],
    '보안 요원': ['STR', 'CON'],
    '외계종족 전문가': ['WIS', 'CHA'],
    '기계공학자': ['INT', 'DEX'],
    '정보 브로커': ['INT', 'CHA'],
    '밀수업자': ['DEX', 'CHA'],
    '저항군 요원': ['DEX', 'CON'],
    '엘리트 경비원': ['STR', 'DEX'],
    '스카운터': ['DEX', 'WIS'],
    '의료 기술자': ['INT', 'WIS']
}

# 직업별 시작 장비
PROFESSION_EQUIPMENT = {
    '마법사': ['마법서', '지팡이', '로브', '마법 재료 파우치', '양초 3개'],
    '전사': ['장검', '방패', '체인 메일', '배낭', '모험가 키트'],
    '도적': ['단검 2개', '가죽 갑옷', '도둑 도구 세트', '후드 망토', '물약 2개'],
    '성직자': ['메이스', '신성한 상징', '갑옷', '치유 키트', '기도문'],
    '음유시인': ['류트', '가죽 갑옷', '단검', '여행 의상 세트', '매력 도구'],
    '연금술사': ['연금술 키트', '로브', '약초 주머니', '실험 노트', '물약 3개'],
    '우주 파일럿': ['레이저 건', '우주복', '통신 장치', '내비게이션 도구', '응급 키트'],
    '사이버 해커': ['휴대용 컴퓨터', '임플란트 도구', '전자 장비 세트', '스텔스 장비', '데이터 칩'],
    '생체공학자': ['의료 키트', '연구 도구', '생체 샘플 세트', '데이터 패드', '실험 장비'],
    '보안 요원': ['에너지 소총', '방탄 조끼', '보안 키트', '통신 장치', '감시 장비'],
    '외계종족 전문가': ['번역기', '외계 유물', '연구 노트', '통신 장치', '생명 지원 시스템'],
    '기계공학자': ['공구 세트', '청사진', '부품 키트', '용접 장비', '분석 장치'],
    '정보 브로커': ['암호화된 데이터 패드', '은밀한 통신 장치', '위장 도구', '정보 칩', '비상금'],
    '밀수업자': ['블래스터 권총', '숨겨진 주머니 의류', '잠금해제 도구', '위조 신분증', '비상 탈출 키트'],
    '저항군 요원': ['숨겨진 무기', '암호화 통신 장치', '위장 키트', '임시 폭발물', '생존 장비'],
    '엘리트 경비원': ['충격봉', '방탄 유니폼', '감시 장치', '통신 이어피스', '신원 확인 장치'],
    '스카운터': ['망원경', '생존 키트', '지도 제작 도구', '위치 추적기', '휴대용 쉘터'],
    '의료 기술자': ['고급 의료 키트', '진단 스캐너', '응급 치료 약품', '수술 도구', '생체 모니터']
}

# 직업별 특수 기술
PROFESSION_SKILLS = {
    '마법사': '마법 시전: 다양한 마법 주문을 시전할 수 있으며, 스크롤에서 주문을 배우는 능력이 있습니다.',
    '전사': '전투 전문가: 모든 무기와 갑옷을 능숙하게 다루며, 전투 중 특별한 기동을 사용할 수 있습니다.',
    '도적': '교묘한 행동: 민첩성을 활용한 은밀한 공격과 함정 해제, 자물쇠 따기에 능숙합니다.',
    '성직자': '신성한 힘: 신성한 마법을 사용하여 치유하고 보호하며, 언데드를 물리칠 수 있습니다.',
    '음유시인': '바드의 영감: 음악을 통해 동료를 격려하고 적을 혼란시키는 마법적 효과를 만들어냅니다.',
    '연금술사': '물약 제조: 다양한 효과의 물약과 폭탄을 제조할 수 있는 지식이 있습니다.',
    '우주 파일럿': '우주선 조종: 어떤 종류의 우주선이든 능숙하게 조종하고 위험한 상황에서 탈출할 수 있습니다.',
    '사이버 해커': '시스템 침입: 컴퓨터 시스템과 보안 네트워크를 침투하고 조작할 수 있습니다.',
    '생체공학자': '생체 분석: 생명체의 생물학적 특성을 분석하고 수정할 수 있는 지식이 있습니다.',
    '보안 요원': '경계 태세: 항상 위험에 대비하여 경계 판정에 +2 보너스를 받습니다.',
    '외계종족 전문가': '외계어 이해: 다양한 외계 언어를 해석하고 의사소통할 수 있습니다.',
    '기계공학자': '장치 수리: 복잡한 기계와 장치를 수리하고 개선할 수 있는 지식이 있습니다.',
    '정보 브로커': '정보망: 유용한 정보를 찾거나 거래하는데 탁월한 능력이 있습니다.',
    '밀수업자': '은밀한 운송: 물건을 숨기고 감시를 피해 운반하는 기술이 있습니다.',
    '저항군 요원': '게릴라 전술: 열세한 상황에서도 효과적으로 전투하고 은신할 수 있습니다.',
    '엘리트 경비원': '경계 태세: 보안 시스템을 이해하고 침입자를 감지하는 능력이 뛰어납니다.',
    '스카운터': '지형 탐색: 위험한 지형을 안전하게 탐색하고 자원을 찾아낼 수 있습니다.',
    '의료 기술자': '응급 처치: 위급한 상황에서 부상을 치료하고 생명을 구할 수 있습니다.'
}

# 배경 태그 색상
BACKGROUND_TAGS_COLORS = {
    "영웅적": "#4CAF50",  # 녹색
    "비극적": "#F44336",  # 빨간색
    "신비로운": "#9C27B0",  # 보라색
    "학자": "#2196F3",  # 파란색
    "범죄자": "#FF9800",  # 주황색
    "전사": "#795548",  # 갈색
    "귀족": "#FFC107",  # 노란색
    "서민": "#607D8B",  # 회색
    "이방인": "#009688",  # 청록색
    "운명적": "#E91E63"   # 분홍색
}



def generate_professions(theme):
    """
    테마에 따른 직업 목록 반환
    
    Args:
        theme (str): 세계관 테마
        
    Returns:
        list: 직업 목록
    """
    professions = {
        'fantasy': ['마법사', '전사', '도적', '성직자', '음유시인', '연금술사'],
        'sci-fi': ['우주 파일럿', '사이버 해커', '생체공학자', '보안 요원', '외계종족 전문가', '기계공학자'],
        'dystopia': ['정보 브로커', '밀수업자', '저항군 요원', '엘리트 경비원', '스카운터', '의료 기술자']
    }
    return professions.get(theme, ['모험가', '전문가', '기술자'])

def generate_races(theme):
    """
    테마에 따른 종족 목록 반환
    
    Args:
        theme (str): 세계관 테마
        
    Returns:
        list: 종족 목록
    """
    races = {
        'fantasy': ['인간', '엘프', '드워프', '하플링', '오크', '고블린', '드라코니안'],
        'sci-fi': ['인간', '안드로이드', '외계인 하이브리드', '변형 인류', '네뷸런', '크로노스피어', '우주 유목민'],
        'dystopia': ['인간', '변이체', '강화인류', '생체기계', '숙주', '정신감응자', '저항자']
    }
    return races.get(theme, ['인간', '비인간', '신비종족'])

def generate_character_options(profession, theme):
    """
    직업과 테마에 기반한 캐릭터 배경 옵션 생성
    
    Args:
        profession (str): 선택한 직업
        theme (str): 세계관 테마
        
    Returns:
        list: 배경 스토리 옵션 목록
    """
    prompt = f"""
    당신은 TRPG 게임 마스터입니다. '{theme}' 테마의 세계에서 '{profession}' 직업을 가진 
    캐릭터의 3가지 다른 배경 스토리 옵션을 한국어로 제안해주세요. 

    각 옵션은 다음 요소를 포함해야 합니다:

    ## 삼위일체 구조
    1. **배경 서사**: 캐릭터가 겪은 결정적 사건 3개
    2. **도덕적 축**: 선택을 규정하는 2가지 원칙
    3. **정체성 기반**: 타인에게 설명하는 5초 자기소개

    ## 개성화를 위한 요소
    - 캐릭터만의 독특한 특성이나 버릇
    - 관계망 (가족, 멘토, 적대자 등)
    - 물리적 특징이나 외형적 특성

    ## 직업 연계성
    - 이 캐릭터가 해당 직업을 가지게 된 이유
    - 직업 관련 전문 기술이나 지식

    각 옵션을 120단어 내외로 작성해주세요.
    모든 문장은 완결된 형태로 작성하세요.
    
    다음 형식으로 반환해주세요:
    
    #옵션 1:
    (첫 번째 배경 스토리)
    
    #옵션 2:
    (두 번째 배경 스토리)
    
    #옵션 3:
    (세 번째 배경 스토리)
    """
    
    from src.modules.ai_service import generate_gemini_text
    response = generate_gemini_text(prompt, 800)
    
    # 옵션 분리
    options = []
    current_option = ""
    for line in response.split('\n'):
        if line.startswith('#옵션') or line.startswith('# 옵션') or line.startswith('옵션'):
            if current_option:
                options.append(current_option.strip())
            current_option = ""
        else:
            current_option += line + "\n"
    
    if current_option:
        options.append(current_option.strip())
    
    # 옵션이 3개 미만이면 백업 옵션 추가
    while len(options) < 3:
        options.append(f"당신은 {profession}으로, 험난한 세계에서 살아남기 위해 기술을 연마했습니다. 특별한 재능을 가지고 있으며, 자신의 운명을 개척하고자 합니다.")
    
    return options[:3]  # 최대 3개까지만 반환

def extract_background_tags(background_text):
    """
    배경 텍스트에서 태그를 추출하는 함수
    
    Args:
        background_text (str): 배경 스토리 텍스트
        
    Returns:
        list: 추출된 태그 목록
    """
    tags = []
    keyword_map = {
        "영웅": "영웅적", "구원": "영웅적", "정의": "영웅적", 
        "비극": "비극적", "상실": "비극적", "슬픔": "비극적", "고통": "비극적",
        "신비": "신비로운", "마법": "신비로운", "초자연": "신비로운", 
        "학자": "학자", "연구": "학자", "지식": "학자", "서적": "학자",
        "범죄": "범죄자", "도둑": "범죄자", "불법": "범죄자", "암흑가": "범죄자",
        "전사": "전사", "전투": "전사", "군인": "전사", "검술": "전사",
        "귀족": "귀족", "왕족": "귀족", "부유": "귀족", "상류층": "귀족",
        "서민": "서민", "평민": "서민", "일반인": "서민", "농부": "서민",
        "이방인": "이방인", "외지인": "이방인", "여행자": "이방인", "이주민": "이방인",
        "운명": "운명적", "예언": "운명적", "선택받은": "운명적"
    }
    
    for keyword, tag in keyword_map.items():
        if keyword.lower() in background_text.lower() and tag not in tags:
            tags.append(tag)
    
    # 최대 3개 태그 제한
    return tags[:3] if tags else ["신비로운"]  # 기본 태그 추가

def extract_background_tags(background_text):
    """
    배경 텍스트에서 태그를 추출하는 함수
    
    Args:
        background_text (str): 배경 스토리 텍스트
        
    Returns:
        list: 추출된 태그 목록
    """
    tags = []
    keyword_map = {
        "영웅": "영웅적", "구원": "영웅적", "정의": "영웅적", 
        "비극": "비극적", "상실": "비극적", "슬픔": "비극적", "고통": "비극적",
        "신비": "신비로운", "마법": "신비로운", "초자연": "신비로운", 
        "학자": "학자", "연구": "학자", "지식": "학자", "서적": "학자",
        "범죄": "범죄자", "도둑": "범죄자", "불법": "범죄자", "암흑가": "범죄자",
        "전사": "전사", "전투": "전사", "군인": "전사", "검술": "전사",
        "귀족": "귀족", "왕족": "귀족", "부유": "귀족", "상류층": "귀족",
        "서민": "서민", "평민": "서민", "일반인": "서민", "농부": "서민",
        "이방인": "이방인", "외지인": "이방인", "여행자": "이방인", "이주민": "이방인",
        "운명": "운명적", "예언": "운명적", "선택받은": "운명적"
    }
    
    for keyword, tag in keyword_map.items():
        if keyword.lower() in background_text.lower() and tag not in tags:
            tags.append(tag)
    
    # 최대 3개 태그 제한
    return tags[:3] if tags else ["신비로운"]  # 기본 태그 추가

def get_stat_info(stat, value, profession):
    """
    스탯별 색상 및 설명 제공
    
    Args:
        stat (str): 능력치 코드
        value (int): 능력치 값
        profession (str): 직업
        
    Returns:
        tuple: (색상 코드, 설명 텍스트)
    """
    # 스탯별 색상 설정 (낮음 - 중간 - 높음)
    if value < 8:
        color = "#F44336"  # 빨강 (낮음)
        level = "낮음"
    elif value < 12:
        color = "#FFC107"  # 노랑 (보통)
        level = "보통"
    elif value < 16:
        color = "#4CAF50"  # 초록 (높음)
        level = "높음"
    else:
        color = "#3F51B5"  # 파랑 (매우 높음)
        level = "매우 높음"
    
    # 직업별 스탯 적합성 설명
    if profession in PROFESSION_KEY_STATS and stat in PROFESSION_KEY_STATS[profession]:
        match = "핵심" if PROFESSION_KEY_STATS[profession][0] == stat else "중요"
        description = f"{level} - {match} 스탯"
    else:
        description = f"{level}"
    
    return color, description

def display_character_panel(character, location):
    """
    캐릭터 정보를 왼쪽 패널에 표시
    
    Args:
        character (dict): 캐릭터 정보
        location (str): 현재 위치
    """
    from modules.item_manager import display_inventory
    
    st.markdown("<div class='character-panel'>", unsafe_allow_html=True)
    st.write(f"## {character['profession']}")
    
    # 능력치 표시
    st.write("### 능력치")
    for stat, value in character['stats'].items():
        # 직업 정보 가져오기
        prof = character['profession']
        color, description = get_stat_info(stat, value, prof)
        
        st.markdown(f"""
        <div class='stat-box' style="border-left: 4px solid {color};">
            <span class='stat-name'>{stat}</span>
            <span class='stat-value'>{value}</span>
            <div style="font-size: 0.8rem; color: #aaaaaa; margin-top: 2px;">{description}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 인벤토리 표시
    st.write("### 인벤토리")
    display_inventory(character['inventory'])
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 위치 정보
    st.markdown(f"""
    <div class='location-box' style='margin-bottom: 15px; padding: 12px; background-color: #2d3748; border-radius: 5px; text-align: center;'>
        <h3 style='margin: 0; color: #e0e0ff;'>현재 위치</h3>
        <div style='font-size: 1.2rem; font-weight: bold; margin-top: 8px;'>{location}</div>
    </div>
    """, unsafe_allow_html=True)

def initialize_character(profession, backstory, stats, theme):
    """
    캐릭터 초기화 및 인벤토리 설정
    
    Args:
        profession (str): 직업
        backstory (str): 배경 스토리
        stats (dict): 능력치
        theme (str): 게임 테마
        
    Returns:
        dict: 초기화된 캐릭터 정보
    """
    # 아이템 객체 리스트로 인벤토리 초기화
    inventory = initialize_inventory(theme)
    
    character = {
        'profession': profession,
        'backstory': backstory,
        'stats': stats,
        'inventory': inventory,
        'special_trait': None
    }
    
    return character

def ability_roll_section(placeholder):
    """
    능력치 주사위 굴리기 기능
    
    Args:
        placeholder (st.empty): 결과를 표시할 플레이스홀더
    """
    # 주사위 굴리기 관련 상태 초기화
    if 'dice_rolled' not in st.session_state:
        st.session_state.dice_rolled = False
    
    if 'reroll_used' not in st.session_state:
        st.session_state.reroll_used = False
        
    # 주사위 굴리기 설명 추가
    placeholder.markdown("""
    <div style='background-color: #2a3549; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
        <p>능력치는 각각 3D6(6면체 주사위 3개) 방식으로 결정됩니다.</p>
        <p>각 능력치는 3~18 사이의 값을 가지며, 평균값은 10-11입니다.</p>
        <p>14 이상은 뛰어난 능력, 16 이상은 탁월한 능력입니다.</p>
        <p><strong>다시 굴리기는 1번만 가능합니다.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 주사위 굴리기 버튼
    if not st.session_state.dice_rolled and placeholder.button("주사위 굴리기", use_container_width=True, key="roll_ability_dice"):
        st.session_state.dice_rolled = True
        
        # 능력치 목록
        ability_names = ['STR', 'INT', 'DEX', 'CON', 'WIS', 'CHA']
        rolled_abilities = {}
        
        # 각 능력치별 주사위 굴리기 결과 애니메이션으로 표시
        ability_placeholders = {}
        for ability in ability_names:
            ability_placeholders[ability] = placeholder.empty()
        
        # 순차적으로 각 능력치 굴리기
        for ability in ability_names:
            # 3D6 주사위 결과 계산
            dice_rolls = [random.randint(1, 6) for _ in range(3)]
            total = sum(dice_rolls)
            
            # 결과 표시
            ability_placeholders[ability].markdown(f"""
            <div style='background-color: #1e2636; padding: 10px; border-radius: 5px; margin-bottom: 5px;'>
                <div style='display: flex; justify-content: space-between;'>
                    <span><strong>{ability}</strong></span>
                    <span>🎲 {dice_rolls[0]} + {dice_rolls[1]} + {dice_rolls[2]} = <strong>{total}</strong></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            rolled_abilities[ability] = total
        
        # 세션에 저장
        st.session_state.rolled_abilities = rolled_abilities
        st.rerun()

def generate_special_trait(theme, background_tags):
    """
    캐릭터의 특별한 특성 생성
    
    Args:
        theme (str): 게임 테마
        background_tags (list): 배경 태그 목록
        
    Returns:
        str: 생성된 특별한 특성
    """
    # 테마별 특성 목록
    fantasy_traits = [
        "마법에 대한 직관: 마법 관련 판정에 +1 보너스",
        "언어 재능: 하나의 추가 언어를 이해할 수 있음",
        "생존 본능: 위험 감지 판정에 +2 보너스",
        "전투 감각: 선제력 판정에 +1 보너스",
        "비밀 감지: 숨겨진 문이나 함정 찾기에 +2 보너스"
    ]
    
    scifi_traits = [
        "기계 친화력: 장치 조작 판정에 +1 보너스",
        "우주 적응: 저중력 환경 적응에 +2 보너스",
        "전술적 사고: 전투 전략 판정에 +1 보너스",
        "네트워크 감각: 정보 검색에 +2 보너스",
        "생체 회복: 휴식 시 추가 체력 회복"
    ]
    
    dystopia_traits = [
        "생존자 본능: 위험한 상황 탈출에 +1 보너스",
        "자원 절약: 소비품 사용 효율 +25%",
        "야간 시력: 어두운 곳에서 시각 판정에 불이익 없음",
        "불굴의 의지: 정신적 충격 저항에 +2 보너스",
        "전술적 직감: 교전 시 선제 행동 확률 +15%"
    ]
    
    # 태그에 따른 특성 선택 확률 조정
    has_hero = "영웅적" in background_tags
    has_scholarly = "학자" in background_tags
    has_tragic = "비극적" in background_tags
    has_criminal = "범죄자" in background_tags
    has_mysterious = "신비로운" in background_tags
    
    if theme == "fantasy":
        traits = fantasy_traits
        if has_hero:
            traits.append("운명의 보호: 하루에 한 번 치명적 공격을 일반 공격으로 낮출 수 있음")
        if has_scholarly:
            traits.append("비전학자: 마법 관련 지식 판정에 +2 보너스")
        if has_tragic:
            traits.append("고통의 힘: 체력이 절반 이하일 때 공격력 +1")
        if has_criminal:
            traits.append("그림자 걷기: 은신 판정에 +2 보너스")
        if has_mysterious:
            traits.append("신비한 직감: 하루에 한 번 주사위를 다시 굴릴 수 있음")
    elif theme == "sci-fi":
        traits = scifi_traits
        if has_hero:
            traits.append("영웅적 리더십: 아군 NPC 의사 결정에 영향력 +25%")
        if has_scholarly:
            traits.append("데이터 분석: 기술 장치 판독에 +2 보너스")
        if has_tragic:
            traits.append("역경의 경험: 위기 상황에서 판단력 +1")
        if has_criminal:
            traits.append("시스템 침투: 보안 해제 시도에 +2 보너스")
        if has_mysterious:
            traits.append("양자 직감: 확률적 사건 예측에 +15% 정확도")
    else:  # dystopia
        traits = dystopia_traits
        if has_hero:
            traits.append("불굴의 영웅: 동료를 보호하는 행동에 +2 보너스")
        if has_scholarly:
            traits.append("생존 지식: 자원 활용 효율 +20%")
        if has_tragic:
            traits.append("상실의 분노: 개인적 원한에 관련된 행동에 +2 보너스")
        if has_criminal:
            traits.append("암시장 연결망: 희귀 물품 거래 시 15% 할인")
        if has_mysterious:
            traits.append("통제 면역: 정신 조작 시도에 대한 저항 +25%")
    
    # 무작위 특성 선택
    return random.choice(traits)
