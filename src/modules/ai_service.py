"""
AI 서비스와의 통신을 담당하는 모듈
"""
import time
import streamlit as st
import re
import json

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from ..config.constants import BACKUP_RESPONSES, API_KEY_SECRET_NAME

@st.cache_resource(ttl=3600)  # 1시간 캐싱
def setup_gemini():
    """
    Gemini API 초기화 - 캐싱 및 오류 처리 개선
    
    Returns:
        GenerativeModel or None: 초기화된 모델 인스턴스 또는 실패 시 None
    """
    try:
        # Streamlit Secrets에서 API 키 가져오기 
        api_key = st.secrets.get(API_KEY_SECRET_NAME, None)
        
        if not api_key:
            st.sidebar.error("API 키가 설정되지 않음")
            st.session_state.use_backup_mode = True
            return None
        
        # Gemini API 초기화
        genai.configure(api_key=api_key)
        
        # 최신 모델 이름으로 시도
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            return model
        except Exception as e:
            # 이전 모델 이름으로 시도
            try:
                model = genai.GenerativeModel("gemini-pro")
                return model
            except Exception as inner_e:
                st.error(f"사용 가능한 Gemini 모델을 찾을 수 없습니다. 백업 응답을 사용합니다.")
                st.session_state.use_backup_mode = True
                return None
                
    except Exception as e:
        st.error(f"Gemini 모델 초기화 오류: {e}")
        st.session_state.use_backup_mode = True
        return None

def generate_gemini_text(prompt, max_tokens=500, retries=2, timeout=10):
    """
    Gemini API를 사용하여 텍스트 생성 - 오류 처리 및 재시도 로직 추가
    
    Args:
        prompt (str): 텍스트 생성을 위한 프롬프트
        max_tokens (int): 생성할 최대 토큰 수
        retries (int): 실패 시 재시도 횟수
        timeout (int): 타임아웃 시간(초)
        
    Returns:
        str: 생성된 텍스트
    """
    # 백업 모드 확인
    if getattr(st.session_state, 'use_backup_mode', False):
        # 백업 모드면 즉시 백업 응답 반환
        if "world" in prompt.lower():
            return BACKUP_RESPONSES["world"]
        elif "character" in prompt.lower():
            return BACKUP_RESPONSES["character"]
        elif "질문" in prompt.lower() or "question" in prompt.lower():
            return BACKUP_RESPONSES["question"]
        else:
            return BACKUP_RESPONSES["story"]
    
    # 재시도 로직
    for attempt in range(retries + 1):
        try:
            model = setup_gemini()
            
            if not model:
                # 모델 초기화 실패 시 백업 응답 사용
                if "world" in prompt.lower():
                    return BACKUP_RESPONSES["world"]
                elif "character" in prompt.lower():
                    return BACKUP_RESPONSES["character"]
                elif "질문" in prompt.lower() or "question" in prompt.lower():
                    return BACKUP_RESPONSES["question"]
                else:
                    return BACKUP_RESPONSES["story"]
            
            # 안전 설정
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]
            
            # 모델 생성 구성
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": max_tokens,
                "stop_sequences": ["USER:", "ASSISTANT:"]
            }
            
            # 텍스트 생성
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # 응답 텍스트 추출 및 길이 제한
            text = response.text
            if len(text) > max_tokens * 4:
                text = text[:max_tokens * 4] + "..."
            
            return text
            
        except Exception as e:
            if attempt < retries:
                st.warning(f"API 호출 오류, 재시도 중... ({attempt+1}/{retries})")
                time.sleep(1)  # 잠시 대기 후 재시도
                continue
            else:
                st.error(f"Gemini API 호출 오류: {e}")
                st.session_state.use_backup_mode = True
                
                # 오류 발생 시 백업 응답 사용
                if "world" in prompt.lower():
                    return BACKUP_RESPONSES["world"]
                elif "character" in prompt.lower():
                    return BACKUP_RESPONSES["character"]
                elif "질문" in prompt.lower() or "question" in prompt.lower():
                    return BACKUP_RESPONSES["question"]
                else:
                    return BACKUP_RESPONSES["story"]
    
    # 이 코드는 실행되지 않음 (위에서 항상 반환함)
    return BACKUP_RESPONSES["story"]

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
