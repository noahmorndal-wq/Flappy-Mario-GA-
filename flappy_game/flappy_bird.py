import pygame
import random
import sys

pygame.init()

# --------------------
# Screen
# --------------------
WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Mario")

CLOCK = pygame.time.Clock()
FPS = 60

# --------------------
# Debug
# --------------------
SHOW_HITBOXES = False

# --------------------
# Colors
# --------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Pipe styling (body)
PIPE_MAIN = (40, 40, 40)
PIPE_LIGHT = (70, 70, 70)
PIPE_DARK = (20, 20, 20)
PIPE_OUTLINE = (0, 0, 0)

# --------------------
# Player
# --------------------
PLAYER_X = 80
GRAVITY = 0.5
JUMP_STRENGTH = -8

# MARIO HITBOX
MARIO_HITBOX_SHRINK_X = 20
MARIO_HITBOX_SHRINK_Y = 6

# --------------------
# Pipes
# --------------------
PIPE_GAP = 150
PIPE_SPEED = 3
PIPE_WIDTH = 85

# Seam fix...
SEAM_OVERLAP = 2

# HITBOX (pipes)
HIT_SHRINK_BODY = 0
HIT_SHRINK_CAP = 58

# --------------------
# Fonts
# --------------------
FONT = pygame.font.SysFont(None, 36)
BIG_FONT = pygame.font.SysFont(None, 56)

high_score = 0

# =========================================================
# Load images
# =========================================================
mario_img = pygame.image.load("assets/mario.png").convert_alpha()
mario_img = pygame.transform.scale(mario_img, (50, 35))

pipe_cap_img = pygame.image.load("assets/pipe.png").convert_alpha()

scale_factor = PIPE_WIDTH / pipe_cap_img.get_width()
cap_h = int(pipe_cap_img.get_height() * scale_factor)
cap_h = max(10, cap_h)

pipe_cap_img = pygame.transform.smoothscale(pipe_cap_img, (PIPE_WIDTH, cap_h))
pipe_cap_img_top = pygame.transform.flip(pipe_cap_img, False, True)

# BACKGROUND IMAGE (lägg din bild här: assets/background.png)
background_img = pygame.image.load("assets/background.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# =========================================================
# Helpers
# =========================================================
def draw_text(text, font, color, center_x, center_y):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(center_x, center_y))
    SCREEN.blit(img, rect)

