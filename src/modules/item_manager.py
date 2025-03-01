"""
아이템 생성, 관리, 사용 관련 기능을 제공하는 모듈
"""
import re
import json
import streamlit as st
from config.constants import ITEM_TYPES, ITEM_RARITY
from modules.ai_service import generate_gemini_text

class Item:
    """게임 내 아이템 기본 클래스"""
    def __init__(self, name, description, type="일반", consumable=False, durability=None, max_durability=None, quantity=1, rarity="일반"):
        self.name = name                    # 아이템 이름
        self.description = description      # 아이템 설명
        self.type = type                    # 아이템 유형 (무기, 방어구, 소비품, 도구, 일반)
        self.consumable = consumable        # 소비성 여부 (사용 후 사라짐)
        self.durability = durability        # 현재 내구도 (None이면 내구도 없음)
        self.max_durability = max_durability or durability  # 최대 내구도
        self.quantity = quantity            # 수량
        self.rarity = rarity                # 희귀도 (일반, 희귀, 영웅, 전설)
        
    def to_dict(self):
        """아이템을 사전 형태로 변환"""
        return {
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'consumable': self.consumable,
            'durability': self.durability,
            'max_durability': self.max_durability,
            'quantity': self.quantity,
            'rarity': self.rarity
        }
    
    @classmethod
    def from_dict(cls, data):
        """사전 형태에서 아이템 객체 생성"""
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            type=data.get('type', '일반'),
            consumable=data.get('consumable', False),
            durability=data.get('durability', None),
            max_durability=data.get('max_durability', None),
            quantity=data.get('quantity', 1),
            rarity=data.get('rarity', '일반')
        )
    
    def use(self):
        """아이템 사용"""
        if self.consumable:
            if self.quantity > 1:
                self.quantity -= 1
                return f"{self.name}을(를) 사용했습니다. 남은 수량: {self.quantity}"
            else:
                return f"{self.name}을(를) 사용했습니다. 모두 소진되었습니다."
        elif self.durability is not None:
            self.durability -= 1
            if self.durability <= 0:
                return f"{self.name}의 내구도가 다 되어 사용할 수 없게 되었습니다."
            else:
                return f"{self.name}을(를) 사용했습니다. 남은 내구도: {self.durability}/{self.max_durability}"
        else:
            return f"{self.name}을(를) 사용했습니다."
    
    def get_icon(self):
        """아이템 유형에 따른 아이콘 반환"""
        return ITEM_TYPES.get(self.type, "📦")
    
    def get_rarity_color(self):
        """아이템 희귀도에 따른 색상 코드 반환"""
        return ITEM_RARITY.get(self.rarity, "#AAAAAA")
    
    def get_durability_percentage(self):
        """내구도 백분율 계산"""
        if self.durability is None or self.max_durability is None or self.max_durability <= 0:
            return 100
        return (self.durability / self.max_durability) * 100

