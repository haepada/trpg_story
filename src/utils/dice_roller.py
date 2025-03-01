"""
주사위 굴리기 관련 유틸리티 함수 모듈
"""
import random
import re
import time
import streamlit as st

def roll_dice(dice_type=20, num_dice=1):
    """
    주사위 굴리기 함수
    
    Args:
        dice_type (int): 주사위 면 수 (기본값: 20)
        num_dice (int): 굴릴 주사위 개수 (기본값: 1)
        
    Returns:
        list: 주사위 결과 목록
    """
    return [random.randint(1, dice_type) for _ in range(num_dice)]

def calculate_dice_result(dice_expression):
    """
    주사위 표현식 계산 (예: '2d6+3', '1d20-2', '3d8' 등)
    
    Args:
        dice_expression (str): 주사위 표현식 
        
    Returns:
        dict: 주사위 결과 정보
    
    Raises:
        ValueError: 표현식이 유효하지 않을 경우
    """
    # 표현식 분석
    pattern = r'(\d+)d(\d+)([+-]\d+)?'
    match = re.match(pattern, dice_expression.lower().replace(' ', ''))
    
    if not match:
        raise ValueError(f"유효하지 않은 주사위 표현식: {dice_expression}")
    
    num_dice = int(match.group(1))
    dice_type = int(match.group(2))
    modifier = match.group(3)
    
    # 주사위 굴리기
    rolls = roll_dice(dice_type, num_dice)
    
    # 보정값 적용
    total = sum(rolls)
    modifier_value = 0
    
    if modifier:
        modifier_value = int(modifier)
        total += modifier_value
    
    return {
        'rolls': rolls,
        'total': total,
        'modifier': modifier_value,
        'num_dice': num_dice,
        'dice_type': dice_type
    }

def display_dice_animation(placeholder, dice_expression='1d20', duration=1.0):
    """
    주사위 굴리기 애니메이션 표시
    
    Args:
        placeholder (st.empty): 애니메이션을 표시할 빈 요소
        dice_expression (str): 주사위 표현식
        duration (float): 애니메이션 지속 시간(초)
        
    Returns:
        dict: 주사위 결과 정보
    """
    # 주사위 표현식 파싱
    pattern = r'(\d+)d(\d+)([+-]\d+)?'
    match = re.match(pattern, dice_expression.lower().replace(' ', ''))
    
    if match:
        num_dice = int(match.group(1))
        dice_type = int(match.group(2))
        modifier = match.group(3) or "+0"
        modifier_value = int(modifier)
    else:
        # 기본값
        num_dice = 1
        dice_type = 20
        modifier_value = 0
        modifier = "+0"
    
    # 굴리기 시작 시간
    start_time = time.time()
    
    # 주사위 아이콘 선택
    dice_icons = {
        4: "🎲 (d4)",
        6: "🎲 (d6)",
        8: "🎲 (d8)",
        10: "🎲 (d10)",
        12: "🎲 (d12)",
        20: "🎲 (d20)",
        100: "🎲 (d%)"
    }
    dice_icon = dice_icons.get(dice_type, "🎲")
    
    # 애니메이션 표시
    while time.time() - start_time < duration:
        # 임시 주사위 결과 생성
        temp_rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
        temp_total = sum(temp_rolls) + modifier_value
        
        # 간소화된 애니메이션 표시
        dice_html = f"""
        <div class='dice-animation'>
            <div class='dice-rolling'>
                {dice_icon}<br>
                <span style='font-size: 1rem;'>{' + '.join([str(r) for r in temp_rolls])}{modifier if modifier_value != 0 else ""}</span><br>
                <span style='font-weight: bold;'>= {temp_total}</span>
            </div>
        </div>
        """
        placeholder.markdown(dice_html, unsafe_allow_html=True)
        time.sleep(0.1)
    
    # 최종 주사위 결과 계산
    result = calculate_dice_result(dice_expression)
    
    # 간소화된 결과 표시
    final_html = f"""
    <div class='dice-result-container'>
        <div style='font-size: 2rem;'>{dice_icon}</div>
        <div>{dice_expression.upper()}</div>
        <div style='margin: 10px 0;'>
    """
    
    # 각 주사위 결과를 간소화하여 표시
    for roll in result['rolls']:
        color = "#4CAF50" if roll == dice_type else "#F44336" if roll == 1 else "#e0e0ff"
        final_html += f"<span style='display:inline-block; margin:0 5px; color:{color};'>{roll}</span>"
    
    # 수정자 및 총점
    if result['modifier'] != 0:
        modifier_sign = "+" if result['modifier'] > 0 else ""
        final_html += f"<br><span>수정자: {modifier_sign}{result['modifier']}</span>"
    
    final_html += f"<br><div style='font-size: 1.8rem; font-weight: bold; color: #FFD700;'>{result['total']}</div></div></div>"
    
    placeholder.markdown(final_html, unsafe_allow_html=True)
    return result