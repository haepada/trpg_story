# 로컬 TRPG 메이커 프로젝트 구조

이제까지 작성된 코드를 기반으로 전체 프로젝트의 구조를 정리하겠습니다. 각 파일과 함수들의 관계와 역할을 체계적으로 설명하겠습니다.

## 프로젝트 폴더 구조

```
📂 src/
├── config/                       # 환경 설정
│   ├── constants.py              # 상수 정의
│   └── styles.py                 # UI 스타일 정의
├── modules/                      # 기능 모듈
│   ├── ai_service.py             # AI 서비스 연동
│   ├── character_creation.py     # 캐릭터 생성 기능
│   ├── character_utils.py        # 캐릭터 관련 유틸리티
│   ├── game_play.py              # 게임 플레이 기능
│   ├── item_manager.py           # 아이템 관리 기능
│   └── world_description.py      # 세계관 설명 기능
├── utils/                        # 유틸리티 함수
│   ├── dice_roller.py            # 주사위 굴림 기능
│   ├── location_manager.py       # 위치 관리 기능
│   ├── session_manager.py        # 세션 상태 관리
│   └── theme_manager.py          # 테마 관리 기능
└── main.py                       # 메인 애플리케이션
```

## 파일별 주요 기능

### main.py
- 애플리케이션의 진입점
- 전체 UI 레이아웃 구성 및 단계 흐름 제어
- 세션 상태 초기화 및 관리
- 현재 단계(stage)에 따른 UI 표시 로직

### config/constants.py
- 애플리케이션 전반에서 사용되는 상수 정의
- 통합된 상수 관리로 일관성 유지
- 주요 상수: 스텟 이름, 테마 유형, AI 서비스 설정 등

### config/styles.py
- UI 스타일 관련 CSS 정의
- 일관된 디자인 시스템 유지
- 주요 스타일: 카드, 버튼, 패널, 알림 등의 스타일 정의

### modules/ai_service.py
- AI 서비스 연동 기능
- 주요 함수:
  - `setup_gemini()`: AI 모델 초기화
  - `generate_gemini_text()`: AI 모델로 텍스트 생성
  - `generate_world_description()`: 세계관 생성
  - `generate_character_options()`: 캐릭터 배경 옵션 생성
  - `generate_story_response()`: 주사위 결과에 따른 스토리 생성
  - `get_ability_suggestion()`: 행동에 적합한 능력치 제안
  - `master_answer_game_question()`: 마스터 질문 응답 생성

### modules/character_creation.py
- 캐릭터 생성 관련 기능
- 주요 함수:
  - `initialize_character_creation_state()`: 캐릭터 생성 상태 초기화
  - `display_character_creation_page()`: 캐릭터 생성 페이지 표시
  - `display_race_selection()`: 종족 선택 UI 표시
  - `display_profession_selection()`: 직업 선택 UI 표시
  - `display_background_selection()`: 배경 선택 UI 표시
  - `display_abilities_selection()`: 능력치 설정 UI 표시
  - `ability_roll_section()`: 주사위 굴림 기반 능력치 생성
  - `base_abilities_section()`: 기본 능력치 설정
  - `display_character_review()`: 캐릭터 최종 확인

### modules/character_utils.py
- 캐릭터 관련 유틸리티 함수
- 주요 함수:
  - `generate_races()`: 테마별 종족 목록 생성
  - `generate_professions()`: 테마별 직업 목록 생성
  - `extract_background_tags()`: 배경 스토리에서 태그 추출
  - `get_stat_info()`: 능력치 정보 및 시각적 표현 제공
  - `generate_special_trait()`: 캐릭터 특별 특성 생성

