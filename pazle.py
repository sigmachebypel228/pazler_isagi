import pygame
import sys
import abc
import random
import os
import time

# Инициализация Pygame
pygame.init()
import pygame.mixer

pygame.mixer.init()
menu_sound = pygame.mixer.Sound('menu.mp3')
pygame.mixer.music.load('start.mp3')
pygame.mixer.music.play(-1)
fon = pygame.image.load('fon.png')
fon = pygame.transform.scale(fon, (1000, 700))  # Масштабируем под размер экрана

# Константы
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
BACKGROUND = (0, 0, 0)
ROWS = 6
COLS = 6
MARGIN = 2
PICTURES_DIR = './resurse/.'

# Шрифты
font = pygame.font.Font('PressStart.ttf', 48)
small_font = pygame.font.Font('PressStart.ttf', 32)
SOUNDTRACKS_DIR = './soundtracks/.'
# Основной экран
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Меню и Пазл')
clock = pygame.time.Clock()

# Глобальные переменные
player_name = "Игрок"  # Имя по умолчанию


# Базовый класс для состояний игры
class State(abc.ABC):
    @abc.abstractmethod
    def handle_events(self, events):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def draw(self, screen):
        pass


# Заставка
class SplashScreen(State):
    def __init__(self):
        self.text = 'Заставка'
        self.surface = font.render(self.text, True, (255, 255, 255))
        self.hint = 'Нажмите для продолжения'
        self.hint_surface = small_font.render(self.hint, True, (255, 255, 255))
        self.hint_visible = True
        self.hint_time = pygame.time.get_ticks()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mixer.music.stop()
                menu_sound.play(-1)
                return MenuScreen()
        return self

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.hint_time > 750:
            self.hint_visible = not self.hint_visible
            self.hint_time = current_time

    def draw(self, screen):
        screen.blit(fon, (0, 0))
        rect = self.surface.get_rect()
        rect.centerx = screen.get_rect().centerx
        rect.centery = screen.get_rect().centery - 100
        screen.blit(self.surface, rect)
        if self.hint_visible:
            hint_rect = self.hint_surface.get_rect()
            hint_rect.centerx = screen.get_rect().centerx
            hint_rect.centery = screen.get_rect().centery + 100
            screen.blit(self.hint_surface, hint_rect)


# Главное меню
class MenuScreen(State):
    def __init__(self):
        self.items = ['Играть', 'Ввести имя игрока', 'Выйти']
        self.surfaces = [font.render(item, True, (255, 255, 255)) for item in self.items]
        self.selected = 0
        self.input_active = False
        self.input_text = player_name

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.input_active:
                    if event.key == pygame.K_RETURN:
                        global player_name
                        player_name = self.input_text
                        self.input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        self.input_text += event.unicode
                else:
                    if event.key == pygame.K_UP:
                        self.prev()
                    if event.key == pygame.K_DOWN:
                        self.next()
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        return self.process_item()
        return self

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(fon, (0, 0))
        for i, surface in enumerate(self.surfaces):
            color = (255, 0, 0) if i == self.selected else (255, 255, 255)
            self.surfaces[i] = font.render(self.items[i], True, color)
            rect = surface.get_rect()
            rect.centerx = screen.get_rect().centerx
            rect.centery = screen.get_rect().centery + i * 60 - 60
            screen.blit(self.surfaces[i], rect)

        # Отображение текущего имени игрока
        name_text = small_font.render(f'Текущее имя: {player_name}', True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
        screen.blit(name_text, name_rect)

        # Поле ввода имени (если активно)
        if self.input_active:
            input_surface = small_font.render(self.input_text, True, (255, 255, 255))
            input_rect = input_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180))
            pygame.draw.rect(screen, (100, 100, 100), input_rect.inflate(20, 10))
            screen.blit(input_surface, input_rect)

    def prev(self):
        self.selected = (self.selected - 1) % len(self.items)

    def next(self):
        self.selected = (self.selected + 1) % len(self.items)

    def process_item(self):
        if self.selected == 0:  # Играть
            menu_sound.stop()

            return PuzzleGame()
        elif self.selected == 1:  # Ввести имя
            self.input_active = True
            self.input_text = player_name
        elif self.selected == 2:  # Выйти
            pygame.quit()
            sys.exit()
        return self


