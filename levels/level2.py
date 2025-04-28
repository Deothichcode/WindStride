import pygame
from pygame.locals import *
import pickle
from os import path
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_with = 1200
screen_height = 700

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
        elif object_type == 'slime':
            # Load only a single frame for slime, no animation
            img = pygame.image.load(f'assests/objects/Creep/Blue_Slime/idle/1.png')
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


class Player():
    def __init__(self, x, y):
        self.images_right = [] #list frame di sang phai
        self.images_left = [] #list frame di sang trai
        self.images_jump_right = [] #list frame nhảy sang phải
        self.images_jump_left = [] #list frame nhảy sang trái
        self.index = 0 #thu tu frame
        self.counter = 0 #thoi gian lam moi frame
        
        # Load frames chạy
        for num in range(1,7):
            img_right = pygame.image.load(f'assests/character/male/run/run{num}.png')
            img_right = pygame.transform.scale(img_right, (47 - 10, 74 - 10))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
            
        # Load frames nhảy
        for num in range(1,8):
            img_jump_right = pygame.image.load(f'assests/character/male/jump/j{num}.png')
            img_jump_right = pygame.transform.scale(img_jump_right, (47 - 10,74 - 10))
            img_jump_left = pygame.transform.flip(img_jump_right, True, False)
            self.images_jump_right.append(img_jump_right)
            self.images_jump_left.append(img_jump_left)

        # Load frame đứng yên
        self.idle_image_right = pygame.image.load('assests/character/male/idle/Idle.png')
        self.idle_image_right = pygame.transform.scale(self.idle_image_right, (37, 64))
        self.idle_image_left = pygame.transform.flip(self.idle_image_right, True, False)
        self.image = self.idle_image_right
        
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
        self.in_air = False  # Biến kiểm tra nhân vật có đang trong không trung

    def update(self):
        dx = 0
        dy = 0
        walk_cooldown = 5
        jump_cooldown = 6

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

        # Cập nhật vị trí
        self.rect.x += dx
        self.rect.y += dy

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
        #pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)


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
        coin_img = pygame.image.load('assests/objects/Item/coin/1.png') # Coin (9)
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
        # Các khung hình động cho đồng xu
        coin_frames = []
        coin_frames.append(pygame.transform.scale(coin_img, (int(tile_size * 0.5), int(tile_size * 0.5))))  # Sử dụng coin_img đã tải làm frame đầu tiên
        for i in range(2, 5):
            img = pygame.image.load(f'assests/objects/Item/coin/{i}.png')
            coin_frames.append(pygame.transform.scale(img, (int(tile_size * 0.5), int(tile_size * 0.5))))
        self.animation_frames['coin'] = coin_frames
        
        # Các khung hình động cho cờ
        flag_frames = []
        flag_frames.append(pygame.transform.scale(exit_img, (int(tile_size*1.5), int(tile_size * 2.25))))  # Sử dụng exit_img đã tải làm frame đầu tiên
        for i in range(2, 5):
            img = pygame.image.load(f'assests/objects/Item/flag/{i}.png')
            flag_frames.append(pygame.transform.scale(img, (int(tile_size*1.5), int(tile_size * 2.25))))
        self.animation_frames['flag'] = flag_frames
        
        # Các khung hình động cho rune
        rune_frames = []
        rune_frames.append(pygame.transform.scale(rune_img, (int(tile_size * 0.5), int(tile_size * 0.5))))  # Sử dụng rune_img đã tải làm frame đầu tiên
        for i in range(2, 5):
            img = pygame.image.load(f'assests/objects/Item/rune/{i}.png')
            rune_frames.append(pygame.transform.scale(img, (int(tile_size * 0.5), int(tile_size * 0.5))))
        self.animation_frames['rune'] = rune_frames
        
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
        self.animation_frames['blue_flower1'] = blue_flower1_frames
        
        # Các khung hình động cho hoa xanh 2
        blue_flower2_frames = []
        blue_flower2_frames.append(pygame.transform.scale(blue_flower2_img, (tile_size*3, tile_size*3)))  # Sử dụng blue_flower2_img đã tải
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
                    img = pygame.transform.scale(lava_img, (tile_size, tile_size // 2))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size + (tile_size // 2)
                    tile = (img, img_rect, 'lava')  # Đánh dấu là dung nham
                    self.tile_list.append(tile)
                    
                elif tile == 9:  # Coin - Có hoạt ảnh
                    img = self.animation_frames['coin'][0]  # Bắt đầu với frame đầu tiên
                    img_rect = img.get_rect()
                    # Căn giữa đồng xu trong ô lưới
                    img_rect.centerx = col_count * tile_size + tile_size // 2
                    img_rect.centery = row_count * tile_size + tile_size // 2
                    tile = (img, img_rect, 'coin')  # Đánh dấu cho hoạt ảnh
                    self.animated_tiles.append(tile)
                    
                elif tile == 10:  # Exit (Flag) - Có hoạt ảnh
                    img = self.animation_frames['flag'][0]  # Bắt đầu với frame đầu tiên
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size//4
                    img_rect.y = row_count * tile_size - (tile_size * 0.75)
                    tile = (img, img_rect, 'flag')  # Đánh dấu cho hoạt ảnh
                    self.animated_tiles.append(tile)
                    
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
                    img = self.animation_frames['rune'][0]  # Bắt đầu với frame đầu tiên
                    img_rect = img.get_rect()
                    # Căn giữa rune trong ô lưới
                    img_rect.centerx = col_count * tile_size + tile_size // 2
                    img_rect.centery = row_count * tile_size + tile_size // 2
                    tile = (img, img_rect, 'rune')  # Đánh dấu cho hoạt ảnh
                    self.animated_tiles.append(tile)
                    
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
                elif tile == 21:  # Skeleton
                    enemy = Enemy(col_count * tile_size, row_count * tile_size, 'skeleton')
                    self.enemies.append(enemy)
                
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
            
            if tile_type == 'coin':
                self.animated_tiles[i] = (self.animation_frames['coin'][self.animation_index % len(self.animation_frames['coin'])], rect, tile_type)
            elif tile_type == 'flag':
                self.animated_tiles[i] = (self.animation_frames['flag'][self.animation_index % len(self.animation_frames['flag'])], rect, tile_type)
            elif tile_type == 'rune':
                self.animated_tiles[i] = (self.animation_frames['rune'][self.animation_index % len(self.animation_frames['rune'])], rect, tile_type)
            elif tile_type == 'plant':
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
                flower_index = (self.animation_index // 2) % len(self.animation_frames['blue_flower1'])  
                self.animated_tiles[i] = (self.animation_frames['blue_flower1'][flower_index], rect, tile_type)
            elif tile_type == 'blue_flower2':
                flower_index = (self.animation_index // 2) % len(self.animation_frames['blue_flower2'])  
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
        
        # Vẽ các tile hoạt ảnh còn lại (đồng xu, rune)
        for tile in self.animated_tiles:
            img, rect, tile_type = tile
            if tile_type != 'flag' and not tile_type.startswith('plant') and tile_type != 'plant' and not tile_type.startswith('blue_flower'):
                screen.blit(img, rect)
        
        # Vẽ các tile đặc biệt phía trên cùng (lava, platforms)
        for tile in self.tile_list:
            if len(tile) > 2 and tile[2] in ['lava', 'platform_x']:
                screen.blit(tile[0], tile[1])
        
        for tile in self.tile_list:
                screen.blit(tile[0], tile[1])
                #pygame.draw.rect(screen, (255, 0, 0), tile[1], 2)  # Vẽ hình chữ nhật xung quanh các tile để kiểm tra va chạm
        
        # Cập nhật và vẽ enemies
        for enemy in self.enemies:
            enemy.update()
            enemy.draw(screen)


class Enemy():
    def __init__(self, x, y, enemy_type):
        self.enemy_type = enemy_type
        
        # Load hình ảnh dựa trên loại enemy
        if enemy_type == 'blue_slime':
            img = pygame.image.load('assests/objects/Creep/Blue_Slime/idle/1.png')
            self.image = pygame.transform.scale(img, (int(tile_size*0.6), int(tile_size*0.6)))
        elif enemy_type == 'green_slime':
            img = pygame.image.load('assests/objects/Creep/Green_Slime/idle/1.png')
            self.image = pygame.transform.scale(img, (int(tile_size*0.6), int(tile_size*0.6)))
        elif enemy_type == 'skeleton':
            img = pygame.image.load('assests/objects/Creep/Skeleton/idle/1.png')
            self.image = pygame.transform.scale(img, (int(tile_size*0.8), int(tile_size*1.3)))
            
        # Set up rect và hitbox
        self.rect = self.image.get_rect()
        self.rect.centerx = x + tile_size // 2   # Căn giữa theo chiều ngang
        self.rect.bottom = y + tile_size # Đặt ở dưới cùng của ô
        
        # Hitbox nhỏ hơn sprite
        self.hitbox = pygame.Rect(
            self.rect.x,
            self.rect.y,
            self.rect.width,
            self.rect.height
        )
        
    def update(self):      
        # Cập nhật hitbox theo vị trí mới
        self.hitbox.x = self.rect.x + 10
        self.hitbox.y = self.rect.y + 1
        
    def draw(self, screen):
        # Vẽ enemy
        screen.blit(self.image, self.rect)
        # Vẽ hitbox cho debug
        #pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)


# Hàm để tải dữ liệu level từ file
def load_level_data(self):
    level_file = f'levels/level.data/level2_data'
    try:
        if path.exists(level_file):
            pickle_in = open(level_file, 'rb')
            data = pickle.load(pickle_in)
            pickle_in.close()
            print(f"Level data loaded from {level_file}")
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
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ]
    except Exception as e:
        print(f"Error loading level: {e}")
        return None

#Lop nhan vat
player = Player(35, screen_height - 210) #Vị trí khởi đầu của nhân vật
# Tải dữ liệu level từ file level1_data
world_data = load_level_data(1)
world = World(world_data)


def run_level(screen, screen_width, screen_height):
    # Khởi tạo âm thanh
    try:
        game_music = pygame.mixer.Sound('assests/sfx/menusfx/NinjaSchool.mp3')
        game_music.set_volume(0.7)  # Đặt âm lượng mặc định 
        game_music.play(-1)  # Phát nhạc lặp lại
    except pygame.error as e:
        print(f"Không thể tải nhạc game: {e}")
        game_music = None

    #vòng lặp xử lý sự kiện game
    run = True
    while run:
        clock.tick(fps)
        screen.blit(background_img,(0,0))
        world.draw()
        #draw_grid()
        player.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if game_music:
                    game_music.stop()
                pygame.quit()
                #sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_music:
                        game_music.stop()
                    pygame.quit()
                    #sys.exit()

        pygame.display.update()
    
    return True  # Trả về True để quay lại menu

# Chỉ chạy trực tiếp file này khi test
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((screen_with, screen_height))
    run_level(screen, screen_with, screen_height)
