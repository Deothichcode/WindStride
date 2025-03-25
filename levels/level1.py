import pygame
import sys
import os
import random
import math

class Cloud:
    def __init__(self, level, image_path, speed, y_pos, scale=1.0, depth=1.0, alpha=255):
        self.level = level
        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
            # Scale hình ảnh theo tỉ lệ
            new_width = int(self.original_image.get_width() * scale)
            new_height = int(self.original_image.get_height() * scale)
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
            
            # Thiết lập độ trong suốt
            self.image.set_alpha(alpha)
        except:
            # Nếu không tải được hình, tạo một surface tạm thời
            print(f"Không thể tải hình ảnh đám mây: {image_path}")
            self.image = pygame.Surface((100, 50), pygame.SRCALPHA)
            self.image.fill((255, 255, 255, alpha))
        
        # Vị trí ban đầu
        self.x = random.randint(-self.image.get_width(), level.screen_width)
        self.y = y_pos
        
        # Vận tốc di chuyển (pixels/second)
        self.speed = speed
        
        # Độ sâu (ảnh hưởng đến tốc độ di chuyển)
        self.depth = depth
        
    
    def update(self, delta_time):
        # Di chuyển đám mây từ trái sang phải với tốc độ phụ thuộc vào delta_time
        self.x += self.speed * delta_time * 60
        
        
        # Khi đám mây đi qua khỏi màn hình, đặt lại vị trí
        if self.x > self.level.screen_width:
            self.x = -self.image.get_width()
            # Thay đổi ngẫu nhiên biên độ và tốc độ dao động
            self.wave_amplitude = random.uniform(0.8, 2.0)
            self.wave_speed = random.uniform(0.3, 0.7)
    
    def draw(self, screen, camera_x=0):
        # Vẽ đám mây lên màn hình với điều chỉnh vị trí theo camera
        adjusted_x = int(self.x - camera_x * self.depth)
        screen.blit(self.image, (adjusted_x, self.y))

class Platform:
    def __init__(self, x, y, width, height, tile_type="grass"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tile_type = tile_type
        self.image = None
        self.load_image()
    
    def load_image(self):
        if self.tile_type == "grass":
            self.image = pygame.image.load('assests/tileset/Forest Tileset/1 Tiles/Tile_02.png').convert_alpha()
        elif self.tile_type == "dirt":
            self.image = pygame.image.load('assests/tileset/Forest Tileset/1 Tiles/Tile_04.png').convert_alpha()
        elif self.tile_type == "stone":
            self.image = pygame.image.load('assests/tileset/Forest Tileset/1 Tiles/Tile_12.png').convert_alpha()
        elif self.tile_type == "mossy":
            self.image = pygame.image.load('assests/tileset/Mossy Tileset/Mossy - TileSet.png').convert_alpha()
            # Lấy một phần của tileset (tile đầu tiên)
            self.image = self.image.subsurface((0, 0, 32, 32))
        else:
            # Tạo một surface trống nếu không tìm thấy tile phù hợp
            self.image = pygame.Surface((32, 32))
            self.image.fill((100, 100, 100))
    
    def draw(self, screen, camera_x):
        # Vẽ tile lặp lại để phủ kín platform
        for x in range(0, self.width, 32):
            for y in range(0, self.height, 32):
                screen.blit(self.image, (self.x + x - camera_x, self.y + y))

class Decoration:
    def __init__(self, x, y, image_path, scale=1.0):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path).convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        if scale != 1.0:
            new_width = int(self.width * scale)
            new_height = int(self.height * scale)
            self.image = pygame.transform.scale(self.image, (new_width, new_height))
            self.width = new_width
            self.height = new_height
    
    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.x - camera_x, self.y))

