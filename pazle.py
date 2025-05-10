import pygame
import random
import os

# Параметры экрана
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
ROWS = 6  # Количество строк
COLS = 6  # Количество столбцов
MARGIN = 2  # Отступ между фрагментами

# Путь к папке с изображениями
PICTURES_DIR = './resurse/.'

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Игра-Пазл')
clock = pygame.time.Clock()

# Загрузка случайного изображения
pictures = os.listdir(PICTURES_DIR)
picture = random.choice(pictures)
image_path = os.path.join(PICTURES_DIR, picture)
image = pygame.image.load(image_path).convert_alpha()

# Расчёт размеров одного фрагмента
image_width, image_height = image.get_size()
TILE_WIDTH = image_width // COLS
TILE_HEIGHT = image_height // ROWS

# Создание массива плиток-фрагментов
tiles = []
for i in range(ROWS):
    for j in range(COLS):
        rect = pygame.Rect(j * TILE_WIDTH, i * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
        tile = image.subsurface(rect)
        tiles.append(tile)

# Переменная для хранения оригинального порядка плиток
origin_tiles = tiles.copy()

# Перемешивание плиток
random.shuffle(tiles)

# Игровые переменные
selected = None  # Выбранная плитка
swaps = 0  # Кол-во перестановок
running = True  # Флаг завершения игры


# Функция рисования плиток
def draw_tiles():
    global screen
    for idx, tile in enumerate(tiles):
        row = idx // ROWS
        col = idx % COLS
        x = col * (TILE_WIDTH + MARGIN) + MARGIN
        y = row * (TILE_HEIGHT + MARGIN) + MARGIN

        if idx == selected:
            pygame.draw.rect(screen, (0, 255, 0),
                             (x - MARGIN, y - MARGIN,
                              TILE_WIDTH + MARGIN * 2, TILE_HEIGHT + MARGIN * 2))

        screen.blit(tile, (x, y))


# Сообщение об успешном завершении игры
def game_over():
    font = pygame.font.SysFont('Arial', 64)
    text = font.render('Ура! Картинка собрана!', True, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(4, 4))
    screen.blit(text, text_rect)


# Рисование счётчика перемещений
def draw_swaps():
    font = pygame.font.SysFont('Arial', 32)
    text = font.render(f'Перестановок: {swaps}', True, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

    pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(4, 4))
    screen.blit(text, text_rect)


# Главный игровой цикл
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for idx, _ in enumerate(tiles):
                row = idx // ROWS
                col = idx % COLS
                x = col * (TILE_WIDTH + MARGIN) + MARGIN
                y = row * (TILE_HEIGHT + MARGIN) + MARGIN

                if x <= mouse_x < x + TILE_WIDTH and y <= mouse_y < y + TILE_HEIGHT:
                    if selected is not None and selected != idx:
                        tiles[idx], tiles[selected] = tiles[selected], tiles[idx]
                        swaps += 1
                        selected = None
                    else:
                        selected = idx

    # Очистка экрана перед перерисовкой
    screen.fill((0, 0, 0))
    draw_tiles()
    draw_swaps()

    # Проверяем победу игрока
    if tiles == origin_tiles:
        game_over()

    # Обновление дисплея
    pygame.display.flip()
    clock.tick(60)

# Завершаем работу
pygame.quit()