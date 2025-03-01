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

from config.constants import BACKUP_RESPONSES, API_KEY_SECRET_NAME

@st.cache_resource(ttl=3600)  # 1시간 캐싱
def setup_gemini():
    """
    Gemini API 초기화 - 캐싱 및 오류 처리 개선
    
    Returns:
        GenerativeModel or None: 초기화된 모델 인스턴스 또는 실패 시 None
    """
    try:
        # Streamlit Secrets에서 API 키 가져오기 
        api_key = st.secrets.get(GEMINI_API_KEY, None)
        
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