class Level1:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.level_complete = False
        
        # Thiết lập camera
        self.camera_x = 0
        
        # Tạo nền (background)
        self.load_background()
        
        # Tạo các layer đám mây
        self.create_clouds()
        
        # Tạo các platform
        self.create_platforms()
        
        # Tạo các decoration
        self.create_decorations()
        
        # Button để quay về menu
        self.back_button = None
        try:
            back_img = pygame.image.load('assests/gui/PNG/btn/pause.png').convert_alpha()
            back_width = int(back_img.get_width() * 0.25)
            back_height = int(back_img.get_height() * 0.25)
            self.back_button = {
                'image': pygame.transform.scale(back_img, (back_width, back_height)),
                'rect': pygame.Rect(20, 20, back_width, back_height),
                'hover': False
            }
        except:
            print("Không thể tải hình ảnh nút Back")
        
        # Biến đếm thời gian
        self.last_time = pygame.time.get_ticks()

    def load_background(self):
        """Load hình nền"""
            # Nền chính với game_background_2.png
        self.bg_main = pygame.image.load('assests/background/PNG/game_background_2/game_background_2.png').convert_alpha()
        self.bg_main = pygame.transform.scale(self.bg_main, (self.screen_width, self.screen_height*0.9))
            
            # Layer 2: Núi xa
        self.bg_mountains = pygame.image.load('assests/background/PNG/game_background_2/layers/rocks_1.png').convert_alpha()
        self.bg_mountains = pygame.transform.scale(self.bg_mountains, (self.screen_width * 1.5, self.screen_height * 0.7))
            
            # Layer 3: Rừng thông phía xa
        self.bg_pines = pygame.image.load('assests/background/PNG/game_background_2/layers/pines.png').convert_alpha()
        self.bg_pines = pygame.transform.scale(self.bg_pines, (self.screen_width * 2, self.screen_height * 0.5))
            
    
    def create_clouds(self):
        self.clouds = []
        
        # Danh sách các hình ảnh đám mây
        cloud_images = [
            'assests/background/PNG/game_background_2/layers/clouds_1.png',
            'assests/background/PNG/game_background_2/layers/clouds_2.png',
            'assests/background/PNG/game_background_2/layers/clouds_3.png',
        ]
        
        # Lớp đám mây xa
        for i in range(5):
            x_pos = i * (self.screen_width // 5)
            self.clouds.append(Cloud(
                self, 
                cloud_images[0],
                0.10,
                random.randint(20, 150),
                scale=0.5,
                depth=0.2,
                alpha=70
            ))
        
        # Lớp đám mây xa thứ hai
        for i in range(5):
            x_pos = i * (self.screen_width // 5) + (self.screen_width // 10)  # Xen kẽ
            self.clouds.append(Cloud(
                self, 
                cloud_images[1],
                0.15,
                random.randint(50, 180),
                scale=0.6,
                depth=0.3,
                alpha=100
            ))
        
        # Lớp đám mây trung bình
        for i in range(4):
            x_pos = i * (self.screen_width // 4)
            self.clouds.append(Cloud(
                self, 
                cloud_images[1],
                0.25,
                random.randint(100, 250),
                scale=0.7,
                depth=0.6,
                alpha=100
            ))
            
    
    def create_platforms(self):
        self.platforms = []
        
        # Platform ban đầu
        self.platforms.append(Platform(0, 500, 500, 100, "grass"))
        
        # Thêm một số platform với tile ngẫu nhiên
        tile_types = ["grass", "dirt", "stone", "mossy"]
        
        self.platforms.append(Platform(600, 450, 300, 32, random.choice(tile_types)))
        self.platforms.append(Platform(1000, 400, 300, 32, random.choice(tile_types)))
        self.platforms.append(Platform(1400, 450, 300, 32, random.choice(tile_types)))
        self.platforms.append(Platform(1800, 500, 300, 32, random.choice(tile_types)))
        
        # Thêm nền dưới cùng
        self.platforms.append(Platform(0, 600, 2000, 200, "dirt"))
        
        # Thêm một số platform ở phần sau của level
        self.platforms.append(Platform(2100, 500, 200, 32, "stone"))
        self.platforms.append(Platform(2400, 450, 200, 32, "stone"))
        self.platforms.append(Platform(2700, 400, 200, 32, "stone"))
        self.platforms.append(Platform(3000, 450, 200, 32, "stone"))
        self.platforms.append(Platform(3300, 500, 200, 32, "stone"))
        
        # Thêm nền cho khu vực cuối
        self.platforms.append(Platform(3600, 500, 500, 300, "grass"))
    
    def create_decorations(self):
        self.decorations = []
        
        # Thêm một số cây
        tree_positions = [(100, 400), (300, 400), (700, 350), (1100, 300), (1500, 350), (1900, 400), (3700, 400)]
        for pos in tree_positions:
            self.decorations.append(Decoration(
                pos[0], pos[1], 
                'assests/tileset/Forest Tileset/1 Tiles/Tile_03.png',
                2.0
            ))
        
        # Thêm một số bụi cây
        bush_positions = [(200, 470), (500, 470), (900, 420), (1300, 370), (1700, 420), (2000, 470), (3800, 470)]
        for pos in bush_positions:
            self.decorations.append(Decoration(
                pos[0], pos[1], 
                'assests/tileset/Forest Tileset/1 Tiles/Tile_58.png',
                1.0
            ))
        
        # Thêm một số trang trí từ tileset Mossy
        mossy_positions = [(350, 450), (850, 400), (1250, 350), (1650, 400), (2250, 450), (2850, 350), (3450, 450)]
        for pos in mossy_positions:
            try:
                self.decorations.append(Decoration(
                    pos[0], pos[1], 
                    'assests/tileset/Mossy Tileset/Mossy - Decorations&Hazards.png',
                    0.5
                ))
            except:
                print("Không thể tải hình ảnh trang trí Mossy")
    
    def update_camera(self, delta_time):
        # Giữ camera đứng yên
        self.camera_x = 0  # Đặt camera cố định ở vị trí 0
    
    def update_clouds(self, delta_time):
        for cloud in self.clouds:
            cloud.update(delta_time)
    
    def update(self, delta_time):
        self.update_camera(delta_time)
        self.update_clouds(delta_time)
    
    def draw(self, screen):
        # Vẽ hình nền chính
        screen.blit(self.bg_main, (0, 0))
        
        # Vẽ núi xa với parallax
        mountain_x = -self.camera_x * 0.2  # Parallax factor
        screen.blit(self.bg_mountains, (mountain_x, self.screen_height - self.bg_mountains.get_height()))
        
        # Vẽ rừng thông xa với parallax
        pines_x = -self.camera_x * 0.4  # Parallax factor
        screen.blit(self.bg_pines, (pines_x, self.screen_height - self.bg_pines.get_height()))
        
        # Vẽ các đám mây
        for cloud in self.clouds:
            cloud.draw(screen, self.camera_x)
        
        # Vẽ các decoration phía sau
        for decoration in self.decorations:
            decoration.draw(screen, self.camera_x)
        
        # Vẽ các platform
        for platform in self.platforms:
            platform.draw(screen, self.camera_x)
        
        # Vẽ nút back
        if self.back_button:
            screen.blit(self.back_button['image'], self.back_button['rect'])
            # Kiểm tra hover
            mouse_pos = pygame.mouse.get_pos()
            if self.back_button['rect'].collidepoint(mouse_pos):
                pygame.draw.rect(screen, (255, 255, 255, 100), self.back_button['rect'], 2)
                self.back_button['hover'] = True
            else:
                self.back_button['hover'] = False
    
    def check_back_button(self, mouse_pos, mouse_clicked):
        if self.back_button and self.back_button['rect'].collidepoint(mouse_pos) and mouse_clicked:
            return True
        return False

def run_level(screen, screen_width, screen_height):
    level = Level1(screen_width, screen_height)
    clock = pygame.time.Clock()
    running = True
    return_to_menu = False
    last_time = pygame.time.get_ticks()
    
    while running:
        # Tính toán delta time
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_time) / 1000.0
        last_time = current_time
        delta_time = min(delta_time, 0.1)  # Giới hạn delta_time
        
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return_to_menu = True
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if level.check_back_button(event.pos, True):
                        return_to_menu = True
                        running = False
        
        # Cập nhật
        level.update(delta_time)
        
        # Vẽ
        screen.fill((0, 0, 0))  # Xóa màn hình
        level.draw(screen)
        
        # Cập nhật màn hình
        pygame.display.flip()
        clock.tick(60)
    
    return return_to_menu

if __name__ == "__main__":
    pygame.init()
    screen_width = 1200
    screen_height = 700
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("WindStride")
    try:
        logo = pygame.image.load('assests/gui/PNG/menu/LogoWindStride.png').convert_alpha()
        logo = pygame.transform.scale(logo, (32, 32))
        pygame.display.set_icon(logo)
    except pygame.error:
        print("Không thể tải icon!")
    run_level(screen, screen_width, screen_height)
    
    pygame.quit()
    sys.exit()
