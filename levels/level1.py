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

tile_size = 60 #mỗi ô grid có pixel là 100x100
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
        self.images_right = [] #di sang phai
        self.images_left = [] #di sang trai
        self.index = 0
        self.counter = 0
        for num in range(1,7): # 7 frame chay
            img_right = pygame.image.load(f'assests/character/male/run/run{num}.png') #frame chay
            img_right = pygame.transform.scale(img_right, (115, 115)) 
            img_left = pygame.transform.flip(img_right,True, False)  #lat nguoc nhan vat theo truc x not y
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        # Load frame dung yen
        self.idle_image_right = pygame.image.load('assests/character/male/idle/Idle.png')
        self.idle_image_right = pygame.transform.scale(self.idle_image_right, (115, 115))
        self.idle_image_left = pygame.transform.flip(self.idle_image_right, True, False)
        self.image = self.idle_image_right
        self.rect = self.image.get_rect()
        self.rect.x = x #di chuyen sang 2 ben
        self.rect.y = y #di chuyen len xuong
        self.vel_y = 0 #trong luc
        self.jumped = False  #nhay
        self.direction = 0 #danh dau huong cua nhan vat
    
    def update(self):

        dx = 0
        dy = 0
        run_cooldown = 5 # tang thoi gian chuyen tiep giua cac chu ki frame

        # di chuyen nhan vat
        key = pygame.key.get_pressed()
        if key[pygame.K_UP] and self.jumped == False:
            self.vel_y = -15
            self.jumped = True
        if key[pygame.K_UP] == False:
            self.jumped = False
        if key[pygame.K_LEFT]:
            dx -= 4
            self.counter += 1
            self.direction = -1
        if key[pygame.K_RIGHT]:
            dx += 4
            self.counter += 1
            self.direction = 1
        if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
            self.counter = 0
            self.index = 0
            if self.direction == 1: #nhan vat di chuyen sang phai
                self.image = self.idle_image_right
            if self.direction == -1: #nhan vat di chuyen sang trai
                self.image = self.idle_image_left
            if self.direction == 0:
                self.image = self.idle_image_right


        #animation nhan vat
        if self.counter > run_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images_right):  # nếu duyệt qua hết các frame đưua trở về 0 bắt đầu lại
                self.index = 0
            if self.direction == 1: #nhan vat di chuyen sang phai
                self.image = self.images_right[self.index]
            if self.direction == -1: #nhan vat di chuyen sang trai
                self.image = self.images_left[self.index]


        #trọng lực
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y


        #check vật cản

        #update vị trí nhân vật
        self.rect.x += dx
        self.rect.y += dy

        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            dy = 0

        screen.blit(self.image, self.rect) #anh va vi tri


