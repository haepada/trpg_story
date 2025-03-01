"""
테마 관련 유틸리티 함수를 제공하는 모듈
"""
import streamlit as st
from PIL import Image

def create_theme_image(theme):
    """테마별 이미지/박스 생성"""
    if theme == "fantasy":
        color = "#4b5d78"
        text = "판타지"
    elif theme == "sci-fi":
        color = "#3a7b9c"
        text = "SF"
    else:  # dystopia
        color = "#8b4045"
        text = "디스토피아"
    
    # HTML로 색상 박스 표시
    return f"""
    <div class="theme-box" style="background-color: {color};">
        {text}
    </div>
    """

def get_theme_description(theme):
    """테마에 대한 상세 설명 제공"""
    theme_descriptions = {
        "fantasy": """
        <p><strong>판타지 세계</strong>는 마법, 신화적 생물, 영웅적 모험이 가득한 세계입니다.</p>
        <p>중세 시대를 연상시키는 배경에 마법과 신비로운 존재들이 공존하며, 
        고대의 유물, 잊혀진 주문서, 드래곤과 같은 전설적 생물들이 있습니다.</p>
        <p>당신은 이 세계에서 마법사, 전사, 도적, 성직자 등 다양한 직업을 가진 모험가가 될 수 있습니다.</p>
        """,
        
        "sci-fi": """
        <p><strong>SF(공상과학) 세계</strong>는 미래 기술, 우주 탐험, 외계 생명체가 존재하는 세계입니다.</p>
        <p>첨단 기술, 우주선, 인공지능, 외계 행성 등이 배경이 되며, 
        인류의 미래 또는 다른 행성계의 이야기를 다룹니다.</p>
        <p>당신은 우주 파일럿, 사이버 해커, 외계종족 전문가 등 미래 지향적인 직업을 가진 캐릭터가 될 수 있습니다.</p>
        """,
        
        "dystopia": """
        <p><strong>디스토피아 세계</strong>는 암울한 미래, 억압적인 사회 체제, 환경 재앙 이후의 세계를 그립니다.</p>
        <p>종종 파괴된 문명의 폐허, 독재 정권, 자원 부족, 계급 사회 등을 배경으로 하며, 
        생존과 자유를 위한 투쟁이 중심 주제입니다.</p>
        <p>당신은 저항군 요원, 밀수업자, 정보 브로커 등 어두운 세계에서 살아남기 위한 직업을 가진 캐릭터가 될 수 있습니다.</p>
        """
    }
    
    return theme_descriptions.get(theme, "")

def get_location_image(location, theme):
    """위치 이미지 생성 함수 (플레이스홀더)"""
    colors = {
        'fantasy': (100, 80, 200),
        'sci-fi': (80, 180, 200),
        'dystopia': (200, 100, 80)
    }
    color = colors.get(theme, (150, 150, 150))
    
    # 색상 이미지 생성
    img = Image.new('RGB', (400, 300), color)
    return img

def setup_responsive_layout():
    """반응형 레이아웃 설정"""
    # 디스플레이 모드 설정 옵션 추가
    display_mode = st.sidebar.radio(
        "디스플레이 모드:",
        ["데스크톱", "모바일"],
        horizontal=True
    )
    
    # 모바일 모드 설정
    st.session_state.is_mobile = (display_mode == "모바일")
    
    # 모바일 모드일 때 사이드바에 추가 메뉴
    if st.session_state.is_mobile:
        st.sidebar.markdown("### 모바일 네비게이션")
        
        # 게임 플레이 단계에서만 패널 선택 옵션 표시
        if st.session_state.get('stage') == 'game_play':
            panel_options = ["스토리", "캐릭터 정보", "게임 도구"]
            current_panel = st.session_state.get('mobile_panel', "스토리")
            
            selected_panel = st.sidebar.radio(
                "표시할 패널:",
                panel_options,
                index=panel_options.index(current_panel)
            )
            
            if selected_panel != current_panel:
                st.session_state.mobile_panel = selected_panel
                st.rerun()

def is_mobile():
    """현재 기기가 모바일인지 확인"""
    # 세션 상태에 설정된 모바일 모드 값 반환
    return st.session_state.get('is_mobile', False)