# Игра-пазл
class PuzzleGame(State):
    def __init__(self):
        # Загрузка изображения
        pictures = os.listdir(PICTURES_DIR)
        picture = random.choice(pictures)
        soundtrack = os.listdir(SOUNDTRACKS_DIR)
        sound = random.choice(soundtrack)
        soundtrack_path = os.path.join(SOUNDTRACKS_DIR,sound)
        self.soundtrackss = pygame.mixer.music.load(soundtrack_path)
        pygame.mixer.music.play()
        image_path = os.path.join(PICTURES_DIR, picture)
        self.image = pygame.image.load(image_path).convert_alpha()

        # Размеры плиток
        self.image_width, self.image_height = self.image.get_size()
        self.TILE_WIDTH = self.image_width // COLS
        self.TILE_HEIGHT = self.image_height // ROWS

        # Создание плиток
        self.tiles = []
        for i in range(ROWS):
            for j in range(COLS):
                rect = pygame.Rect(j * self.TILE_WIDTH, i * self.TILE_HEIGHT,
                                   self.TILE_WIDTH, self.TILE_HEIGHT)
                tile = self.image.subsurface(rect)
                self.tiles.append(tile)

        # Оригинальный порядок
        self.origin_tiles = self.tiles.copy()
        random.shuffle(self.tiles)

        # Игровые переменные
        self.selected = None
        self.swaps = 0
        self.game_completed = False
        self.start_time = time.time()
        self.final_time = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return MenuScreen()  # Выход в меню по ESC
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.game_completed:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for idx, _ in enumerate(self.tiles):
                    row = idx // ROWS
                    col = idx % COLS
                    x = col * (self.TILE_WIDTH + MARGIN) + MARGIN
                    y = row * (self.TILE_HEIGHT + MARGIN) + MARGIN

                    if x <= mouse_x < x + self.TILE_WIDTH and y <= mouse_y < y + self.TILE_HEIGHT:
                        if self.selected is not None and self.selected != idx:
                            self.tiles[idx], self.tiles[self.selected] = self.tiles[self.selected], self.tiles[idx]
                            self.swaps += 1
                            self.selected = None
                        else:
                            self.selected = idx
        return self

    def update(self):
        if not self.game_completed and self.tiles == self.origin_tiles:
            self.game_completed = True
            self.final_time = int(time.time() - self.start_time)

    def draw(self, screen):
        screen.blit(fon, (0, 0))

        # Отрисовка плиток
        for idx, tile in enumerate(self.tiles):
            row = idx // ROWS
            col = idx % COLS
            x = col * (self.TILE_WIDTH + MARGIN) + MARGIN
            y = row * (self.TILE_HEIGHT + MARGIN) + MARGIN

            if idx == self.selected:
                pygame.draw.rect(screen, (0, 255, 0),
                                 (x - MARGIN, y - MARGIN,
                                  self.TILE_WIDTH + MARGIN * 2, self.TILE_HEIGHT + MARGIN * 2))
            screen.blit(tile, (x, y))

        # Статистика (левый нижний угол)
        current_time = int(time.time() - self.start_time) if not self.game_completed else self.final_time
        minutes = current_time // 60
        seconds = current_time % 60

        # Таймер + мотивация
        time_text = small_font.render(f'Время: {minutes:02d}:{seconds:02d}', True, (255, 255, 255))
        motivation_text = small_font.render(f'{player_name}, ты сможешь!', True, (255, 255, 255))
        swaps_text = small_font.render(f'Шаги: {self.swaps}', True, (255, 255, 255))

        screen.blit(time_text, (20, SCREEN_HEIGHT - 120))
        screen.blit(motivation_text, (20, SCREEN_HEIGHT - 80))
        screen.blit(swaps_text, (20, SCREEN_HEIGHT - 40))

        # Сообщение о победе
        if self.game_completed:
            text = font.render('Пазл собран!', True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(20, 20))
            screen.blit(text, text_rect)

            hint = small_font.render('Нажмите ESC для выхода в меню', True, (255, 255, 255))
            hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            screen.blit(hint, hint_rect)


# Запуск игры
def main():
    current_state = SplashScreen()

    while True:
        events = pygame.event.get()
        current_state = current_state.handle_events(events)
        current_state.update()
        current_state.draw(screen)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()