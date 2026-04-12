# settings.py — All game constants and configuration

# ── Screen ──────────────────────────────────────────────
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_TITLE = "Fuck My Sheepo Life"

# ── Colors ──────────────────────────────────────────────
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)         # Grass
DARK_GREEN = (20, 100, 20)    # Bush
SKY_BLUE = (135, 206, 235)    # Background
POND_BLUE = (64, 164, 223)
FIRE_ORANGE = (255, 100, 0)
FIRE_RED = (255, 30, 30)
WOOL_WHITE = (245, 245, 245)
WOOL_POOFY = (255, 255, 220)  # Yellowish tint when too wooly
SHEEPO_BODY = (240, 240, 240)
SHEEPO_FACE = (60, 60, 60)
BEE_YELLOW = (255, 220, 0)
BEE_BLACK = (40, 40, 40)
SUN_YELLOW = (255, 230, 50)
NIHILIST_COLOR = (80, 80, 80)
UI_BG = (40, 40, 40, 180)    # Semi-transparent dark
UI_TEXT = (255, 255, 255)
DGAF_GRAY = (150, 150, 150)
OVERLAY_DARK = (0, 0, 0, 120) # Screen darkening overlay
TOOLBAR_BG = (50, 45, 40)
TOOLBAR_BORDER = (120, 110, 100)
BUCKET_BLUE = (80, 140, 220)
CLIPPER_SILVER = (180, 180, 190)

# ── Sheepo ──────────────────────────────────────────────
SHEEPO_SIZE = (48, 48)
SHEEPO_SPEED = 40             # Pixels per second
SHEEPO_WANDER_PAUSE_MIN = 1.0 # Seconds
SHEEPO_WANDER_PAUSE_MAX = 4.0
SHEEPO_WANDER_DIST_MIN = 20   # Pixels
SHEEPO_WANDER_DIST_MAX = 80
SHEEPO_CENTER_BOUNDS = (       # Rectangle Sheepo stays within
    SCREEN_WIDTH * 0.25,
    SCREEN_HEIGHT * 0.2,
    SCREEN_WIDTH * 0.5,
    SCREEN_HEIGHT * 0.45,
)

# ── Wool ────────────────────────────────────────────────
WOOL_STAGE_NORMAL = 0
WOOL_STAGE_WOOLY = 1
WOOL_STAGE_TOO_WOOLY = 2

WOOL_NORMAL_DURATION = 15.0    # Seconds before going wooly
WOOL_WOOLY_DURATION = 5.0     # Seconds of warning before too wooly
# Too wooly = game over (no duration, it's instant death)

# ── Fire ────────────────────────────────────────────────
FIRE_TIMER = 5.0               # Seconds to extinguish before game over

# ── DGAF ────────────────────────────────────────────────
DGAF_BASE_REFUSE_CHANCE = 0.5  # 50% per stack, formula: 1 - (0.5 ^ stacks)
DGAF_BUBBLE_DURATION = 1.5     # How long "ya i dont even gaf bro" shows
DGAF_TEXT = "ya i dont even gaf bro"

# ── Bee ─────────────────────────────────────────────────
BEE_SIZE = (24, 24)
BEE_SPEED = 180                # Pixels per second — fast!
BEE_INITIAL_INTERVAL = 5.0    # Seconds between bee spawns
BEE_MIN_INTERVAL = 1.5        # Fastest bee spawn rate

# ── Sun ─────────────────────────────────────────────────
SUN_SIZE = (64, 64)
SUN_APPROACH_SPEED = 15        # Pixels per second — very slow
SUN_FIRE_THRESHOLD_X = SCREEN_WIDTH * 0.75  # X position that triggers fire
SUN_FIRE_THRESHOLD_Y = SCREEN_HEIGHT * 0.05
SUN_ESCAPE_SPEED = 300         # Pixels per second — hastily exits
SUN_INITIAL_COOLDOWN = 20.0    # First appearance delay
SUN_FIRST_RETURN = 5.0        # Seconds after first exit
SUN_RETURN_DECAY = 0.5        # Multiply return time by this each cycle
SUN_MIN_RETURN = 1.0          # Minimum return time

# ── Nihilist ────────────────────────────────────────────
NIHILIST_SIZE = (32, 48)
NIHILIST_SNEAK_SPEED = 300     # Very fast between bushes
NIHILIST_BUSH_WAIT_MIN = 1.0   # Min seconds hiding in bush
NIHILIST_BUSH_WAIT_MAX = 15.0  # Max seconds hiding in bush