def initialize_inventory(theme):
    """
    테마별 기본 인벤토리 초기화
    
    Args:
        theme (str): 게임 테마
        
    Returns:
        list: 기본 인벤토리 아이템 목록
    """
    inventory = []
    
    if theme == 'fantasy':
        inventory = [
            Item("기본 의류", "일반적인 모험가 복장입니다.", type="방어구", consumable=False),
            Item("여행용 가방", "다양한 물건을 담을 수 있는 가방입니다.", type="도구", consumable=False),
            Item("횃불", "어두운 곳을 밝힐 수 있습니다. 약 1시간 정도 사용 가능합니다.", type="소비품", consumable=True, quantity=3),
            Item("단검", "기본적인 근접 무기입니다.", type="무기", consumable=False, durability=20, max_durability=20),
            Item("물통", "물을 담아 갈 수 있습니다.", type="도구", consumable=False),
            Item("식량", "하루치 식량입니다.", type="소비품", consumable=True, quantity=5),
            Item("치유 물약", "체력을 회복시켜주는 물약입니다.", type="소비품", consumable=True, quantity=2, rarity="고급")
        ]
    elif theme == 'sci-fi':
        inventory = [
            Item("기본 의류", "표준 우주 여행자 복장입니다.", type="방어구", consumable=False),
            Item("휴대용 컴퓨터", "간단한 정보 검색과 해킹에 사용할 수 있습니다.", type="도구", consumable=False, durability=30, max_durability=30),
            Item("에너지 셀", "장비 작동에 필요한 에너지 셀입니다.", type="소비품", consumable=True, quantity=3),
            Item("레이저 포인터", "기본적인 레이저 도구입니다.", type="도구", consumable=False, durability=15, max_durability=15),
            Item("통신 장치", "다른 사람과 통신할 수 있습니다.", type="도구", consumable=False, durability=25, max_durability=25),
            Item("비상 식량", "우주 여행용 압축 식량입니다.", type="소비품", consumable=True, quantity=5),
            Item("의료 키트", "부상을 치료할 수 있는 기본 의료 키트입니다.", type="소비품", consumable=True, quantity=2, rarity="고급")
        ]
    else:  # dystopia
        inventory = [
            Item("작업용 의류", "튼튼하고 방호력이 있는 작업복입니다.", type="방어구", consumable=False, durability=15, max_durability=15),
            Item("가스 마스크", "유해 가스를 걸러냅니다.", type="방어구", consumable=False, durability=20, max_durability=20),
            Item("필터", "가스 마스크에 사용하는 필터입니다.", type="소비품", consumable=True, quantity=3),
            Item("생존 나이프", "다용도 생존 도구입니다.", type="무기", consumable=False, durability=25, max_durability=25),
            Item("정수 알약", "오염된 물을 정화할 수 있습니다.", type="소비품", consumable=True, quantity=5),
            Item("식량 배급 카드", "배급소에서 식량을 받을 수 있는 카드입니다.", type="도구", consumable=False),
            Item("응급 주사기", "위급 상황에서 생명 유지에 도움이 됩니다.", type="소비품", consumable=True, quantity=1, rarity="희귀")
        ]
    
    return inventory

def display_inventory(inventory):
    """
    인벤토리 아이템을 시각적으로 표시하는 함수
    
    Args:
        inventory (list): 표시할 인벤토리 아이템 목록
    """
    # 인벤토리가 비어있는 경우 처리
    if not inventory:
        st.write("인벤토리가 비어있습니다.")
        return
    
    # 아이템 유형별 분류
    categorized_items = {
        "무기": [],
        "방어구": [],
        "소비품": [],
        "도구": [],
        "마법": [],
        "기술": [],
        "일반": []
    }
    
    # 아이템을 카테고리별로 분류
    for item in inventory:
        try:
            item_type = item.type if hasattr(item, 'type') else "일반"
            if item_type in categorized_items:
                categorized_items[item_type].append(item)
            else:
                categorized_items["일반"].append(item)
        except:
            # 문자열이나 다른 형태의 아이템은 일반으로 분류
            categorized_items["일반"].append(item)
    
    # 카테고리별로 아이템 표시
    for category, items in categorized_items.items():
        if items:  # 해당 카테고리에 아이템이 있는 경우에만 표시
            # 카테고리 아이콘 선택
            category_icon = ITEM_TYPES.get(category, "📦")
            
            st.write(f"{category_icon} **{category}**")
            
            # 카테고리 내 아이템 표시 - 간소화된 버전
            for item in items:
                try:
                    # 아이템 정보 안전하게 추출
                    if hasattr(item, 'name'):
                        item_name = item.name
                        item_desc = getattr(item, 'description', '설명 없음')
                        item_quantity = getattr(item, 'quantity', 1)
                        
                        # 아이콘 가져오기
                        icon = getattr(item, 'get_icon', lambda: "📦")
                        if callable(icon):
                            icon = icon()
                            
                        # 수량 표시
                        quantity_text = f" x{item_quantity}" if item_quantity > 1 else ""
                        
                        # 단순화된 표시 방식
                        st.markdown(f"{icon} **{item_name}**{quantity_text} - {item_desc}")
                    else:
                        # 문자열 아이템
                        st.markdown(f"📦 {str(item)}")
                except Exception as e:
                    st.markdown(f"📦 {str(item)} (표시 오류: {str(e)})")

