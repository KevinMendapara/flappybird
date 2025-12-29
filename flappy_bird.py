import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()

# ---------------- SCREEN ----------------
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Ultimate")
clock = pygame.time.Clock()
FPS = 60

# ---------------- LOAD ASSETS ----------------
def load_img(path, size=None):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size) if size else img

BG = load_img("assets/bg.png", (WIDTH, HEIGHT))
GROUND = load_img("assets/ground.png", (WIDTH, 100))

# 🔥 WIDER PIPE HERE
PIPE = load_img("assets/pipe.png", (90, 500))

BIRDS = [
    load_img("assets/bird1.png", (40, 30)),
    load_img("assets/bird2.png", (40, 30)),
    load_img("assets/bird3.png", (40, 30))
]

jump_sound = pygame.mixer.Sound("sounds/jump.wav")
hit_sound = pygame.mixer.Sound("sounds/hit.wav")
score_sound = pygame.mixer.Sound("sounds/score.wav")

# ---------------- FONTS ----------------
font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 36)

# ---------------- BUTTON ----------------
class Button:
    def __init__(self, text, x, y):
        self.text = text
        self.rect = pygame.Rect(x, y, 160, 45)

    def draw(self):
        pygame.draw.rect(screen, (0, 0, 0), self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        t = font.render(self.text, True, (255, 255, 255))
        screen.blit(t, (self.rect.x + 30, self.rect.y + 10))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

# ---------------- DIFFICULTY ----------------
DIFFICULTY = {
    "EASY": {"speed": 2.5, "gap": 190},
    "MEDIUM": {"speed": 3.2, "gap": 170},
    "HARD": {"speed": 4.0, "gap": 150}
}

difficulty = "MEDIUM"
pipe_speed = DIFFICULTY[difficulty]["speed"]
pipe_gap = DIFFICULTY[difficulty]["gap"]

# ---------------- GAME VARIABLES ----------------
bird_x = 60
bird_y = HEIGHT // 2
bird_vel = 0
gravity = 0.5
jump_strength = -8
bird_index = 0

ground_x = 0
pipes = []
score = 0
dead = False
death_rotation = 0

# ---------------- HIGH SCORE (SAFE) ----------------
if not os.path.exists("highscore.txt"):
    with open("highscore.txt", "w") as f:
        f.write("0")

with open("highscore.txt", "r") as f:
    data = f.read().strip()
    high_score = int(data) if data.isdigit() else 0

# ---------------- BUTTONS ----------------
play_btn = Button("PLAY", 120, 250)
easy_btn = Button("EASY", 120, 310)
med_btn = Button("MEDIUM", 120, 360)
hard_btn = Button("HARD", 120, 410)

# ---------------- STATES ----------------
MENU = True
GAME = False
PAUSED = False

# ---------------- FUNCTIONS ----------------
def create_pipe():
    h = random.randint(150, 400)
    return (
        PIPE.get_rect(midbottom=(WIDTH, h)),
        PIPE.get_rect(midtop=(WIDTH, h + pipe_gap))
    )

def reset_game():
    global bird_y, bird_vel, pipes, score, dead, death_rotation
    bird_y = HEIGHT // 2
    bird_vel = 0
    pipes = list(create_pipe())
    score = 0
    dead = False
    death_rotation = 0

# ---------------- MAIN LOOP ----------------
while True:
    screen.blit(BG, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Touch control (mobile)
        if event.type == pygame.FINGERDOWN and GAME and not PAUSED:
            bird_vel = jump_strength
            jump_sound.play()

        # Mouse menu
        if event.type == pygame.MOUSEBUTTONDOWN and MENU:
            pos = pygame.mouse.get_pos()
            if play_btn.clicked(pos):
                pipe_speed = DIFFICULTY[difficulty]["speed"]
                pipe_gap = DIFFICULTY[difficulty]["gap"]
                reset_game()
                MENU = False
                GAME = True
            if easy_btn.clicked(pos): difficulty = "EASY"
            if med_btn.clicked(pos): difficulty = "MEDIUM"
            if hard_btn.clicked(pos): difficulty = "HARD"

        # Keyboard
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and GAME and not PAUSED:
                bird_vel = jump_strength
                jump_sound.play()

            if event.key == pygame.K_p and GAME:
                PAUSED = not PAUSED

            if event.key == pygame.K_r and not GAME:
                reset_game()
                GAME = True

    # ---------------- MENU ----------------
    if MENU:
        screen.blit(big_font.render("FLAPPY BIRD", True, (255,255,255)), (85, 180))
        screen.blit(font.render(f"Selected: {difficulty}", True, (255,255,255)), (120, 470))
        play_btn.draw()
        easy_btn.draw()
        med_btn.draw()
        hard_btn.draw()

    # ---------------- GAME ----------------
    elif GAME and not PAUSED:
        bird_index = (bird_index + 1) % 3
        bird_vel += gravity
        bird_y += bird_vel

        angle = -20 if bird_vel < 0 else min(90, bird_vel * 6)
        bird_img = pygame.transform.rotate(BIRDS[bird_index], -angle)
        bird_rect = bird_img.get_rect(center=(bird_x, bird_y))
        screen.blit(bird_img, bird_rect)

        # Pipes
        for pipe in pipes:
            pipe.x -= pipe_speed
            screen.blit(PIPE, pipe)

        # Auto difficulty
        if score and score % 5 == 0:
            pipe_speed = min(pipe_speed + 0.002, 6)
            pipe_gap = max(pipe_gap - 0.5, 120)

        # 🔥 UPDATED REMOVAL FOR WIDE PIPE
        if pipes[0].x < -100:
            pipes.pop(0)
            pipes.pop(0)
            pipes.extend(create_pipe())
            score += 1
            score_sound.play()

        # Collision
        for pipe in pipes:
            if bird_rect.colliderect(pipe):
                hit_sound.play()
                dead = True
                GAME = False

        if bird_y <= 0 or bird_y >= HEIGHT - 100:
            hit_sound.play()
            dead = True
            GAME = False

        ground_x = (ground_x - pipe_speed) % WIDTH

        screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (10, 10))
        screen.blit(font.render(f"High: {high_score}", True, (255,255,255)), (10, 40))

    # ---------------- PAUSE ----------------
    elif PAUSED:
        screen.blit(big_font.render("PAUSED", True, (255,255,255)), (130, 250))

    # ---------------- GAME OVER ----------------
    else:
        if dead:
            bird_vel += gravity
            bird_y += bird_vel
            death_rotation += 5
            img = pygame.transform.rotate(BIRDS[0], death_rotation)
            screen.blit(img, img.get_rect(center=(bird_x, bird_y)))

        screen.blit(big_font.render("GAME OVER", True, (255,255,255)), (95, 250))
        screen.blit(font.render("Press R to Restart", True, (255,255,255)), (110, 300))

        if score > high_score:
            high_score = score
            with open("highscore.txt", "w") as f:
                f.write(str(high_score))

    # Ground
    screen.blit(GROUND, (ground_x, HEIGHT - 100))
    screen.blit(GROUND, (ground_x + WIDTH, HEIGHT - 100))

    pygame.display.update()
    clock.tick(FPS)
