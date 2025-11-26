import streamlit as st
import random
from googleapiclient.discovery import build

# --- 페이지 설정 ---
st.set_page_config(page_title="즐거운 수학 놀이", page_icon="🎈", layout="centered")

# --- 세션 상태 초기화 (점수, 문제 유지 등을 위함) ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'problem' not in st.session_state:
    st.session_state.problem = None
if 'show_reward' not in st.session_state:
    st.session_state.show_reward = False

# --- 함수 정의 ---

def get_youtube_video(api_key, query):
    """유튜브 API를 사용하여 검색어에 맞는 첫 번째 영상 ID를 가져옵니다."""
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.search().list(
            part="snippet",
            maxResults=1,
            q=query,
            type="video"
        )
        response = request.execute()
        if response['items']:
            return response['items'][0]['id']['videoId']
        else:
            return None
    except Exception as e:
        st.error(f"유튜브 키를 확인해주세요: {e}")
        return None

def generate_problem():
    """새로운 가르기/모으기 문제를 생성합니다."""
    # 1~5 사이의 숫자로 구성 (합이 10 이하)
    num1 = random.randint(1, 5)
    num2 = random.randint(1, 5)
    total = num1 + num2
    
    # 모드 결정 (0: 모으기, 1: 가르기)
    mode = random.choice(['gather', 'split'])
    
    # 이모지 랜덤 선택 (흥미 유발)
    emoji = random.choice(['🍎', '🍌', '🐶', '🐱', '⭐', '🚗', '🎈'])
    
    st.session_state.problem = {
        'num1': num1,
        'num2': num2,
        'total': total,
        'mode': mode,
        'emoji': emoji
    }

# --- 사이드바 설정 (선생님 전용) ---
with st.sidebar:
    st.header("⚙️ 선생님 설정")
    st.write("아이들이 좋아할 보상을 설정해주세요.")
    
    youtube_api_key = st.text_input("유튜브 API 키 입력", type="password")
    reward_keyword = st.text_input("보상 영상 검색어", value="뽀로로 노래")
    goal_score = st.number_input("목표 점수 (몇 개 맞추면 볼까요?)", min_value=1, value=5)
    
    if st.button("점수 초기화"):
        st.session_state.score = 0
        st.session_state.show_reward = False
        generate_problem()
        st.rerun()

    st.info("※ API 키가 없으면 영상은 나오지 않고 축하 메시지만 나옵니다.")

# --- 메인 화면 ---
st.title("🎈 즐거운 숫자 놀이 🎈")

# 목표 달성 시 화면
if st.session_state.score >= goal_score:
    st.balloons()
    st.success(f"와아! {goal_score}개를 모두 맞췄어요! 참 잘했어요! 👏")
    st.markdown("### 🎁 선물 영상이 도착했어요!")
    
    if youtube_api_key:
        video_id = get_youtube_video(youtube_api_key, reward_keyword)
        if video_id:
            st.video(f"https://www.youtube.com/watch?v={video_id}")
        else:
            st.warning("영상을 찾을 수 없어요. API 키나 검색어를 확인해주세요.")
    else:
        st.image("https://media.giphy.com/media/l41Yh18f5TDiOKGdl/giphy.gif", caption="축하해요!")

    if st.button("다시 시작하기"):
        st.session_state.score = 0
        st.session_state.show_reward = False
        generate_problem()
        st.rerun()

# 문제 풀이 화면
else:
    # 문제가 없으면 생성
    if st.session_state.problem is None:
        generate_problem()
    
    p = st.session_state.problem
    current_emoji = p['emoji']
    
    # 진행 상황 표시 (프로그레스 바)
    progress = st.session_state.score / goal_score
    st.progress(progress)
    st.write(f"현재 점수: {st.session_state.score} / {goal_score}")

    st.markdown("---")

    # 1. 모으기 문제 (A + B = ?)
    if p['mode'] == 'gather':
        st.header(f"❓ 모두 모으면 몇 개일까요?")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.markdown(f"<h1 style='text-align: center;'>{current_emoji * p['num1']}</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center;'>{p['num1']}</h3>", unsafe_allow_html=True)
        with col2:
            st.markdown("<h1 style='text-align: center;'>+</h1>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<h1 style='text-align: center;'>{current_emoji * p['num2']}</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center;'>{p['num2']}</h3>", unsafe_allow_html=True)
        
        correct_answer = p['total']

    # 2. 가르기 문제 (Total - A = ?)
    else:
        st.header(f"❓ 빈 칸에 들어갈 숫자는?")
        
        # 전체 보여주기
        st.markdown(f"<div style='text-align: center; font-size: 20px;'>전체: {current_emoji * p['total']} ({p['total']})</div>", unsafe_allow_html=True)
        st.markdown("---")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.markdown(f"<h1 style='text-align: center;'>{current_emoji * p['num1']}</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center;'>{p['num1']}</h3>", unsafe_allow_html=True)
        with col2:
            st.markdown("<h1 style='text-align: center;'>와</h1>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<h1 style='text-align: center;'>❓</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center;'>?</h3>", unsafe_allow_html=True)
            
        correct_answer = p['num2']

    st.markdown("---")
    
    # 정답 입력 받기 (폼을 사용하여 엔터키 입력 가능하게 함)
    with st.form(key='answer_form'):
        user_input = st.number_input("정답을 숫자로 입력하세요:", min_value=0, max_value=20, step=1)
        submit_button = st.form_submit_button(label='정답 확인! 🚀')

    if submit_button:
        if user_input == correct_answer:
            st.success("딩동댕! 정답입니다! 🎉")
            st.session_state.score += 1
            generate_problem() # 다음 문제 생성
            st.rerun() # 화면 갱신
        else:
            st.error("땡! 다시 한 번 세어볼까요? 힘내세요! 💪")