def extract_items_from_story(story_text):
    """
    스토리 텍스트에서 획득한 아이템을 자동 추출
    
    Args:
        story_text (str): 스토리 텍스트
        
    Returns:
        list: 추출된 아이템 목록
    """
    # 굵게 표시된 텍스트를 우선 추출 (** 사이의 내용)
    bold_items = re.findall(r'\*\*(.*?)\*\*', story_text)
    
    prompt = f"""
    다음 TRPG 스토리 텍스트를 분석하여 플레이어가 획득했거나 발견한 모든 아이템을 추출해주세요.
    일반적인 배경 요소가 아닌, 플레이어가 실제로 소지하거나 사용할 수 있는 아이템만 추출하세요.
    특히 굵게 표시된 아이템(**, ** 사이의 텍스트)에 주목하세요.
    
    스토리 텍스트:
    {story_text}
    
    다음 JSON 형식으로 반환해주세요:
    [
      {{
        "name": "아이템 이름",
        "description": "아이템 설명 (없으면 빈 문자열)",
        "consumable": true/false (소비성 여부, 기본값 false),
        "durability": 숫자 (내구도, 없으면 null),
        "quantity": 숫자 (수량, 기본값 1),
        "type": "아이템 유형"
      }},
      ...
    ]
    
    아이템이 없으면 빈 배열 []을 반환하세요.
    """
    
    try:
        response = generate_gemini_text(prompt, 300)
        
        # 응답에서 JSON 구조 추출 시도
        try:
            # 응답 텍스트에서 JSON 부분만 추출 시도
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                items_data = json.loads(json_match.group(0))
            else:
                # 전체 응답을 JSON으로 파싱 시도
                items_data = json.loads(response)
        except:
            # JSON 파싱 실패 시 기본 아이템 생성
            items_data = []
            for item_name in bold_items:
                items_data.append({
                    "name": item_name,
                    "description": "발견한 아이템입니다.",
                    "consumable": False,
                    "durability": None,
                    "quantity": 1,
                    "type": "일반"
                })
        
        # Item 객체 목록 생성
        items = []
        for item_data in items_data:
            items.append(Item.from_dict(item_data))
        
        # 굵게 표시된 아이템이 있지만 JSON에 포함되지 않은 경우 추가
        existing_names = [item.name for item in items]
        for bold_item in bold_items:
            if bold_item not in existing_names:
                items.append(Item(
                    name=bold_item,
                    description="발견한 아이템입니다.",
                    consumable=False,
                    quantity=1
                ))
        
        return items
    
    except Exception as e:
        st.error(f"아이템 추출 오류: {e}")
        # 오류 시 기본 아이템 생성
        items = []
        for item_name in bold_items:
            items.append(Item(
                name=item_name,
                description="발견한 아이템입니다.",
                consumable=False,
                quantity=1
            ))
        return items

