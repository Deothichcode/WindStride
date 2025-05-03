import pygame # type: ignore
from pygame.locals import * # type: ignore
import pickle
from os import path
import random

import io
# import sys

# if hasattr(sys.stdout, "buffer"):
#     sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_with = 1200
screen_height = 700
game_over = False
game_win = False

#Define
score = 0
gold = 0

# Tạo sprite groups
blue_slime_group = pygame.sprite.Group()
green_slime_group = pygame.sprite.Group()
skeleton_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
rune_group = pygame.sprite.Group()
flag_group = pygame.sprite.Group()

#define font
font_score = pygame.font.SysFont('Bauhaus 93', 30)
font_small = pygame.font.Font('assests/font/Arial.ttf', 36)
font_small2 = pygame.font.Font('assests/font/Arial.ttf', 20)

#define col
white = (255,255,255)

screen = pygame.display.set_mode((screen_with, screen_height))
pygame.display.set_caption('WindStride')

try:
    logo = pygame.image.load('assests/gui/PNG/menu/LogoWindStride.png').convert_alpha()
    logo = pygame.transform.scale(logo, (32, 32))
    pygame.display.set_icon(logo)
except pygame.error:
    print("Không thể tải icon!")

#load ảnh
background_img = pygame.image.load('assests/background/PNG/game_background_2/game_background_2.png')
background_img = pygame.transform.scale(background_img, (screen_with, screen_height))
#Ảnh số sao nhận được khi chơi xong
star_images = [
    pygame.image.load("assests/gui/PNG/level_select/star_4.png").convert_alpha(),
    pygame.image.load("assests/gui/PNG/level_select/star_1.png").convert_alpha(),
    pygame.image.load("assests/gui/PNG/level_select/star_2.png").convert_alpha(),
    pygame.image.load("assests/gui/PNG/level_select/star_3.png").convert_alpha(),
]
# Quy đổi điểm thành sao 
def get_star_count(score, max_score):
    ratio = score / max_score
    if ratio >= 0.9:
        return 1
    elif ratio >= 0.6:
        return 2
    elif ratio >= 0.3:
        return 3
    else:
        return 0

#Vẽ sao     
def draw_stars(screen, score, max_score, x, y):
    star_count = get_star_count(score, max_score)
    screen.blit(star_images[star_count], (x, y))

