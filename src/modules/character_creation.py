import streamlit as st
import random
import time
from typing import Dict, List, Any, Tuple, Optional

from config.constants import STATS_NAMES
from utils.dice_roller import roll_dice, display_dice_animation
from modules.ai_service import generate_character_options
from modules.character_utils import extract_background_tags, get_stat_info

def initialize_character_creation_state():
    """캐릭터 생성 관련 상태 초기화"""
    if 'character_creation_step' not in st.session_state:
        st.session_state.character_creation_step = 'race'
    
    if 'background_options_generated' not in st.session_state:
        st.session_state.background_options_generated = False
    
    if 'dice_rolled' not in st.session_state:
        st.session_state.dice_rolled = False
    
    if 'reroll_used' not in st.session_state:
        st.session_state.reroll_used = False

def display_character_creation_page():
    """캐릭터 생성 페이지 전체 표시"""
    st.header("2️⃣ 캐릭터 생성")
    
    # 마스터 메시지 표시
    st.markdown(f"<div class='master-text'>{st.session_state.master_message}</div>", unsafe_allow_html=True)
    
    # 상태 초기화
    initialize_character_creation_state()
    
    # 현재 단계에 따라 다른 UI 표시
    if st.session_state.character_creation_step == 'race':
        display_race_selection()
    elif st.session_state.character_creation_step == 'profession':
        display_profession_selection()
    elif st.session_state.character_creation_step == 'background':
        display_background_selection()
    elif st.session_state.character_creation_step == 'abilities':
        display_abilities_selection()
    elif st.session_state.character_creation_step == 'review':
        display_character_review()

