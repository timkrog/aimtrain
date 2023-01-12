import pygame
import random
import time
from typing import List
from pygame import mixer


class Circle:
    def __init__(self, rect, time, x_speed, y_speed):
        self.rect = rect
        self.time = time
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.hits_to_destroy = HITS_TO_DESTROY


# CONSTANTS
SHOT_FREQ = 40  # max 5 shots/s
MAX_CIRCLES = 5
RADIUS_SPHERE = 20
SPHERE_TIME = 5  # seconds
SPHERE_SPEED = 15
HITS_TO_DESTROY = 10
STATUS_FONT_SIZE = 32
STATUS_Y = 20
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
X_RES = 1200
Y_RES = 600
MAX_CHANNELS = 12
MOVING = True
TIMED = True
mixer.init()
pygame.init()
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
mixer.set_num_channels(MAX_CHANNELS+3)
screen = pygame.display.set_mode([X_RES, Y_RES])
clock = pygame.time.Clock()

# VARIABLES
done = False
game_over = False
circles = []  # type: List[Circle]
mouse_clicks = 0
lives = 3
hits = 0

status_font = pygame.font.Font('freesansbold.ttf', STATUS_FONT_SIZE)
accuracy_text = status_font.render("Acc:0.0", True, GREEN, BLACK)
accuracy_text_rect = accuracy_text.get_rect()
accuracy_text_rect.center = (X_RES//15, STATUS_Y)
mc_text = status_font.render(f"MC:{mouse_clicks:.0f}", True, GREEN, BLACK)
mc_text_rect = mc_text.get_rect()
mc_text_rect.center = (X_RES - 300, STATUS_Y)
lives_text = status_font.render(f"Lives:{lives}", True, GREEN, BLACK)
lives_text_rect = lives_text.get_rect()
lives_text_rect.center = (X_RES // 2, STATUS_Y)
hits_text = status_font.render(f"Hits:{hits:.0f}", True, GREEN, BLACK)
hits_text_rect = hits_text.get_rect()
hits_text_rect.center = (X_RES - 100, STATUS_Y)

# loop
shooting = False
last_shot = time.time()
channel = 0
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            done = True
        elif not pygame.mouse.get_pressed()[0]:  # left mousebutton released
            shooting = False
        elif pygame.mouse.get_pressed()[0] and not game_over:  # left mouse button
            shooting = True
    if shooting and time.time()-last_shot > (1/SHOT_FREQ):
        mouse_clicks += 1
        mixer.Channel(channel).play(pygame.mixer.Sound('sounds/miss.mp3'))
        pos = pygame.mouse.get_pos()  # pos = event.pos
        for c in circles:
            if c.rect.collidepoint(pos):  # is it within the circle?
                hits += 1
                channel = (channel+1) % MAX_CHANNELS
                mixer.Channel(channel).play(pygame.mixer.Sound('sounds/hit.mp3'))
                c.hits_to_destroy -= 1
                if c.hits_to_destroy <= 0:
                    circles.remove(c)  # remove it from the list
                break

        channel = (channel+1) % MAX_CHANNELS
        last_shot = time.time()
    if not game_over:
        while len(circles) < MAX_CIRCLES:  # spawn circles
            x, y = random.randint(0, X_RES-RADIUS_SPHERE*2), random.randint(Y_RES // 12, Y_RES-RADIUS_SPHERE*2)
            x_speed = SPHERE_SPEED*random.random()-SPHERE_SPEED/2
            y_speed = SPHERE_SPEED*random.random()-SPHERE_SPEED/2
            circles.append(Circle(pygame.Rect(x, y, RADIUS_SPHERE*2, RADIUS_SPHERE*2), time.time(), x_speed, y_speed))
        screen.fill(BLACK)

        # render circles:
        for c in circles:
            if TIMED:
                time_diff = time.time()-c.time
                if time_diff > SPHERE_TIME:
                    circles.remove(c)
                    lives -= 1
                    mixer.Channel(MAX_CHANNELS+1).play(pygame.mixer.Sound('sounds/loss.wav'))
                    if lives <= 0:
                        game_over = True
                        mixer.Channel(MAX_CHANNELS+2).play(pygame.mixer.Sound('sounds/gameover.wav'))
                        break

            if MOVING:
                c.rect.x += c.x_speed
                if c.rect.x >= X_RES-RADIUS_SPHERE*2 or c.rect.x <= 1:
                    c.x_speed = -c.x_speed
                    c.rect.x += c.x_speed
                c.rect.y += c.y_speed

                if c.rect.y >= Y_RES-RADIUS_SPHERE*2 or c.rect.y <= STATUS_Y:
                    c.y_speed = -c.y_speed
                    c.rect.y += c.y_speed
            pygame.draw.ellipse(screen, WHITE, c.rect)
            pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(c.rect.x, c.rect.y-RADIUS_SPHERE, RADIUS_SPHERE*2, 10), 1)   # life bar
            pygame.draw.rect(screen, RED, pygame.Rect(c.rect.x, c.rect.y-RADIUS_SPHERE, c.hits_to_destroy/HITS_TO_DESTROY*RADIUS_SPHERE*2, 10), 0)
            time_s_font = pygame.font.Font('freesansbold.ttf', 10)
            if TIMED:
                time_s_text = time_s_font.render(f'{SPHERE_TIME-time_diff:.0f}', True, BLACK, WHITE)
            else:
                time_s_text = time_s_font.render('', True, BLACK, WHITE)

            time_s_text_rect = time_s_text.get_rect()
            time_s_text_rect.center = (c.rect.x+RADIUS_SPHERE, c.rect.y+RADIUS_SPHERE)
            screen.blit(time_s_text, time_s_text_rect)

    else:  # game over:
        screen.fill(BLACK)
        circles.clear()
        go_font = pygame.font.Font('freesansbold.ttf', 50)
        go_text = go_font.render("Game over! Press r to restart", True, WHITE, BLACK)
        go_text_rect = go_text.get_rect()
        go_text_rect.center = (X_RES // 2, Y_RES // 2)
        screen.blit(go_text, go_text_rect)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            game_over = False
            lives = 3
            mouse_clicks = 0
            hits = 0

    # render permanent:
    if mouse_clicks > 0:
        accuracy_text = status_font.render(f'Acc:{(hits/mouse_clicks)*100:.1f}%', True, GREEN, BLACK)
    else:
        accuracy_text = status_font.render('Acc:0.0%', True, GREEN, BLACK)

    lives_text = status_font.render(f"Lives:{lives}", True, GREEN, BLACK)
    hits_text = status_font.render(f"Hits:{hits:.0f}", True, GREEN, BLACK)
    mc_text = status_font.render(f"MC:{mouse_clicks:.0f}", True, GREEN, BLACK)
    screen.blit(hits_text, hits_text_rect)
    screen.blit(accuracy_text, accuracy_text_rect)
    screen.blit(lives_text, lives_text_rect)
    screen.blit(mc_text, mc_text_rect)
    # pygame.display.flip()
    clock.tick(60)
    pygame.display.update()

pygame.quit()
