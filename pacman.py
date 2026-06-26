import pygame
import sys
import random
import math
import numpy as np

# Inicijalizacija
pygame.init()
pygame.mixer.init()

# Ignorisanje svih dogadjaja osim onih koji su potrebni za igricu
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])

# Dimenzije ekrana
WIDTH, HEIGHT = 600, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blossom Hunt")
clock = pygame.time.Clock()

# --- MIRNE PASTEL BOJE ---
BACKGROUND_COLOR = (245, 239, 230)  # Krem
GRASS_COLOR = (210, 230, 200)       # Trava
WALL_COLOR = (150, 180, 140)        # Žbunje
FLOWER_COLORS = [
    (230, 150, 190),  # Blago roze
    (220, 150, 160),  # Blago žuti
    (200, 150, 210),  # Blago ljubičasti
    (170, 150, 210),  # Blago plavi
]
BUTTERFLY_COLORS = [
    (255, 150, 180),  # Svijetlo roze
    (150, 200, 255),  # Svijetlo plavi
    (255, 220, 100),  # Svijetlo žuti
]
SUPER_FLOWER_COLOR = (255, 215, 0)   # Zlatni
SUPER_FLOWER_GLOW = (255, 235, 150)  # Sjaj
SCARED_GHOST_COLOR = (140, 130, 190) # Plavo-siva za uplašene leptire
UI_TEXT_COLOR = (100, 10, 110)       # Ljubicasta
PACMAN_COLOR = (255, 213, 113)       # Pčela žuta