# ── Bushes ──────────────────────────────────────────────
BUSH_SIZE = (64, 48)
# Bush positions — 2 bushes on each side, between edge and center
BUSH_POSITIONS_LEFT = [
    (80, SCREEN_HEIGHT * 0.45),
    (200, SCREEN_HEIGHT * 0.5),
]
BUSH_POSITIONS_RIGHT = [
    (SCREEN_WIDTH - 200, SCREEN_HEIGHT * 0.5),
    (SCREEN_WIDTH - 80, SCREEN_HEIGHT * 0.45),
]
ALL_BUSH_POSITIONS = BUSH_POSITIONS_LEFT + BUSH_POSITIONS_RIGHT

# ── Pond ────────────────────────────────────────────────
POND_SIZE = (80, 50)
POND_POSITION = (SCREEN_WIDTH - 150, SCREEN_HEIGHT * 0.42)

# ── Tools ───────────────────────────────────────────────
TOOL_NONE = "hand"
TOOL_CLIPPERS = "clippers"
TOOL_BUCKET_EMPTY = "bucket_empty"
TOOL_BUCKET_FULL = "bucket_full"

TOOL_ICON_SIZE = (40, 40)
TOOLBAR_Y = SCREEN_HEIGHT - 70
TOOLBAR_X = SCREEN_WIDTH // 2 - 80

WET_CLIPPERS_SLIP_INTERVAL = 2.0   # Seconds between slips
WET_CLIPPERS_SLIP_DURATION = 1.0   # Seconds to recover
WET_CLIPPERS_ACTIVE_DURATION = 10.0 # How long clippers stay wet

# ── Event Scaling ───────────────────────────────────────
GRACE_PERIOD = 10.0  # No events for first 10 seconds

EVENT_SCHEDULE = [
    # (time_start, time_end, interval_between_events)
    (10.0, 25.0, 5.0),
    (25.0, 40.0, 5.0),
    (40.0, 55.0, 2.5),
    (55.0, float('inf'), 2.5),
]

# ── UI ──────────────────────────────────────────────────
TIMER_FONT_SIZE = 28
TIMER_POSITION = (SCREEN_WIDTH // 2, 20)

STIM_BOARD_SIZE = (180, 140)
STIM_BOARD_TOGGLE_POS = (SCREEN_WIDTH - 60, SCREEN_HEIGHT - 50)
STIM_BUTTON_COUNT = 3

DEBUFF_ICON_SIZE = (24, 24)
DEBUFF_BAR_OFFSET_Y = 10  # Pixels below Sheepo

DESCRIPTION_BOX_POS = (SCREEN_WIDTH - 220, 10)
DESCRIPTION_BOX_SIZE = (210, 60)

# ── High Scores ─────────────────────────────────────────
HIGH_SCORE_FILE = "highscores.json"
MAX_HIGH_SCORES = 5

# ── Asset Paths ─────────────────────────────────────────
# Sprites — use these paths, fall back to placeholder if missing
SPRITE_DIR = "assets/sprites/"
AUDIO_DIR = "assets/audio/"
FONT_DIR = "assets/fonts/"

# Placeholder: when a sprite file doesn't exist, entities draw colored shapes
USE_PLACEHOLDER_SPRITES = True  # Set False when real sprites are ready

# Audio slots — set to None or filename
MUSIC_TITLE = None       # e.g., "title_music.ogg"
MUSIC_INGAME = None      # e.g., "ingame_music.ogg"

SFX_CLIP = None          # "clip.ogg"
SFX_FIRE_START = None    # "fire_start.ogg"
SFX_WATER_SPLASH = None  # "water_splash.ogg"
SFX_BEE_BUZZ = None      # "bee_buzz.ogg"
SFX_BEE_SWAT = None      # "bee_swat.ogg"
SFX_DGAF = None          # "dgaf.ogg"
SFX_GAME_OVER = None     # "game_over.ogg"
SFX_STIM_1 = None        # "stim_1.ogg"
SFX_STIM_2 = None        # "stim_2.ogg"
SFX_STIM_3 = None        # "stim_3.ogg"
SFX_TOOL_EQUIP = None    # "tool_equip.ogg"
SFX_WET_SLIP = None      # "wet_slip.ogg"
SFX_SUN_ARRIVE = None    # "sun_arrive.ogg"
SFX_NIHILIST = None       # "nihilist.ogg"