def extract_used_items_from_story(story_text, inventory):
    """
    스토리 텍스트에서 사용한 아이템 추출
    
    Args:
        story_text (str): 스토리 텍스트
        inventory (list): 현재 인벤토리
        
    Returns:
        list: 사용된 아이템 데이터
    """
    # 인벤토리 아이템 이름 목록 생성
    inventory_names = [item.name if hasattr(item, 'name') else str(item) for item in inventory]
    
    # 굵게 표시된 텍스트를 우선 추출 (** 사이의 내용)
    bold_items = re.findall(r'\*\*(.*?)\*\*', story_text)
    
    prompt = f"""
    다음 TRPG 스토리 텍스트를 분석하여 플레이어가 사용한 아이템을 추출해주세요.
    특히 굵게 표시된 아이템(**, ** 사이의 텍스트)에 주목하세요.
    
    인벤토리에 있는 아이템: {', '.join(inventory_names)}
    
    스토리 텍스트:
    {story_text}
    
    다음 JSON 형식으로 반환해주세요:
    [
      {{
        "name": "아이템 이름",
        "quantity": 사용한 수량 (기본값 1)
      }},
      ...
    ]
    
    아무 아이템도 사용하지 않았다면 빈 배열 []을 반환하세요.
    """
    
    try:
        response = generate_gemini_text(prompt, 200)
        
        # 응답에서 JSON 구조 추출 시도
        try:
            # 응답 텍스트에서 JSON 부분만 추출 시도
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                used_items_data = json.loads(json_match.group(0))
            else:
                # 전체 응답을 JSON으로 파싱 시도
                used_items_data = json.loads(response)
        except:
            # JSON 파싱 실패 시 기본 데이터 생성
            used_items_data = []
            for item_name in bold_items:
                if item_name in inventory_names:
                    used_items_data.append({
                        "name": item_name,
                        "quantity": 1
                    })
        
        # 사용된 아이템 데이터 필터링 (인벤토리에 있는 아이템만)
        filtered_items_data = []
        for item_data in used_items_data:
            if item_data["name"] in inventory_names:
                filtered_items_data.append(item_data)
        
        # 굵게 표시된 아이템이 있지만 JSON에 포함되지 않은 경우 추가
        existing_names = [item["name"] for item in filtered_items_data]
        for bold_item in bold_items:
            if bold_item in inventory_names and bold_item not in existing_names:
                filtered_items_data.append({
                    "name": bold_item,
                    "quantity": 1
                })
        
        return filtered_items_data
    
    except Exception as e:
        st.error(f"사용된 아이템 추출 오류: {e}")
        # 오류 시 기본 데이터 생성
        used_items_data = []
        for item_name in bold_items:
            if item_name in inventory_names:
                used_items_data.append({
                    "name": item_name,
                    "quantity": 1
                })
        return used_items_data

def update_inventory(action, item_data, inventory):
    """
    인벤토리 아이템 추가/제거/사용
    
    Args:
        action (str): 'add', 'use', 'remove' 중 하나
        item_data (Item, dict, str): 추가/사용/제거할 아이템 정보
        inventory (list): 현재 인벤토리
        
    Returns:
        str: 작업 결과 메시지
    """
    if action == "add":
        # 새 아이템인 경우
        if isinstance(item_data, Item):
            item = item_data
        else:
            # 딕셔너리 형태로 전달된 경우
            if isinstance(item_data, dict):
                item = Item.from_dict(item_data)
            else:
                # 문자열인 경우
                item = Item(name=str(item_data), description="획득한 아이템입니다.")
        
        # 기존 아이템인지 확인
        for existing_item in inventory:
            if hasattr(existing_item, 'name') and existing_item.name == item.name:
                # 유형이 같은지 확인 (다른 유형이면 별도 아이템으로 처리)
                existing_type = getattr(existing_item, 'type', '일반')
                new_type = getattr(item, 'type', '일반')
                
                if existing_type == new_type:
                    # 수량 증가
                    existing_item.quantity += item.quantity
                    return f"**{item.name}** {item.quantity}개가 추가되었습니다. (총 {existing_item.quantity}개)"
        
        # 새 아이템 추가
        inventory.append(item)
        quantity_text = f" {item.quantity}개" if item.quantity > 1 else ""
        return f"새 아이템 **{item.name}**{quantity_text}을(를) 획득했습니다!"
    
    elif action == "use":
        # 아이템 사용 (소비성 아이템 소모 또는 내구도 감소)
        if isinstance(item_data, dict):
            item_name = item_data.get("name", "")
            quantity = item_data.get("quantity", 1)
        else:
            item_name = str(item_data)
            quantity = 1
        
        for i, item in enumerate(inventory):
            item_n = item.name if hasattr(item, 'name') else str(item)
            if item_n == item_name:
                # 소비성 아이템인지 확인
                if hasattr(item, 'consumable') and item.consumable:
                    # 소비성 아이템 수량 감소
                    if item.quantity <= quantity:
                        # 모두 소모
                        removed_item = inventory.pop(i)
                        return f"**{removed_item.name}**을(를) 모두 사용했습니다."
                    else:
                        # 일부 소모
                        item.quantity -= quantity
                        return f"**{item.name}** {quantity}개를 사용했습니다. (남은 수량: {item.quantity})"
                
                # 내구도 있는 아이템인지 확인
                elif hasattr(item, 'durability') and item.durability is not None:
                    # 내구도 감소
                    item.durability -= 1
                    if item.durability <= 0:
                        # 내구도 소진으로 파괴
                        removed_item = inventory.pop(i)
                        return f"**{removed_item.name}**의 내구도가 다 되어 사용할 수 없게 되었습니다."
                    else:
                        # 내구도 감소
                        max_durability = getattr(item, 'max_durability', item.durability)
                        return f"**{item.name}**의 내구도가 감소했습니다. (남은 내구도: {item.durability}/{max_durability})"
                else:
                    # 일반 아이템 사용 (변화 없음)
                    return f"**{item.name}**을(를) 사용했습니다."
        
        return f"**{item_name}**이(가) 인벤토리에 없습니다."
    
    elif action == "remove":
        # 아이템 제거
        if isinstance(item_data, dict):
            item_name = item_data.get("name", "")
        else:
            item_name = str(item_data)
        
        for i, item in enumerate(inventory):
            item_n = item.name if hasattr(item, 'name') else str(item)
            if item_n == item_name:
                removed_item = inventory.pop(i)
                item_name = removed_item.name if hasattr(removed_item, 'name') else str(removed_item)
                return f"**{item_name}**을(를) 인벤토리에서 제거했습니다."
        
        return f"**{item_name}**이(가) 인벤토리에 없습니다."
    
    return "아이템 작업에 실패했습니다."

