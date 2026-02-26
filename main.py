import pygame
import sys
import math
import random
import os
import time


pygame.init()
WIDTH, HEIGHT = 1250, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Eclipse Visual Demo")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 18)

#анимки косма
bg_offset_x = 0
bg_offset_y = 0
bg_speed_x = 0.1
bg_speed_y = 0.05
shake_amp = 5  # амплитуда покачивания планет

# цветики самоцветики
SPACE = (5, 5, 15)
YELLOW = (255, 220, 0)
BLUE = (100, 150, 255)
GRAY = (200, 200, 200)
WHITE = (230, 230, 230)
ORBIT = (60, 60, 80)
SHADOW = (20, 20, 20, 200)

sun_radius = 60
earth_radius = 28
moon_radius = 12
moon_angle = 0

sun_pos = (300, HEIGHT // 2)

mode = "normal"
transition_speed = 0.05

# дефы ебать

def smooth_angle(current, target, speed):
    diff = (target - current + math.pi) % (2*math.pi) - math.pi
    return current + diff * speed

def draw_glow(surface, position, radius):
    #градик
    glow_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

    for i in range(radius):
        t = i / radius  # 0 = центр, 1 = край
        
        i += 60
        r = 255
        g = int(220*(1-t) + 120*t)
        b = 0
        alpha = int((150 * (1 - t)**2) * 0.0)  

        pygame.draw.circle(
            glow_surface,
            (r, g, b, 9),
            (radius, radius),
            radius 
        )

    surface.blit(glow_surface, (position[0]-radius, position[1]-radius))

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

icon = pygame.image.load(resource_path("icon.ico"))
pygame.display.set_icon(icon)

def generate_stars():
    return [(random.randint(0, WIDTH),
             random.randint(0, HEIGHT),
             random.randint(1, 2)) for _ in range(300)]

stars = generate_stars()

def draw_text(text, x, y):
    screen.blit(font.render(text, True, WHITE), (x, y))

def lerp(a, b, t):
    return a + (b - a) * t

def smooth_move(current, target):
    return (lerp(current[0], target[0], transition_speed),
            lerp(current[1], target[1], transition_speed))

def draw_shadow(source_pos, blocker_pos, blocker_r):
    dx = blocker_pos[0] - source_pos[0]
    dy = blocker_pos[1] - source_pos[1]
    dist = math.hypot(dx, dy)
    if dist == 0:
        return

    dir_x = dx / dist
    dir_y = dy / dist

    length = 2000
    end = (blocker_pos[0] + dir_x * length,
           blocker_pos[1] + dir_y * length)

    perp = (-dir_y, dir_x)

    p1 = (blocker_pos[0] + perp[0]*blocker_r,
          blocker_pos[1] + perp[1]*blocker_r)
    p2 = (blocker_pos[0] - perp[0]*blocker_r,
          blocker_pos[1] - perp[1]*blocker_r)
    p3 = (end[0] - perp[0]*blocker_r*0.2,
          end[1] - perp[1]*blocker_r*0.2)
    p4 = (end[0] + perp[0]*blocker_r*0.2,
          end[1] + perp[1]*blocker_r*0.2)

    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(s, SHADOW, [p1, p2, p3, p4])
    screen.blit(s, (0, 0))

# анальные позиции
earth_pos = (850, HEIGHT//2 - 100)
moon_pos = (950, HEIGHT//2 + 80)

running = True
while running:
    dt = clock.tick(60)
    t = pygame.time.get_ticks() / 1200  # время в секундах
    screen.fill(SPACE)
    moon_orbit_r = 190

    # анимка
    bg_offset_x += bg_speed_x
    bg_offset_y += bg_speed_y

    for x, y, r in stars:
        px = (x + bg_offset_x) % WIDTH
        py = (y + bg_offset_y) % HEIGHT
        pygame.draw.circle(screen, (180, 180, 220), (int(px), int(py)), r)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                mode = "solar"
            if event.key == pygame.K_2:
                mode = "lunar"
            if event.key == pygame.K_3:
                mode = "normal"
        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            sun_pos = (300, HEIGHT // 2)
            stars = generate_stars()

    # позиции
    if mode == "solar":
        target_earth = (900, HEIGHT//2)
        #angle = math.pi  # 0 = справа, math.pi = слева
        #target_moon = (target_earth[0] + moon_orbit_r * math.cos(angle), 
        #               target_earth[1] + moon_orbit_r * math.sin(angle))
        target_angle = math.pi
    elif mode == "lunar":
        target_earth = (900, HEIGHT//2)
        #angle = 0  # 0 = справа, math.pi = слева
        #target_moon = (target_earth[0] + moon_orbit_r * math.cos(angle),
        #               target_earth[1] + moon_orbit_r * math.sin(angle))
        target_angle = 0
    else:
        target_earth = (900, HEIGHT//2)# - 140)
        #target_moon = (1030, HEIGHT//2 + 137)
        target_angle = math.pi / 4
    moon_angle = smooth_angle(moon_angle, target_angle, 0.05)
    earth_pos = smooth_move(earth_pos, target_earth)
    moon_pos = (
        earth_pos[0] + moon_orbit_r * math.cos(moon_angle),
        earth_pos[1] + moon_orbit_r * math.sin(moon_angle)
    )

    # анимка планет
    earth_draw_pos = (
        int(earth_pos[0] + math.sin(t*2) * shake_amp),
        int(earth_pos[1] + math.cos(t*1.5) * shake_amp)
    )
    moon_draw_pos = (
        int(moon_pos[0] + math.sin(t*2.5) * shake_amp),
        int(moon_pos[1] + math.cos(t*2) * shake_amp)
    )
    orbit_draw_pos = (
        int(earth_pos[0] + math.sin(t) * 2),
        int(earth_pos[1] + math.cos(t*0.8) * 2)
    )

    # жвачки орбит
    
    pygame.draw.circle(screen, ORBIT, sun_pos, 600, 1)
    pygame.draw.circle(screen, ORBIT, orbit_draw_pos, moon_orbit_r, 1)

    # when ya in da club ya bumping that
    if mode == "solar":
        draw_shadow(sun_pos, moon_pos, moon_radius)
    if mode == "lunar":
        draw_shadow(sun_pos, earth_pos, earth_radius)

    # Свечение Солнца
    draw_glow(screen, sun_pos, 150)
    #glow = pygame.Surface((sun_radius*4, sun_radius*4), pygame.SRCALPHA)
    #pygame.draw.circle(glow, (255, 200, 0, 40), (sun_radius*2, sun_radius*2), sun_radius*2)
    #screen.blit(glow, (sun_pos[0]-sun_radius*2, sun_pos[1]-sun_radius*2))

    # каки
    pygame.draw.circle(screen, YELLOW, sun_pos, sun_radius)
    pygame.draw.circle(screen, BLUE, (int(earth_pos[0]), int(earth_pos[1])), earth_radius)
    pygame.draw.circle(screen, GRAY, (int(moon_pos[0]), int(moon_pos[1])), moon_radius)

    draw_text("1 для солнечного затмения", 20, 20)
    draw_text("2 для лунного затмения", 20, 45)
    draw_text("3 для не затмения", 20, 70)

    pygame.display.flip()

pygame.quit()
sys.exit()