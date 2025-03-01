"""
세계관 설명 페이지 모듈
"""
import streamlit as st
from datetime import datetime
from config.constants import SUGGESTED_WORLD_QUESTIONS
from modules.world_generator import (
    master_answer_question,
    generate_world_expansion
)

def world_description_page():
    """세계관 설명 및 질문 페이지 구현"""
    st.header("2️⃣ 세계관 설명")
    
    # 마스터 메시지 표시
    st.markdown(f"<div class='master-text'>{st.session_state.master_message}</div>", unsafe_allow_html=True)
    
    # 세계관 설명 표시 - 단락 구분 개선
    world_desc_paragraphs = st.session_state.world_description.split("\n\n")
    formatted_desc = ""
    for para in world_desc_paragraphs:
        formatted_desc += f"<p>{para}</p>\n"
    
    st.markdown(f"<div class='story-text'>{formatted_desc}</div>", unsafe_allow_html=True)
    
    # "다른 세계 탐험하기" 버튼 추가
    if st.button("🌍 다른 세계 탐험하기", key="explore_other_world", use_container_width=True):
        # 세션 상태 초기화 (일부만)
        for key in ['theme', 'world_description', 'world_generated', 'world_accepted', 
                   'question_answers', 'question_count', 'current_location']:
            if key in st.session_state:
                del st.session_state[key]
        
        # 테마 선택 화면으로 돌아가기
        st.session_state.stage = 'theme_selection'
        st.session_state.master_message = "새로운 세계를 탐험해보세요!"
        st.rerun()
    
    # 탭 기반 UI로 변경
    tabs = st.tabs(["세계관 확장", "질문하기", "탐험 시작"])
    
    # 세계관 확장 탭
    with tabs[0]:
        world_expansion_tab()
    
    # 질문하기 탭
    with tabs[1]:
        world_question_tab()
    
    # 탐험 시작 탭
    with tabs[2]:
        exploration_start_tab()

