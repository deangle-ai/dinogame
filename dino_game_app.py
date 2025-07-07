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
OBSTACLE_SPEED = 5
GRAVITY = 1
JUMP_VELOCITY = -12

# ----------------------------
# 이미지 로드 함수
# ----------------------------
def load_player_sprite():
    img = Image.open("dino_sprite.png").convert("RGBA")
    return img.resize((PLAYER_SIZE, PLAYER_SIZE))

def load_background_image():
    # PNG 배경 → RGBA로 불러서 투명도 유지
    bg = Image.open("background_space.png").convert("RGBA")
    return bg.resize((GAME_WIDTH, GAME_HEIGHT))

PLAYER_SPRITE = load_player_sprite()
BACKGROUND_IMAGE = load_background_image()

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
st.caption("🌌 background_space.png 별자리 배경 위에서 장애물을 넘자!")

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
# ✔️ PNG 배경은 이미 RGBA → 복사해서 베이스로 사용
frame = BACKGROUND_IMAGE.copy()
draw = ImageDraw.Draw(frame)

# 바닥선
draw.line([(0, GROUND_Y), (GAME_WIDTH, GROUND_Y)], fill="white", width=3)

# 장애물
for ox, oy in st.session_state.obstacles:
    draw.rectangle(
        [ox, oy, ox + OBSTACLE_WIDTH, oy + OBSTACLE_HEIGHT],
        fill="red"
    )

# 플레이어 공룡 스프라이트
frame.paste(PLAYER_SPRITE, (st.session_state.player_x, st.session_state.player_y), PLAYER_SPRITE)

# 최종 출력 → RGB로 변환 (알파채널 제거)
final_frame = frame.convert("RGB")

# ----------------------------
# 출력 (placeholder로 중복 방지)
# ----------------------------
placeholder = st.empty()
placeholder.image(final_frame)

time.sleep(0.05)
placeholder.empty()
st.experimental_rerun()
