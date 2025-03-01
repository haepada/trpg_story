import streamlit as st
from modules.character_creation import character_creation_page
from modules.game_play import game_play_page
from modules.world_description import world_description_page
from utils.theme_manager import setup_responsive_layout
from config.constants import INITIAL_MASTER_MESSAGE
from config.styles import apply_custom_styles

def initialize_session_state():
    """세션 상태 초기화 함수"""
    if 'initialized' not in st.session_state:
        st.session_state.stage = 'theme_selection'
        st.session_state.world_description = ""
        st.session_state.character = {
            'profession': '',
            'stats': {'STR': 0, 'INT': 0, 'DEX': 0, 'CON': 0, 'WIS': 0, 'CHA': 0},
            'backstory': '',
            'inventory': ['기본 의류', '작은 주머니 (5 골드)']
        }
        st.session_state.story_log = []
        st.session_state.current_location = ""
        st.session_state.use_backup_mode = False
        st.session_state.world_generated = False
        st.session_state.world_accepted = False
        st.session_state.question_answers = []
        st.session_state.question_count = 0
        st.session_state.question_submitted = False
        st.session_state.question_answered = False
        st.session_state.question_current = ""
        st.session_state.answer_current = ""
        
        st.session_state.background_options_generated = False
        st.session_state.character_backgrounds = []
        
        st.session_state.dice_rolled = False
        st.session_state.dice_result = 0
        st.session_state.dice_rolling_animation = False
        
        st.session_state.action_submitted = False
        st.session_state.action_processed = False
        st.session_state.current_action = ""
        st.session_state.action_response = ""
        st.session_state.ability_check_done = False
        
        st.session_state.suggestions_generated = False
        st.session_state.action_suggestions = []
        
        st.session_state.master_question_submitted = False
        st.session_state.master_question_answered = False
        st.session_state.master_question = ""
        st.session_state.master_answer = ""
        
        st.session_state.move_submitted = False
        st.session_state.move_processed = False
        st.session_state.move_destination = ""
        st.session_state.move_response = ""
        
        st.session_state.available_locations = []
        st.session_state.action_phase = 'suggestions'
        
        st.session_state.continuation_mode = False
        st.session_state.continuation_text = ""
        
        st.session_state.item_notification = ""
        st.session_state.show_item_notification = False
        
        st.session_state.world_questions = []
        st.session_state.world_question_count = 0
        
        st.session_state.active_section = None
        
        st.session_state.master_message = INITIAL_MASTER_MESSAGE
        
        st.session_state.initialized = True

def reset_game_session():
    """게임 세션을 완전히 초기화하고 첫 화면으로 돌아가는 함수"""
    all_keys = list(st.session_state.keys())
    
    for key in all_keys:
        if key != 'initialized':
            if key in st.session_state:
                del st.session_state[key]
    
    st.session_state.stage = 'theme_selection'
    st.session_state.master_message = INITIAL_MASTER_MESSAGE

