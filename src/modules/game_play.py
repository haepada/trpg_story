import streamlit as st
import random
import time
import re
from typing import Dict, List, Any, Tuple, Optional

from utils.dice_roller import roll_dice, display_dice_animation, calculate_dice_result
from utils.theme_manager import create_theme_image
from utils.location_manager import generate_locations, generate_movement_story
from modules.ai_service import (
    generate_action_suggestions, 
    master_answer_game_question, 
    generate_story_response
)
from modules.item_manager import (
    display_inventory, 
    extract_items_from_story,
    extract_used_items_from_story,
    update_inventory
)

def initialize_game_state():
    """게임 관련 상태 초기화"""
    # 게임 플레이 상태 초기화
    if 'story_log' not in st.session_state:
        st.session_state.story_log = []
    
    if 'action_phase' not in st.session_state:
        st.session_state.action_phase = 'suggestions'
    
    if 'suggestions_generated' not in st.session_state:
        st.session_state.suggestions_generated = False
    
    if 'dice_rolled' not in st.session_state:
        st.session_state.dice_rolled = False
    
    if 'action_submitted' not in st.session_state:
        st.session_state.action_submitted = False
    
    if 'action_processed' not in st.session_state:
        st.session_state.action_processed = False
    
    if 'ability_check_done' not in st.session_state:
        st.session_state.ability_check_done = False
    
    # 이동 관련 상태
    if 'move_submitted' not in st.session_state:
        st.session_state.move_submitted = False
    
    if 'move_processed' not in st.session_state:
        st.session_state.move_processed = False
    
    if 'move_destination' not in st.session_state:
        st.session_state.move_destination = ""
    
    # 아이템 알림 관련 상태
    if 'item_notification' not in st.session_state:
        st.session_state.item_notification = ""
    
    if 'show_item_notification' not in st.session_state:
        st.session_state.show_item_notification = False
    
    # 마스터 질문 상태
    if 'master_question_processing' not in st.session_state:
        st.session_state.master_question_processing = False
    
    if 'selected_master_question' not in st.session_state:
        st.session_state.selected_master_question = None
    
    if 'master_question_history' not in st.session_state:
        st.session_state.master_question_history = []

def display_game_play_page():
    """게임 플레이 페이지 전체 표시"""
    # 모바일 모드 확인
    mobile_mode = is_mobile()
    
    # 모바일 패널 상태 초기화
    if mobile_mode and 'mobile_panel' not in st.session_state:
        st.session_state.mobile_panel = "스토리"
    
    # 레이아웃 설정 - 모바일/데스크톱 모드에 따라 다르게
    if mobile_mode:
        # 모바일: 선택된 패널만 표시
        current_panel = st.session_state.mobile_panel
        
        if current_panel == "캐릭터 정보":
            # 캐릭터 정보 패널
            display_character_panel(st.session_state.character, st.session_state.current_location)
            
            # 아이템 알림 표시 (있을 경우)
            display_item_notification()
        
        elif current_panel == "게임 도구":
            # 게임 도구 패널
            display_game_tools()
        
        else:  # "스토리" (기본)
            # 스토리 영역
            display_story_and_actions()
    
    else:
        # 데스크톱: 3열 레이아웃
        game_col1, game_col2, game_col3 = st.columns([1, 2, 1])
        
        # 왼쪽 열 - 캐릭터 정보
        with game_col1:
            # 캐릭터 정보 패널
            display_character_panel(st.session_state.character, st.session_state.current_location)
            
            # 아이템 알림 표시 (있을 경우)
            display_item_notification()
        
        # 중앙 열 - 스토리 및 행동
        with game_col2:
            display_story_and_actions()
        
        # 오른쪽 열 - 게임 도구
        with game_col3:
            display_game_tools()

def is_mobile() -> bool:
    """현재 기기가 모바일인지 확인"""
    return st.session_state.get('is_mobile', False)

def display_character_panel(character: Dict[str, Any], location: str):
    """캐릭터 정보를 왼쪽 패널에 표시"""
    st.markdown("<div class='character-panel'>", unsafe_allow_html=True)
    st.write(f"## {character['profession']}")
    
    # 능력치 표시
    st.write("### 능력치")
    for stat, value in character['stats'].items():
        # 직업 정보 가져오기
        prof = character['profession']
        from modules.character_utils import get_stat_info
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