def display_race_selection():
    """종족 선택 UI"""
    st.subheader("종족 선택")
    
    # 종족 선택 설명 추가
    st.markdown("""
    <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
        <p>캐릭터의 종족은 당신의 모험에 큰 영향을 미칩니다. 각 종족은 고유한 특성과 문화적 배경을 가지고 있습니다.</p>
        <p>종족에 따라 특정 능력치에 보너스가 부여될 수 있으며, 스토리텔링에도 영향을 줍니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 종족 목록 가져오기
    from modules.character_utils import generate_races
    races = generate_races(st.session_state.theme)
    
    # 종족별 아이콘 매핑
    from modules.character_utils import RACE_ICONS, RACE_BONUSES, RACE_ABILITIES, RACE_DESCRIPTIONS
    
    # 종족 선택 버튼 표시 (개선된 카드 형식)
    race_cols = st.columns(3)
    for i, race in enumerate(races):
        with race_cols[i % 3]:
            icon = RACE_ICONS.get(race, '👤')  # 기본 아이콘
            bonus = RACE_BONUSES.get(race, {'??': '+?'})  # 기본 보너스
            ability = RACE_ABILITIES.get(race, '특수 능력 없음')  # 기본 특수 능력
            
            # 종족 카드 생성 (개선된 UI)
            st.markdown(f"""
            <div class='option-card' style='padding: 15px; position: relative;'>
                <div style='position: absolute; top: 10px; right: 10px; font-size: 2rem;'>{icon}</div>
                <h3 style='margin-bottom: 10px;'>{race}</h3>
                <div style='margin-top: 10px; font-size: 0.9rem;'>
                    <strong>능력치 보너스:</strong> <br>
                    {"<br>".join([f"{k}: {v}" for k, v in bonus.items()])}
                </div>
                <div style='margin-top: 10px; font-size: 0.9rem;'>
                    <strong>특수 능력:</strong> <br>
                    {ability}
                </div>
            """, unsafe_allow_html=True)
            
            # 종족별 간단한 설명
            if race in RACE_DESCRIPTIONS:
                st.markdown(f"""
                <div style='margin-top: 10px; font-size: 0.9rem; color: #aaaaaa;'>
                    {RACE_DESCRIPTIONS[race]}
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.button(f"선택", key=f"race_{race}"):
                st.session_state.selected_race = race
                st.session_state.race_bonus = bonus
                st.session_state.race_ability = ability
                st.session_state.race_icon = icon
                st.session_state.character_creation_step = 'profession'
                st.session_state.master_message = f"{race} 종족을 선택하셨군요! 이제 당신의 직업을 선택해보세요."
                st.rerun()
    
    # 직접 입력 옵션
    st.markdown("<div class='option-card'>", unsafe_allow_html=True)
    st.write("### 다른 종족 직접 입력")
    st.write("원하는 종족이 목록에 없다면, 직접 입력할 수 있습니다.")
    custom_race = st.text_input("종족 이름:")
    custom_icon = st.selectbox("아이콘 선택:", ['👤', '🧙', '🧝', '🧟', '👻', '👽', '🤖', '🦊', '🐲', '🌟'])
    
    # 능력치 보너스 선택 (최대 2개)
    st.write("능력치 보너스 선택 (최대 2개):")
    bonus_cols = st.columns(3)
    
    all_stats = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
    custom_bonuses = {}
    
    for i, stat in enumerate(all_stats):
        with bonus_cols[i % 3]:
            bonus_value = st.selectbox(f"{stat} 보너스:", ['+0', '+1', '+2'], key=f"custom_bonus_{stat}")
            if bonus_value != '+0':
                custom_bonuses[stat] = bonus_value
    
    # 특수 능력 입력
    custom_ability = st.text_area("특수 능력 (선택사항):", 
                                  placeholder="예: 어둠 속에서도 잘 볼 수 있는 능력")
    
    if custom_race and st.button("이 종족으로 선택"):
        st.session_state.selected_race = custom_race
        st.session_state.race_bonus = custom_bonuses if custom_bonuses else {'없음': '+0'}
        st.session_state.race_ability = custom_ability if custom_ability else "특수 능력 없음"
        st.session_state.race_icon = custom_icon
        st.session_state.character_creation_step = 'profession'
        st.session_state.master_message = f"{custom_race} 종족을 선택하셨군요! 이제 당신의 직업을 선택해보세요."
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    def display_profession_selection():
    """직업 선택 UI"""
    st.subheader("직업 선택")
    
    # 직업 선택 설명 추가
    st.markdown("""
    <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
        <p>직업은 캐릭터가 세계에서 수행하는 역할과 전문 기술을 결정합니다.</p>
        <p>각 직업마다 중요한 능력치가 다르며, 독특한 기술과 성장 경로를 가집니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 선택된 종족 표시 (개선된 UI)
    race_icon = st.session_state.get('race_icon', '👤')
    race_bonuses = st.session_state.get('race_bonus', {})
    race_ability = st.session_state.get('race_ability', "특수 능력 없음")
    
    st.markdown(f"""
    <div style='background-color: #2a3549; padding: 15px; border-radius: 5px; margin-bottom: 15px; display: flex; align-items: center;'>
        <div style='font-size: 2.5rem; margin-right: 15px;'>{race_icon}</div>
        <div style='flex-grow: 1;'>
            <h3 style='margin: 0; color: #4CAF50;'>선택한 종족: {st.session_state.selected_race}</h3>
            <div style='margin-top: 5px; font-size: 0.9rem;'>
                <strong>능력치 보너스:</strong> {', '.join([f"{k} {v}" for k, v in race_bonuses.items()])}
            </div>
            <div style='margin-top: 5px; font-size: 0.9rem;'>
                <strong>특수 능력:</strong> {race_ability}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 직업 선택 방식
    profession_method = st.radio(
        "직업 선택 방식:",
        ["기본 직업 선택", "직접 직업 만들기"],
        horizontal=True
    )
    
    if profession_method == "기본 직업 선택":
        # 직업 목록 가져오기
        from modules.character_utils import generate_professions
        professions = generate_professions(st.session_state.theme)
        
        # 직업별 아이콘 및 정보 가져오기
        from modules.character_utils import (
            PROFESSION_ICONS, PROFESSION_STATS, 
            PROFESSION_EQUIPMENT, PROFESSION_SKILLS
        )
        
        # 직업 선택 버튼 표시 (개선된 카드 형식)
        profession_cols = st.columns(3)
        for i, profession in enumerate(professions):
            with profession_cols[i % 3]:
                icon = PROFESSION_ICONS.get(profession, '👤')  # 기본 아이콘
                key_stats = PROFESSION_STATS.get(profession, ['??', '??'])  # 주요 능력치
                equipment = PROFESSION_EQUIPMENT.get(profession, ['기본 장비'])  # 시작 장비
                skill = PROFESSION_SKILLS.get(profession, '특수 기술 없음')  # 특수 기술
                
                # 직업 카드 생성 (개선된 UI)
                st.markdown(f"""
                <div class='option-card' style='padding: 15px; position: relative;'>
                    <div style='position: absolute; top: 10px; right: 10px; font-size: 2rem;'>{icon}</div>
                    <h3 style='margin-bottom: 10px;'>{profession}</h3>
                    <div style='margin-top: 10px; font-size: 0.9rem;'>
                        <strong>주요 능력치:</strong> {' & '.join(key_stats)}
                    </div>
                    <div style='margin-top: 10px; font-size: 0.9rem;'>
                        <strong>시작 장비:</strong>
                        <ul style='margin-top: 5px; padding-left: 20px; margin-bottom: 5px;'>
                            {"".join([f"<li>{item}</li>" for item in equipment[:3]])}
                            {"" if len(equipment) <= 3 else "<li>...</li>"}
                        </ul>
                    </div>
                    <div style='margin-top: 10px; font-size: 0.9rem;'>
                        <strong>특수 기술:</strong> <br>
                        {skill}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"선택", key=f"prof_{profession}"):
                    st.session_state.selected_profession = profession
                    st.session_state.profession_icon = icon
                    st.session_state.profession_stats = key_stats
                    st.session_state.profession_equipment = equipment
                    st.session_state.profession_skill = skill
                    
                    # 배경 옵션 생성 상태 확인
                    if not st.session_state.background_options_generated:
                        with st.spinner("캐릭터 배경 옵션을 생성 중..."):
                            st.session_state.character_backgrounds = generate_character_options(
                                profession, st.session_state.theme
                            )
                            st.session_state.background_options_generated = True
                    
                    st.session_state.character_creation_step = 'background'
                    st.session_state.master_message = f"{profession} 직업을 선택하셨군요! 이제 캐릭터의 배경 이야기를 선택해보세요."
                    st.rerun()
    else:  # 직접 직업 만들기
        st.markdown("<div class='option-card'>", unsafe_allow_html=True)
        st.write("### 나만의 직업 만들기")
        st.write("세계관에 맞는 독특한 직업을 직접 만들어보세요")
        custom_profession = st.text_input("직업 이름:")
        custom_icon = st.selectbox("아이콘 선택:", ['🧙', '⚔️', '🗡️', '🧪', '📚', '🔮', '🎭', '⚗️', '🛡️', '🚀', '💻', '🧬', '👽', '⚙️', '📡', '📦', '💉', '🔭'])
        
        # 주요 능력치 선택 (최대 2개)
        st.write("주요 능력치 선택 (최대 2개):")
        stat_cols = st.columns(3)
        
        all_stats = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
        selected_stats = []
        
        for i, stat in enumerate(all_stats):
            with stat_cols[i % 3]:
                if st.checkbox(f"{stat}", key=f"custom_prof_stat_{stat}"):
                    selected_stats.append(stat)
        
        # 3개 이상 선택 시 경고
        if len(selected_stats) > 2:
            st.warning("주요 능력치는 최대 2개까지만 선택할 수 있습니다. 처음 2개만 적용됩니다.")
            selected_stats = selected_stats[:2]
        elif len(selected_stats) == 0:
            st.info("주요 능력치를 1~2개 선택하세요.")
        
        # 시작 장비 입력
        st.write("시작 장비 (콤마로 구분):")
        equipment_input = st.text_area("예: 검, 방패, 물약 3개", height=100)
        
        # 특수 기술 입력
        special_skill = st.text_input("특수 기술 (예: 숨기: 은신 판정에 +2 보너스):")
        
        # 직업 설명
        profession_desc = st.text_area("직업 설명:", 
                                      placeholder="이 직업의 역할, 행동 방식, 세계관에서의 위치 등을 설명해주세요.",
                                      height=100)
        
        if st.button("이 직업으로 선택", use_container_width=True):
            if custom_profession and len(selected_stats) > 0 and special_skill:
                # 사용자 정의 직업 정보 저장
                st.session_state.selected_profession = custom_profession
                st.session_state.profession_icon = custom_icon
                st.session_state.profession_stats = selected_stats
                
                # 장비 파싱
                equipment_list = [item.strip() for item in equipment_input.split(',') if item.strip()]
                if not equipment_list:
                    equipment_list = ["기본 장비"]
                st.session_state.profession_equipment = equipment_list
                
                st.session_state.profession_skill = special_skill
                st.session_state.profession_description = profession_desc
                
                # 배경 옵션 생성 상태 확인
                if not st.session_state.background_options_generated:
                    with st.spinner("캐릭터 배경 옵션을 생성 중..."):
                        st.session_state.character_backgrounds = generate_character_options(
                            custom_profession, st.session_state.theme
                        )
                        st.session_state.background_options_generated = True
                
                st.session_state.character_creation_step = 'background'
                st.session_state.master_message = f"{custom_profession} 직업을 선택하셨군요! 이제 캐릭터의 배경 이야기를 선택해보세요."
                st.rerun()
            else:
                st.error("직업 이름, 최소 1개의 주요 능력치, 특수 기술은 필수 입력사항입니다.")
        st.markdown("</div>", unsafe_allow_html=True)
        
def display_abilities_selection():
    """능력치 설정 UI"""
    st.subheader("능력치 설정")
    
    # 능력치 설정 설명 추가
    st.markdown("""
    <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
        <p>능력치는 캐릭터의 신체적, 정신적 역량을 수치화한 것입니다.</p>
        <p>주사위를 굴려 결정하거나, 기본값을 사용할 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 선택된 종족, 직업, 배경 태그 표시 (개선된 UI)
    race_icon = st.session_state.get('race_icon', '👤')
    profession_icon = st.session_state.get('profession_icon', '👤')
    key_stats = st.session_state.get('profession_stats', ['??', '??'])
    race_bonuses = st.session_state.get('race_bonus', {})
    bg_tags = st.session_state.get('background_tags', ["신비로운"])
    
    # 태그 표시용 HTML 생성
    tags_html = ""
    from modules.character_utils import BACKGROUND_TAGS_COLORS
    for tag in bg_tags:
        tag_color = BACKGROUND_TAGS_COLORS.get(tag, "#607D8B")  # 기본값은 회색
        tags_html += f"""
        <span style='background-color: {tag_color}; color: white; 
                   padding: 3px 8px; border-radius: 12px; font-size: 0.8rem; 
                   margin-right: 5px; display: inline-block;'>
            {tag}
        </span>
        """
        
    # 캐릭터 요약 표시
    st.markdown(f"""
    <div style='background-color: #2a3549; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
        <div style='display: flex; flex-wrap: wrap; align-items: center; margin-bottom: 10px;'>
            <div style='font-size: 2.5rem; margin-right: 15px;'>{race_icon}</div>
            <div style='flex-grow: 1; margin-right: 15px;'>
                <h3 style='margin: 0; color: #4CAF50;'>{st.session_state.selected_race} {st.session_state.selected_profession}</h3>
                <div style='font-size: 0.9rem; margin-top: 5px;'>
                    {tags_html}
                </div>
            </div>
            <div style='font-size: 2.5rem;'>{profession_icon}</div>
        </div>
        <div style='display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;'>
            <div style='flex: 1; min-width: 200px; background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px;'>
                <div style='font-weight: bold; margin-bottom: 5px;'>핵심 능력치</div>
                <div>{"・".join(key_stats)}</div>
            </div>
            <div style='flex: 1; min-width: 200px; background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px;'>
                <div style='font-weight: bold; margin-bottom: 5px;'>종족 보너스</div>
                <div>{"・".join([f"{k} {v}" for k, v in race_bonuses.items()])}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    ability_col1, ability_col2 = st.columns([3, 1])
    
    with ability_col1:
        # 능력치 설정 방법 선택
        ability_method = st.radio(
            "능력치 설정 방법:",
            ["3D6 주사위 굴리기", "기본 능력치 사용"],
            horizontal=True
        )
        
        if ability_method == "3D6 주사위 굴리기":
            ability_roll_section()
        else:  # 기본 능력치 사용
            base_abilities_section()
    
    with ability_col2:
        # 능력치 설명 및 정보 표시
        st.markdown("""
        <div style='background-color: #1e2636; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0;'>능력치 정보</h4>
            <table style='width: 100%; font-size: 0.9rem;'>
                <tr><td><strong>STR</strong></td><td>근력, 물리적 공격력</td></tr>
                <tr><td><strong>DEX</strong></td><td>민첩성, 회피/정확도</td></tr>
                <tr><td><strong>CON</strong></td><td>체력, 생존력</td></tr>
                <tr><td><strong>INT</strong></td><td>지능, 마법/기술 이해력</td></tr>
                <tr><td><strong>WIS</strong></td><td>지혜, 직관/인식력</td></tr>
                <tr><td><strong>CHA</strong></td><td>매력, 설득력/교섭력</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # 능력치 점수 해석
        st.markdown("""
        <div style='background-color: #1e2636; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
            <h4 style='margin-top: 0;'>능력치 점수 해석</h4>
            <table style='width: 100%; font-size: 0.9rem;'>
                <tr><td>1-3</td><td>심각한 약점</td></tr>
                <tr><td>4-6</td><td>약함</td></tr>
                <tr><td>7-9</td><td>평균 이하</td></tr>
                <tr><td>10-12</td><td>평균적</td></tr>
                <tr><td>13-15</td><td>평균 이상</td></tr>
                <tr><td>16-17</td><td>매우 뛰어남</td></tr>
                <tr><td>18+</td><td>전설적 수준</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # 배경 요약
        st.markdown("""
        <div style='background-color: #1e2636; padding: 10px; border-radius: 5px;'>
            <h4 style='margin-top: 0;'>배경 요약</h4>
            <div style='max-height: 200px; overflow-y: auto; font-size: 0.9rem;'>
        """, unsafe_allow_html=True)
        
        # 배경 텍스트에서 중요 부분만 추출 (첫 200자)
        bg_summary = st.session_state.selected_background[:200]
        if len(st.session_state.selected_background) > 200:
            bg_summary += "..."
            
        st.markdown(f"{bg_summary}", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # 뒤로 가기 옵션
    if st.button("← 배경 선택으로 돌아가기", use_container_width=True):
        st.session_state.character_creation_step = 'background'
        
        # 주사위 굴리기 관련 상태 초기화
        if 'dice_rolled' in st.session_state:
            del st.session_state.dice_rolled
        if 'reroll_used' in st.session_state:
            del st.session_state.reroll_used
        if 'rolled_abilities' in st.session_state:
            del st.session_state.rolled_abilities
            
        st.session_state.master_message = "배경을 다시 선택해 보세요!"
        st.rerun()

def ability_roll_section():
    """주사위 굴리기로 능력치 결정하는 UI 섹션"""
    # 주사위 굴리기 관련 상태 초기화
    if 'dice_rolled' not in st.session_state:
        st.session_state.dice_rolled = False
    
    if 'reroll_used' not in st.session_state:
        st.session_state.reroll_used = False
        
    # 주사위 굴리기 설명 추가
    st.markdown("""
    <div style='background-color: #2a3549; padding: 10px; border-radius: 5px; margin-bottom: 15px;'>
        <p>능력치는 각각 3D6(6면체 주사위 3개) 방식으로 결정됩니다.</p>
        <p>각 능력치는 3~18 사이의 값을 가지며, 평균값은 10-11입니다.</p>
        <p>14 이상은 뛰어난 능력, 16 이상은 탁월한 능력입니다.</p>
        <p><strong>다시 굴리기는 1번만 가능합니다.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 주사위 굴리기 버튼
    if not st.session_state.dice_rolled and st.button("주사위 굴리기", use_container_width=True, key="roll_ability_dice"):
        st.session_state.dice_rolled = True
        
        # 능력치 목록
        ability_names = ['STR', 'INT', 'DEX', 'CON', 'WIS', 'CHA']
        rolled_abilities = {}
        
        # 각 능력치별 주사위 굴리기 결과 애니메이션으로 표시
        ability_placeholders = {}
        for ability in ability_names:
            ability_placeholders[ability] = st.empty()
        
        # 순차적으로 각 능력치 굴리기
        for ability in ability_names:
            with st.spinner(f"{ability} 굴리는 중..."):
                # 주사위 애니메이션 표시
                dice_result = display_dice_animation(ability_placeholders[ability], "3d6", 0.5)
                rolled_abilities[ability] = dice_result['total']
                time.sleep(0.2)  # 약간의 딜레이
        
        # 세션에 저장
        st.session_state.rolled_abilities = rolled_abilities
        st.rerun()
    
    # 굴린 결과 표시
    if st.session_state.dice_rolled and 'rolled_abilities' in st.session_state:
        st.write("#### 주사위 결과:")
        cols = st.columns(3)
        i = 0
        
        # 직업 정보를 미리 가져옴
        prof = st.session_state.selected_profession if 'selected_profession' in st.session_state else ""
        
        # 직업별 중요 능력치 정보
        profession_key_stats = st.session_state.get('profession_stats', [])
        
        # 능력치 총점 계산 (나중에 보여주기 위함)
        total_points = sum(st.session_state.rolled_abilities.values())
        
        # 결과를 정렬하여 먼저 중요 능력치를 표시
        sorted_abilities = sorted(
            st.session_state.rolled_abilities.items(),
            key=lambda x: (x[0] not in profession_key_stats, profession_key_stats.index(x[0]) if x[0] in profession_key_stats else 999)
        )
        
        for ability, value in sorted_abilities:
            with cols[i % 3]:
                # 직업에 중요한 능력치인지 확인
                is_key_stat = ability in profession_key_stats
                
                # 색상 및 설명 가져오기
                color, description = get_stat_info(ability, value, prof)
                
                # 중요 능력치 강조 스타일
                highlight = "border: 2px solid gold; background-color: rgba(255, 215, 0, 0.1);" if is_key_stat else ""
                key_badge = "<span style='background-color: #FFD700; color: #000; padding: 1px 5px; border-radius: 3px; font-size: 0.7rem; margin-left: 5px;'>핵심</span>" if is_key_stat else ""
                
                # 능력치 값에 따른 바 그래프 너비 계산 (백분율, 최대 18 기준)
                bar_width = min(100, (value / 18) * 100)
                
                # 개선된 능력치 표시
                st.markdown(f"""
                <div class='stat-box' style="border-left: 4px solid {color}; {highlight}">
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span class='stat-name'>{ability}{key_badge}</span>
                        <span class='stat-value'>{value}</span>
                    </div>
                    <div style='margin-top: 5px; background-color: #1e2636; height: 8px; border-radius: 4px;'>
                        <div style='background-color: {color}; width: {bar_width}%; height: 100%; border-radius: 4px;'></div>
                    </div>
                    <div style="font-size: 0.8rem; color: #aaaaaa; margin-top: 5px;">{description}</div>
                </div>
                """, unsafe_allow_html=True)
            i += 1
        
        # 능력치 총점 표시
        avg_total = 63  # 3D6 6개의 평균
        
        # 총점 평가 (낮음, 평균, 높음)
        if total_points < avg_total - 5:
            total_rating = "낮음"
            total_color = "#F44336"  # 빨간색
        elif total_points > avg_total + 5:
            total_rating = "높음"
            total_color = "#4CAF50"  # 녹색
        else:
            total_rating = "평균"
            total_color = "#FFC107"  # 노란색
        
        st.markdown(f"""
        <div style='background-color: #2a3549; padding: 10px; border-radius: 5px; margin: 15px 0; text-align: center;'>
            <div style='font-weight: bold;'>능력치 총점:</div>
            <div style='display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 5px;'>
                <span style='color: {total_color}; font-size: 1.5rem; font-weight: bold;'>{total_points}</span>
                <span style='background-color: {total_color}; color: black; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem;'>{total_rating}</span>
            </div>
            <div style='font-size: 0.8rem; margin-top: 5px;'>(평균 63, 70+ 우수, 80+ 탁월)</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 버튼 열 생성
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이 능력치로 진행하기", use_container_width=True, key="use_these_stats"):
                st.session_state.character['stats'] = st.session_state.rolled_abilities
                st.session_state.character['profession'] = st.session_state.selected_profession
                st.session_state.character['race'] = st.session_state.selected_race
                st.session_state.character['backstory'] = st.session_state.selected_background
                st.session_state.character_creation_step = 'review'
                st.session_state.master_message = "좋습니다! 캐릭터가 거의 완성되었습니다. 최종 확인을 해 볼까요?"
                
                # 다시 굴리기 관련 상태 초기화
                st.session_state.dice_rolled = False
                st.session_state.reroll_used = False
                st.rerun()
        
        with col2:
            # 다시 굴리기 버튼 - 한번만 사용 가능하도록 제한
            if st.button("다시 굴리기", 
                        use_container_width=True, 
                        key="reroll_ability_dice",
                        disabled=st.session_state.reroll_used):
                if not st.session_state.reroll_used:
                    # 다시 굴리기 사용 표시
                    st.session_state.reroll_used = True
                    
                    # 능력치 목록
                    ability_names = ['STR', 'INT', 'DEX', 'CON', 'WIS', 'CHA']
                    rerolled_abilities = {}
                    
                    # 각 능력치별 재굴림 결과 표시
                    reroll_placeholders = {}
                    for ability in ability_names:
                        reroll_placeholders[ability] = st.empty()
                    
                    # 순차적으로 각 능력치 다시 굴리기
                    for ability in ability_names:
                        with st.spinner(f"{ability} 다시 굴리는 중..."):
                            # 다시 굴림 애니메이션 표시
                            dice_result = display_dice_animation(reroll_placeholders[ability], "3d6", 0.5)
                            rerolled_abilities[ability] = dice_result['total']
                            time.sleep(0.1)  # 약간의 딜레이
                    
                    # 결과 저장 및 상태 업데이트
                    st.session_state.rolled_abilities = rerolled_abilities
                    st.session_state.reroll_message = "다시 굴리기 기회를 사용했습니다."
                    st.rerun()
        
        # 다시 굴리기 사용 여부 표시
        if st.session_state.reroll_used:
            st.info("다시 굴리기 기회를 이미 사용했습니다.")

def base_abilities_section():
    """기본 능력치 설정 UI 섹션"""
    st.write("#### 기본 능력치:")
    base_abilities = {'STR': 10, 'INT': 10, 'DEX': 10, 'CON': 10, 'WIS': 10, 'CHA': 10}
    
    # 직업에 따른 추천 능력치 조정
    if 'selected_profession' in st.session_state:
        profession = st.session_state.selected_profession
        profession_key_stats = st.session_state.get('profession_stats', [])
        
        # 주요 능력치에 보너스 부여
        for stat in profession_key_stats:
            if stat in base_abilities:
                base_abilities[stat] = 14  # 주요 능력치는 14로 설정
    
    # 종족에 따른 능력치 보너스 적용
    if 'race_bonus' in st.session_state:
        for stat, bonus in st.session_state.race_bonus.items():
            if stat in base_abilities:
                # 보너스값에서 '+'를 제거하고 정수로 변환
                bonus_value = int(bonus.replace('+', ''))
                base_abilities[stat] += bonus_value
            elif stat == "모든 능력치":
                # 모든 능력치에 보너스 적용
                bonus_value = int(bonus.replace('+', ''))
                for ability in base_abilities:
                    base_abilities[ability] += bonus_value
    
    # 결과 표시 (향상된 시각적 표현)
    cols = st.columns(3)
    i = 0
    
    # 직업 정보 가져오기
    prof = st.session_state.selected_profession if 'selected_profession' in st.session_state else ""
    key_stats = st.session_state.get('profession_stats', [])
    
    # 정렬: 주요 능력치 먼저
    sorted_abilities = sorted(
        base_abilities.items(),
        key=lambda x: (x[0] not in key_stats, key_stats.index(x[0]) if x[0] in key_stats else 999)
    )
    
    for ability, value in sorted_abilities:
        with cols[i % 3]:
            color, description = get_stat_info(ability, value, prof)
            is_key_stat = ability in key_stats
            
            # 중요 능력치 강조 스타일
            highlight = "border: 2px solid gold; background-color: rgba(255, 215, 0, 0.1);" if is_key_stat else ""
            key_badge = "<span style='background-color: #FFD700; color: #000; padding: 1px 5px; border-radius: 3px; font-size: 0.7rem; margin-left: 5px;'>핵심</span>" if is_key_stat else ""
            
            # 종족 보너스 표시
            race_bonus_badge = ""
            for stat, bonus in st.session_state.race_bonus.items():
                if stat == ability or stat == "모든 능력치":
                    race_bonus_badge = f"<span style='background-color: #4CAF50; color: white; padding: 1px 5px; border-radius: 3px; font-size: 0.7rem; margin-left: 5px;'>{bonus}</span>"
            
            # 개선된 능력치 표시
            st.markdown(f"""
            <div class='stat-box' style="border-left: 4px solid {color}; {highlight}">
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span class='stat-name'>{ability}{key_badge}{race_bonus_badge}</span>
                    <span class='stat-value'>{value}</span>
                </div>
                <div style='margin-top: 5px;'>
                    <div style='background-color: #444; height: 4px; border-radius: 2px;'>
                        <div style='background-color: {color}; width: {min(value * 5, 100)}%; height: 100%; border-radius: 2px;'></div>
                    </div>
                </div>
                <div style="font-size: 0.8rem; color: #aaaaaa; margin-top: 5px;">{description}</div>
            </div>
            """, unsafe_allow_html=True)
        i += 1
    
    # 능력치 총점 표시
    total_points = sum(base_abilities.values())
    avg_total = 60  # 평균 총점
    
    # 총점 평가 (낮음, 평균, 높음)
    if total_points < avg_total - 5:
        total_rating = "낮음"
        total_color = "#F44336"  # 빨간색
    elif total_points > avg_total + 5:
        total_rating = "높음"
        total_color = "#4CAF50"  # 녹색
    else:
        total_rating = "평균"
        total_color = "#FFC107"  # 노란색
    
    st.markdown(f"""
    <div style='background-color: #2a3549; padding: 10px; border-radius: 5px; margin: 15px 0; text-align: center;'>
        <span style='font-weight: bold;'>능력치 총점:</span> 
        <span style='color: {total_color}; font-size: 1.2rem; font-weight: bold;'>{total_points}</span>
        <span style='margin-left: 10px; background-color: {total_color}; color: black; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem;'>{total_rating}</span>
        <div style='font-size: 0.8rem; margin-top: 5px;'>(평균 60-65, 70+ 우수, 80+ 탁월)</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("기본 능력치로 진행하기", use_container_width=True):
        st.session_state.character['stats'] = base_abilities
        st.session_state.character['profession'] = st.session_state.selected_profession
        st.session_state.character['race'] = st.session_state.selected_race
        st.session_state.character['backstory'] = st.session_state.selected_background
        st.session_state.character_creation_step = 'review'
        st.session_state.master_message = "좋습니다! 캐릭터가 거의 완성되었습니다. 최종 확인을 해 볼까요?"
        st.rerun()

def display_character_review():
    """캐릭터 최종 확인 UI"""
    st.subheader("캐릭터 최종 확인")
    
    # 마지막 설명 추가
    st.markdown("""
    <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
        <p>당신의 캐릭터가 완성되었습니다! 최종 정보를 확인하고 모험을 시작하세요.</p>
        <p>능력치, 장비, 특수 능력을 확인하고 필요하다면 수정할 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    review_col1, review_col2 = st.columns([2, 1])
    
    with review_col1:
        # 종족 및 직업 아이콘 가져오기
        race_icon = st.session_state.get('race_icon', '👤')
        profession_icon = st.session_state.get('profession_icon', '👤')
        bg_tags = st.session_state.get('background_tags', ["신비로운"])
        
        # 태그 표시용 HTML 생성
        tags_html = ""
        from modules.character_utils import BACKGROUND_TAGS_COLORS
        for tag in bg_tags:
            tag_color = BACKGROUND_TAGS_COLORS.get(tag, "#607D8B")  # 기본값은 회색
            tags_html += f"""
            <span style='background-color: {tag_color}; color: white; 
                       padding: 3px 8px; border-radius: 12px; font-size: 0.8rem; 
                       margin-right: 5px; display: inline-block;'>
                {tag}
            </span>
            """
        
        # 캐릭터 카드 생성 (화려한 디자인)
        st.markdown(f"""
        <div style='background-color: #2a3549; padding: 20px; border-radius: 10px; margin-bottom: 20px; 
                  border: 2px solid #6b8afd; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
            <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                <div style='font-size: 3rem; margin-right: 15px;'>{race_icon}</div>
                <div style='flex-grow: 1;'>
                    <h2 style='margin: 0; color: #e0e0ff;'>
                        {st.session_state.character['race']} {st.session_state.character['profession']}
                    </h2>
                    <div style='margin-top: 5px;'>
                        {tags_html}
                    </div>
                </div>
                <div style='font-size: 3rem;'>{profession_icon}</div>
            </div>
            
            <div style='margin: 15px 0 20px 0;'>
                <div style='font-weight: bold; margin-bottom: 5px; color: #6b8afd;'>캐릭터 특성</div>
                <div style='background-color: rgba(107, 138, 253, 0.1); padding: 10px; border-radius: 5px; border-left: 3px solid #6b8afd;'>
                    {st.session_state.get('race_ability', '종족 특성 없음')}
                </div>
                <div style='margin-top: 10px; background-color: rgba(76, 175, 80, 0.1); padding: 10px; border-radius: 5px; border-left: 3px solid #4CAF50;'>
                    {st.session_state.get('profession_skill', '직업 특성 없음')}
                </div>
            </div>
            
            <div style='font-weight: bold; margin-bottom: 10px; color: #6b8afd;'>배경 스토리</div>
            <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; max-height: 200px; overflow-y: auto;'>
                {st.session_state.character['backstory']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 인벤토리 표시 (개선된 버전)
        st.markdown("""
        <div style='background-color: #2a3549; padding: 15px; border-radius: 10px; margin-bottom: 20px; 
                  border: 2px solid #FFD700; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
            <h3 style='margin-top: 0; color: #FFD700;'>인벤토리</h3>
        """, unsafe_allow_html=True)
        
        # 인벤토리 아이템 정렬
        from modules.item_manager import display_inventory_for_review
        display_inventory_for_review(st.session_state.character['inventory'])
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 특별한 특성 추가
        if 'special_trait' not in st.session_state:
            # 테마와 배경 태그에 따른 특성 선택
            from modules.character_utils import generate_special_trait
            st.session_state.special_trait = generate_special_trait(
                st.session_state.theme, 
                st.session_state.get('background_tags', ["신비로운"])
            )
        
        # 특수 특성 표시
        st.markdown(f"""
        <div style='background-color: #2a3549; padding: 15px; border-radius: 10px; margin-bottom: 20px; 
                  border: 2px solid #9C27B0; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
            <h3 style='margin-top: 0; color: #9C27B0;'>특별한 특성</h3>
            <div style='background-color: rgba(156, 39, 176, 0.1); padding: 15px; border-radius: 5px; border-left: 3px solid #9C27B0;'>
                <div style='font-weight: bold;'>🌟 {st.session_state.special_trait.split(":")[0]}</div>
                <div style='margin-top: 5px;'>{":".join(st.session_state.special_trait.split(":")[1:])}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with review_col2:
        # 능력치 표시
        st.markdown("""
        <div style='background-color: #2a3549; padding: 15px; border-radius: 10px; margin-bottom: 20px; 
                  border: 2px solid #4CAF50; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
            <h3 style='margin-top: 0; color: #4CAF50;'>능력치</h3>
        """, unsafe_allow_html=True)
        
        # 직업 정보 가져오기
        prof = st.session_state.character['profession']
        key_stats = st.session_state.get('profession_stats', [])
        
        # 능력치 값 총합 계산
        total_points = sum(st.session_state.character['stats'].values())
        
        # 능력치 설정
        for stat, value in st.session_state.character['stats'].items():
            # 색상 및 설명 가져오기
            color, description = get_stat_info(stat, value, prof)
            is_key_stat = stat in key_stats
            
            # 키 스탯 표시
            key_badge = ""
            if is_key_stat:
                key_badge = f"<span style='background-color: #FFD700; color: black; padding: 1px 5px; border-radius: 3px; font-size: 0.7rem; margin-left: 5px;'>핵심</span>"
            
            # 바 그래프 너비 계산 (백분율, 최대 18 기준)
            bar_width = min(100, (value / 18) * 100)
            
            # 능력치 바 생성
            st.markdown(f"""
            <div style='margin-bottom: 15px;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='font-weight: bold;'>{stat}</span>
                        {key_badge}
                    </div>
                    <span style='font-weight: bold; color: {color};'>{value}</span>
                </div>
                <div style='margin-top: 5px; background-color: #1e2636; height: 8px; border-radius: 4px;'>
                    <div style='background-color: {color}; width: {bar_width}%; height: 100%; border-radius: 4px;'></div>
                </div>
                <div style='font-size: 0.8rem; color: #aaaaaa; margin-top: 3px;'>{description}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 능력치 총점 표시
        avg_total = 60  # 평균 총점
        
        # 총점 평가 (낮음, 평균, 높음)
        if total_points < avg_total - 5:
            total_rating = "낮음"
            total_color = "#F44336"  # 빨간색
        elif total_points > avg_total + 5:
            total_rating = "높음"
            total_color = "#4CAF50"  # 녹색
        else:
            total_rating = "평균"
            total_color = "#FFC107"  # 노란색
        
        st.markdown(f"""
        <div style='text-align: center; margin-top: 10px; padding: 10px; background-color: rgba(0,0,0,0.2); border-radius: 5px;'>
            <span style='font-weight: bold;'>능력치 총점:</span> 
            <span style='color: {total_color}; font-size: 1.2rem; font-weight: bold;'>{total_points}</span>
            <span style='margin-left: 10px; background-color: {total_color}; color: black; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem;'>{total_rating}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 시작 위치 정보
        st.markdown(f"""
        <div style='background-color: #2a3549; padding: 15px; border-radius: 10px; margin-bottom: 20px; 
                  border: 2px solid #2196F3; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
            <h3 style='margin-top: 0; color: #2196F3;'>시작 위치</h3>
            <div style='background-color: rgba(33, 150, 243, 0.1); padding: 15px; border-radius: 5px; border-left: 3px solid #2196F3;'>
                <div style='font-size: 1.2rem; font-weight: bold; text-align: center;'>{st.session_state.current_location}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 캐릭터 플레이 팁
        st.markdown(f"""
        <div style='background-color: #2a3549; padding: 15px; border-radius: 10px; 
                  border: 2px solid #FF9800; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
            <h3 style='margin-top: 0; color: #FF9800;'>플레이 팁</h3>
            <ul style='margin-top: 10px; padding-left: 20px;'>
                <li>당신의 핵심 능력치({', '.join(key_stats)})를 활용하는 행동을 시도하세요.</li>
                <li>"{st.session_state.special_trait.split(':')[0]}" 특성을 중요한 순간에 활용하세요.</li>
                <li>배경 스토리와 일관된 캐릭터 플레이를 하면 더 몰입감 있는 경험을 할 수 있습니다.</li>
                <li>마스터에게 세계관에 대한 궁금한 점을 자유롭게 질문하세요.</li>
                <li>창의적인 문제 해결 방법을 시도해보세요.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 최종 선택 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("이 캐릭터로 게임 시작", use_container_width=True):
            # 특별한 특성 저장
            if 'special_trait' in st.session_state:
                st.session_state.character['special_trait'] = st.session_state.special_trait
            
            # 게임 시작 준비
            with st.spinner("게임을 준비하는 중..."):
                # 시작 메시지 생성
                from modules.ai_service import generate_game_intro
                intro = generate_game_intro(
                    st.session_state.world_description,
                    st.session_state.character,
                    st.session_state.current_location
                )
                st.session_state.story_log.append(intro)
                
                # 행동 제안 생성 상태 설정
                st.session_state.suggestions_generated = False
            
            # 게임 시작
            st.session_state.stage = 'game_play'
            st.session_state.master_message = f"모험이 시작되었습니다! {st.session_state.character['race']} {st.session_state.character['profession']}으로서의 여정이 펼쳐집니다."
            
            # 행동 단계 초기화
            st.session_state.action_phase = 'suggestions'
            st.rerun()
    
    with col2:
        if st.button("처음부터 다시 만들기", use_container_width=True):
            # 캐릭터 생성 단계 초기화
            st.session_state.character_creation_step = 'race'
            st.session_state.background_options_generated = False
            
            # 임시 데이터 삭제
            for key in ['selected_race', 'selected_profession', 'character_backgrounds', 'selected_background', 
                      'rolled_abilities', 'special_trait', 'race_bonus', 'race_ability', 'race_icon',
                      'profession_icon', 'profession_stats', 'profession_equipment', 'profession_skill',
                      'background_tags', 'dice_rolled', 'reroll_used']:
                if key in st.session_state:
                    del st.session_state[key]
            
            # 캐릭터 정보 초기화
            from modules.item_manager import initialize_inventory
            st.session_state.character = {
                'profession': '',
                'stats': {'STR': 0, 'INT': 0, 'DEX': 0, 'CON': 0, 'WIS': 0, 'CHA': 0},
                'backstory': '',
                'inventory': initialize_inventory(st.session_state.theme)
            }
            
            st.session_state.master_message = "다시 시작해봅시다! 어떤 종족을 선택하시겠어요?"
            st.rerun()