### modules/game_play.py
- 게임 플레이 핵심 기능
- 주요 함수:
  - `initialize_game_state()`: 게임 상태 초기화
  - `display_game_play_page()`: 게임 플레이 페이지 표시
  - `display_character_panel()`: 캐릭터 정보 패널 표시
  - `display_story_and_actions()`: 스토리 및 행동 UI 표시
  - `handle_action_phase()`: 행동 단계 관리
  - `handle_movement()`: 위치 이동 처리
  - `handle_ability_check()`: 능력치 판정 처리
  - `handle_action_suggestions()`: 행동 제안 관리
  - `handle_story_progression()`: 스토리 진행 처리
  - `display_game_tools()`: 게임 도구 패널 표시
  - `display_master_question_ui()`: 마스터 질문 UI 표시

### modules/item_manager.py
- 아이템 관리 기능
- 주요 함수 및 클래스:
  - `Item` 클래스: 아이템 데이터 및 메서드 정의
  - `initialize_inventory()`: 테마별 기본 인벤토리 초기화
  - `display_inventory()`: 인벤토리 아이템 표시
  - `display_inventory_for_review()`: 캐릭터 검토용 인벤토리 표시
  - `extract_items_from_story()`: 스토리에서 아이템 추출
  - `extract_used_items_from_story()`: 사용된 아이템 추출
  - `update_inventory()`: 인벤토리 아이템 추가/제거/사용

### modules/world_description.py
- 세계관 설명 관련 기능
- 주요 함수:
  - `world_description_page()`: 세계관 설명 페이지 표시
  - `process_question()`: 세계관 질문 처리
  - `handle_world_expansion()`: 세계관 확장 처리

### utils/dice_roller.py
- 주사위 관련 유틸리티
- 주요 함수:
  - `roll_dice()`: 기본 주사위 굴림
  - `calculate_dice_result()`: 주사위 표현식 계산
  - `display_dice_animation()`: 주사위 굴림 애니메이션

### utils/location_manager.py
- 위치 관련 유틸리티
- 주요 함수:
  - `generate_locations()`: 테마별 위치 생성
  - `generate_movement_story()`: 이동 스토리 생성
  - `get_location_image()`: 위치 이미지 생성

### utils/session_manager.py
- 세션 상태 관리 유틸리티
- 주요 함수:
  - `reset_game_session()`: 게임 세션 초기화
  - `initialize_session_state()`: 세션 상태 초기화

### utils/theme_manager.py
- 테마 관련 유틸리티
- 주요 함수:
  - `create_theme_image()`: 테마별 이미지 생성
  - `get_theme_description()`: 테마 설명 제공

## 주요 기능 흐름

1. **초기화 및 메인 UI**: `main.py`에서 시작하여 각 모듈 초기화
2. **테마 선택**: 사용자가 테마 선택 → `theme_manager.py`의 함수 활용
3. **세계관 생성**: `ai_service.py`를 통해 세계관 생성
4. **세계관 탐색**: `world_description.py`를 통해 세계관 확장 및 질문 처리
5. **캐릭터 생성**: `character_creation.py`의 단계별 함수를 통해 캐릭터 생성
6. **게임 플레이**: `game_play.py`를 통해 스토리 진행, 행동 처리, 능력치 판정 등

## 개선된 설계 특징

1. **모듈화**: 기능별로 명확히 분리된 모듈로 유지보수성 향상
2. **단일 책임 원칙**: 각 모듈과 함수가 명확한 하나의 책임을 가짐
3. **상태 관리**: 세션 상태를 효율적으로 관리하여 일관된 사용자 경험 제공
4. **UI/비즈니스 로직 분리**: 표시 로직과 비즈니스 로직을 분리
5. **확장성**: 새로운 기능, 테마, 아이템 등을 쉽게 추가할 수 있는 구조
6. **재사용성**: 공통 유틸리티 함수를 통해 코드 중복 제거

이 구조는 기존의 단일 파일 애플리케이션(app.py)에 비해 훨씬 더 체계적이고 유지보수하기 쉬운 코드베이스를 제공합니다. 각 모듈은 독립적으로 테스트하고 개발할 수 있으며, 전체 시스템의 복잡성을 관리하기 쉽게 합니다.