def display_item_notification():
    """아이템 관련 알림 표시"""
    if st.session_state.get('show_item_notification', False) and st.session_state.get('item_notification', ''):
        # 아이템 이름 강조를 위한 정규식 처리
        import re
        # 아이템 이름을 추출하여 강조 처리
        notification = st.session_state.item_notification
        
        # 아이템 이름 강조 처리 추가
        notification = re.sub(r"'([^']+)'", r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", notification)
        notification = re.sub(r'"([^"]+)"', r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", notification)
        notification = re.sub(r'\*\*([^*]+)\*\*', r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", notification)
        
        st.markdown(f"""
        <div class='item-notification' style="animation: pulse 2s infinite; background-color: #2a3549; padding: 18px; border-radius: 8px; margin: 18px 0; border-left: 8px solid #FFD700; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 2rem; margin-right: 15px;">🎁</div>
                <div style="font-size: 1.1rem;">{notification}</div>
            </div>
        </div>
        <style>
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0px rgba(255, 215, 0, 0.3); transform: scale(1); }}
            50% {{ box-shadow: 0 0 10px 3px rgba(255, 215, 0, 0.2); transform: scale(1.01); }}
            100% {{ box-shadow: 0 0 0 0px rgba(255, 215, 0, 0.3); transform: scale(1); }}
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # 알림을 표시한 후 초기화 (다음 번에 사라지게)
        st.session_state.show_item_notification = False
        
def display_story_and_actions():
    """스토리 로그와 플레이어 행동 관련 UI를 표시하는 함수"""
    st.header("모험의 이야기")
    
    # 마스터 메시지 표시
    st.markdown(f"<div class='master-text'>{st.session_state.master_message}</div>", unsafe_allow_html=True)
    
    # 스토리 로그가 있으면 표시
    if st.session_state.story_log:
        # 가장 최근 이야기는 강조하여 표시
        latest_story = st.session_state.story_log[-1]
        
        # 단락 구분 개선
        story_paragraphs = latest_story.split("\n\n")
        formatted_story = ""
        for para in story_paragraphs:
            # HTML 이스케이프 처리
            para = para.replace("<", "&lt;").replace(">", "&gt;")
            # 아이템 이름 강조 처리 추가
            para = re.sub(r"'([^']+)'", r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", para)
            para = re.sub(r'"([^"]+)"', r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", para)
            para = re.sub(r'\*\*([^*]+)\*\*', r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", para)
            # 중요 키워드 강조 처리 추가
            para = re.sub(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', r"<span style='color: #6b8afd; font-weight: bold;'>\1</span>", para)
            
            formatted_story += f"<p>{para}</p>\n"
        
        st.markdown(f"<div class='story-text'>{formatted_story}</div>", unsafe_allow_html=True)
            
        # 이전 이야기 표시 (접을 수 있는 형태)
        if len(st.session_state.story_log) > 1:
            with st.expander("이전 이야기", expanded=False):
                # 최신 것부터 역순으로 표시 (가장 최근 것 제외)
                for story in reversed(st.session_state.story_log[:-1]):
                    # 단락 구분 개선
                    prev_paragraphs = story.split("\n\n")
                    formatted_prev = ""
                    for para in prev_paragraphs:
                        # 아이템 이름 강조 처리 추가
                        para = re.sub(r"'([^']+)'", r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", para)
                        para = re.sub(r'"([^"]+)"', r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", para)
                        para = re.sub(r'\*\*([^*]+)\*\*', r"<span style='color: #FFD700; font-weight: bold;'>\1</span>", para)
                        # 중요 키워드 강조 처리 추가
                        para = re.sub(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', r"<span style='color: #6b8afd; font-weight: bold;'>\1</span>", para)
                        
                        formatted_prev += f"<p>{para}</p>\n"
                    
                    st.markdown(f"<div class='previous-story'>{formatted_prev}</div>", unsafe_allow_html=True)
    
    # 아이템 알림 표시 (있을 경우)
    display_item_notification()
    
    # 행동 단계 처리
    st.subheader("당신의 행동")
    
    # 행동 처리 함수 호출
    handle_action_phase()

def handle_action_phase():
    """행동 선택 및 처리 부분을 관리하는 함수"""
    # 행동 단계 관리
    action_phase = st.session_state.get('action_phase', 'suggestions')
    
    # 1. 이동 처리
    if action_phase == "moving":
        handle_movement()
    
    # 2. 능력치 판정 단계
    elif action_phase == "ability_check":
        handle_ability_check()
    
    # 3. 행동 제안 및 선택 단계
    elif action_phase == 'suggestions':
        handle_action_suggestions()
        
def handle_movement():
    """위치 이동 처리"""
    with st.spinner(f"{st.session_state.move_destination}(으)로 이동 중..."):
        # 로딩 표시
        loading_placeholder = st.empty()
        loading_placeholder.info(f"{st.session_state.move_destination}(으)로 이동하는 중... 잠시만 기다려주세요.")
        
        # 이동 스토리 생성
        movement_story = generate_movement_story(
            st.session_state.current_location,
            st.session_state.move_destination,
            st.session_state.theme
        )
        
        # 스토리 로그에 추가
        st.session_state.story_log.append(movement_story)
        
        # 현재 위치 업데이트
        st.session_state.current_location = st.session_state.move_destination
        
        # 이동 상태 초기화
        st.session_state.move_destination = ""
        st.session_state.action_phase = 'suggestions'
        st.session_state.suggestions_generated = False
        
        # 로딩 메시지 제거
        loading_placeholder.empty()
    
    st.rerun()

def handle_ability_check():
    """능력치 판정 과정을 처리하는 함수"""
    with st.spinner("주사위를 굴리고 있습니다..."):
        # 로딩 표시
        loading_placeholder = st.empty()
        loading_placeholder.info("주사위를 굴려 스토리의 진행을 판단하는 중... 잠시만 기다려주세요.")
    
    st.subheader("능력치 판정")
    
    # 행동 표시
    st.markdown(f"""
    <div style='background-color: #2a3549; padding: 15px; border-radius: 5px; margin: 10px 0;'>
        <h4 style='margin-top: 0; margin-bottom: 10px; color: #e0e0ff;'>선택한 행동:</h4>
        <p style='margin: 0;'>{st.session_state.current_action}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 마스터가 능력치와 난이도 제안
    if 'suggested_ability' not in st.session_state:
        with st.spinner("마스터가 판정 방식을 결정 중..."):
            # 행동 분석을 위한 프롬프트
            suggested_ability = suggest_ability_for_action(
                st.session_state.current_action,
                st.session_state.character['profession'],
                st.session_state.current_location
            )
            
            # 세션에 저장
            st.session_state.suggested_ability = suggested_ability
        
        st.rerun()
    
    # 마스터의 제안 표시 - 향상된 UI
    ability = st.session_state.suggested_ability
    st.markdown(f"""
    <div style='background-color: #2a3549; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #6b8afd;'>
        <h4 style='margin-top: 0;'>마스터의 판정 제안</h4>
        <div style='display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;'>
            <div style='flex: 1; min-width: 200px; background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px;'>
                <div style='font-weight: bold; margin-bottom: 5px; color: #6b8afd;'>능력치</div>
                <div style='font-size: 1.2rem;'>{ability['code']} ({ability['name']})</div>
            </div>
            <div style='flex: 1; min-width: 200px; background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px;'>
                <div style='font-weight: bold; margin-bottom: 5px; color: #FFC107;'>난이도</div>
                <div style='font-size: 1.2rem;'>{ability['difficulty']}</div>
            </div>
        </div>
        <div style='margin-top: 10px; background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px;'>
            <div style='font-weight: bold; margin-bottom: 5px;'>이유</div>
            <div>{ability['reason']}</div>
        </div>
        <div style='display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;'>
            <div style='flex: 1; min-width: 200px; background-color: rgba(76, 175, 80, 0.1); padding: 10px; border-radius: 5px; border-left: 3px solid #4CAF50;'>
                <div style='font-weight: bold; margin-bottom: 5px; color: #4CAF50;'>성공 시</div>
                <div>{ability['success_outcome']}</div>
            </div>
            <div style='flex: 1; min-width: 200px; background-color: rgba(244, 67, 54, 0.1); padding: 10px; border-radius: 5px; border-left: 3px solid #F44336;'>
                <div style='font-weight: bold; margin-bottom: 5px; color: #F44336;'>실패 시</div>
                <div>{ability['failure_outcome']}</div>
            </div>
        </div>
        <div style='margin-top: 10px; text-align: center; font-size: 0.9rem; color: #aaaaaa;'>
            추천 주사위: {ability.get('recommended_dice', '1d20')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
# 주사위 굴리기 자동 실행
    if not st.session_state.get('dice_rolled', False):
        # 주사위 애니메이션을 위한 플레이스홀더
        dice_placeholder = st.empty()
        
        # 주사위 표현식 결정
        dice_expression = ability.get('recommended_dice', "1d20")
        
        # 능력치 수정자 적용 (표현식에 이미 능력치가 포함되어 있지 않은 경우)
        ability_code = ability['code']
        ability_value = st.session_state.character['stats'][ability_code]
        
        if "+" not in dice_expression and "-" not in dice_expression:
            # 능력치 수정자 적용
            dice_expression = f"{dice_expression}+{ability_value}"
        
        with st.spinner("주사위 굴리는 중..."):
            # 주사위 굴리기 애니메이션 및 결과 표시
            dice_result = display_dice_animation(dice_placeholder, dice_expression, 1.0)
            
            st.session_state.dice_rolled = True
            st.session_state.dice_result = dice_result
    else:
        # 이미 굴린 주사위 결과 표시
        dice_placeholder = st.empty()
        dice_result = st.session_state.dice_result
    
    # 판정 결과 계산
    difficulty = ability['difficulty']
    success = dice_result['total'] >= difficulty
    
    # 결과 표시 (더 풍부하게 개선)
    result_color = "#1e3a23" if success else "#3a1e1e"
    result_border = "#4CAF50" if success else "#F44336"
    result_text = "성공" if success else "실패"
    outcome_text = ability['success_outcome'] if success else ability['failure_outcome']
    
    st.markdown(f"""
    <div style='background-color: {result_color}; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid {result_border};'>
        <h3 style='margin-top: 0;'>판정 결과: <span style='color: {result_border};'>{result_text}</span></h3>
        <div style='display: flex; align-items: center; margin: 10px 0;'>
            <div style='background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px; text-align: center; margin-right: 10px;'>
                <span style='font-size: 0.8rem;'>주사위 + 능력치</span>
                <div style='font-size: 1.2rem; font-weight: bold;'>{dice_result['total']}</div>
            </div>
            <div style='font-size: 1.5rem; margin: 0 10px;'>VS</div>
            <div style='background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px; text-align: center;'>
                <span style='font-size: 0.8rem;'>난이도</span>
                <div style='font-size: 1.2rem; font-weight: bold;'>{difficulty}</div>
            </div>
        </div>
        <div style='background-color: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px; margin-top: 10px;'>
            <p><strong>결과:</strong> {outcome_text}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 스토리 진행 버튼 - 더 매력적인 UI
    if st.button("스토리 진행", key="continue_story_button", use_container_width=True):
        handle_story_progression(
            st.session_state.current_action, 
            dice_result['total'], 
            success, 
            ability['code'], 
            difficulty
        )
        
    return success, dice_result['total'], ability['code'], dice_result['total'], difficulty

def suggest_ability_for_action(action: str, profession: str, location: str) -> Dict[str, Any]:
    """행동 분석 후 능력치 및 난이도 제안"""
    from modules.ai_service import get_ability_suggestion
    
    # AI 서비스에 능력치 제안 요청
    suggestion = get_ability_suggestion(action, profession, location)
    
    # 능력치 전체 이름 매핑
    ability_names = {
        'STR': '근력', 'INT': '지능', 'DEX': '민첩', 
        'CON': '체력', 'WIS': '지혜', 'CHA': '매력'
    }
    
    # 기본값 설정 (오류 방지)
    ability_code = suggestion.get('ability_code', 'STR')
    difficulty = suggestion.get('difficulty', 15)
    reason = suggestion.get('reason', '이 행동에는 능력이 필요합니다.')
    success_outcome = suggestion.get('success_outcome', '행동에 성공합니다.')
    failure_outcome = suggestion.get('failure_outcome', '행동에 실패합니다.')
    recommended_dice = suggestion.get('recommended_dice', '1d20')
    
    return {
        'code': ability_code,
        'name': ability_names.get(ability_code, ''),
        'difficulty': difficulty,
        'reason': reason,
        'success_outcome': success_outcome,
        'failure_outcome': failure_outcome,
        'recommended_dice': recommended_dice
    }
    
def handle_action_suggestions():
    """행동 제안 및 선택 처리"""
    st.subheader("행동 선택")
    
    # 위치 이동 옵션
    if 'available_locations' in st.session_state and len(st.session_state.available_locations) > 1:
        with st.expander("다른 장소로 이동", expanded=False):
            st.write("이동할 장소를 선택하세요:")
            
            # 현재 위치를 제외한 장소 목록 생성
            other_locations = [loc for loc in st.session_state.available_locations 
                              if loc != st.session_state.current_location]
            
            # 장소 버튼 표시
            location_cols = st.columns(2)
            for i, location in enumerate(other_locations):
                with location_cols[i % 2]:
                    if st.button(f"{location}로 이동", key=f"move_to_{i}", use_container_width=True):
                        st.session_state.move_destination = location
                        st.session_state.action_phase = 'moving'
                        st.rerun()
    
    # 행동 제안 표시
    if st.session_state.get('suggestions_generated', False):
        # 행동 제안 표시 (간소화된 방식)
        st.write("### 제안된 행동")
        for i, action in enumerate(st.session_state.action_suggestions):
            # 행동 유형 아이콘 결정
            if "[아이템 획득]" in action:
                icon = "🔍"
            elif "[아이템 사용]" in action:
                icon = "🧰"
            elif "[위험]" in action:
                icon = "⚠️"
            elif "[상호작용]" in action:
                icon = "💬"
            else:  # [일반]
                icon = "🔎"
            
            # 선택지 표시
            expander = st.expander(f"{icon} {action}")
            with expander:
                if st.button(f"이 행동 선택", key=f"action_{i}", use_container_width=True):
                    st.session_state.current_action = action
                    st.session_state.action_phase = 'ability_check'
                    # 초기화
                    st.session_state.dice_rolled = False
                    if 'dice_result' in st.session_state:
                        del st.session_state.dice_result
                    if 'suggested_ability' in st.session_state:
                        del st.session_state.suggested_ability
                    st.rerun()
        
        # 직접 행동 입력 옵션
        st.markdown("---")
        st.write("### 직접 행동 입력")
        custom_action = st.text_input("행동 설명:", key="custom_action_input")
        if st.button("실행", key="custom_action_button") and custom_action:
            # 행동 선택 시 주사위 굴림 상태 초기화
            st.session_state.current_action = custom_action
            st.session_state.action_phase = 'ability_check'
            # 초기화
            st.session_state.dice_rolled = False
            if 'dice_result' in st.session_state:
                del st.session_state.dice_result
            if 'suggested_ability' in st.session_state:
                del st.session_state.suggested_ability
            st.rerun()
    
    # 행동 제안 생성
    else:
        with st.spinner("마스터가 행동을 제안 중..."):
            # 로딩 표시
            loading_placeholder = st.empty()
            loading_placeholder.info("마스터가 행동을 제안하는 중... 잠시만 기다려주세요.")
            
            if st.session_state.story_log:
                last_entry = st.session_state.story_log[-1]
            else:
                last_entry = "모험의 시작"
            
            st.session_state.action_suggestions = generate_action_suggestions(
                st.session_state.current_location,
                st.session_state.theme,
                last_entry,
                st.session_state.character
            )
            st.session_state.suggestions_generated = True
            
            # 로딩 메시지 제거
            loading_placeholder.empty()
        
        st.rerun()

def display_game_tools():
    """게임 도구 및 옵션 UI 표시"""
    # 게임 정보 및 도구
    st.markdown("""
    <div style='background-color: #2a3549; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
        <h3 style='margin-top: 0; color: #e0e0ff;'>게임 도구</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 세계관 요약 표시
    with st.expander("세계관 요약", expanded=False):
        # 세계관에서 주요 부분만 추출해서 요약 표시
        world_desc = st.session_state.world_description
        # 200자 내외로 잘라내기
        summary = world_desc[:200] + "..." if len(world_desc) > 200 else world_desc
        
        # 단락 구분 적용
        summary_paragraphs = summary.split("\n\n")
        formatted_summary = ""
        for para in summary_paragraphs:
            formatted_summary += f"<p>{para}</p>\n"
            
        st.markdown(f"<div class='story-text'>{formatted_summary}</div>", unsafe_allow_html=True)
        
        # 전체 보기 버튼
        if st.button("세계관 전체 보기", key="view_full_world"):
            st.markdown("<div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-top: 10px;'>", unsafe_allow_html=True)
            
            # 단락 구분 적용
            world_paragraphs = world_desc.split("\n\n")
            formatted_world = ""
            for para in world_paragraphs:
                formatted_world += f"<p>{para}</p>\n"
            
            st.markdown(f"<div style='max-height: 300px; overflow-y: auto;'>{formatted_world}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # 마스터에게 질문
    st.markdown("""
    <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
        <h4 style='margin-top: 0; color: #e0e0ff;'>마스터에게 질문</h4>
    </div>
    """, unsafe_allow_html=True)
    
    display_master_question_ui()
    
    # 주사위 직접 굴리기 기능
    with st.expander("주사위 굴리기", expanded=False):
        dice_cols = st.columns(3)
        
        with dice_cols[0]:
            d6 = st.button("D6", use_container_width=True)
        with dice_cols[1]:
            d20 = st.button("D20", use_container_width=True)
        with dice_cols[2]:
            custom_dice = st.selectbox("커스텀", options=[4, 8, 10, 12, 100])
            roll_custom = st.button("굴리기", key="roll_custom")
        
        dice_result_placeholder = st.empty()
        
        if d6:
            result = random.randint(1, 6)
            dice_result_placeholder.markdown(f"<div class='dice-result'>🎲 {result}</div>", unsafe_allow_html=True)
        elif d20:
            result = random.randint(1, 20)
            dice_result_placeholder.markdown(f"<div class='dice-result'>🎲 {result}</div>", unsafe_allow_html=True)
        elif roll_custom:
            result = random.randint(1, custom_dice)
            dice_result_placeholder.markdown(f"<div class='dice-result'>🎲 {result}</div>", unsafe_allow_html=True)
    
    # 게임 관리 기능
    st.markdown("""
    <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-top: 20px;'>
        <h4 style='margin-top: 0; color: #e0e0ff;'>게임 관리</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # 세계관 설정화면으로 돌아가기
    if st.button("세계관 설정화면으로 돌아가기", use_container_width=True):
        st.warning("⚠️ 주의: 모든 게임 진행 상황이 초기화됩니다!")
        restart_confirm = st.radio(
            "정말 세계관 설정화면으로 돌아가시겠습니까? 모든 진행사항과 세계관이 초기화됩니다.",
            ["아니오", "예"]
        )
        
        if restart_confirm == "예":
            # 확인 버튼
            if st.button("확인 - 처음부터 다시 시작", key="final_restart_confirm"):
                # 게임 세션 완전 초기화
                from utils.session_manager import reset_game_session
                reset_game_session()
                st.success("첫 화면으로 돌아갑니다...")
                st.rerun()

def display_master_question_ui():
    """마스터에게 질문하는 UI 표시"""
    # 질문 제안 목록
    suggested_questions = [
        "이 지역의 위험 요소는 무엇인가요?",
        "주변에 어떤 중요한 인물이 있나요?",
        "이 장소에서 찾을 수 있는 가치 있는 것은?",
        "이 지역의 역사는 어떻게 되나요?",
        "현재 상황에서 가장 좋은 선택은?",
    ]
    
    # 질문 처리 상태 관리
    if 'master_question_processing' not in st.session_state:
        st.session_state.master_question_processing = False
    
    # 현재 선택된 질문 상태 관리
    if 'selected_master_question' not in st.session_state:
        st.session_state.selected_master_question = None
    
    # 제안된 질문 버튼 - 선택 시 시각적 피드백 개선
    with st.expander("제안된 질문", expanded=False):
        for i, q in enumerate(suggested_questions):
            # 선택된 질문인지 확인하고 스타일 변경
            is_selected = st.session_state.selected_master_question == q
            
            st.markdown(f"""
            <div style='background-color: {"#4CAF50" if is_selected else "#1e2636"}; 
                        padding: 10px; border-radius: 5px; margin-bottom: 10px;
                        border-left: 4px solid {"#FFFFFF" if is_selected else "#6b8afd"};'>
                <p style='margin: 0; color: {"#FFFFFF" if is_selected else "#e0e0ff"};'>
                    {q} {" ✓" if is_selected else ""}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"{'이 질문 선택됨 ✓' if is_selected else '선택'}", 
                         key=f"master_q_{i}", 
                         use_container_width=True,
                         disabled=is_selected):
                st.session_state.selected_master_question = q
                st.session_state.master_question_input = q  # 입력 필드에 자동 입력
                st.rerun()
    
    # 질문 입력 폼 - 상태 유지를 위해 form 사용
    with st.form(key="master_question_form"):
        # 선택된 질문이 있으면 입력 필드에 표시
        default_question = st.session_state.get('selected_master_question', '')
        master_question = st.text_input("질문:", value=default_question, key="master_question_input")
        
        # 로딩 중이면 버튼 비활성화
        submit_question = st.form_submit_button(
            "질문하기", 
            disabled=st.session_state.master_question_processing
        )
    
    # 질문이 제출되었을 때
    if submit_question and master_question:
        st.session_state.master_question_processing = True
        
        # 플레이스홀더 생성 - 응답을 표시할 위치
        response_placeholder = st.empty()
        response_placeholder.info("마스터가 답변을 작성 중입니다... 잠시만 기다려주세요.")
        
        with st.spinner("마스터가 응답 중..."):
            try:
                # 질문에 대한 답변 생성
                answer = master_answer_game_question(
                    master_question,
                    st.session_state.theme,
                    st.session_state.current_location,
                    st.session_state.world_description
                )
                
                # 마스터 응답을 세계관에 반영하되, 별도의 상태로 저장
                if 'master_question_history' not in st.session_state:
                    st.session_state.master_question_history = []
                
                st.session_state.master_question_history.append({
                    "question": master_question,
                    "answer": answer
                })
                
                # 세계관에 반영 (나중에 참조 가능)
                st.session_state.world_description += f"\n\n질문-{master_question}: {answer}"
                
                # 단락 구분 적용
                answer_paragraphs = answer.split("\n\n")
                formatted_answer = ""
                for para in answer_paragraphs:
                    formatted_answer += f"<p>{para}</p>\n"
                
                # 응답 표시 - 페이지 새로고침 없이 표시
                response_placeholder.markdown(f"""
                <div style='background-color: #2d3748; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #6b8afd;'>
                    <div style='font-weight: bold; margin-bottom: 5px;'>질문: {master_question}</div>
                    <div>{formatted_answer}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 선택된 질문 초기화
                st.session_state.selected_master_question = None
            
            except Exception as e:
                st.error(f"응답 생성 중 오류가 발생했습니다: {e}")
                response_placeholder.error("질문 처리 중 오류가 발생했습니다. 다시 시도해주세요.")
            
            finally:
                # 처리 완료 상태로 변경
                st.session_state.master_question_processing = False
    
    # 질문 기록 표시
    if 'master_question_history' in st.session_state and st.session_state.master_question_history:
        with st.expander("이전 질문 기록"):
            for i, qa in enumerate(st.session_state.master_question_history):
                st.markdown(f"**Q{i+1}:** {qa['question']}")
                
                # 단락 구분 적용
                answer_paragraphs = qa['answer'].split("\n\n")
                formatted_answer = ""
                for para in answer_paragraphs:
                    formatted_answer += f"<p>{para}</p>\n"
                    
                st.markdown(f"**A:** <div>{formatted_answer}</div>", unsafe_allow_html=True)
                st.markdown("---")
                
