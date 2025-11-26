import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 페이지 기본 설정
st.set_page_config(
    page_title="함께 만드는 안전한 요리 시간",
    page_icon="🍳",
    layout="wide"
)

# ----- 간단한 스타일(글자 크게, 카드 느낌) -----
CUSTOM_CSS = """
<style>
/* 전체 배경 */
.main {
    background-color: #f8fafc;
}

/* 제목 */
h1 {
    font-size: 2.2rem !important;
}

/* 부제목 */
h2, h3 {
    font-size: 1.3rem !important;
}

/* 규칙 카드 공통 스타일 */
.rule-card {
    background-color: #ffffff;
    padding: 16px 18px;
    border-radius: 16px;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.08);
    margin-bottom: 14px;
    border-left: 8px solid #fbbf24;
}

/* 퀴즈 카드 */
.quiz-card {
    background-color: #ffffff;
    padding: 14px 16px;
    border-radius: 14px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    margin-bottom: 12px;
}

/* 큰 버튼 느낌 */
.stButton>button {
    border-radius: 999px;
    padding: 0.6rem 1.4rem;
    font-size: 1rem;
    font-weight: 600;
}

/* 사이드바 제목 크기 */
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3 {
    font-size: 1.1rem !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ----- 규칙 데이터 -----
RULES = [
    {
        "id": 1,
        "title": "요리 전에는 꼭 손을 씻어요",
        "short": "30초 이상 비누로 꼼꼼하게 손 씻기 ✋🧼",
        "detail": "손, 손목, 손톱 사이까지 깨끗하게 씻고 종이타월로 잘 닦아요.",
        "emoji": "🧼",
        "yt_query": "어린이 손 씻기 노래 손 씻는 방법"
    },
    {
        "id": 2,
        "title": "긴 머리는 묶고, 소매는 걷어요",
        "short": "머리카락과 옷이 음식에 닿지 않게 정리하기 👧👕",
        "detail": "머리는 꼭 묶고, 긴 소매는 걷어서 깔끔하게 준비해요.",
        "emoji": "🎀",
        "yt_query": "어린이 요리 교실 안전수칙 옷 차림"
    },
    {
        "id": 3,
        "title": "칼, 가위는 선생님과 함께 사용해요",
        "short": "위험한 도구는 혼자 쓰지 않기 🔪",
        "detail": "칼, 가위, 꼬치는 선생님이 옆에 있을 때만 사용해요.",
        "emoji": "🛡️",
        "yt_query": "어린이 요리 도구 안전하게 사용하기"
    },
    {
        "id": 4,
        "title": "요리할 때는 뛰지 않아요",
        "short": "부딪히거나 넘어지지 않도록 천천히 움직이기 🚫🏃",
        "detail": "주방에서는 뛰지 않고, 장난치지 않고, 줄을 서서 기다려요.",
        "emoji": "🚶",
        "yt_query": "어린이 안전수칙 주방에서 지켜야 할 것"
    },
    {
        "id": 5,
        "title": "뜨거운 것과 전기는 선생님께 먼저 말해요",
        "short": "전자레인지, 인덕션, 뜨거운 냄비는 직접 만지지 않기 🔥⚡",
        "detail": "뜨거워 보이는 것과 전기 기구는 꼭 선생님과 함께 사용해요.",
        "emoji": "🔥",
        "yt_query": "어린이 전기 안전 뜨거운 것 조심"
    },
    {
        "id": 6,
        "title": "알레르기가 있으면 꼭 알려요",
        "short": "못 먹는 음식이 있으면 선생님께 미리 말하기 🌰🥛",
        "detail": "우유, 견과류, 달걀 등 알레르기가 있으면 꼭 이야기해요.",
        "emoji": "💬",
        "yt_query": "어린이 음식 알레르기 알리기 교육"
    },
]


# ----- 퀴즈 데이터 -----
QUIZ = [
    {
        "question": "요리하기 전에 손을 씻지 않아도 괜찮아요.",
        "options": ["맞아요", "틀려요"],
        "correct_index": 1,
        "rule_id": 1
    },
    {
        "question": "긴 머리는 그냥 두고 요리해도 괜찮아요.",
        "options": ["맞아요", "틀려요"],
        "correct_index": 1,
        "rule_id": 2
    },
    {
        "question": "칼과 가위는 선생님이 안 보셔도 혼자 사용할 수 있어요.",
        "options": ["맞아요", "틀려요"],
        "correct_index": 1,
        "rule_id": 3
    },
    {
        "question": "요리 시간에는 친구들과 장난치지 않고 천천히 움직여야 해요.",
        "options": ["맞아요", "틀려요"],
        "correct_index": 0,
        "rule_id": 4
    },
    {
        "question": "알레르기가 있어도 말하지 않아도 상관없어요.",
        "options": ["맞아요", "틀려요"],
        "correct_index": 1,
        "rule_id": 6
    },
]


# ----- 유틸 함수들 -----
def get_api_key():
    """
    스트림릿 시크릿에 YOUTUBE_API_KEY가 있으면 우선 사용.
    없으면 사이드바에서 입력받은 값 사용.
    """
    default_secret = ""
    try:
        default_secret = st.secrets.get("YOUTUBE_API_KEY", "")
    except Exception:
        default_secret = ""

    st.sidebar.markdown("### 🔑 YouTube API 키 설정")
    st.sidebar.write("시크릿에 저장된 키가 없다면 여기에서 직접 입력할 수 있어요.")

    api_key_input = st.sidebar.text_input(
        "YouTube API 키",
        value=default_secret,
        type="password",
        help="스트림릿 시크릿 또는 여기 중 편한 방법으로 입력해 주세요."
    )

    api_key = api_key_input.strip() if api_key_input else ""
    if not api_key:
        st.sidebar.warning("YouTube 영상을 자동으로 찾으려면 API 키가 필요해요.")
    else:
        st.sidebar.success("YouTube API 키가 설정되었습니다.")
    return api_key


@st.cache_data(show_spinner=False)
def search_youtube_video_id(query: str, api_key: str):
    """
    YouTube 검색 API를 사용해 첫 번째 영상의 videoId를 반환.
    못 찾으면 None.
    """
    if not api_key:
        return None

    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=1,
            safeSearch="strict",
            videoEmbeddable="true"
        )
        response = request.execute()
        items = response.get("items", [])
        if not items:
            return None
        return items[0]["id"]["videoId"]
    except HttpError:
        return None
    except Exception:
        return None


def render_rule_card(rule):
    st.markdown(
        f"""
        <div class="rule-card">
            <h3>{rule["emoji"]} {rule["title"]}</h3>
            <p style="font-size: 1.05rem; margin-top: 6px;"><b>{rule["short"]}</b></p>
            <p style="font-size: 0.98rem; color: #4b5563; margin-top: 4px;">{rule["detail"]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_quiz_card(idx, quiz_item):
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.write(f"**Q{idx + 1}. {quiz_item['question']}**")
    st.radio(
        " ",
        quiz_item["options"],
        key=f"quiz_{idx}",
        horizontal=True,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)


# ----- 본문 시작 -----
api_key = get_api_key()

st.title("🍳 함께 만드는 안전한 요리 시간")
st.subheader("요리하기 전에, 안전 규칙을 먼저 익혀봐요!")

st.markdown(
    """
    오늘은 친구들과 함께 **맛있는 음식을 만드는 날**이에요.  
    요리를 시작하기 전에, 우리가 꼭 지켜야 할 **안전 규칙**을 함께 살펴보고  
    영상도 보고, 퀴즈도 풀어보면서 준비해 볼까요?
    """
)

tab1, tab2, tab3 = st.tabs(["📋 규칙 살펴보기", "🎥 영상으로 보기", "✅ 퀴즈로 확인하기"])

# ----- TAB 1: 규칙 살펴보기 -----
with tab1:
    st.markdown("### 📋 요리 시간에 지켜야 할 규칙")

    st.markdown("아래 규칙 카드들을 친구들과 한 줄씩 읽어보며 이야기해 보세요.")

    cols = st.columns(2)
    for idx, rule in enumerate(RULES):
        with cols[idx % 2]:
            render_rule_card(rule)

    st.markdown("---")
    st.markdown(
        """
        **활동 아이디어**  
        - 학생에게 가장 중요한 규칙 하나씩 골라 스티커 붙이기  
        - \"지킬 수 있어요/조금 어려워요\" 에 손들기, 이야기 나누기  
        """
    )

# ----- TAB 2: 영상으로 보기 -----
with tab2:
    st.markdown("### 🎥 규칙을 영상으로 더 알아보기")

    st.write("보고 싶은 규칙을 고르면, YouTube에서 관련 영상을 찾아서 보여줘요.")

    selected_rule = st.selectbox(
        "어떤 규칙 영상을 볼까요?",
        RULES,
        format_func=lambda r: f"{r['emoji']} {r['title']}"
    )

    if selected_rule:
        st.markdown(
            f"""
            **선택한 규칙:** {selected_rule['emoji']} {selected_rule['title']}  
            - 내용: {selected_rule['short']}  
            - 검색 키워드: `{selected_rule['yt_query']}`
            """
        )

        if not api_key:
            st.info(
                "YouTube API 키가 설정되면 이 규칙과 관련된 영상을 자동으로 불러올 수 있어요.\n\n"
                "지금은 교사가 직접 준비한 링크를 `st.video()`로 추가해서 사용해도 좋아요."
            )
        else:
            with st.spinner("YouTube에서 알맞은 영상을 찾고 있어요..."):
                video_id = search_youtube_video_id(selected_rule["yt_query"], api_key)

            if video_id:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                st.video(video_url)
                st.caption("※ 자동으로 검색된 영상이므로, 수업 전에 한 번 미리 확인해 주세요.")
            else:
                st.warning(
                    "검색 조건에 맞는 영상을 찾지 못했어요. 검색어를 조금 바꾸어 사용하는 것도 방법이에요."
                )

    st.markdown("---")
    st.markdown(
        """
        **교사용 TIP**  
        - 실제 수업에서는 미리 검토한 영상 URL을 따로 준비해 두고,  
          `st.video("https://www.youtube.com/...")` 형태로 고정하는 것도 안전해요.  
        """
    )

# ----- TAB 3: 퀴즈로 확인하기 -----
with tab3:
    st.markdown("### ✅ 나는 규칙을 잘 알고 있을까?")

    st.write("문장을 읽고 **맞아요 / 틀려요** 중에서 골라보세요.")

    for idx, quiz_item in enumerate(QUIZ):
        render_quiz_card(idx, quiz_item)

    if st.button("📊 채점하기"):
        score = 0
        for idx, quiz_item in enumerate(QUIZ):
            user_answer = st.session_state.get(f"quiz_{idx}", None)
            if user_answer is None:
                continue
            if user_answer == quiz_item["options"][quiz_item["correct_index"]]:
                score += 1

        total = len(QUIZ)
        st.markdown(f"### 결과: **{score} / {total} 점**")

        if score == total:
            st.success("완벽해요! 이제 안전하게 요리를 시작해볼 준비가 되었어요. 👏🧑‍🍳")
        elif score >= total // 2:
            st.info("거의 다 왔어요. 틀린 문제를 다시 보면서 규칙을 한 번 더 확인해 볼까요?")
        else:
            st.warning("괜찮아요. 규칙을 다시 읽고 함께 이야기 나누면서 한 번 더 도전해 봐요!")

    st.markdown("---")
    st.markdown(
        """
        **확장 활동**  
        - 학생이 직접 \"새로운 규칙\"을 생각해서 한 문장으로 만들어 보기  
        - 규칙을 그림으로 표현해서 규칙 포스터 만들기  
        """
    )