def world_expansion_tab():
    """세계관 확장 탭 내용"""
    st.subheader("세계관 이어서 작성")
    
    # 설명 추가
    st.markdown("""
    <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
        <p>세계관을 더 풍부하게 만들어보세요. AI 마스터에게 특정 부분을 확장해달라고 요청하거나, 직접 내용을 추가할 수 있습니다.</p>
        <p>추가된 내용은 기존 세계관과 자연스럽게 통합되어 더 깊이 있는 세계를 만들어갑니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 직접 입력 옵션 추가
    expand_method = st.radio(
        "확장 방법 선택:",
        ["AI 마스터에게 맡기기", "직접 작성하기"],
        horizontal=True
    )
    
    # AI 확장 선택 시
    if expand_method == "AI 마스터에게 맡기기":
        handle_ai_expansion()
    # 직접 작성 선택 시
    else:
        handle_manual_expansion()

def handle_ai_expansion():
    """AI가 세계관을 확장하는 기능 처리"""
    # 확장할 주제 선택 (더 구체적인 세계관 생성 유도)
    expansion_topics = {
        "역사와 전설": "세계의 역사적 사건, 신화, 전설적 영웅 등에 대한 이야기를 확장합니다.",
        "마법/기술 체계": "세계의 마법 시스템이나 기술 체계의 작동 방식과 한계를 자세히 설명합니다.",
        "종족과 문화": "세계에 존재하는 다양한 종족들과 그들의 문화, 관습, 생활 방식을 확장합니다.",
        "정치 체계와 세력": "권력 구조, 주요 세력 간의 관계, 정치적 갈등 등을 더 자세히 설명합니다.",
        "지리와 환경": "세계의 지리적 특성, 주요 지역, 기후, 자연환경에 대해 확장합니다.",
        "현재 갈등과 위기": "세계에서 진행 중인 갈등, 위기, 중요한 문제에 대해 자세히 설명합니다."
    }
    
    topic_options = list(expansion_topics.keys())
    topic_descriptions = list(expansion_topics.values())
    
    # 설명과 함께 확장 주제 선택
    expansion_topic_idx = st.selectbox(
        "확장할 세계관 요소를 선택하세요:",
        range(len(topic_options)),
        format_func=lambda i: topic_options[i]
    )
    
    expansion_topic = topic_options[expansion_topic_idx]
    
    # 선택한 주제에 대한 설명 표시
    st.markdown(f"""
    <div style='background-color: #1e2636; padding: 10px; border-radius: 5px; margin: 10px 0;'>
        <p>{topic_descriptions[expansion_topic_idx]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 확장 버튼 누르기 전과 후의 상태 관리
    if 'continuation_generated' not in st.session_state:
        st.session_state.continuation_generated = False
        
    if not st.session_state.continuation_generated:
        if st.button("세계관 확장하기", key="expand_world"):
            with st.spinner("이어질 내용을 생성 중..."):
                try:
                    # 확장 내용 생성
                    st.session_state.continuation_text = generate_world_expansion(
                        st.session_state.world_description, 
                        st.session_state.theme,
                        expansion_topic
                    )
                    st.session_state.continuation_generated = True
                except Exception as e:
                    st.error(f"내용 생성 중 오류 발생: {e}")
                    # 오류 발생 시 백업 응답
                    st.session_state.continuation_text = "이 세계는 더 많은 비밀과 모험으로 가득 차 있습니다. 숨겨진 장소와 만날 수 있는 흥미로운 캐릭터들이 여러분을 기다리고 있습니다."
                    st.session_state.continuation_generated = True
            st.rerun()
                
    # 생성된 내용이 있으면 표시
    if st.session_state.continuation_generated:
        # 생성된 내용과 어떻게 반영되는지 시각적으로 표시
        st.subheader("확장된 세계관 내용:")
        st.info("다음 내용이 세계관에 추가됩니다. '이 내용으로 적용하기'를 클릭하면 세계관에 반영됩니다.")
        
        # 단락 나누기 - 가독성 개선
        continuation_paragraphs = st.session_state.continuation_text.split("\n\n")
        formatted_continuation = ""
        for para in continuation_paragraphs:
            formatted_continuation += f"<p>{para}</p>\n"
        
        st.markdown(f"<div class='story-text' style='border-left: 4px solid #4CAF50;'>{formatted_continuation}</div>", unsafe_allow_html=True)
        
        # 적용 버튼과 다시 생성 버튼 병렬 배치
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이 내용으로 적용하기", key="apply_expansion"):
                # 세계 설명에 추가
                st.session_state.world_description += "\n\n## " + expansion_topic + "\n" + st.session_state.continuation_text
                
                # 상태 초기화
                st.session_state.continuation_generated = False
                if "continuation_text" in st.session_state:
                    del st.session_state.continuation_text
                
                st.session_state.master_message = "세계관이 더욱 풍부해졌습니다! 이 세계에 대해 더 궁금한 점이 있으신가요?"
                st.success("세계관이 성공적으로 확장되었습니다!")
                st.rerun()
        
        with col2:
            if st.button("다시 생성하기", key="regenerate_expansion"):
                # 내용 다시 생성하도록 상태 초기화
                st.session_state.continuation_generated = False
                if "continuation_text" in st.session_state:
                    del st.session_state.continuation_text
                st.rerun()

def handle_manual_expansion():
    """사용자가 직접 세계관을 확장하는 기능 처리"""
    st.write("세계관에 추가하고 싶은 내용을 직접 작성해보세요:")
    user_continuation = st.text_area("세계관 추가 내용:", height=200)
    
    # 사용성 개선: 무한 추가 방지를 위한 확인 메시지
    if user_continuation and st.button("내용 추가하기", key="add_user_content"):
        # 미리보기 표시
        st.subheader("추가될 내용:")
        st.info("다음 내용이 세계관에 추가됩니다. 내용이 올바른지 확인하세요.")
        
        # 단락 나누기 - 가독성 개선
        user_paragraphs = user_continuation.split("\n\n")
        formatted_user_content = ""
        for para in user_paragraphs:
            formatted_user_content += f"<p>{para}</p>\n"
        
        st.markdown(f"<div class='story-text' style='border-left: 4px solid #4CAF50;'>{formatted_user_content}</div>", unsafe_allow_html=True)
        
        # 확인 후 추가
        confirm = st.checkbox("위 내용을 세계관에 추가하시겠습니까?", key="confirm_add_content")
        if confirm and st.button("확인 후 추가하기", key="confirm_add_user_content"):
            # 작성한 내용 추가
            st.session_state.world_description += "\n\n## 직접 추가한 세계관 내용\n" + user_continuation
            st.session_state.master_message = "직접 작성하신 내용이 세계관에 추가되었습니다! 이 세계가 더욱 풍부해졌습니다."
            st.success("세계관에 내용이 성공적으로 추가되었습니다!")
            st.rerun()

def world_question_tab():
    """세계관 질문 탭 내용"""
    st.subheader("세계관에 대한 질문")
    
    # 설명 추가
    st.markdown("""
    <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
        <p>세계에 대해 궁금한 점을 마스터에게 질문해보세요. 세계의 역사, 문화, 종족, 마법/기술 체계 등에 대한 질문을 할 수 있습니다.</p>
        <p>마스터의 답변은 세계관에 추가되어 더 풍부한 배경을 만들어갑니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 질문 처리 상태 관리
    if 'question_processing' not in st.session_state:
        st.session_state.question_processing = False
    
    if 'selected_suggested_question' not in st.session_state:
        st.session_state.selected_suggested_question = None
        
    if 'world_questions_history' not in st.session_state:
        st.session_state.world_questions_history = []
    
    # 제안된 질문 표시
    st.write("제안된 질문:")
    question_cols = st.columns(2)
    
    for i, q in enumerate(SUGGESTED_WORLD_QUESTIONS):
        with question_cols[i % 2]:
            # 토글 버튼으로 질문 선택
            is_selected = st.checkbox(q, key=f"toggle_q_{i}", value=(st.session_state.selected_suggested_question == q))
            
            if is_selected:
                st.session_state.selected_suggested_question = q
            elif st.session_state.selected_suggested_question == q:
                st.session_state.selected_suggested_question = None
    
    # 선택된 질문이 있으면 질문하기 버튼 표시
    if st.session_state.selected_suggested_question:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        st.success(f"'{st.session_state.selected_suggested_question}' 질문이 선택되었습니다.")
    
    # 직접 질문 입력 섹션
    st.markdown("<div style='margin-top: 20px; padding-top: 10px; border-top: 1px solid #3d4c63;'></div>", unsafe_allow_html=True)
    st.write("### 직접 질문 입력")
    
    # 기본값 설정 (선택된 질문이 있으면 해당 질문 표시)
    default_question = st.session_state.get('custom_question_value', st.session_state.get('selected_suggested_question', ''))
    
    # 폼 사용으로 무한 생성 방지
    with st.form(key="world_question_form"):
        custom_question = st.text_input("질문 내용:", value=default_question, key="custom_world_question")
        submit_question = st.form_submit_button("질문하기", use_container_width=True, disabled=st.session_state.question_processing)
    
    # 질문이 제출되었을 때
    if submit_question and (custom_question or st.session_state.selected_suggested_question):
        process_world_question(custom_question or st.session_state.selected_suggested_question)
    
    # 이전 질문 및 답변 표시
    if st.session_state.world_questions_history:
        st.markdown("<div style='margin-top: 30px; padding-top: 10px; border-top: 1px solid #3d4c63;'></div>", unsafe_allow_html=True)
        st.write("### 이전 질문 및 답변")
        
        for i, qa in enumerate(reversed(st.session_state.world_questions_history)):
            with st.expander(f"Q: {qa['question']} ({qa['timestamp']})"):
                st.markdown(qa['answer'])

def process_world_question(question):
    """세계관 질문 처리 함수"""
    # 이미 처리 중이 아닐 때만 실행
    if not st.session_state.question_processing:
        st.session_state.question_processing = True
        
        # 응답 표시할 플레이스홀더 생성
        response_placeholder = st.empty()
        response_placeholder.info("마스터가 답변을 작성 중입니다... 잠시만 기다려주세요.")
        
        # 질문 처리 및 답변 생성
        try:
            answer = master_answer_question(
                question,
                st.session_state.world_description,
                st.session_state.theme
            )
            
            # 질문과 답변을 세션 상태에 저장
            qa_pair = {
                "question": question,
                "answer": answer,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.world_questions_history.append(qa_pair)
            
            # 세계관에 질문과 답변 추가
            st.session_state.world_description += f"\n\n## 질문: {question}\n{answer}"
            
            # 단락 구분 적용
            answer_paragraphs = answer.split("\n\n")
            formatted_answer = ""
            for para in answer_paragraphs:
                formatted_answer += f"<p>{para}</p>\n"
            
            # 응답 표시
            response_placeholder.markdown(f"""
            <div style='background-color: #2d3748; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #6b8afd;'>
                <div style='font-weight: bold; margin-bottom: 5px;'>질문: {question}</div>
                <div>{formatted_answer}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 상태 초기화
            st.session_state.master_message = "질문에 답변했습니다. 더 궁금한 점이 있으신가요?"
        
        except Exception as e:
            st.error(f"응답 생성 중 오류가 발생했습니다: {e}")
            response_placeholder.error("질문 처리 중 오류가 발생했습니다. 다시 시도해주세요.")
        
        finally:
            # 처리 완료 상태로 변경
            st.session_state.question_processing = False
            st.session_state.selected_suggested_question = None
            st.session_state.custom_question_value = ''

def exploration_start_tab():
    """탐험 시작 탭 내용"""
    st.subheader("탐험 시작하기")
    
    # 설명 추가
    st.markdown("""
    <div style='background-color: #1e2636; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
        <p>모험을 시작할 지역을 선택하고 캐릭터 생성으로 진행하세요.</p>
        <p>선택한 지역은 캐릭터가 모험을 시작하는 첫 장소가 됩니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 시작 지점 선택
    if 'available_locations' in st.session_state and st.session_state.available_locations:
        st.write("#### 시작 지점 선택")
        st.write("모험을 시작할 위치를 선택하세요:")
        
        # 사용성 개선: 선택된 위치를 표시
        selected_location = st.session_state.get('current_location', '')
        
        # 시작 지점 그리드 표시
        location_cols = st.columns(3)
        for i, location in enumerate(st.session_state.available_locations):
            with location_cols[i % 3]:
                # 현재 선택된 위치인 경우 다른 스타일로 표시
                if location == selected_location:
                    st.markdown(f"""
                    <div style='background-color: #4CAF50; color: white; padding: 10px; 
                                border-radius: 5px; text-align: center; margin-bottom: 10px;'>
                        ✓ {location} (선택됨)
                    </div>
                    """, unsafe_allow_html=True)
                    # 선택 취소 버튼
                    if st.button("선택 취소", key=f"unselect_loc_{i}"):
                        st.session_state.current_location = ""
                        st.rerun()
                else:
                    if st.button(location, key=f"start_loc_{i}", use_container_width=True):
                        st.session_state.current_location = location
                        st.session_state.master_message = f"{location}에서 모험을 시작합니다. 이제 캐릭터를 생성할 차례입니다."
                        st.rerun()
    
    # 캐릭터 생성으로 이동 버튼
    st.write("#### 캐릭터 생성")
    st.write("세계를 충분히 탐색했다면, 이제 당신의 캐릭터를 만들어 모험을 시작할 수 있습니다.")
    
    # 선택된 시작 위치 없으면 경고
    if not st.session_state.get('current_location'):
        st.warning("캐릭터 생성으로 진행하기 전에 시작 지점을 선택해주세요!")
        proceed_button = st.button("캐릭터 생성으로 진행", key="to_character_creation", 
                                 use_container_width=True, disabled=True)
    else:
        proceed_button = st.button("캐릭터 생성으로 진행", key="to_character_creation", 
                                 use_container_width=True)
        if proceed_button:
            st.session_state.stage = 'character_creation'
            st.session_state.master_message = "이제 이 세계에서 모험을 떠날 당신의 캐릭터를 만들어 볼까요?"
            st.rerun()