def theme_selection_page():
    """테마 선택 페이지"""
    from utils.theme_manager import create_theme_image, get_theme_description
    from modules.world_generator import generate_world_description
    from utils.location_manager import generate_locations
    
    st.title("유니버스 원: 세상에서 하나뿐인 TRPG")
    
    st.markdown("""
    <div style='background-color: #2a3549; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
        <p>🌟 <strong>유니버스 원</strong>은 AI가 만들어내는 유일무이한 세계와 이야기를 경험하는 TRPG 플랫폼입니다.</p>
        <p>🎲 당신이 내리는 모든 선택과 행동이 세계를 형성하고, 이야기를 만들어갑니다.</p>
        <p>✨ 누구도 똑같은 이야기를 경험할 수 없습니다. 오직 당신만의 단 하나뿐인 모험이 시작됩니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("1️⃣ 세계관 선택")
    
    # 마스터 메시지 표시
    st.markdown(f"<div class='master-text'>{st.session_state.master_message}</div>", unsafe_allow_html=True)
    
    # 테마 설명 추가
    st.markdown("""
    <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
        <p>모험을 시작할 세계의 테마를 선택하세요. 각 테마는 독특한 분위기와 가능성을 제공합니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='theme-card'>", unsafe_allow_html=True)
        st.markdown(create_theme_image("fantasy"), unsafe_allow_html=True)
        st.markdown(get_theme_description("fantasy"), unsafe_allow_html=True)
        
        if st.button("판타지", key="fantasy"):
            with st.spinner("AI 마스터가 세계를 생성 중입니다..."):
                loading_placeholder = st.empty()
                loading_placeholder.info("판타지 세계를 생성하는 중... 잠시만 기다려주세요.")
                
                st.session_state.theme = "fantasy"
                st.session_state.world_description = generate_world_description("fantasy")
                st.session_state.current_location = "왕국의 수도"
                st.session_state.available_locations = generate_locations("fantasy")
                st.session_state.master_message = "판타지 세계에 오신 것을 환영합니다! 아래 세계 설명을 읽어보시고, 질문이 있으시면 언제든지 물어보세요."
                st.session_state.world_generated = True
                st.session_state.stage = 'world_description'
                
                loading_placeholder.empty()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='theme-card'>", unsafe_allow_html=True)
        st.markdown(create_theme_image("sci-fi"), unsafe_allow_html=True)
        st.markdown(get_theme_description("sci-fi"), unsafe_allow_html=True)
        
        if st.button("SF", key="scifi"):
            with st.spinner("AI 마스터가 세계를 생성 중입니다..."):
                loading_placeholder = st.empty()
                loading_placeholder.info("SF 세계를 생성하는 중... 잠시만 기다려주세요.")
                
                st.session_state.theme = "sci-fi"
                st.session_state.world_description = generate_world_description("sci-fi")
                st.session_state.current_location = "중앙 우주 정거장"
                st.session_state.available_locations = generate_locations("sci-fi")
                st.session_state.master_message = "SF 세계에 오신 것을 환영합니다! 아래 세계 설명을 읽어보시고, 질문이 있으시면 언제든지 물어보세요."
                st.session_state.world_generated = True
                st.session_state.stage = 'world_description'
                
                loading_placeholder.empty()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("<div class='theme-card'>", unsafe_allow_html=True)
        st.markdown(create_theme_image("dystopia"), unsafe_allow_html=True)
        st.markdown(get_theme_description("dystopia"), unsafe_allow_html=True)
        
        if st.button("디스토피아", key="dystopia"):
            with st.spinner("AI 마스터가 세계를 생성 중입니다..."):
                loading_placeholder = st.empty()
                loading_placeholder.info("디스토피아 세계를 생성하는 중... 잠시만 기다려주세요.")
                
                st.session_state.theme = "dystopia"
                st.session_state.world_description = generate_world_description("dystopia")
                st.session_state.current_location = "지하 피난처"
                st.session_state.available_locations = generate_locations("dystopia")
                st.session_state.master_message = "디스토피아 세계에 오신 것을 환영합니다! 아래 세계 설명을 읽어보시고, 질문이 있으시면 언제든지 물어보세요."
                st.session_state.world_generated = True
                st.session_state.stage = 'world_description'
                
                loading_placeholder.empty()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def main():
    """메인 애플리케이션 함수"""
    # 스트림릿 페이지 설정
    st.set_page_config(
        page_title="TRPG 주사위 기반 스토리텔링",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 커스텀 CSS 적용
    apply_custom_styles()
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # 반응형 레이아웃 설정
    setup_responsive_layout()
    
    # 현재 단계에 따라 다른 페이지 표시
    if st.session_state.stage == 'theme_selection':
        theme_selection_page()
    elif st.session_state.stage == 'world_description':
        world_description_page()
    elif st.session_state.stage == 'character_creation':
        character_creation_page()
    elif st.session_state.stage == 'game_play':
        game_play_page()

if __name__ == "__main__":
    main()