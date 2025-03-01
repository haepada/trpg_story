import streamlit as st

def apply_custom_styles():
    """애플리케이션에 커스텀 CSS 스타일 적용"""
    st.markdown("""
    <style>
        /* 기본 스타일 */
        .main {
            background-color: #151a28;
            color: #d0d0d0;
        }
        
        /* 버튼 스타일 */
        .stButton>button {
            background-color: #4b5d78;
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
        
        /* 캐릭터 패널 스타일 */
        .character-panel {
            background-color: #1e2636;
            padding: 15px;
            border-radius: 5px;
            height: 100%;
            margin-bottom: 15px;
        }
        
        /* 스탯 박스 스타일 */
        .stat-box {
            background-color: #2a3549;
            padding: 8px 12px;
            border-radius: 5px;
            margin: 5px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .stat-name {
            font-weight: bold;
            color: #e0e0ff;
        }
        
        .stat-value {
            font-weight: bold;
            color: #ffcc00;
            font-size: 1.2rem;
        }
        
        /* 카드 스타일 */
        .theme-card {
            background-color: #2a3549;
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
            cursor: pointer;
            transition: transform 0.3s;
        }
        
        .theme-card:hover {
            transform: scale(1.05);
        }
        
        /* 옵션 카드 스타일 */
        .option-card {
            background-color: #2a3549;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            cursor: pointer;
            transition: transform 0.2s;
            border-left: 3px solid #4a90e2;
        }
        
        .option-card:hover {
            transform: translateX(5px);
            background-color: #344261;
        }
        
        h1, h2, h3 {
            color: #e0e0ff;
        }
        .dice-result {
            font-size: 3rem;
            text-align: center;
            color: #ffcc00;
            font-weight: bold;
            margin: 10px 0;
        }
        .player-section {
            border-top: 2px solid #3d4c63;
            padding-top: 10px;
            margin-top: 15px;
        }
        .suggested-action {
            margin: 5px 0;
            padding: 10px;
            background-color: #2a3549;
            border-radius: 5px;
            cursor: pointer;
        }
        .suggested-action:hover {
            background-color: #344261;
        }
        
        .item-action {
            margin: 5px 0;
            padding: 10px;
            background-color: #2a3549;
            border-radius: 5px;
            cursor: pointer;
            border-left: 4px solid #ffcc00;
        }
        .item-notification {
            background-color: #2a3549;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            border-left: 4px solid #ffcc00;
            animation: fadeIn 1s;
        }
        .item-action:hover {
            background-color: #344261;
        }
        .qa-section {
            margin-top: 15px;
            padding: 10px;
            background-color: #1e2636;
            border-radius: 5px;
        }
        .question {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .answer {
            margin-left: 10px;
            margin-bottom: 15px;
        }
        .theme-box {
            width: 300px;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .check-result {
            background-color: #2a3549;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .success {
            color: #4CAF50;
            font-weight: bold;
        }
        .failure {
            color: #F44336;
            font-weight: bold;
        }
        /* 상태창 UI 개선 */
        .stat-box {
            background-color: #2a3549;
            padding: 8px 12px;
            border-radius: 5px;
            margin: 5px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .stat-name {
            font-weight: bold;
            color: #e0e0ff;
        }
        .stat-value {
            font-weight: bold;
            color: #ffcc00;
            font-size: 1.2rem;
        }
        .inventory-item {
            background-color: #2a3549;
            padding: 8px 12px;
            border-radius: 5px;
            margin: 5px 0;
            display: flex;
            align-items: center;
        }
        .inventory-item:before {
            content: "•";
            color: #4a90e2;
            font-size: 1.2rem;
            margin-right: 8px;
        }
        .location-button {
            margin: 5px 0;
            padding: 8px 12px;
            background-color: #3d4c63;
            color: white;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.2s;
            text-align: center;
        }
        .location-button:hover {
            background-color: #4b5d78;
        }
        /* 주사위 애니메이션 개선 */
        @keyframes dice-roll {
            0% { transform: rotate(0deg) translateY(0px); }
            25% { transform: rotate(90deg) translateY(-20px); }
            50% { transform: rotate(180deg) translateY(0px); }
            75% { transform: rotate(270deg) translateY(-10px); }
            100% { transform: rotate(360deg) translateY(0px); }
        }
        .dice-animation {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 150px;
        }
        .dice-rolling {
            font-size: 4rem;
            color: #ffcc00;
            animation: dice-roll 1s ease-out;
        }
        .previous-story {
            background-color: #1e2636;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #6b8afd;
            opacity: 0.8;
        }
        .continuation-box {
            background-color: #2d3748;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            border: 2px solid #6b8afd;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .item-action {
            margin: 5px 0;
            padding: 10px;
            background-color: #2a3549;
            border-radius: 5px;
            cursor: pointer;
        }
        .item-acquire {
            border-left: 4px solid #ffcc00;
        }
        .item-use {
            border-left: 4px solid #4CAF50;
        }
        .item-action:hover {
            background-color: #344261;
        }
        .action-number {
            font-weight: bold;
            display: inline-block;
            margin-right: 10px;
            color: #ffcc00;
        }
        .action-text {
            display: inline-block;
        }
        .story-continuation {
            background-color: #1e2636;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #4CAF50;
        }
        .world-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
        }
        .world-action-button {
            flex-grow: 1;
            min-width: 150px;
        }
        .question-box {
            background-color: #2a3549;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #ffcc00;
        }
        .loading-spinner {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px;
            margin: 20px 0;
        }
        .loading-text {
            color: #6b8afd;
            font-weight: bold;
            margin-left: 10px;
        }
        
        /* 선택된 버튼 스타일 */
        .selected-button {
            background-color: #4CAF50 !important;
            color: white !important;
            border-left: 4px solid #FFFFFF !important;
            transform: translateX(5px);
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
        }
        
        /* 질문/선택지 선택 후 표시되는 버튼 강조 */
        .action-button {
            background-color: #4b5d78 !important;
            color: white !important;
            font-weight: bold !important;
            padding: 0.8rem !important;
            border-radius: 5px !important;
            margin-top: 10px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        }
        
        .action-button:hover {
            background-color: #3a4a5e !important;
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2) !important;
            transform: translateY(-2px) !important;
        }
        
        .primary-action-button {
            background-color: #6b8afd !important;
            color: white !important;
            font-weight: bold !important;
            padding: 0.8rem !important;
            border-radius: 5px !important;
            margin-top: 10px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(107, 138, 253, 0.3) !important;
        }
        
        .primary-action-button:hover {
            background-color: #5a79ec !important;
            box-shadow: 0 6px 8px rgba(107, 138, 253, 0.4) !important;
            transform: translateY(-2px) !important;
        }
        
        /* 선택된 질문/옵션 스타일 */
        .selected-option {
            background-color: #344261 !important;
            border-left: 4px solid #6b8afd !important;
            transform: translateX(5px);
            transition: all 0.3s ease;
        }
        
        /* 선택된 행동 스타일 */
        .selected-action {
            background-color: #344261 !important;
            border-left: 4px solid #ffcc00 !important;
            transform: translateX(5px);
        }
        
        /* 마스터 텍스트 스타일 */
        .master-text {
            background-color: #2a3549;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            border-left: 4px solid #6b8afd;
        }
        
        /* 스토리 텍스트 스타일 */
        .story-text {
            background-color: #1e2636;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            line-height: 1.6;
        }
    </style>
    """, unsafe_allow_html=True)