def display_item_notification(notification):
    """
    아이템 관련 알림 표시 - 더 눈에 띄게 개선
    
    Args:
        notification (str): 표시할 알림 텍스트
    """
    if notification:
        # 아이템 이름 강조를 위한 정규식 처리
        import re
        # 아이템 이름을 추출하여 강조 처리
        highlighted_notification = notification
        item_names = re.findall(r'아이템: (.*?)(,|$|\))', notification)
        
        for item_name in item_names:
            # 아이템 이름에 강조 스타일 적용 (더 눈에 띄게 수정)
            highlighted_notification = highlighted_notification.replace(
                item_name[0], 
                f'<span style="color: #FFD700; font-weight: bold; background-color: rgba(255, 215, 0, 0.2); padding: 3px 6px; border-radius: 3px; box-shadow: 0 0 5px rgba(255, 215, 0, 0.3);">{item_name[0]}</span>'
            )
        
        # 획득/사용 키워드에 더 눈에 띄는 스타일 적용
        highlighted_notification = highlighted_notification.replace(
            "획득한 아이템", 
            '<span style="color: #4CAF50; font-weight: bold; background-color: rgba(76, 175, 80, 0.1); padding: 2px 5px; border-radius: 3px;">🆕 획득한 아이템</span>'
        ).replace(
            "사용한 아이템", 
            '<span style="color: #FF9800; font-weight: bold; background-color: rgba(255, 152, 0, 0.1); padding: 2px 5px; border-radius: 3px;">⚙️ 사용한 아이템</span>'
        )
        
        st.markdown(f"""
        <div class='item-notification' style="animation: pulse 2s infinite; background-color: #2a3549; padding: 18px; border-radius: 8px; margin: 18px 0; border-left: 8px solid #FFD700; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 2rem; margin-right: 15px;">🎁</div>
                <div style="font-size: 1.1rem;">{highlighted_notification}</div>
            </div>
        </div>
        <style>
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0px rgba(255, 215, 0, 0.3); transform: scale(1); }}
            50% {{ box-shadow: 0 0 10px 3px rgba(255, 215, 0, 0.2); transform: scale(1.01); }}
            100% {{ box-shadow: 0 0 0 0px rgba(255, 215, 0, 0.3); transform: scale(1); }}
        }}
        </style>
        """, unsafe_allow_html=True)