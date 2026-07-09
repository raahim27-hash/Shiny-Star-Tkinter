import math

# ==========================
# Window
# ==========================
WIDTH = 1920
HEIGHT = 1080
FPS = 60

TITLE = "Starry Sea Flowing Light"

# ==========================
# Colors
# ==========================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Soft glow colors
GLOW1 = (255, 255, 255, 20)
GLOW2 = (255, 255, 255, 40)
GLOW3 = (255, 255, 255, 80)

# ==========================
# Heart
# ==========================
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2 - 40

HEART_SCALE = 24

HEART_POINTS = 3500

PULSE_SPEED = 2.0
PULSE_AMOUNT = 0.05

# ==========================
# Particles
# ==========================
PARTICLE_COUNT = 6000

PARTICLE_MIN_SIZE = 1.0
PARTICLE_MAX_SIZE = 3.5

PARTICLE_SPEED = 0.002

PARTICLE_ALPHA = 210

# ==========================
# Stars
# ==========================
STAR_COUNT = 500

STAR_MIN_SIZE = 1
STAR_MAX_SIZE = 3

STAR_TWINKLE_SPEED = 0.03

# ==========================
# Glow
# ==========================
GLOW_RADIUS = 18

# ==========================
# Trails
# ==========================
TRAIL_ALPHA = 20

# ==========================
# Waves
# ==========================
WAVE_COUNT = 4

WAVE_SPEED = 0.02

# ==========================
# Recording
# ==========================
VIDEO_SECONDS = 30

FRAME_TOTAL = FPS * VIDEO_SECONDS

VIDEO_NAME = "output/starry_heart.mp4"

# ==========================
# Randomness
# ==========================
SEED = None