"""
위치 관련 유틸리티 함수를 제공하는 모듈
"""
from modules.ai_service import generate_gemini_text

def generate_locations(theme):
    """
    테마에 따른 위치 목록 반환
    
    Args:
        theme (str): 세계관 테마
        
    Returns:
        list: 생성된 위치 목록
    """
    locations = {
        'fantasy': ["왕국의 수도", "마법사의 탑", "고대 숲", "상인 거리", "지하 미궁"],
        'sci-fi': ["중앙 우주 정거장", "연구 시설", "거주 구역", "우주선 정비소", "외계 식민지"],
        'dystopia': ["지하 피난처", "통제 구역", "폐허 지대", "저항군 은신처", "권력자 거주구"]
    }
    return locations.get(theme, ["시작 지점", "미지의 땅", "중심부", "외곽 지역", "비밀 장소"])

def generate_movement_story(current_location, destination, theme):
    """
    장소 이동 시 스토리 생성
    
    Args:
        current_location (str): 현재 위치
        destination (str): 목적지
        theme (str): 세계관 테마
        
    Returns:
        str: 이동 스토리 텍스트
    """
    prompt = f"""
    당신은 TRPG 게임 마스터입니다. 플레이어가 {current_location}에서 {destination}으로 이동하려고 합니다.
    
    ## 이동 스토리 지침
    1. 이동 과정과 새로운 장소에 도착했을 때의 상황을 생생하게 묘사해주세요.
    2. 이동 중 발생하는 작은 사건이나 만남을 포함하세요.
    3. 출발지와 목적지의 대비되는 분위기나 환경적 차이를 강조하세요.
    4. 다양한 감각적 묘사(시각, 청각, 후각, 촉각)를 포함하세요.
    5. 도착 장소에서 플레이어가 볼 수 있는 주요 랜드마크나 특징적 요소를 설명하세요.
    6. 현지 주민이나 생물의 반응이나 활동을 포함하세요.
    
    ## 정보
    세계 테마: {theme}
    출발 위치: {current_location}
    목적지: {destination}
    
    약 200단어 내외로 작성해주세요.
    모든 문장은 완결된 형태로 작성하세요.
    """
    
    return generate_gemini_text(prompt, 500)