#You win
def show_win_popup(screen, score, max_score, star_images, screen_width, screen_height):
    popup_width = 500
    popup_height = 350
    popup_x = (screen_width - popup_width) // 2
    popup_y = (screen_height - popup_height) // 2

    # Nền mờ
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Hộp popup
    pygame.draw.rect(screen, (30, 30, 30), (popup_x, popup_y, popup_width, popup_height), border_radius=20)
    pygame.draw.rect(screen, (255, 255, 255), (popup_x, popup_y, popup_width, popup_height), 4, border_radius=20)

    # Load hình "You Win!"
    you_win_img = pygame.image.load("assests/gui/PNG/you_win/header.png").convert_alpha()
    you_win_rect = you_win_img.get_rect(center=(screen_width // 2, popup_y + 60))
    screen.blit(you_win_img, you_win_rect)

    # Hiển thị số sao theo điểm
    star_count = get_star_count(score, max_score)
    star_img = star_images[star_count]  # đã load trước: danh sách star_0 đến star_3
    star_rect = star_img.get_rect(center=(screen_width // 2, popup_y + 140))
    screen.blit(star_img, star_rect)

    # Nút chơi tiếp và về menu
    continue_button = Button("assests/gui/PNG/btn/play.png", popup_x + 140, popup_y + 250, 0.5)
    menu_button = Button("assests/gui/PNG/btn/menu.png", popup_x + 360, popup_y + 250, 0.5)

    pygame.display.update()

    # Đợi người chơi nhấn nút
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()

        if continue_button.draw():
            return "continue"
        if menu_button.draw():
            return "menu"

        pygame.display.update()

#You lose
def show_lose_popup(screen,screen_width, screen_height):
    popup_width = 500
    popup_height = 350
    popup_x = (screen_width - popup_width) // 2
    popup_y = (screen_height - popup_height) // 2

    # Nền mờ
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Hộp popup
    pygame.draw.rect(screen, (30, 30, 30), (popup_x, popup_y, popup_width, popup_height), border_radius=20)
    pygame.draw.rect(screen, (255, 255, 255), (popup_x, popup_y, popup_width, popup_height), 4, border_radius=20)

    # Load hình "You Lose!"
    you_lose_img = pygame.image.load("assests/gui/PNG/you_lose/header.png").convert_alpha()
    you_lose_rect = you_lose_img.get_rect(center=(screen_width // 2, popup_y + 60))
    screen.blit(you_lose_img, you_lose_rect)

    # Nút chơi tiếp và về menu
    restart_button = Button("assests/gui/PNG/btn/restart.png", popup_x + 140, popup_y + 250, 0.5)
    menu_button = Button("assests/gui/PNG/btn/menu.png", popup_x + 360, popup_y + 250, 0.5)

    pygame.display.update()

    # Đợi người chơi nhấn nút
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()

        if restart_button.draw():
            return "restart"
        if menu_button.draw():
            return "menu"

        pygame.display.update()
        
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))


tile_size = 60 #mỗi ô grid có pixel là 60
def draw_grid():
    # Tính số lượng đường cần vẽ dựa trên kích thước màn hình
    horizontal_lines = screen_height // tile_size + 1
    vertical_lines = screen_with // tile_size + 1
    
    # Vẽ đường ngang
    for line in range(horizontal_lines):
        pygame.draw.line(screen, (255,255,255), (0, line * tile_size), (screen_with, line * tile_size))
    # Vẽ đường dọc
    for line in range(vertical_lines):
        pygame.draw.line(screen, (255,255,255), (line * tile_size, 0), (line * tile_size, screen_height))

#lop chuyen dong cua vat the
class AnimatedObject:
    def __init__(self, x, y, image_path, scale, object_type, animation_speed=10, move_range=3):
        self.images = [] #list chua khung hinh
        self.index = 0 #thu tu khung hinh
        self.counter = 0 #thoi gian lam moi khung hinh
        # dieu chinh toc do lam moi frame
        if object_type in ['coin', 'rune']:
            self.animation_speed = animation_speed*1.5
        elif object_type in ['flag']:
            self.animation_speed = animation_speed*2.5 #lam cham toc do lam moi frame cua la co
        else:
            self.animation_speed = animation_speed
        
        self.object_type = object_type
        self.original_y = y
        self.original_x = x
        self.direction = 1  
        self.move_counter = 0
        self.move_range = move_range
        
        # load animation
        if object_type == 'coin':
            for i in range(1, 5): 
                img = pygame.image.load(f'assests/objects/Item/coin/{i}.png')
                img = pygame.transform.scale(img, scale)
                self.images.append(img)
        elif object_type == 'rune':
            for i in range(1, 5):  
                img = pygame.image.load(f'assests/objects/Item/rune/{i}.png')
                img = pygame.transform.scale(img, scale)
                self.images.append(img)
        elif object_type == 'flag':
            for i in range(1, 5):  
                img = pygame.image.load(f'assests/objects/Item/flag/{i}.png')
                img = pygame.transform.scale(img, scale)
                self.images.append(img)
        elif object_type == 'plant':
            for i in range(0, 90): 
                img = pygame.image.load(f'assests/objects/Plant Animations/Plant 1/Plant1_{i:05d}.png')
                img = pygame.transform.scale(img, scale)
                self.images.append(img)
        
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def update(self):
        # Update animation frame
        self.counter += 1
        if self.counter > self.animation_speed:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
            self.image = self.images[self.index]
        
        # Removed slime movement code to make slimes static
    
    def draw(self):
        screen.blit(self.image, self.rect)
class Button():
    def __init__(self, image, x, y, scale=1.0):
        self.image = pygame.image.load(image).convert_alpha()
        width = int(self.image.get_width() * scale)
        height = int(self.image.get_height() * scale)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        screen.blit(self.image, self.rect)
        return action
class Player():
    def __init__(self, x, y):
        self.reset(x,y)

    def update(self,game_over, game_win):
        dx = 0
        dy = 0
        walk_cooldown = 5
        jump_cooldown = 6
        if game_over == False: 
            # Lấy trạng thái phím
            key = pygame.key.get_pressed()
            
            # Xử lý nhảy
            if key[pygame.K_UP] and not self.jumped and not self.in_air:
                self.vel_y = -15
                self.jumped = True
                self.in_air = True
                self.counter = 0
                self.index = 0
                
            # Xử lý di chuyển trái/phải
            if key[pygame.K_LEFT]:
                dx -= 4
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 4
                self.counter += 1
                self.direction = 1
                
            # Xử lý animation
            if not (key[pygame.K_LEFT] or key[pygame.K_RIGHT]) and not self.in_air:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.idle_image_right
                elif self.direction == -1:
                    self.image = self.idle_image_left
                else:
                    self.image = self.idle_image_right

            # Animation nhảy và chạy
            if self.in_air:
                if self.counter > jump_cooldown:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len(self.images_jump_right):
                        self.index = len(self.images_jump_right) - 1
                    if self.direction >= 0:
                        self.image = self.images_jump_right[self.index]
                    else:
                        self.image = self.images_jump_left[self.index]
            elif self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Áp dụng trọng lực
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Xử lý va chạm với địa hình
            for tile in world.tile_list:
                # Va chạm theo chiều dọc
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:  # Đang nhảy lên
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:  # Đang rơi xuống
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.jumped = False
                        self.in_air = False
                # Va chạm theo chiều ngang
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #Xử lý va chạm với Lava 
                if pygame.sprite.spritecollide(self,lava_group,False):
                    game_over = True
                #Xử lý va chạm với Enemy
                if pygame.sprite.spritecollide(self,blue_slime_group,False) or pygame.sprite.spritecollide(self,green_slime_group,False) or pygame.sprite.spritecollide(self,skeleton_group,False) :
                    game_over = True
                #Xử lý va chạm với Flag
                if pygame.sprite.spritecollide(self, flag_group, True):
                    game_win = True

            # Cập nhật vị trí
            self.rect.x += dx
            self.rect.y += dy
        else:
        # Chạy animation chết
            if self.death_index < len(self.dead_image):
                self.death_counter += 1
                if self.death_counter >= 10:  # số frame chờ giữa 2 hình
                    self.image = self.dead_image[self.death_index]
                    self.death_index += 1
                    self.death_counter = 0
           
            else:
            # Animation đã xong giữ frame cuối
                self.image = self.dead_image[-1]
                if self.vel_y > 10:  # Giới hạn tốc độ rơi tối đa
                    self.vel_y = 10
                self.rect.y += self.vel_y

                for tile in world.tile_list:
                    if tile[1].colliderect(self.rect.x, self.rect.y, self.width, self.height):
                        # Dừng rơi khi chạm đất
                        self.rect.bottom = tile[1].top
                        self.vel_y = 0  

        # Giới hạn màn hình
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_with:
            self.rect.right = screen_with
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            dy = 0
            self.jumped = False
            self.in_air = False

        # Cập nhật vị trí sprite dựa trên hitbox
        sprite_width = 47
        sprite_height = 74
        sprite_x = self.rect.x - (sprite_width - self.width) // 2
        sprite_y = self.rect.y - (sprite_height - self.height) // 2
        
        # Vẽ nhân vật và hitbox
        screen.blit(self.image, (sprite_x, sprite_y))
        return game_over, game_win
    def draw(self):
        sprite_width = 47
        sprite_height = 74
        sprite_x = self.rect.x - (sprite_width - self.width) // 2
        sprite_y = self.rect.y - (sprite_height - self.height) // 2
        
        # Vẽ nhân vật và hitbox
        screen.blit(self.image, (sprite_x, sprite_y))
        #pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

    def reset(self, x ,y):
        self.images_right = [] #list frame di sang phai
        self.images_left = [] #list frame di sang trai
        self.images_jump_right = [] #list frame nhảy sang phải
        self.images_jump_left = [] #list frame nhảy sang trái
        self.index = 0 #thu tu frame
        self.counter = 0 #thoi gian lam moi frame
        
        # Load frames chạy
        for num in range(1,7):
            img_right = pygame.image.load(f'assests/character/male/run/run{num}.png')
            img_right = pygame.transform.scale(img_right, (37, 64))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
            
        # Load frames nhảy
        for num in range(1,8):
            img_jump_right = pygame.image.load(f'assests/character/male/jump/j{num}.png')
            img_jump_right = pygame.transform.scale(img_jump_right, (37,64))
            img_jump_left = pygame.transform.flip(img_jump_right, True, False)
            self.images_jump_right.append(img_jump_right)
            self.images_jump_left.append(img_jump_left)

        # Load frame đứng yên
        self.idle_image_right = pygame.image.load('assests/character/male/idle/Idle.png')
        self.idle_image_right = pygame.transform.scale(self.idle_image_right, (37, 64))
        self.idle_image_left = pygame.transform.flip(self.idle_image_right, True, False)
        self.image = self.idle_image_right
        
        # Nhân vật game over 
        self.dead_image = [pygame.image.load('assests/character/male/dead/1.png'),
                           pygame.image.load('assests/character/male/dead/2.png'),
                           pygame.image.load('assests/character/male/dead/3.png'),
                           pygame.image.load('assests/character/male/dead/4.png')]
        self.death_index = 0
        self.death_counter = 0
        # Tạo hitbox nhỏ hơn sprite
        self.width = 22  
        self.height = 55 
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        

        sprite_width = 37
        sprite_height = 64
        self.rect.x = x + (sprite_width - self.width) // 2  # Căn giữa theo chiều ngang
        self.rect.y = y + (sprite_height - self.height) // 2  # Căn giữa theo chiều dọc
        
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = False  #Biến kiểm tra nhân vật có đang trong không trung

class World():
    def __init__(self,data):
        self.tile_list = []
        self.animated_tiles = []
        self.enemies = []  # Thêm list để lưu các enemy
        self.animation_frames = {}  # Dictionary lưu các frame animation
        self.animation_count = 0  # Biến đếm cho animation
        self.animation_index = 0  # Index hiện tại của animation
        
        # Tải tất cả các hình ảnh cần thiết FIRST
        ground_img = pygame.image.load('assests/tileset/Forest Tileset/1 Tiles/Tile_12.png') # Ground tile (1)
        dirt_img = pygame.image.load('assests/tileset/Forest Tileset/1 Tiles/Tile_02.png') # Dirt blocks (2)
        grass_img = pygame.image.load('assests/objects/Plant Animations/Plant 1/Plant1_00000.png') # Plant1 (3)
        blue_slime_img = pygame.image.load('assests/objects/Creep/Blue_Slime/idle/1.png') # Blue slime (5)
        platform_x_img = pygame.image.load('assests/tileset/Forest Tileset/1 Tiles/Tile_08.png') # Platforms (6, 17)
        lava_img = pygame.image.load('assests/tileset/Forest Tileset/1 Tiles/Tile_20.png') # Lava (8)
        # coin_img = pygame.image.load('assests/objects/Item/coin/1.png') # Coin (9)
        exit_img = pygame.image.load('assests/objects/Item/flag/1.png') # Exit (10)
        plant2_img = pygame.image.load('assests/objects/Plant Animations/Plant 2/Plant2_00000.png') # Plant2 (11)
        plant3_img = pygame.image.load('assests/objects/Plant Animations/Plant 3/Plant3_00000.png') # Plant3 (12)
        plant4_img = pygame.image.load('assests/objects/Plant Animations/Plant 4/Plant4_00000.png') if path.exists('assests/objects/Plant Animations/Plant 4/Plant4_00000.png') else grass_img # Plant4 (13)
        plant5_img = pygame.image.load('assests/objects/Plant Animations/Plant 5/Plant5_00000.png') if path.exists('assests/objects/Plant Animations/Plant 5/Plant5_00000.png') else grass_img # Plant5 (14)
        plant6_img = pygame.image.load('assests/objects/Plant Animations/Plant 6/Plant6_00000.png') if path.exists('assests/objects/Plant Animations/Plant 6/Plant6_00000.png') else grass_img # Plant6 (15)
        rune_img = pygame.image.load('assests/objects/Item/rune/1.png') # Rune (16)
        blue_flower1_img = pygame.image.load('assests/objects/Plant Animations/BlueFlower1/BlueFlower_00000.png') # BlueFlower1 (18)
        blue_flower2_img = pygame.image.load('assests/objects/Plant Animations/BlueFlower2/BluePlantClosed_00000.png') # BlueFlower2 (19)
        green_slime_img = pygame.image.load('assests/objects/Creep/Green_Slime/idle/1.png') # Green slime
        skeleton_img = pygame.image.load('assests/objects/Creep/Skeleton/idle/1.png') # Skeleton
        # tải các khung hình động cho các đối tượng khác nhau
        
        # Các khung hình động cho cờ
        # flag_frames = []
        # flag_frames.append(pygame.transform.scale(exit_img, (int(tile_size*1.5), int(tile_size * 2.25))))  # Sử dụng exit_img đã tải làm frame đầu tiên
        # for i in range(2, 5):
        #     img = pygame.image.load(f'assests/objects/Item/flag/{i}.png')
        #     flag_frames.append(pygame.transform.scale(img, (int(tile_size*1.5), int(tile_size * 2.25))))
        # self.animation_frames['flag'] = flag_frames
        
        # Các khung hình động cho cây - thêm hoạt ảnh cho cây
        plant_frames = []
        plant_frames.append(pygame.transform.scale(grass_img, (tile_size*3, tile_size*3)))  # Sử dụng grass_img đã tải làm frame đầu tiên
        for i in range(0, 90):
            img = pygame.image.load(f'assests/objects/Plant Animations/Plant 1/Plant1_{i:05d}.png')
            plant_frames.append(pygame.transform.scale(img, (tile_size*3, tile_size*3)))
        self.animation_frames['plant'] = plant_frames
        
        # Các khung hình động cho Plant2
        plant2_frames = []
        plant2_frames.append(pygame.transform.scale(plant2_img, (tile_size*3, tile_size*3)))  # Sử dụng plant2_img đã tải
        for i in range(0, 90):
            img = pygame.image.load(f'assests/objects/Plant Animations/Plant 2/Plant2_{i:05d}.png')
            plant2_frames.append(pygame.transform.scale(img, (tile_size*3, tile_size*3)))
        self.animation_frames['plant2'] = plant2_frames
        
        # Các khung hình động cho Plant3
        plant3_frames = []
        plant3_frames.append(pygame.transform.scale(plant3_img, (tile_size*3, tile_size*3)))  # Sử dụng plant3_img đã tải
        self.animation_frames['plant3'] = plant3_frames
        
        # Các khung hình động cho Plant4
        plant4_frames = []
        plant4_frames.append(pygame.transform.scale(plant4_img, (tile_size*3, tile_size*3)))  # Sử dụng plant4_img đã tải
        self.animation_frames['plant4'] = plant4_frames
        
        # Các khung hình động cho Plant5
        plant5_frames = []
        plant5_frames.append(pygame.transform.scale(plant5_img, (tile_size*3, tile_size*3)))  # Sử dụng plant5_img đã tải
        self.animation_frames['plant5'] = plant5_frames
        
        # Các khung hình động cho Plant6
        plant6_frames = []
        plant6_frames.append(pygame.transform.scale(plant6_img, (tile_size*3, tile_size*3)))  # Sử dụng plant6_img đã tải
        self.animation_frames['plant6'] = plant6_frames
        
        # Các khung hình động cho hoa xanh 1
        blue_flower1_frames = []
        blue_flower1_frames.append(pygame.transform.scale(blue_flower1_img, (tile_size*3, tile_size*3)))  # Sử dụng blue_flower1_img đã tải
        for i in range(0, 60):
            img = pygame.image.load(f'assests/objects/Plant Animations/BlueFlower1/BlueFlower_{i:05d}.png')
            blue_flower1_frames.append(pygame.transform.scale(img, (tile_size*3, tile_size*3)))
        self.animation_frames['blue_flower1'] = blue_flower1_frames
        
        # Các khung hình động cho hoa xanh 2
        blue_flower2_frames = []
        blue_flower2_frames.append(pygame.transform.scale(blue_flower2_img, (tile_size*3, tile_size*3)))  # Sử dụng blue_flower2_img đã tải
        for i in range(0, 60):
            img = pygame.image.load(f'assests/objects/Plant Animations/BlueFlower2/BluePlantClosed_{i:05d}.png')
            blue_flower2_frames.append(pygame.transform.scale(img, (tile_size*3, tile_size*3)))
        self.animation_frames['blue_flower2'] = blue_flower2_frames
        
        row_count = 0  
        for row in data:
            col_count = 0 # Biến đếm cột hiện tại
            for tile in row:
                # Xử lý từng loại tile theo giá trị của nó
                if tile == 1:  # Ground blocks
                    img = pygame.transform.scale(ground_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                    
                elif tile == 2:  # Dirt blocks
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                    
                elif tile == 3:  # Plant1 - Có hoạt ảnh
                    img = self.animation_frames['plant'][0]  # Bắt đầu với frame đầu tiên
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect, 'plant')  # Đánh dấu cho hoạt ảnh
                    self.animated_tiles.append(tile)
                    
                elif tile == 5:  # Blue slime
                    enemy = Enemy(col_count * tile_size, row_count * tile_size, 'blue_slime')
                    self.enemies.append(enemy)
                    blue_slime_group.add(enemy)
                    
                elif tile == 6:  # Platform X (top)
                    img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 2.5))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect, 'platform_x')  # Đánh dấu là platform di chuyển ngang
                    self.tile_list.append(tile)
                    
                elif tile == 17:  # Platform X (bottom)
                    img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 2.5))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size + tile_size // 2 + 5
                    tile = (img, img_rect, 'platform_x')  # Đánh dấu là platform di chuyển ngang
                    self.tile_list.append(tile)
                    
                elif tile == 8:  # Lava
                    lava = Lava( col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                    
                elif tile == 9:  # Coin - Có hoạt ảnh
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                    
                elif tile == 10:  # Exit (Flag) - Có hoạt ảnh
                    flag = Flag(col_count * tile_size - tile_size//4, row_count * tile_size - (tile_size * 1.25) )
                    flag_group.add(flag)
                    
                elif tile == 11:  # Plant2 - Có hoạt ảnh
                    img = self.animation_frames['plant2'][0]  # Sử dụng hoạt ảnh cụ thể cho plant2
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect, 'plant2')  # Sử dụng định danh duy nhất
                    self.animated_tiles.append(tile)
                    
                elif tile == 12:  # Plant3 - Có hoạt ảnh
                    img = self.animation_frames['plant3'][0]  # Sử dụng hoạt ảnh cụ thể cho plant3
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect, 'plant3')  # Sử dụng định danh duy nhất
                    self.animated_tiles.append(tile)
                    
                elif tile == 13:  # Plant4 - Có hoạt ảnh
                    img = self.animation_frames['plant4'][0]  # Sử dụng hoạt ảnh cụ thể cho plant4
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect, 'plant4')  # Sử dụng định danh duy nhất
                    self.animated_tiles.append(tile)
                    
                elif tile == 14:  # Plant5 - Có hoạt ảnh
                    img = self.animation_frames['plant5'][0]  # Sử dụng hoạt ảnh cụ thể cho plant5
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect, 'plant5')  # Sử dụng định danh duy nhất
                    self.animated_tiles.append(tile)
                    
                elif tile == 15:  # Plant6 - Có hoạt ảnh
                    img = self.animation_frames['plant6'][0]  # Sử dụng hoạt ảnh cụ thể cho plant6
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect, 'plant6')  # Sử dụng định danh duy nhất
                    self.animated_tiles.append(tile)
                    
                elif tile == 16:  # Rune - Có hoạt ảnh
                    rune = Rune(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    rune_group.add(rune)
                    
                elif tile == 18:  # BlueFlower1 - Có hoạt ảnh
                    img = self.animation_frames['blue_flower1'][0]  # Sử dụng hoạt ảnh blue_flower1
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect, 'blue_flower1')  # Sử dụng định danh duy nhất
                    self.animated_tiles.append(tile)
                    
                elif tile == 19:  # BlueFlower2 - Có hoạt ảnh
                    img = self.animation_frames['blue_flower2'][0]  # Sử dụng hoạt ảnh blue_flower2
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect, 'blue_flower2')  # Sử dụng định danh duy nhất
                    self.animated_tiles.append(tile)
                elif tile == 20:  # Green slime
                    enemy = Enemy(col_count * tile_size, row_count * tile_size, 'green_slime')
                    self.enemies.append(enemy)
                    green_slime_group.add(enemy) 
                elif tile == 21:  # Skeleton
                    enemy = Enemy(col_count * tile_size, row_count * tile_size, 'skeleton')
                    self.enemies.append(enemy)
                    skeleton_group.add(enemy)
                
                # Tăng chỉ số cột sau khi xử lý một ô
                col_count += 1
            # Tăng chỉ số hàng sau khi xử lý một hàng hoàn chỉnh
            row_count += 1

    def update_animations(self):
        # Cập nhật bộ đếm hoạt ảnh
        self.animation_count += 1
        
        # Thay đổi khung hình hoạt ảnh mỗi 10 khung hình cho hầu hết các đối tượng
        if self.animation_count >= 10:
            self.animation_count = 0
            self.animation_index = (self.animation_index + 1) % 4  # Lặp qua 4 khung hình cho hầu hết các đối tượng
            
        # Cập nhật tất cả các tile hoạt ảnh với khung hình mới
        for i, tile in enumerate(self.animated_tiles):
            img, rect, tile_type = tile
            
            # if tile_type == 'flag':
            #     self.animated_tiles[i] = (self.animation_frames['flag'][self.animation_index % len(self.animation_frames['flag'])], rect, tile_type)
            if tile_type == 'plant':
                plant_index = (pygame.time.get_ticks() // 50) % len(self.animation_frames['plant'])  # Sử dụng thời gian thực để animation mượt mà và nhanh hơn
                self.animated_tiles[i] = (self.animation_frames['plant'][plant_index], rect, tile_type)
            elif tile_type == 'plant2':
                plant_index = (pygame.time.get_ticks() // 50) % len(self.animation_frames['plant2'])  # Sử dụng thời gian thực để animation mượt mà và nhanh hơn
                self.animated_tiles[i] = (self.animation_frames['plant2'][plant_index], rect, tile_type)
            elif tile_type == 'plant3':
                plant_index = (pygame.time.get_ticks() // 50) % len(self.animation_frames['plant3'])
                self.animated_tiles[i] = (self.animation_frames['plant3'][plant_index], rect, tile_type)
            elif tile_type == 'plant4':
                plant_index = (pygame.time.get_ticks() // 50) % len(self.animation_frames['plant4'])
                self.animated_tiles[i] = (self.animation_frames['plant4'][plant_index], rect, tile_type)
            elif tile_type == 'plant5':
                plant_index = (pygame.time.get_ticks() // 50) % len(self.animation_frames['plant5'])
                self.animated_tiles[i] = (self.animation_frames['plant5'][plant_index], rect, tile_type)
            elif tile_type == 'plant6':
                plant_index = (pygame.time.get_ticks() // 50) % len(self.animation_frames['plant6'])
                self.animated_tiles[i] = (self.animation_frames['plant6'][plant_index], rect, tile_type)
            elif tile_type == 'blue_flower1':
                flower_index = (pygame.time.get_ticks() // 50) % len(self.animation_frames['blue_flower1'])  
                self.animated_tiles[i] = (self.animation_frames['blue_flower1'][flower_index], rect, tile_type)
            elif tile_type == 'blue_flower2':
                flower_index = (pygame.time.get_ticks() // 50) % len(self.animation_frames['blue_flower2'])  
                self.animated_tiles[i] = (self.animation_frames['blue_flower2'][flower_index], rect, tile_type)
    
    def draw(self):
        # Cập nhật hoạt ảnh
        self.update_animations()
        
        # Vẽ đối tượng cờ trước tiên (chúng nên hiển thị đằng sau mọi thứ)
        for tile in self.animated_tiles:
            img, rect, tile_type = tile
            if tile_type == 'flag':
                screen.blit(img, rect)
        
        # Vẽ đối tượng cây (chúng nên hiển thị đằng sau các tile thông thường nhưng phía trên cờ)
        for tile in self.animated_tiles:
            img, rect, tile_type = tile
            if tile_type.startswith('plant') or tile_type == 'plant' or tile_type.startswith('blue_flower'):
                screen.blit(img, rect)
        
        # Vẽ các tile tĩnh thông thường
        for tile in self.tile_list:
            # Bỏ qua các tile đặc biệt cần vẽ riêng
            if len(tile) <= 2 or tile[2] not in ['lava', 'platform_x']:
                screen.blit(tile[0], tile[1])
        
        # Vẽ các tile đặc biệt phía trên cùng (lava, platforms)
        for tile in self.tile_list:
            if len(tile) > 2 and tile[2] in ['lava', 'platform_x']:
                screen.blit(tile[0], tile[1])
        
        for tile in self.tile_list:
                screen.blit(tile[0], tile[1])
                #pygame.draw.rect(screen, (255, 0, 0), tile[1], 2)
                
        # Vẽ và cập nhật các enemy
        for enemy in self.enemies:
            enemy.update()
            enemy.draw(screen)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        pygame.sprite.Sprite.__init__(self)
        self.enemy_type = enemy_type
        self.animation_frames = []
        self.frame_index = 0
        self.animation_cooldown = 15
        self.counter = 0
        
        if enemy_type == 'blue_slime' or enemy_type == 'green_slime':
            folder = 'Blue_Slime' if enemy_type == 'blue_slime' else 'Green_Slime'
            for i in range(1, 12):  # Load tất cả frame nhảy
                img = pygame.image.load(f'assests/objects/Creep/{folder}/jump/{i}.png')
                img = pygame.transform.scale(img, (int(tile_size*0.6), int(tile_size*0.6)))
                self.animation_frames.append(img)
            
            self.image = self.animation_frames[0]
            self.direction = 1  # 1 = phải, -1 = trái
            self.vel_y = 0
            self.jumping = False
            self.jump_count = 0  # Đếm số lần nhảy ở mỗi bên
            self.max_jumps = 3  # Số lần nhảy tối đa mỗi bên
            self.jump_delay = 0  # Thời gian chờ giữa các lần nhảy
            self.jump_cooldown = 40  # Số frame chờ trước khi nhảy tiếp
            self.on_ground = True
            self.move_speed = 0.6
            self.first_jump = True  # Đánh dấu nhảy lần đầu không bị delay
            
        elif enemy_type == 'skeleton':
            for i in range(1, 7):  # Load tất cả frame đi bộ
                img = pygame.image.load(f'assests/objects/Creep/Skeleton/walk/{i}.png')
                img = pygame.transform.scale(img, (int(tile_size*0.8), int(tile_size*1.3)))
                self.animation_frames.append(img)
            
            self.image = self.animation_frames[0]
            self.direction = 1
            self.move_speed = 0.6
        
        # Set up rect và hitbox
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Hitbox nhỏ hơn sprite
        self.hitbox = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 5,
            self.rect.width - 20,
            self.rect.height - 10
        )

    def check_collision(self, dx, dy):
        for tile in world.tile_list:
            # Va chạm theo chiều dọc
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.vel_y < 0:  # Đang nhảy lên
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:  # Đang rơi xuống
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    if self.enemy_type in ['blue_slime', 'green_slime']:
                        self.jumping = False
                        self.on_ground = True
            
            # Va chạm theo chiều ngang
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                self.direction *= -1
                return 0, dy
                
        return dx, dy

    def check_edge(self):
        ahead_x = self.rect.x + (self.rect.width if self.direction == 1 else -5)
        test_rect = pygame.Rect(ahead_x, self.rect.bottom + 5, 5, 5)
        
        has_ground = False
        for tile in world.tile_list:
            if tile[1].colliderect(test_rect):
                has_ground = True
                break
        
        if not has_ground:
            self.direction *= -1

    def update(self):
        dx = 0
        dy = 0
        
        # Xử lý animation
        self.counter += 1
        if self.counter >= self.animation_cooldown:
            self.counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.animation_frames)
            if self.direction == 1:
                self.image = self.animation_frames[self.frame_index]
            else:
                self.image = pygame.transform.flip(self.animation_frames[self.frame_index], True, False)

        if self.enemy_type in ['blue_slime', 'green_slime']:
            # Xử lý nhảy
            if self.on_ground and not self.jumping:
                if self.first_jump or self.jump_delay >= self.jump_cooldown:
                    # Nhảy ngay lập tức nếu là lần đầu hoặc đã đủ thời gian chờ
                    self.jumping = True
                    self.on_ground = False
                    self.vel_y = -5  # Lực nhảy
                    self.jump_count += 1
                    self.jump_delay = 0
                    self.first_jump = False  # Đánh dấu đã nhảy lần đầu
                else:
                    self.jump_delay += 1  # Đếm thời gian chờ nếu không nhảy
                
            # Áp dụng trọng lực
            if not self.on_ground:
                self.vel_y += 0.4
                if self.vel_y > 8:
                    self.vel_y = 8
            
            # Chuyển động
            dy = self.vel_y
            dx = self.move_speed * self.direction
            
            # Kiểm tra va chạm
            dx, dy = self.check_collision(dx, dy)
            
            # Cập nhật vị trí
            self.rect.x += dx
            self.rect.y += dy
            
            # Kiểm tra đổi hướng sau 3 lần nhảy
            if self.on_ground and self.jump_count >= self.max_jumps:
                self.direction *= -1
                self.jump_count = 0
            
        elif self.enemy_type == 'skeleton':
            dx = self.move_speed * self.direction
            
            # Áp dụng trọng lực
            self.vel_y = 5  # Tốc độ rơi cố định
            dy = self.vel_y
            
            # Kiểm tra va chạm và rìa
            dx, dy = self.check_collision(dx, dy)
            self.check_edge()
            
            # Cập nhật vị trí
            self.rect.x += dx
            self.rect.y += dy
        
        # Cập nhật hitbox
        self.hitbox.x = self.rect.x + 10
        self.hitbox.y = self.rect.y + 5
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        #pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)


class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('assests/tileset/Forest Tileset/1 Tiles/Tile_20.png')
        self.image = pygame.transform.scale(img,(tile_size,tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y= y
                        
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, is_icon=False):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('assests/objects/Item/coin/1.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.is_icon = is_icon  # Đánh dấu nếu là icon

        self.coin_frames = []
        self.coin_frames.append(pygame.transform.scale(img, (int(tile_size * 0.5), int(tile_size * 0.5))))
        for i in range(2, 5):
            img = pygame.image.load(f'assests/objects/Item/coin/{i}.png')
            self.coin_frames.append(pygame.transform.scale(img, (int(tile_size * 0.5), int(tile_size * 0.5))))
        self.animation_count = 0
        self.animation_index = 0

    def update(self):
        self.animation_count += 1
        if self.animation_count >= 10:
            self.animation_count = 0
            self.animation_index = (self.animation_index + 1) % len(self.coin_frames)
            img = self.coin_frames[self.animation_index]
            self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        

class Rune(pygame.sprite.Sprite):
    def __init__(self, x, y, is_icon=False):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('assests/objects/Item/rune/1.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.is_icon = is_icon  # Đánh dấu nếu là icon

        self.rune_frames = []
        self.rune_frames.append(pygame.transform.scale(img, (int(tile_size * 0.5), int(tile_size * 0.5))))
        for i in range(2, 5):
            img = pygame.image.load(f'assests/objects/Item/rune/{i}.png')
            self.rune_frames.append(pygame.transform.scale(img, (int(tile_size * 0.5), int(tile_size * 0.5))))
        self.animation_count = 0
        self.animation_index = 0

    def update(self):
        self.animation_count += 1
        if self.animation_count >= 10:
            self.animation_count = 0
            self.animation_index = (self.animation_index + 1) % len(self.rune_frames)
            img = self.rune_frames[self.animation_index]
            self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))

class Flag(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('assests/objects/Item/flag/1.png')
        self.image = pygame.transform.scale(img,(int(tile_size * 1.5), int(tile_size * 2.25)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.flag_frames = []
        self.flag_frames.append(pygame.transform.scale(img, (int(tile_size * 1.5), int(tile_size * 2.25))))
        for i in range(2, 5):
            img = pygame.image.load(f'assests/objects/Item/flag/{i}.png')
            self.flag_frames.append(pygame.transform.scale(img, (int(tile_size * 1.5), int(tile_size * 2.25))))
        self.animation_count = 0
        self.animation_index = 0

    def update(self):
        self.animation_count += 1
        if self.animation_count >= 10:
            self.animation_count = 0
            self.animation_index = (self.animation_index + 1) % len(self.flag_frames)
            img = self.flag_frames[self.animation_index]
            self.image = pygame.transform.scale(img, (int(tile_size * 1.5), int(tile_size * 2.25)))

# Hàm để tải dữ liệu level từ file
def load_level_data(self):
    level_file = f'levels/level.data/level1_data'
    try:
        if path.exists(level_file):
            pickle_in = open(level_file, 'rb')
            data = pickle.load(pickle_in)
            pickle_in.close()
            #print(f"Level data loaded from {level_file}")
            return data
        else:
            print(f"File not found: {level_file}")
            # Trả về dữ liệu mặc định nếu không tìm thấy file
            return [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ]
    except Exception as e:
        print(f"Error loading level: {e}")
        return None

#Lop nhan vat
player = Player(35, screen_height - 210) #Vị trí khởi đầu của nhân vật


# Tạo coin icon cho điểm số (đánh dấu là icon)
score_coin = Coin(tile_size - 30, 25, True)  # Đặt is_icon=True
coin_group.add(score_coin)
score_rune = Rune(tile_size + 130, 25, True)  # Đặt is_icon=True
rune_group.add(score_rune)

# Tải dữ liệu level từ file
world_data = load_level_data(1)
world = World(world_data)

def show_loading_screen():
        # Tải hình ảnh cho loading screen
        try:
            loadbar_bg = pygame.image.load('assests/gui/PNG/load_bar/bg.png').convert_alpha()
            loadbar_1 = pygame.image.load('assests/gui/PNG/load_bar/1.png').convert_alpha()
            loadbar_2 = pygame.image.load('assests/gui/PNG/load_bar/2.png').convert_alpha()
            loadbar_3 = pygame.image.load('assests/gui/PNG/load_bar/3.png').convert_alpha()
            loading_text = pygame.image.load('assests/gui/PNG/load_bar/text.png').convert_alpha()
        except pygame.error as e:
            print(f"Không thể tải hình ảnh loading bar: {e}")
            return
        
        # Scale hình ảnh nếu cần
        bar_width = 600
        bar_height = 40
        
        loadbar_bg = pygame.transform.scale(loadbar_bg, (bar_width, bar_height))
        loadbar_1 = pygame.transform.scale(loadbar_1, (bar_width, bar_height))
        loadbar_2 = pygame.transform.scale(loadbar_2, (bar_width, bar_height))
        loadbar_3 = pygame.transform.scale(loadbar_3, (bar_width, bar_height))
        loading_text = pygame.transform.scale(loading_text, (400, 70))
        
        # Vị trí trung tâm màn hình
        bar_x = screen_with // 2 - bar_width // 2
        bar_y = screen_height // 2 - bar_height // 2
        text_x = screen_with // 2 - loading_text.get_width() // 2
        text_y = bar_y - loading_text.get_height() - 20
        
        # Thiết lập thời gian loading
        loading_time = 3.0  # 3 giây
        start_time = pygame.time.get_ticks()
        current_time = start_time
        
        while (current_time - start_time) / 1000.0 < loading_time:
            # Xử lý sự kiện trong khi loading (cho phép thoát game)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
            
            # Tính toán progress (0-100%)
            progress = min(100, ((current_time - start_time) / 1000.0) / loading_time * 100)
            
            # Vẽ màn hình đen
            screen.fill((0, 0, 0))
            
            # Vẽ text "Loading..."
            screen.blit(loading_text, (text_x, text_y))
            
            # Vẽ loadbar background
            screen.blit(loadbar_bg, (bar_x, bar_y))
            
            # Vẽ loadbar progress dựa vào % hoàn thành
            if progress < 33:
                # Hiển thị lần lượt 1/3 đầu thanh loading
                progress_width = int(bar_width * progress / 33)
                loadbar_crop = loadbar_1.subsurface((0, 0, progress_width, bar_height))
                screen.blit(loadbar_crop, (bar_x, bar_y))
            elif progress < 66:
                # Hiển thị đầy đủ 1/3 đầu và một phần của 1/3 giữa
                screen.blit(loadbar_1, (bar_x, bar_y))
                progress_width = int(bar_width * (progress - 33) / 33)
                loadbar_crop = loadbar_2.subsurface((0, 0, progress_width, bar_height))
                screen.blit(loadbar_crop, (bar_x, bar_y))
            else:
                # Hiển thị đầy đủ 2/3 đầu và một phần của 1/3 cuối
                screen.blit(loadbar_1, (bar_x, bar_y))
                screen.blit(loadbar_2, (bar_x, bar_y))
                progress_width = int(bar_width * (progress - 66) / 34)
                loadbar_crop = loadbar_3.subsurface((0, 0, progress_width, bar_height))
                screen.blit(loadbar_crop, (bar_x, bar_y))
            
            # Hiển thị % loading
            percent_text = font_small.render(f"{int(progress)}%", True, white)
            percent_rect = percent_text.get_rect(center=(screen_with // 2, bar_y + bar_height + 30))
            screen.blit(percent_text, percent_rect)
            
            tips = [
                "Đừng quên thu thập đủ vàng nhé chiến binh!!!"
            ]
            current_tip = random.choice(tips)
            tip_text = font_small2.render(current_tip, True, (200, 200, 200))
            screen.blit(tip_text, tip_text.get_rect(center=(screen_with // 2, screen_height - 100)))
            
            # Cập nhật màn hình
            pygame.display.flip()
            
            # Cập nhật thời gian hiện tại
            current_time = pygame.time.get_ticks()
            
            # Giới hạn FPS
            clock.tick(60)

        # Hiển thị frame cuối cùng với loading 100%
        screen.fill((0, 0, 0))
        screen.blit(loading_text, (text_x, text_y))
        screen.blit(loadbar_bg, (bar_x, bar_y))
        screen.blit(loadbar_1, (bar_x, bar_y))
        screen.blit(loadbar_2, (bar_x, bar_y))
        screen.blit(loadbar_3, (bar_x, bar_y))
        percent_text = font_small.render("100%", True, white)
        screen.blit(percent_text, percent_rect)
        screen.blit(tip_text, tip_text.get_rect(center=(screen_with // 2, screen_height - 100)))
        pygame.display.flip()

class PauseDialog():
    def __init__(self):
        # Load background cho dialog
        self.bg = pygame.image.load('assests/gui/PNG/pause/bg.png')
        self.bg = pygame.transform.scale(self.bg, (500, 300))
        self.bg_rect = self.bg.get_rect()
        self.bg_rect.center = (screen_with // 2, screen_height // 2)

        self.buttons = []

        # Cấu hình button
        button_info = [
            ("home", 'assests/gui/PNG/btn/menu.png', -120),
            ("restart", 'assests/gui/PNG/btn/restart.png', 0),
            ("continue", 'assests/gui/PNG/btn/play.png', 120)
        ]
        
        # Load và setup các buttons với hiệu ứng hover
        button_scale = 0.4
        base_y = self.bg_rect.centery - 20
        
        # Tạo buttons với 2 trạng thái: normal và hover
        for name, path, offset_x in button_info:
            image = pygame.image.load(path)
            normal_image = pygame.transform.scale(image, (
                int(image.get_width() * button_scale),
                int(image.get_height() * button_scale)
            ))
            # Scale ảnh hover từ ảnh normal
            hover_image = pygame.transform.scale(normal_image, (
                int(normal_image.get_width() * 1.1),
                int(normal_image.get_height() * 1.1)
            ))
            rect = normal_image.get_rect()
            rect.center = (self.bg_rect.centerx + offset_x, base_y)
            self.buttons.append({
                'name': name,
                'normal': normal_image,
                'hover': hover_image,
                'rect': rect,
                'is_hovered': False
            })
        
        
        # Text "PAUSE"
        self.font = pygame.font.Font('assests/font/Arial.ttf', 48)
        self.text = self.font.render('PAUSE', True, (255, 255, 255))
        self.text_rect = self.text.get_rect(center=(self.bg_rect.centerx, self.bg_rect.centery - 100))

    def draw(self, screen):
        # Tạo overlay mờ
        s = pygame.Surface((screen_with, screen_height))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        screen.blit(s, (0, 0))
        
        # Vẽ background dialog
        screen.blit(self.bg, self.bg_rect)
        
        # Vẽ text "PAUSE"
        screen.blit(self.text, self.text_rect)
        
        # Lấy vị trí chuột
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        # Xử lý hover và click cho từng button
        for btn in self.buttons:
            if btn['rect'].collidepoint(mouse_pos):
                btn['is_hovered'] = True
                # Cập nhật lại rect center sau khi scale
                hover_rect = btn['hover'].get_rect(center=btn['rect'].center)
                screen.blit(btn['hover'], hover_rect)
                btn['rect'] = hover_rect  # cập nhật lại vị trí hitbox
                if mouse_clicked:
                    return btn['name']
            else:
                btn['is_hovered'] = False
                screen.blit(btn['normal'], btn['rect'])

        
        return None

def run_level(screen, screen_width, screen_height):
    global score
    global gold
    global game_over
    global game_win
    global world
    # Khởi tạo âm thanh
    try:
        game_music = pygame.mixer.Sound('assests/sfx/menusfx/NinjaSchool.mp3')
        game_music.set_volume(0.7)  # Đặt âm lượng mặc định 
        game_music.play(-1)  # Phát nhạc lặp lại
    except pygame.error as e:
        print(f"Không thể tải nhạc game: {e}")
        game_music = None
    pause_button = Button('assests/gui/PNG/btn/pause.png', screen_width - 50, 40, 0.25)  # Thêm nút pause
    pause_dialog = PauseDialog()  # Tạo đối tượng PauseDialog
    paused = False  # Biến trạng thái pause
    #vòng lặp xử lý sự kiện game
    run = True
    while run:
        clock.tick(fps)
        screen.blit(background_img,(0,0))
        world.draw()
        #draw_grid()

        # Cập nhật và vẽ các enemy  
        blue_slime_group.draw(screen)
        green_slime_group.draw(screen)
        skeleton_group.draw(screen)
        flag_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        rune_group.draw(screen)
        player.draw()  
        if pause_button.draw():
            paused = True
        if not paused:
            blue_slime_group.draw(screen)
            green_slime_group.draw(screen)
            skeleton_group.draw(screen)
            
            blue_slime_group.update()
            green_slime_group.update()
            skeleton_group.update()


            flag_group.draw(screen)
            flag_group.update()

            lava_group.draw(screen)
            coin_group.draw(screen)
            coin_group.update()
            rune_group.draw(screen)
            rune_group.update()

            game_over, game_win = player.update(game_over, game_win)
            # game_over = player.update(game_over)
            #Restart khi game over
            if game_over == True:
                if game_music:
                        game_music.stop()
                action = show_lose_popup(screen,screen_width,screen_height)
                if action == 'restart':
                    blue_slime_group.empty()
                    green_slime_group.empty()
                    skeleton_group.empty()
                    coin_group.empty()
                    rune_group.empty()
                    flag_group.empty()
                    score_coin = Coin(tile_size - 30, 25, True)  # Đặt is_icon=True
                    coin_group.add(score_coin)
                    score_rune = Rune(tile_size + 130, 25, True)  # Đặt is_icon=True
                    rune_group.add(score_rune)
                    world_data = []
                    world_data = load_level_data(1)
                    world = World(world_data)
                    player.reset(35, screen_height - 210) #Vị trí khởi đầu của nhân vật
                    game_over = False
                    score = 0
                    gold = 0
                if action == 'menu' :
                    show_loading_screen()
                    blue_slime_group.empty()
                    green_slime_group.empty()
                    skeleton_group.empty()
                    coin_group.empty()
                    rune_group.empty()
                    flag_group.empty()
                    score_coin = Coin(tile_size - 30, 25, True)  # Đặt is_icon=True
                    coin_group.add(score_coin)
                    score_rune = Rune(tile_size + 130, 25, True)  # Đặt is_icon=True
                    rune_group.add(score_rune)
                    world_data = []
                    world_data = load_level_data(1)
                    world = World(world_data)
                    player.reset(35, screen_height - 210) #Vị trí khởi đầu của nhân vật
                    score_rs = 0
                    score = 0
                    gold = 0
                    game_over = False
                    return True , score_rs, False
            else:        
                for sprite in coin_group:
                    if pygame.sprite.collide_rect(player, sprite) and not sprite.is_icon:
                        sprite.kill()
                        score += 1
                draw_text('X ' + str(score) + '/3', font_score, white, tile_size - 10, 10)
                coin_group.update()

                for sprite in rune_group:
                    if pygame.sprite.collide_rect(player, sprite) and not sprite.is_icon:
                        sprite.kill()
                        gold += 1
                draw_text('X ' + str(gold), font_score, white, tile_size + 150, 10)
                rune_group.update()
            if game_win == True:
                if game_music:
                        game_music.stop()
                action = show_win_popup(screen, score, 3, star_images, screen_width, screen_height)

                if action == "continue":
                    blue_slime_group.empty()
                    green_slime_group.empty()
                    skeleton_group.empty()
                    coin_group.empty()
                    rune_group.empty()
                    flag_group.empty()
                    score_coin = Coin(tile_size - 30, 25, True)  # Đặt is_icon=True
                    coin_group.add(score_coin)
                    score_rune = Rune(tile_size + 130, 25, True)  # Đặt is_icon=True
                    rune_group.add(score_rune)
                    world_data = []
                    world_data = load_level_data(1)
                    world = World(world_data)
                    player.reset(35, screen_height - 210) #Vị trí khởi đầu của nhân vật
                    score_rs = score
                    score = 0
                    gold = 0
                    game_win = False
                    # import levels.level2 as lv2
                    # screen = pygame.display.set_mode((screen_width, screen_height))
                    # show_loading_screen()
                    # run_lv = lv2.run_level(screen, screen_width, screen_height)
                    return False, score_rs, True
                elif action == "menu":
                    show_loading_screen()
                    blue_slime_group.empty()
                    green_slime_group.empty()
                    skeleton_group.empty()
                    coin_group.empty()
                    rune_group.empty()
                    flag_group.empty()
                    score_coin = Coin(tile_size - 30, 25, True)  # Đặt is_icon=True
                    coin_group.add(score_coin)
                    score_rune = Rune(tile_size + 130, 25, True)  # Đặt is_icon=True
                    rune_group.add(score_rune)
                    world_data = []
                    world_data = load_level_data(1)
                    world = World(world_data)
                    player.reset(35, screen_height - 210) #Vị trí khởi đầu của nhân vật
                    score_rs = score
                    score = 0
                    gold = 0
                    game_win = False
                    return True, score_rs, False # hoặc chuyển về menu chính nếu có

        if paused:
            action = pause_dialog.draw(screen)
            if action == 'home':
                if game_music:
                    game_music.stop()
                show_loading_screen()
                blue_slime_group.empty()
                green_slime_group.empty()
                skeleton_group.empty()
                coin_group.empty()
                rune_group.empty()
                flag_group.empty()
                score_coin = Coin(tile_size - 30, 25, True)  # Đặt is_icon=True
                coin_group.add(score_coin)
                score_rune = Rune(tile_size + 130, 25, True)  # Đặt is_icon=True
                rune_group.add(score_rune)
                world_data = []
                world_data = load_level_data(1)
                world = World(world_data)
                player.reset(35, screen_height - 210) #Vị trí khởi đầu của nhân vật
                score_rs = 0
                score = 0
                gold = 0
                game_win = False
                return True, score_rs, False  # hoặc chuyển về menu chính nếu có
            elif action == 'restart':
                blue_slime_group.empty()
                green_slime_group.empty()
                skeleton_group.empty()
                coin_group.empty()
                rune_group.empty()
                flag_group.empty()
                score_coin = Coin(tile_size - 30, 25, True)  # Đặt is_icon=True
                coin_group.add(score_coin)
                score_rune = Rune(tile_size + 130, 25, True)  # Đặt is_icon=True
                rune_group.add(score_rune)
                world_data = []
                world_data = load_level_data(1)
                world = World(world_data)
                player.reset(35, screen_height - 210) #Vị trí khởi đầu của nhân vật
                game_over = False
                score = 0
                gold = 0
                paused = False
            elif action == 'continue':
                paused = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if game_music:
                    game_music.stop()
                pygame.quit()
                return False, score
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                    #sys.exit()

        pygame.display.update()
    
    return True  # Trả về True để quay lại menu

# Chỉ chạy trực tiếp file này khi test
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((screen_with, screen_height))
    run_level(screen, screen_with, screen_height)