def draw_pipe_body(x, y, w, h):
    if h <= 0:
        return
    pygame.draw.rect(SCREEN, PIPE_MAIN, (x, y, w, h))
    pygame.draw.rect(SCREEN, PIPE_LIGHT, (x + 2, y, max(1, w // 6), h))
    pygame.draw.rect(SCREEN, PIPE_DARK, (x + w - max(2, w // 8), y, max(2, w // 8), h))
    pygame.draw.rect(SCREEN, PIPE_OUTLINE, (x, y, w, h), 2)

def draw_button(text, x, y, w, h, mouse_pos, mouse_click):
    rect = pygame.Rect(x, y, w, h)
    hovered = rect.collidepoint(mouse_pos)

    color = (230, 230, 230) if hovered else (200, 200, 200)
    pygame.draw.rect(SCREEN, color, rect, border_radius=10)
    pygame.draw.rect(SCREEN, BLACK, rect, 2, border_radius=10)

    draw_text(text, FONT, BLACK, rect.centerx, rect.centery)
    return hovered and mouse_click

def draw_hud(score, high_score):
    hud = pygame.Surface((190, 70), pygame.SRCALPHA)
    hud.fill((0, 0, 0, 150))
    SCREEN.blit(hud, (10, 10))

    txt1 = FONT.render(f"Score: {score}", True, WHITE)
    txt2 = FONT.render(f"High score: {high_score}", True, WHITE)
    SCREEN.blit(txt1, (20, 18))
    SCREEN.blit(txt2, (20, 40))

# ✅ NY: background med bild (istället för att rita)
def draw_background(frame):
    SCREEN.blit(background_img, (0, 0))

def create_pipe():
    gap_start = random.randint(140, HEIGHT - 240)
    top = pygame.Rect(WIDTH, 0, PIPE_WIDTH, gap_start)
    bottom = pygame.Rect(WIDTH, gap_start + PIPE_GAP, PIPE_WIDTH, HEIGHT - (gap_start + PIPE_GAP))
    return top, bottom

def reset_game():
    player_y = HEIGHT // 2
    player_vel = 0
    pipes = [create_pipe()]
    score = 0
    return player_y, player_vel, pipes, score

def get_pipe_hitboxes(top_rect, bottom_rect):
    def shrink_x(rect, shrink_amount):
        hit_w = max(1, PIPE_WIDTH - shrink_amount)
        x_off = (PIPE_WIDTH - hit_w) // 2
        return pygame.Rect(rect.x + x_off, rect.y, hit_w, rect.height)

    cap_zone_h = min(cap_h, top_rect.height)
    top_cap_rect = pygame.Rect(top_rect.x, top_rect.height - cap_zone_h, PIPE_WIDTH, cap_zone_h)
    top_body_rect = pygame.Rect(top_rect.x, 0, PIPE_WIDTH, max(0, top_rect.height - cap_zone_h))

    top_cap_hit = shrink_x(top_cap_rect, HIT_SHRINK_CAP)
    top_body_hit = shrink_x(top_body_rect, HIT_SHRINK_BODY)

    cap_zone_h2 = min(cap_h, bottom_rect.height)
    bottom_cap_rect = pygame.Rect(bottom_rect.x, bottom_rect.y, PIPE_WIDTH, cap_zone_h2)
    bottom_body_rect = pygame.Rect(
        bottom_rect.x,
        bottom_rect.y + cap_zone_h2,
        PIPE_WIDTH,
        max(0, bottom_rect.height - cap_zone_h2)
    )

    bottom_cap_hit = shrink_x(bottom_cap_rect, HIT_SHRINK_CAP)
    bottom_body_hit = shrink_x(bottom_body_rect, HIT_SHRINK_BODY)

    return top_cap_hit, top_body_hit, bottom_cap_hit, bottom_body_hit

def get_mario_hitbox(center_x, center_y):
    rect = mario_img.get_rect(center=(center_x, int(center_y)))
    return rect.inflate(-MARIO_HITBOX_SHRINK_X, -MARIO_HITBOX_SHRINK_Y)

# =========================================================
# Menu
# =========================================================
def menu():
    while True:
        CLOCK.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True

        frame = pygame.time.get_ticks() // 16
        draw_background(frame)

        draw_text("FLAPPY Mario", BIG_FONT, WHITE, WIDTH // 2, 130)
        draw_text(f"High score: {high_score}", FONT, WHITE, WIDTH // 2, 180)

        if draw_button("Play", 120, 260, 160, 55, mouse_pos, mouse_click):
            return

        if draw_button("Quit", 120, 330, 160, 55, mouse_pos, mouse_click):
            pygame.quit()
            sys.exit()

        draw_text("SPACE = jump", FONT, WHITE, WIDTH // 2, 430)
        pygame.display.update()

# =========================================================
# Game
# =========================================================
def game():
    global high_score

    player_y, player_vel, pipes, score = reset_game()
    game_over = False

    while True:
        CLOCK.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not game_over:
                    player_vel = JUMP_STRENGTH
                else:
                    player_y, player_vel, pipes, score = reset_game()
                    game_over = False

        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            return

        if not game_over:
            player_vel += GRAVITY
            player_y += player_vel

            if pipes[-1][0].x < WIDTH - 220:
                pipes.append(create_pipe())

            for top, bottom in pipes:
                top.x -= PIPE_SPEED
                bottom.x -= PIPE_SPEED

            if pipes and pipes[0][0].x < -PIPE_WIDTH:
                pipes.pop(0)
                score += 1

            player_hitbox = get_mario_hitbox(PLAYER_X, player_y)

            if player_y < 0 or player_y > HEIGHT:
                game_over = True
                high_score = max(high_score, score)

            for top, bottom in pipes:
                top_cap_hit, top_body_hit, bottom_cap_hit, bottom_body_hit = get_pipe_hitboxes(top, bottom)
                if (player_hitbox.colliderect(top_cap_hit) or
                    player_hitbox.colliderect(top_body_hit) or
                    player_hitbox.colliderect(bottom_cap_hit) or
                    player_hitbox.colliderect(bottom_body_hit)):
                    game_over = True
                    high_score = max(high_score, score)
                    break

        frame = pygame.time.get_ticks() // 16
        draw_background(frame)

        for top, bottom in pipes:
            top_body_h = max(0, top.height - cap_h)
            draw_pipe_body(top.x, 0, PIPE_WIDTH, top_body_h + SEAM_OVERLAP)

            SCREEN.blit(pipe_cap_img_top, (top.x, top_body_h - SEAM_OVERLAP))
            SCREEN.blit(pipe_cap_img, (bottom.x, bottom.y - SEAM_OVERLAP + 3))

            bottom_body_y = bottom.y + cap_h - SEAM_OVERLAP
            bottom_body_h = max(0, HEIGHT - bottom_body_y)
            draw_pipe_body(bottom.x, bottom_body_y, PIPE_WIDTH, bottom_body_h)

        # Draw mario
        mario_draw_rect = mario_img.get_rect(center=(PLAYER_X, int(player_y)))
        SCREEN.blit(mario_img, mario_draw_rect)

        # Debug hitboxes
        if SHOW_HITBOXES:
            pygame.draw.rect(SCREEN, (0, 255, 0), get_mario_hitbox(PLAYER_X, player_y), 2)

            for top, bottom in pipes:
                top_cap_hit, top_body_hit, bottom_cap_hit, bottom_body_hit = get_pipe_hitboxes(top, bottom)
                pygame.draw.rect(SCREEN, (180, 180, 180), top_cap_hit, 2)
                pygame.draw.rect(SCREEN, (180, 180, 180), bottom_cap_hit, 2)
                pygame.draw.rect(SCREEN, (120, 120, 120), top_body_hit, 2)
                pygame.draw.rect(SCREEN, (120, 120, 120), bottom_body_hit, 2)

        draw_hud(score, high_score)

        if game_over:
            draw_text("GAME OVER", BIG_FONT, WHITE, WIDTH // 2, HEIGHT // 2 - 40)
            draw_text("Press SPACE to restart", FONT, WHITE, WIDTH // 2, HEIGHT // 2 + 10)
            draw_text("Press ESC for menu", FONT, WHITE, WIDTH // 2, HEIGHT // 2 + 45)

        pygame.display.update()

def main():
    while True:
        menu()
        game()

if __name__ == "__main__":
    main()