"""
캐릭터 생성 및 관리를 위한 유틸리티 모듈
"""
import random
import streamlit as st
import re
from modules.ai_service import generate_gemini_text
from modules.item_manager import initialize_inventory
from config.constants import PROFESSION_KEY_STATS, BACKGROUND_TAGS, ABILITY_NAMES

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