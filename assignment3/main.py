import pygame
import random
import math

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Shape and Sound Interaction')

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

bg_colors = [WHITE, (240, 240, 240), (200, 200, 200), (100, 100, 255), (50, 200, 150)]

shape_colors = [RED, BLUE, GREEN, YELLOW, CYAN, PURPLE, ORANGE]

sounds = [
    pygame.mixer.Sound("sounds/107-bpm-industrial-drum-loop-6318-wav.wav"),
    pygame.mixer.Sound("sounds/120-bpm-industrial-ambient-loop-6317-wav.wav"),
    pygame.mixer.Sound("sounds/donald-duck-ouch.wav"),
    pygame.mixer.Sound("sounds/piano-loops-167-octave-up-short-loop-120-bpm.wav")
]

shape_pos = [400, 300]
shape_size = 50

clock = pygame.time.Clock()

def draw_star(screen, color, pos, size):
    x, y = pos
    points = []
    for i in range(5):
        outer_x = x + size * math.cos(math.radians(i * 72))
        outer_y = y - size * math.sin(math.radians(i * 72))
        inner_x = x + (size / 2) * math.cos(math.radians(i * 72 + 36))
        inner_y = y - (size / 2) * math.sin(math.radians(i * 72 + 36))
        points.extend([(outer_x, outer_y), (inner_x, inner_y)])
    pygame.draw.polygon(screen, color, points)

def draw_shape(shape, color, pos, size):
    x, y = pos
    if shape == "circle":
        pygame.draw.circle(screen, color, pos, size)
    elif shape == "triangle":
        points = [(x, y - size), (x - size, y + size), (x + size, y + size)]
        pygame.draw.polygon(screen, color, points)
    elif shape == "square":
        pygame.draw.rect(screen, color, (x - size, y - size, size * 2, size * 2))
    elif shape == "diamond":
        points = [(x, y - size), (x + size, y), (x, y + size), (x - size, y)]
        pygame.draw.polygon(screen, color, points)
    elif shape == "pentagon":
        points = []
        for i in range(5):
            px = x + size * math.cos(2 * math.pi * i / 5)
            py = y + size * math.sin(2 * math.pi * i / 5)
            points.append([px, py])
        pygame.draw.polygon(screen, color, points)
    elif shape == "star":
        draw_star(screen, color, pos, size)

def check_click(pos):
    dist = ((pos[0] - shape_pos[0])**2 + (pos[1] - shape_pos[1])**2)**0.5
    return dist <= shape_size

def move_shape():
    shape_pos[0] = random.randint(50, 750)
    shape_pos[1] = random.randint(50, 550)
    return random.randint(30, 100)  # 随机返回大小

running = True
current_shape_color = random.choice(shape_colors)  # 初始随机形状颜色
current_bg_color = random.choice(bg_colors)  # 初始随机背景颜色
current_shape = random.choice(["circle", "triangle", "square", "diamond", "pentagon", "star"])  # 随机形状

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if check_click(event.pos):
                random.choice(sounds).play()
                shape_size = move_shape()
                current_shape_color = random.choice(shape_colors)
                current_bg_color = random.choice(bg_colors)
                current_shape = random.choice(["circle", "triangle", "square", "diamond", "pentagon", "star"])

    screen.fill(current_bg_color)
    draw_shape(current_shape, current_shape_color, shape_pos, shape_size)
    pygame.display.update()

    clock.tick(60)

pygame.quit()