import sys #Nhập mô-đun sys, cho phép bạn tương tác với các tham số và chức năng của hệ thống.
import pygame
from pygame.locals import*
import random
import math

class Cloud:
    def __init__(self, game, image_path, speed, y_pos, scale=1.0, depth=1.0, alpha=255):
        self.game = game
        self.image_original = pygame.image.load(image_path).convert_alpha()
        
        # Thay đổi kích thước đám mây
        width = int(self.image_original.get_width() * scale)
        height = int(self.image_original.get_height() * scale)
        self.image = pygame.transform.scale(self.image_original, (width, height))
        
        # Thiết lập độ trong suốt nếu cần
        if alpha < 255:
            self.image.set_alpha(alpha)
        
        # Đặt vị trí ban đầu ngẫu nhiên trên màn hình
        self.x = random.randint(-self.image.get_width(), game.screen_width)
        self.y = y_pos
        self.base_y = y_pos  # Lưu vị trí y ban đầu để tạo hiệu ứng lên xuống
        self.speed = speed
        self.depth = depth  # Độ sâu để tạo hiệu ứng parallax
        self.time_offset = random.random() * 100  # Offset thời gian để mỗi đám mây có chuyển động riêng
        self.wave_amplitude = random.uniform(0.5, 1.5)  # Biên độ dao động lên xuống
        self.wave_speed = random.uniform(0.2, 0.5)  # Tốc độ dao động lên xuống
        
    def update(self, delta_time):
        # Di chuyển đám mây từ trái sang phải với tốc độ phụ thuộc vào delta_time
        self.x += self.speed * delta_time * 60
        
        # Tạo hiệu ứng lên xuống nhẹ nhàng cho đám mây
        
        # Nếu đám mây đi ra khỏi màn hình bên phải, đặt lại vị trí bên trái
        if self.x > self.game.screen_width:
            self.x = -self.image.get_width()
            # Thay đổi ngẫu nhiên vị trí y khi đám mây quay lại
            self.base_y = random.randint(0, int(self.game.screen_height * 0.6))
            self.y = self.base_y
            # Thay đổi ngẫu nhiên biên độ và tốc độ dao động
            self.wave_amplitude = random.uniform(0.5, 1.5)
            self.wave_speed = random.uniform(0.2, 0.5)
    
    def draw(self):
        # Sử dụng surface tạm thời để áp dụng hiệu ứng mờ nếu cần
        self.game.screen.blit(self.image, (int(self.x), int(self.y)))

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Wind Stride')
        self.screen_width = 1024 #x2
        self.screen_height = 768 #x1.6
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock() #fps
        self.last_time = pygame.time.get_ticks()
        
        # Tải hình ảnh
        self.cloud_img = pygame.image.load('assests/background/PNG/game_background_2/layers/clouds_3.png').convert_alpha()
        
        # Tải background menu
        self.background_img = pygame.image.load("assests/background/PNG/game_background_1/game_background_1.png").convert()
        
        # Thay đổi kích thước hình ảnh nền để vừa với màn hình
        self.background = pygame.transform.scale(self.background_img, (self.screen_width, self.screen_height))
        
        # Giữ nguyên kích thước đám mây hoặc thay đổi nếu cần
        cloud_width = min(self.cloud_img.get_width(), self.screen_width // 3)  # Đám mây chiếm 1/3 màn hình
        cloud_height = min(self.cloud_img.get_height(), self.screen_height // 4)  # Đám mây chiếm 1/4 chiều cao
        self.img = pygame.transform.scale(self.cloud_img, (cloud_width, cloud_height))
        
        # Tạo các đám mây di chuyển với nhiều lớp độ sâu khác nhau
        self.clouds = []
        
        # Lớp đám mây xa nhất (chậm nhất, mờ nhất)
        for i in range(3):
            self.clouds.append(Cloud(
                self, 
                'assests/background/PNG/game_background_1/layers/clouds_2.png', 
                0.15,  #speed - tăng nhẹ để mượt hơn
                random.randint(50, 150),  #Vị trí xuất hiện random
                scale=0.6, #tỉ lệ kích thước
                depth=0.3, #Dộ sâu layer
                alpha=150 #Trong suốt
            ))
        
        # Lớp đám mây trung bình
        for i in range(4):
            self.clouds.append(Cloud(
                self, 
                'assests/background/PNG/game_background_1/layers/clouds_2.png', 
                0.25, 
                random.randint(100, 250), 
                scale=0.7, 
                depth=0.6,
                alpha=200
            ))
            
            self.clouds.append(Cloud(
                self, 
                'assests/background/PNG/game_background_1/layers/clouds_4.png', 
                0.35, 
                random.randint(150, 300), 
                scale=0.75, 
                depth=0.7,
                alpha=220
            ))
        
        # Lớp đám mây gần nhất (nhanh nhất, rõ nhất)
        for i in range(2):
            self.clouds.append(Cloud(
                self, 
                'assests/background/PNG/game_background_1/layers/clouds_3.png', 
                0.45, 
                random.randint(200, 350), 
                scale=0.9, 
                depth=1.0,
                alpha=260
            ))
        
    def run(self):
        while True:
            # Tính toán delta time để chuyển động mượt mà hơn
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - self.last_time) / 1000.0  # Chuyển đổi sang giây
            self.last_time = current_time
            
            # Giới hạn delta_time để tránh "time jump" khi game bị lag
            delta_time = min(delta_time, 0.1)
            
            self.screen.blit(self.background, (0, 0))

            # Cập nhật và vẽ các đám mây di chuyển
            # Sắp xếp đám mây theo độ sâu để vẽ đúng thứ tự (xa đến gần)
            sorted_clouds = sorted(self.clouds, key=lambda cloud: cloud.depth)
            for cloud in sorted_clouds:
                cloud.update(delta_time)
                cloud.draw()
    
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            self.clock.tick(60) 
                
Game().run()