# --- MATRICA BAŠTE ---
# 1 = Žbunje, 0 = Cvijet, 2 = Veliki cvijet, 3 = Prazno
BAŠTA = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,2,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,0,1,2,1,1,1,1,1,2,1,0,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,0,1,1,0,1,0,1,1,0,1],
    [1,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,1],
    [1,0,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
    [1,2,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,2,1],
    [1,0,0,1,0,1,0,1,1,1,1,1,0,1,0,1,0,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

GRID_SIZE = 30
OFFSET_X = (WIDTH - (len(BAŠTA[0]) * GRID_SIZE)) // 2
OFFSET_Y = 60

# --- GENERIŠI FIKSNE BOJE ZA SVAKI CVIJET ---
flower_colors_map = {}
for r_idx, row in enumerate(BAŠTA):
    for c_idx, val in enumerate(row):
        if val == 0:
            flower_colors_map[(r_idx, c_idx)] = random.choice(FLOWER_COLORS)
        elif val == 2:
            flower_colors_map[(r_idx, c_idx)] = SUPER_FLOWER_COLOR

# --- ZVUKOVI ---
def create_collect_sound():
    sample_rate = 22050
    duration = 0.06
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    base = np.sin(2 * np.pi * 880 * t)
    soft = 0.5 * base + 0.3 * np.sin(2 * np.pi * 1320 * t)
    envelope = np.exp(-30 * t)
    wave = soft * envelope
    audio = (wave * 32767).astype(np.int16)
    audio = np.column_stack((audio, audio))
    sound = pygame.sndarray.make_sound(audio)
    sound.set_volume(0.06)
    return sound

def create_super_sound():
    sample_rate = 22050
    duration = 0.3
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    freq1 = 523.25
    freq2 = 659.25
    freq3 = 783.99
    note1 = np.sin(2 * np.pi * freq1 * t[:len(t)//3])
    note2 = np.sin(2 * np.pi * freq2 * t[len(t)//3:2*len(t)//3])
    note3 = np.sin(2 * np.pi * freq3 * t[2*len(t)//3:])
    wave = np.concatenate([note1, note2, note3]) * 0.5
    envelope = np.exp(-5 * t)
    wave = wave * envelope
    audio = (wave * 32767).astype(np.int16)
    audio = np.column_stack((audio, audio))
    sound = pygame.sndarray.make_sound(audio)
    sound.set_volume(0.08)
    return sound

def create_background_music():
    sample_rate = 22050
    duration = 4.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    melody = []
    notes = [261.63, 293.66, 329.63, 261.63, 329.63, 293.66, 261.63]
    for i, note in enumerate(notes):
        note_duration = duration / len(notes)
        start = int(i * note_duration * sample_rate)
        end = int((i + 1) * note_duration * sample_rate)
        segment = np.sin(2 * np.pi * note * t[start:end])
        envelope = np.exp(-3 * (t[start:end] - t[start]))
        melody.extend(segment * envelope)
    melody = np.array(melody) * 0.3
    audio = (melody * 32767).astype(np.int16)
    audio = np.column_stack((audio, audio))
    sound = pygame.sndarray.make_sound(audio)
    sound.set_volume(0.2)
    return sound

def create_death_sound():
    sample_rate = 22050
    duration = 0.3
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(2 * np.pi * 200 * t) * np.exp(-10 * t)
    wave = wave * 0.3
    audio = (wave * 32767).astype(np.int16)
    audio = np.column_stack((audio, audio))
    sound = pygame.sndarray.make_sound(audio)
    sound.set_volume(0.3)
    return sound

# ============ KLASE ============

# --- KLASA ZA EFEKAT SKUPLJANJA ---
class CollectEffect:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = 15
        self.lifetime = 15
        
    def update(self):
        self.size -= 1
        self.lifetime -= 1
        
    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size, 2)

# --- KLASA ZA LATICE ---
class Petal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-2, -1)
        self.color = random.choice(FLOWER_COLORS)
        self.lifetime = 40
        self.size = random.randint(3, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.03
        self.lifetime -= 1
        self.size = max(1, self.size - 0.02)

    def draw(self, surface):
        if self.lifetime > 0:
            points = [
                (self.x, self.y - self.size),
                (self.x - self.size, self.y),
                (self.x, self.y + self.size),
                (self.x + self.size, self.y)
            ]
            pygame.draw.polygon(surface, self.color, points)

# --- KLASA ZA LEPTIRA ---
class Butterfly:
    def __init__(self, x, y, base_speed):
        self.grid_x = x
        self.grid_y = y
        self.x = x * GRID_SIZE + GRID_SIZE // 2 + OFFSET_X
        self.y = y * GRID_SIZE + GRID_SIZE // 2 + OFFSET_Y
        self.base_color = random.choice(BUTTERFLY_COLORS)
        self.dir_x = 0
        self.dir_y = 1
        self.wing_angle = 0
        self.base_speed = base_speed
        self.speed = base_speed

    def move(self, grid, scared_mode, bee_pos):
        self.speed = self.base_speed * 0.4 if scared_mode else self.base_speed

        if not scared_mode and random.random() < 0.05:  # 5% šanse
            bee_x, bee_y = bee_pos
            dx = bee_x - self.grid_x
            dy = bee_y - self.grid_y
            if abs(dx) > abs(dy):
                self.dir_x = 1 if dx > 0 else -1
                self.dir_y = 0
            else:
                self.dir_x = 0
                self.dir_y = 1 if dy > 0 else -1
        
        if not scared_mode:
            bee_x, bee_y = bee_pos
            dx_to_bee = self.grid_x - bee_x
            dy_to_bee = self.grid_y - bee_y
            distance = math.hypot(dx_to_bee, dy_to_bee)
            
            if distance < 3:
                if abs(dx_to_bee) > abs(dy_to_bee):
                    preferred_dir = (1 if dx_to_bee > 0 else -1, 0)
                else:
                    preferred_dir = (0, 1 if dy_to_bee > 0 else -1)
                
                nx, ny = self.grid_x + preferred_dir[0], self.grid_y + preferred_dir[1]
                if (0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] != 1):
                    self.dir_x, self.dir_y = preferred_dir
        
        target_x = self.grid_x * GRID_SIZE + GRID_SIZE // 2 + OFFSET_X
        target_y = self.grid_y * GRID_SIZE + GRID_SIZE // 2 + OFFSET_Y
        
        if abs(self.x - target_x) < 2 and abs(self.y - target_y) < 2:
            new_x = self.grid_x + self.dir_x
            new_y = self.grid_y + self.dir_y
            
            if (0 <= new_x < len(grid[0]) and 0 <= new_y < len(grid) and grid[new_y][new_x] != 1):
                self.grid_x = new_x
                self.grid_y = new_y
            else:
                valid_moves = []
                for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                    nx, ny = self.grid_x + dx, self.grid_y + dy
                    if (0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] != 1):
                        valid_moves.append((dx, dy))
                
                if valid_moves:
                    self.dir_x, self.dir_y = random.choice(valid_moves)
                    self.grid_x += self.dir_x
                    self.grid_y += self.dir_y
                else:
                    self.dir_x, self.dir_y = 0, 0
        
        self.x += (target_x - self.x) * (0.1 * self.speed)
        self.y += (target_y - self.y) * (0.1 * self.speed)
        self.wing_angle += 0.08 * self.speed

    def draw(self, surface, scared_mode):
        wing_offset = int(6 * abs(math.sin(self.wing_angle)))
        color = SCARED_GHOST_COLOR if scared_mode else self.base_color
        
        pygame.draw.ellipse(surface, (60, 40, 60), (self.x - 4, self.y - 8, 8, 16))
        pygame.draw.ellipse(surface, color, (self.x - 14 - wing_offset//2, self.y - 8, 12 + wing_offset, 12))
        pygame.draw.ellipse(surface, color, (self.x + 2 + wing_offset//2, self.y - 8, 12 + wing_offset, 12))

# --- KLASA ZA PČELU ---
class Bee:
    def __init__(self):
        self.grid_x = 9
        self.grid_y = 15
        self.x = self.grid_x * GRID_SIZE + GRID_SIZE // 2 + OFFSET_X
        self.y = self.grid_y * GRID_SIZE + GRID_SIZE // 2 + OFFSET_Y
        self.dir_x = 0
        self.dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0
        self.buzz_offset = 0

    def get_position(self):
        return (self.grid_x, self.grid_y)

    def move(self, grid):
        current_target_x = self.grid_x * GRID_SIZE + GRID_SIZE // 2 + OFFSET_X
        current_target_y = self.grid_y * GRID_SIZE + GRID_SIZE // 2 + OFFSET_Y

        if abs(self.x - current_target_x) < 2 and abs(self.y - current_target_y) < 2:
            if 0 <= self.grid_y + self.next_dir_y < len(grid) and 0 <= self.grid_x + self.next_dir_x < len(grid[0]):
                if grid[self.grid_y + self.next_dir_y][self.grid_x + self.next_dir_x] != 1:
                    self.dir_x = self.next_dir_x
                    self.dir_y = self.next_dir_y

            if 0 <= self.grid_y + self.dir_y < len(grid) and 0 <= self.grid_x + self.dir_x < len(grid[0]):
                if grid[self.grid_y + self.dir_y][self.grid_x + self.dir_x] != 1:
                    self.grid_x += self.dir_x
                    self.grid_y += self.dir_y
            else:
                self.dir_x = 0
                self.dir_y = 0

        target_x = self.grid_x * GRID_SIZE + GRID_SIZE // 2 + OFFSET_X
        target_y = self.grid_y * GRID_SIZE + GRID_SIZE // 2 + OFFSET_Y

        self.x += (target_x - self.x) * 0.15
        self.y += (target_y - self.y) * 0.15
        self.buzz_offset += 0.1

    def draw(self, surface):
        pos = (int(self.x), int(self.y + 2 * math.sin(self.buzz_offset)))
        pygame.draw.circle(surface, PACMAN_COLOR, pos, GRID_SIZE // 2 - 2)
        pygame.draw.circle(surface, (60, 50, 50), (pos[0]-5, pos[1]), 3)
        pygame.draw.circle(surface, (60, 50, 50), (pos[0]+5, pos[1]), 3)
        
        pygame.draw.ellipse(surface, (220, 240, 255), (pos[0]-8, pos[1]-12, 6, 8))
        pygame.draw.ellipse(surface, (220, 240, 255), (pos[0]+2, pos[1]-12, 6, 8))
        
        pygame.draw.circle(surface, (255,255,255), (pos[0]-4, pos[1]-4), 4)
        pygame.draw.circle(surface, (255,255,255), (pos[0]+4, pos[1]-4), 4)
        pygame.draw.circle(surface, (0,0,0), (pos[0]-3, pos[1]-4), 2)
        pygame.draw.circle(surface, (0,0,0), (pos[0]+3, pos[1]-4), 2)

# ============ FUNKCIJE ============

# --- FUNKCIJE ZA HIGH SCORE ---
def load_high_score():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0

def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

# --- FUNKCIJA ZA PODEŠAVANJE NIVOA ---
def setup_level(level, butterflies, grid):
    """Podešava težinu nivoa"""
    # Povećaj brzinu leptira
    for b in butterflies:
        b.base_speed = 0.6 + (level - 1) * 0.15
    
    # Dodaj novog leptira na svakom 3. nivou
    if level >= 3 and len(butterflies) < 6:
        new_butterfly = Butterfly(9, 9, 0.7 + (level - 1) * 0.1)
        butterflies.append(new_butterfly)
    
    # Dodaj još jednog na 5. nivou
    if level >= 5 and len(butterflies) < 7:
        new_butterfly = Butterfly(5, 5, 0.8 + (level - 1) * 0.1)
        butterflies.append(new_butterfly)

# Funkcija koja pronalazi slobodno polje (travu) za bezbjedan respawn leptira
def get_random_grass_position(grid, bee=None):
    while True:
        rx = random.randint(1, len(grid[0]) - 2)
        ry = random.randint(1, len(grid) - 2)
        if grid[ry][rx] != 1:
            if bee:
                dist = math.hypot(rx - bee.grid_x, ry - bee.grid_y)
                if dist < 4:
                    continue
            return rx, ry

# --- UVODNI EKRAN ---
def show_start_screen():
    screen.fill(BACKGROUND_COLOR)

    # UCITAVANJE LOGO-a
    try:
        logo = pygame.image.load("assets/Pacman_logo.png").convert_alpha()
        logo = pygame.transform.scale(logo, (250, 200))
        logo_exists = True
    except:
        logo_exists = False
        print("Logo nije pronadjen")
    
    title_font = pygame.font.SysFont("Courier New", 55, bold=True)
    instruction_font = pygame.font.SysFont("Courier New", 20)
    
    # Crtanje ukrasnog cveća na dnu
    for i in range(10):
        x = 30 + i * 60
        y = HEIGHT - 90
        color = random.choice(FLOWER_COLORS)
        for j in range(5):
            angle = j * 72
            petal_x = x + 10 * math.cos(math.radians(angle))
            petal_y = y + 10 * math.sin(math.radians(angle))
            pygame.draw.circle(screen, color, (int(petal_x), int(petal_y)), 5)
        pygame.draw.circle(screen, (240, 230, 180), (x, y), 4)
    
    # CRTANJE LOGO-a
    if logo_exists:
        # Centriraj logo
        logo_rect = logo.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 170))
        screen.blit(logo, logo_rect)  
    else:
        # Ako nema logo, koristi tekst
        title_text = title_font.render("BLOSSOM HUNT", True, UI_TEXT_COLOR)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
        shadow_text = title_font.render("BLOSSOM HUNT", True, (180, 160, 190))
        shadow_rect = shadow_text.get_rect(center=(WIDTH // 2 + 3, HEIGHT // 2 - 117))
        screen.blit(shadow_text, shadow_rect)
        screen.blit(title_text, title_rect)
        pygame.draw.line(screen, UI_TEXT_COLOR, (WIDTH//2 - 150, HEIGHT//2 - 50), (WIDTH//2 + 150, HEIGHT//2 - 50), 2)
    
    # Instrukcije
    instructions = [
        "Kontroliši pčelu pomoću strelica",
        "Sakupljaj cvijeće (10 poena)",
        "Zlatni cvijet daje power-up (50 poena)",
        "Izbjegavaj leptire dok nisi moćna",
        "U power-up modu pojedi leptire (100 poena)"
    ]
    
    y_offset = HEIGHT // 2 - 20 if logo_exists else HEIGHT // 2
    for instr in instructions:
        instr_text = instruction_font.render(instr, True, UI_TEXT_COLOR)
        instr_rect = instr_text.get_rect(center=(WIDTH // 2, y_offset))
        screen.blit(instr_text, instr_rect)
        y_offset += 35
    
    # High score
    high_score = load_high_score()
    high_text = instruction_font.render(f"NAJBOLJI REZULTAT: {high_score}", True, (255, 150, 0))
    high_rect = high_text.get_rect(center=(WIDTH // 2, HEIGHT - 140))
    screen.blit(high_text, high_rect)
    
    # Poruka za početak
    press_text = instruction_font.render("PRITISNI SPACE ILI ENTER TASTER ZA POČETAK", True, (150, 50, 160))
    press_rect = press_text.get_rect(center=(WIDTH // 2, HEIGHT - 45))
    screen.blit(press_text, press_rect)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    waiting = False
    
    return True

# ============ GLAVNA FUNKCIJA ============

def main():
    if not show_start_screen():
        pygame.quit()
        sys.exit()

    try:
        logo = pygame.image.load("assets/Pacman_logo.png").convert_alpha()
        # Skaliraj logo na zeljenu velicinu (npr. 400x120)
        logo = pygame.transform.scale(logo, (400, 120))
    except:
        # Ako logo ne postoji, koristi tekst
        logo = None
        print("Logo nije pronadjen, koristi se tekstualni naslov")
    
    # Kreiraj zvukove jednom
    collect_sound = create_collect_sound()
    super_sound = create_super_sound()
    bg_music = create_background_music()
    bg_music.play(-1)
    death_sound = create_death_sound()
    
    # Inicijalizacija svih varijabli za restart
    def init_game():
        grid = [row[:] for row in BAŠTA]
        bee = Bee()
        butterfly_speeds = [0.6, 0.7, 0.8, 0.9, 0.5]
        butterflies = [
            Butterfly(2, 2, butterfly_speeds[0]),
            Butterfly(16, 2, butterfly_speeds[1]),
            Butterfly(2, 16, butterfly_speeds[2]),
            Butterfly(16, 16, butterfly_speeds[3]),
            Butterfly(9, 3, butterfly_speeds[4]),
        ]
        return grid, bee, butterflies
    
    grid, bee, butterflies = init_game()
    high_score = load_high_score()
    
    petals = []
    collect_effects = []
    score = 0
    lives = 3
    level = 1
    power_up_timer = 0
    scared_mode = False

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        
        # --- CRTANJE BAŠTE ---
        for r_idx, row in enumerate(grid):
            for c_idx, val in enumerate(row):
                x = c_idx * GRID_SIZE + OFFSET_X
                y = r_idx * GRID_SIZE + OFFSET_Y
                
                if val != 1:
                    pygame.draw.rect(screen, GRASS_COLOR, (x, y, GRID_SIZE, GRID_SIZE))
                
                if val == 1:
                    pygame.draw.rect(screen, WALL_COLOR, (x, y, GRID_SIZE-1, GRID_SIZE-1), border_radius=6)
                elif val == 0:
                    center = (x + GRID_SIZE//2, y + GRID_SIZE//2)
                    color = flower_colors_map.get((r_idx, c_idx), FLOWER_COLORS[0])
                    for i in range(5):
                        angle = i * 72
                        petal_x = center[0] + 5 * math.cos(math.radians(angle))
                        petal_y = center[1] + 5 * math.sin(math.radians(angle))
                        pygame.draw.circle(screen, color, (int(petal_x), int(petal_y)), 4)
                    pygame.draw.circle(screen, (240, 230, 180), center, 3)
                elif val == 2:
                    center = (x + GRID_SIZE//2, y + GRID_SIZE//2)
                    for i in range(12):
                        angle = i * 30
                        glow_x = center[0] + 14 * math.cos(math.radians(angle))
                        glow_y = center[1] + 14 * math.sin(math.radians(angle))
                        pygame.draw.circle(screen, SUPER_FLOWER_GLOW, (int(glow_x), int(glow_y)), 3)
                    for i in range(8):
                        angle = i * 45
                        petal_x = center[0] + 12 * math.cos(math.radians(angle))
                        petal_y = center[1] + 12 * math.sin(math.radians(angle))
                        pygame.draw.circle(screen, SUPER_FLOWER_COLOR, (int(petal_x), int(petal_y)), 6)
                    pygame.draw.circle(screen, (255, 255, 200), center, 5)

        # --- LOGIKA KORISNIČKOG UNOSA ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:    bee.next_dir_x, bee.next_dir_y = 0, -1
                elif event.key == pygame.K_DOWN:  bee.next_dir_x, bee.next_dir_y = 0, 1
                elif event.key == pygame.K_LEFT:  bee.next_dir_x, bee.next_dir_y = -1, 0
                elif event.key == pygame.K_RIGHT: bee.next_dir_x, bee.next_dir_y = 1, 0

        bee.move(grid)

        # Sakupljanje cvijeća
        if grid[bee.grid_y][bee.grid_x] == 0:
            grid[bee.grid_y][bee.grid_x] = 3
            score += 10
            collect_sound.play()
            for _ in range(4):
                petals.append(Petal(bee.x, bee.y))
            collect_effects.append(CollectEffect(bee.x, bee.y, FLOWER_COLORS[0]))
        elif grid[bee.grid_y][bee.grid_x] == 2:
            grid[bee.grid_y][bee.grid_x] = 3
            score += 50
            scared_mode = True
            power_up_timer = 300
            super_sound.play()
            for _ in range(12):
                petals.append(Petal(bee.x, bee.y))
            collect_effects.append(CollectEffect(bee.x, bee.y, SUPER_FLOWER_COLOR))

        if scared_mode:
            power_up_timer -= 1
            if power_up_timer <= 0:
                scared_mode = False

        # LOGIKA PROVJERE ZA NOVI NIVO (LEVEL UP)
        flowers_left = any(0 in row or 2 in row for row in grid)
        if not flowers_left:
            level += 1
            grid = [row[:] for row in BAŠTA]
            bee.__init__()
            
            # Podesi težinu nivoa
            setup_level(level, butterflies, grid)
            
            # Dodaj dodatni super cvijet na višim nivoima (ispravljeno: val == 0 umjesto 3)
            if level >= 3:
                empty_spots = [(x, y) for y, row in enumerate(grid) for x, val in enumerate(row) if val == 0]
                if empty_spots:
                    x, y = random.choice(empty_spots)
                    grid[y][x] = 2
                    flower_colors_map[(y, x)] = SUPER_FLOWER_COLOR
            
            # Respawan leptira (sa provjerom udaljenosti od pčele)
            for b in butterflies:
                rx, ry = get_random_grass_position(grid, bee)
                b.grid_x, b.grid_y = rx, ry
                b.x = rx * GRID_SIZE + GRID_SIZE // 2 + OFFSET_X
                b.y = ry * GRID_SIZE + GRID_SIZE // 2 + OFFSET_Y
            
            scared_mode = False
            pygame.time.wait(1000)
            continue

        # Leptiri i kolizije
        bee_pos = bee.get_position()
        for butterfly in butterflies:
            butterfly.move(grid, scared_mode, bee_pos)
            dist = math.hypot(bee.x - butterfly.x, bee.y - butterfly.y)
            if dist < GRID_SIZE / 1.3:
                if scared_mode:
                    score += 100
                    rx, ry = get_random_grass_position(grid, bee)
                    butterfly.grid_x, butterfly.grid_y = rx, ry
                    butterfly.x = rx * GRID_SIZE + GRID_SIZE // 2 + OFFSET_X
                    butterfly.y = ry * GRID_SIZE + GRID_SIZE // 2 + OFFSET_Y
                    collect_effects.append(CollectEffect(butterfly.x, butterfly.y, (200, 200, 255)))
                    collect_sound.play()
                else:
                    lives -= 1
                    death_sound.play()
                    collect_sound.play()
                    bee.__init__()
                    for b in butterflies:
                        rx, ry = get_random_grass_position(grid, bee)
                        b.grid_x, b.grid_y = rx, ry
                        b.x = rx * GRID_SIZE + GRID_SIZE // 2 + OFFSET_X
                        b.y = ry * GRID_SIZE + GRID_SIZE // 2 + OFFSET_Y
                    
                    if lives <= 0:
                        # Game Over ekran sa opcijama
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
                            new_record = True
                        else:
                            new_record = False
                        
                        screen.fill(BACKGROUND_COLOR)
                        try:
                            logo = pygame.image.load("assets/Pacman_logo.png").convert_alpha()
                            logo = pygame.transform.scale(logo, (200, 170))
                            logo_rect = logo.get_rect(center=(WIDTH // 2, 120))
                            screen.blit(logo, logo_rect)
                        except:
                            pass

                        font_large = pygame.font.SysFont("Courier New", 40, bold=True)
                        font_small = pygame.font.SysFont("Courier New", 25)
                        font_options = pygame.font.SysFont("Courier New", 20)
                        
                        go_text = font_large.render("Game Over", True, UI_TEXT_COLOR)
                        score_text = font_small.render(f"Score: {score}", True, UI_TEXT_COLOR)
                        screen.blit(go_text, (WIDTH//2 - 100, HEIGHT//2 - 80))
                        screen.blit(score_text, (WIDTH//2 - 70, HEIGHT//2 - 30))
                        
                        if new_record:
                            new_record_text = font_small.render("NEW HIGH SCORE!", True, (255, 215, 0))
                            screen.blit(new_record_text, (WIDTH//2 - 100, HEIGHT//2 + 10))
                        
                        restart_text = font_options.render("R - Restart", True, UI_TEXT_COLOR)
                        exit_text = font_options.render("ESC - Exit", True, UI_TEXT_COLOR)
                        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
                        exit_rect = exit_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 90))
                        screen.blit(restart_text, restart_rect)
                        screen.blit(exit_text, exit_rect)
                        
                        pygame.display.flip()
                        
                        waiting_for_input = True
                        while waiting_for_input:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    waiting_for_input = False
                                    running = False
                                elif event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_r:
                                        waiting_for_input = False
                                        # Restart igre - zaustavi staru muziku i pokreni novu
                                        pygame.mixer.stop()
                                        bg_music.play(-1)
                                        grid, bee, butterflies = init_game()
                                        score = 0
                                        lives = 3
                                        level = 1
                                        power_up_timer = 0
                                        scared_mode = False
                                        petals.clear()
                                        collect_effects.clear()
                                        high_score = load_high_score()
                                    elif event.key == pygame.K_ESCAPE:
                                        waiting_for_input = False
                                        running = False
                        continue

        # Ažuriranje čestica latica
        for p in petals[:]:
            p.update()
            if p.lifetime <= 0:
                petals.remove(p)
        
        # Ažuriranje efekata skupljanja
        for effect in collect_effects[:]:
            effect.update()
            effect.draw(screen)
            if effect.lifetime <= 0:
                collect_effects.remove(effect)

        # --- CRTANJE LIKOVA ---
        bee.draw(screen)
        for butterfly in butterflies:
            butterfly.draw(screen, scared_mode)
        for p in petals:
            p.draw(screen)

        # --- POWER-UP INDIKATOR ---
        if scared_mode:
            if power_up_timer % 30 < 15:
                font_power = pygame.font.SysFont("Courier New", 28, bold=True)
                power_text = font_power.render(" POWER UP! ", True, (255, 215, 0))
                text_rect = power_text.get_rect(center=(WIDTH//2, 50))
                screen.blit(power_text, text_rect)
            
            # Ispravljeno prikazivanje sekundi
            seconds_left = math.ceil(power_up_timer / 60)
            font_timer = pygame.font.SysFont("Courier New", 18)
            timer_text = font_timer.render(f" {seconds_left}s", True, (255, 215, 0))
            timer_rect = timer_text.get_rect(center=(WIDTH//2 + 170, 50))
            screen.blit(timer_text, timer_rect)

        # --- REFREŠOVANJE UI-A ---
        font = pygame.font.SysFont("Courier New", 20, bold=True)
        score_text = font.render(f"Score: {score}", True, UI_TEXT_COLOR)
        lives_text = font.render(f"Lives: {lives}", True, UI_TEXT_COLOR)
        level_text = font.render(f"Level: {level}", True, UI_TEXT_COLOR)
        highscore_text = font.render(f"Best: {high_score}", True, UI_TEXT_COLOR)
        
        screen.blit(score_text, (20, 20))
        screen.blit(lives_text, (180, 20))
        screen.blit(level_text, (350, 20))
        screen.blit(highscore_text, (WIDTH - 130, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()