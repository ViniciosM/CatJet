import pygame
import sys
import random as rand

# Game Configurations
SCREEN_WIDTH, SCREEN_HEIGHT = 580, 624
FLOOR_Y_POS = 530
PIPE_SPAWN_TIME = 1200
CAT_ANIMATION_TIME = 200
GRAVITY = 0.25
JUMP_STRENGTH = -7

# Initialize Pygame
pygame.mixer.pre_init(frequency=44000, size=-16, channels=2, buffer=524)
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Load Assets
def load_image(path, scale=True):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale2x(img) if scale else img

background_surface = load_image("../../PythonProject/CatJet/Images/background.png")
floor_surface = load_image("../../PythonProject/CatJet/Images/base.png")
pipe_surface = load_image("../../PythonProject/CatJet/Images/pipe-red.png")

cat_frames = [
    load_image("../../PythonProject/CatJet/Images/catjet-less-turbine.png"),
    load_image("../../PythonProject/CatJet/Images/catjet-stable-turbine.png"),
    load_image("../../PythonProject/CatJet/Images/catjet-up.png")
]

# Icon and Title
pygame.display.set_caption("CatJet")
pygame.display.set_icon(cat_frames[2])

# Sounds
def load_sound(path, volume):
    sound = pygame.mixer.Sound(path)
    sound.set_volume(volume)
    return sound

turbine_sound = load_sound("../../PythonProject/CatJet/Sounds/sfx_jet_turbine.wav", 0.08)
death_sound = load_sound("../../PythonProject/CatJet/Sounds/sfx_hit.wav", 0.05)
score_sound = load_sound("../../PythonProject/CatJet/Sounds/sfx_point.wav", 0.02)

# Game Variables
floor_x_pos = 0
cat_index = 0
cat_surface = cat_frames[cat_index]
cat_rect = cat_surface.get_rect(center=(100, SCREEN_HEIGHT // 2))
cat_movement = 0
game_active = True
score = 0
highest_score = 0
can_score = True
pipe_list = []
pipe_height = [250, 250, 450]

# Events
SPAWNPIPE = pygame.USEREVENT
CATTURBINE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWNPIPE, PIPE_SPAWN_TIME)
pygame.time.set_timer(CATTURBINE, CAT_ANIMATION_TIME)

# Utility Functions
def draw_floor():
    global floor_x_pos
    floor_x_pos = (floor_x_pos - 1) % -576
    screen.blit(floor_surface, (floor_x_pos, FLOOR_Y_POS))
    screen.blit(floor_surface, (floor_x_pos + 576, FLOOR_Y_POS))

def draw_cat():
    global cat_movement
    cat_movement += GRAVITY
    rotated_cat = pygame.transform.rotozoom(cat_surface, -cat_movement * 3, 1)
    cat_rect.centery += cat_movement
    screen.blit(rotated_cat, cat_rect)

def create_pipe():
    pos = rand.choice(pipe_height)
    bottom = pipe_surface.get_rect(midtop=(700, pos))
    top = pipe_surface.get_rect(midbottom=(700, pos - 200))
    return bottom, top

def move_pipes(pipes):
    return [pipe.move(-5, 0) for pipe in pipes if pipe.right > -50]

def draw_pipes(pipes):
    for pipe in pipes:
        image = pygame.transform.flip(pipe_surface, False, True) if pipe.bottom < SCREEN_HEIGHT else pipe_surface
        screen.blit(image, pipe)

def check_collision(pipes):
    global can_score
    for pipe in pipes:
        if cat_rect.colliderect(pipe):
            death_sound.play()
            can_score = True
            return False
    if cat_rect.top <= -100 or cat_rect.bottom >= FLOOR_Y_POS:
        can_score = True
        return False
    return True

def cat_animation():
    new_cat = cat_frames[cat_index]
    new_rect = new_cat.get_rect(center=(100, cat_rect.centery))
    return new_cat, new_rect

def show_text(text, pos, color, size):
    font = pygame.font.Font("04B_19.TTF", size)
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=pos)
    screen.blit(surface, rect)

def score_display(state):
    show_text(f"Score: {int(score)}", (288, 100), (255, 255, 255), 35)
    if state == "game_over":
        show_text(f"Maior score: {int(highest_score)}", (288, 450), (255, 255, 255), 35)

def score_check():
    global score, can_score
    for pipe in pipe_list:
        if 95 < pipe.centerx < 105 and can_score:
            score += 1
            score_sound.play()
            can_score = False
        if pipe.centerx < 0:
            can_score = True

# Game Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_active:
                    cat_movement = JUMP_STRENGTH
                    turbine_sound.play()
                else:
                    game_active = True
                    pipe_list.clear()
                    cat_rect.center = (100, SCREEN_HEIGHT // 2)
                    cat_movement = 0
                    score = 0

        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())

        if event.type == CATTURBINE:
            cat_index = (cat_index + 1) % 3
            cat_surface, cat_rect = cat_animation()

    screen.blit(background_surface, (0, -350))
    draw_floor()

    if game_active:
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)
        draw_cat()
        game_active = check_collision(pipe_list)
        score_check()
        score_display("main_game")
    else:
        show_text("Game Over", (288, 260), (255, 0, 0), 60)
        show_text("Pressione Space para tentar novamente", (288, 300), (255, 0, 0), 25)
        highest_score = max(score, highest_score)
        score_display("game_over")

    pygame.display.update()
    clock.tick(120)