class World():
    def __init__(self,data):
        # Khởi tạo list rỗng để lưu trữ tất cả các tile
        self.tile_list = [] #list chứa tile 
        self.animated_objects = []  # List chua chuyen dong vat the
        
        # Tải tất cả các hình ảnh cần thiết
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
                    
                elif tile == 3:  # Plant1 - Animated
                    img = pygame.transform.scale(grass_img, (tile_size*3, tile_size*3))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                    
                elif tile == 5:  # Blue slime - Static now
                    img = pygame.transform.scale(blue_slime_img, (int(tile_size*2), int(tile_size * 1.5)))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size//2
                    img_rect.y = row_count * tile_size - tile_size//2
                    tile = (img, img_rect, 'enemy')  # Mark as enemy
                    self.tile_list.append(tile)
                    
                elif tile == 6:  # Platform X (top)
                    img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 1.5))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect, 'platform_x')  # Đánh dấu là platform di chuyển ngang
                    self.tile_list.append(tile)
                    
                elif tile == 17:  # Platform X (bottom)
                    img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 1.5))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size + tile_size // 2 + 11
                    tile = (img, img_rect, 'platform_x')  # Đánh dấu là platform di chuyển ngang
                    self.tile_list.append(tile)
                    
                elif tile == 8:  # Lava
                    img = pygame.transform.scale(lava_img, (tile_size, tile_size // 2))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size + (tile_size // 2)
                    tile = (img, img_rect, 'lava')  # Đánh dấu là dung nham
                    self.tile_list.append(tile)
                    
                elif tile == 9:  # Coin - Static now
                    img = pygame.transform.scale(coin_img, (int(tile_size * 0.5), int(tile_size * 0.5)))
                    img_rect = img.get_rect()
                    # Center coin in its grid cell
                    img_rect.centerx = col_count * tile_size + tile_size // 2
                    img_rect.centery = row_count * tile_size + tile_size // 2
                    tile = (img, img_rect, 'coin')  # Mark as coin
                    self.tile_list.append(tile)
                    
                elif tile == 10:  # Exit (Flag) - Static now
                    img = pygame.transform.scale(exit_img, (int(tile_size*1.5), int(tile_size * 2.25)))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size//4
                    img_rect.y = row_count * tile_size - (tile_size * 0.75)
                    tile = (img, img_rect, 'exit')  # Mark as exit
                    self.tile_list.append(tile)
                    
                elif tile == 11:  # Plant2 - Static now
                    img = pygame.transform.scale(plant2_img, (tile_size*3, tile_size*3))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                    
                elif tile == 12:  # Plant3 - Static now
                    img = pygame.transform.scale(plant3_img, (tile_size*3, tile_size*3))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                    
                elif tile == 13:  # Plant4 - Static now
                    img = pygame.transform.scale(plant4_img, (tile_size*3, tile_size*3))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                    
                elif tile == 14:  # Plant5 - Static now
                    img = pygame.transform.scale(plant5_img, (tile_size*3, tile_size*3))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                    
                elif tile == 15:  # Plant6 - Static now
                    img = pygame.transform.scale(plant6_img, (tile_size*3, tile_size*3))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                    
                elif tile == 16:  # Rune - Static now
                    img = pygame.transform.scale(rune_img, (int(tile_size * 0.5), int(tile_size * 0.5)))
                    img_rect = img.get_rect()
                    # Center rune in its grid cell
                    img_rect.centerx = col_count * tile_size + tile_size // 2
                    img_rect.centery = row_count * tile_size + tile_size // 2
                    tile = (img, img_rect, 'rune')  # Mark as rune
                    self.tile_list.append(tile)
                    
                elif tile == 18:  # BlueFlower1 - Static now
                    img = pygame.transform.scale(blue_flower1_img, (tile_size*3, tile_size*3))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                    
                elif tile == 19:  # BlueFlower2 - Static now
                    img = pygame.transform.scale(blue_flower2_img, (tile_size*3, tile_size*3))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size - tile_size
                    img_rect.y = row_count * tile_size - tile_size + 6
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                
                # Tăng chỉ số cột sau khi xử lý một ô
                col_count += 1
            # Tăng chỉ số hàng sau khi xử lý một hàng hoàn chỉnh
            row_count += 1

    def draw(self):
        # First draw plant objects and flag (they should be behind other objects)
        for obj in self.animated_objects:
            if obj.object_type == 'plant' or obj.object_type == 'flag':
                obj.update()
                obj.draw()
        
        # Then draw static tiles
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1]) #lôi tuple trong tile_list ra vị trí tile[0] là ảnh, tile[1] là vị trí
        
        # Finally draw other animated objects (coin, rune, slime)
        for obj in self.animated_objects:
            if obj.object_type != 'plant' and obj.object_type != 'flag':
                obj.update()
                obj.draw()


# Hàm để tải dữ liệu level từ file
def load_level_data(level_number):
    level_file = f'levels/level.data/level{level_number}_data'
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
                [0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
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

run = True
#vòng lặp xử lý sự kiện game
while run:

    clock.tick(fps) #fps
    screen.blit(background_img,(0,0)) #Tải background từ góc trái bên trên
    world.draw()
    #draw_grid()

    player.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False    

    pygame.display.update() #cập nhật màn hình
pygame.quit()
