import streamlit as st
import time
import random
from PIL import Image, ImageDraw

# ----------------------------
# 게임 상수
# ----------------------------
GAME_WIDTH = 600
GAME_HEIGHT = 300
GROUND_Y = GAME_HEIGHT - 40

PLAYER_SIZE = 50
OBSTACLE_WIDTH = 15
OBSTACLE_HEIGHT = 12
OBSTACLE_SPEED = 5  # 기존 200에서 5로 수정 (적당한 속도)
GRAVITY = 1        # 기존 3 → 4 (더 빨리 내려옴)
JUMP_VELOCITY = -12  # 기존 -12에서 -8로 수정 (점프 높이 낮춤)

# ----------------------------
# 플레이어 스프라이트 불러오기
# ----------------------------
@st.cache_resource
def load_sprite():
    img = Image.open("dino_sprite.png").convert("RGBA")
    return img.resize((PLAYER_SIZE, PLAYER_SIZE))

PLAYER_SPRITE = load_sprite()

# ----------------------------
# 세션 상태 초기화
# ----------------------------
if "player_x" not in st.session_state:
    st.session_state.player_x = 50
if "player_y" not in st.session_state:
    st.session_state.player_y = GROUND_Y - PLAYER_SIZE
if "velocity_y" not in st.session_state:
    st.session_state.velocity_y = 0
if "obstacles" not in st.session_state:
    st.session_state.obstacles = []
if "score" not in st.session_state:
    st.session_state.score = 0
if "game_over" not in st.session_state:
    st.session_state.game_over = False

# ----------------------------
# UI 헤더
# ----------------------------
st.title("🦖 Dino-like 공룡 점프 게임")
st.caption("오른쪽에서 오는 장애물을 점프해 피하세요!")

# ----------------------------
# 게임 오버 화면
# ----------------------------
if st.session_state.game_over:
    st.header("💥 게임 오버!")
    st.subheader(f"최종 점수: {st.session_state.score}")
    if st.button("🔄 다시 시작"):
        st.session_state.player_x = 50
        st.session_state.player_y = GROUND_Y - PLAYER_SIZE
        st.session_state.velocity_y = 0
        st.session_state.obstacles = []
        st.session_state.score = 0
        st.session_state.game_over = False
    st.stop()

# ----------------------------
# 점프 버튼
# ----------------------------
if st.button("⬆️ Jump"):
    if st.session_state.player_y >= GROUND_Y - PLAYER_SIZE:
        st.session_state.velocity_y = JUMP_VELOCITY

# ----------------------------
# 물리 엔진 적용
# ----------------------------
st.session_state.velocity_y += GRAVITY
st.session_state.player_y += st.session_state.velocity_y

if st.session_state.player_y >= GROUND_Y - PLAYER_SIZE:
    st.session_state.player_y = GROUND_Y - PLAYER_SIZE
    st.session_state.velocity_y = 0

# ----------------------------
# 장애물 생성 (한 번에 한 개만)
# ----------------------------
if (not st.session_state.obstacles) or (st.session_state.obstacles[-1][0] < GAME_WIDTH - 200):
    # 장애물이 없거나, 마지막 장애물이 충분히 왼쪽으로 이동했을 때만 새 장애물 생성
    st.session_state.obstacles.append([
        GAME_WIDTH,
        GROUND_Y - OBSTACLE_HEIGHT
    ])

# 장애물 이동
new_obstacles = []
for x, y in st.session_state.obstacles:
    x -= OBSTACLE_SPEED
    if x + OBSTACLE_WIDTH > 0:
        new_obstacles.append([x, y])
st.session_state.obstacles = new_obstacles

# ----------------------------
# 충돌 감지
# ----------------------------
for ox, oy in st.session_state.obstacles:
    if (
        st.session_state.player_x + PLAYER_SIZE > ox and
        st.session_state.player_x < ox + OBSTACLE_WIDTH and
        st.session_state.player_y + PLAYER_SIZE > oy and
        st.session_state.player_y < oy + OBSTACLE_HEIGHT
    ):
        st.session_state.game_over = True

# ----------------------------
# 점수
# ----------------------------
st.session_state.score += 1
st.subheader(f"🏆 현재 점수: {st.session_state.score}")

# ----------------------------
# 이미지 합성 (Pillow)
# ----------------------------
frame = Image.new("RGBA", (GAME_WIDTH, GAME_HEIGHT), (255, 255, 255, 255))
draw = ImageDraw.Draw(frame)

# 바닥선
draw.line([(0, GROUND_Y), (GAME_WIDTH, GROUND_Y)], fill="black", width=3)

# 장애물
for ox, oy in st.session_state.obstacles:
    draw.rectangle(
        [ox, oy, ox + OBSTACLE_WIDTH, oy + OBSTACLE_HEIGHT],
        fill="red"
    )

# 플레이어 공룡 스프라이트
frame.paste(PLAYER_SPRITE, (st.session_state.player_x, st.session_state.player_y), PLAYER_SPRITE)

# 출력
st.image(frame)

# ----------------------------
# 게임 루프
# ----------------------------
time.sleep(0.05)
st.rerun()

