import sys #Nhập mô-đun sys, cho phép bạn tương tác với các tham số và chức năng của hệ thống.
import pygame
from pygame.locals import*
import random
import math
import webbrowser  # Thêm thư viện webbrowser để mở trang web

# Thiết lập mã hóa UTF-8 cho đầu ra console
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class Button:
    def __init__(self, game, image, x, y, scale=1.0):
        self.game = game
        self.image = pygame.image.load(image).convert_alpha()
        width = int(self.image.get_width() * scale)
        height = int(self.image.get_height() * scale)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.clicked = False
        
    def draw(self):
        # Lấy vị trí chuột
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]  # Nút chuột trái
        
        # Vẽ nút lên màn hình
        self.game.screen.blit(self.image, self.rect.topleft)
        
        # Kiểm tra sự kiện hover và click
        if self.rect.collidepoint(mouse_pos):
            # Hiệu ứng hover - phóng to nút nhẹ
            hover_img = pygame.transform.scale(self.image, 
                                              (int(self.rect.width * 1.1), 
                                               int(self.rect.height * 1.1)))
            hover_rect = hover_img.get_rect(center=self.rect.center)
            self.game.screen.blit(hover_img, hover_rect.topleft)
            
            # Kiểm tra sự kiện click
            if mouse_clicked and not self.clicked:
                self.clicked = True
                return True
            
        # Reset trạng thái click khi nhả chuột
        if not mouse_clicked:
            self.clicked = False
            
        return False

class Cloud:
    def __init__(self, game, image_path, speed, y_pos, scale=1.0, depth=1.0, alpha=255):
        self.game = game
        try:
            self.image_original = pygame.image.load(image_path).convert_alpha()
            
            # Thay đổi kích thước đám mây
            width = int(self.image_original.get_width() * scale)
            height = int(self.image_original.get_height() * scale)
            self.image = pygame.transform.scale(self.image_original, (width, height))
            
            # Thiết lập độ trong suốt nếu cần
            if alpha < 255:
                self.image.set_alpha(alpha)
            
            # Đặt vị trí ban đầu đều khắp màn hình
            self.x = random.randint(0, game.screen_width)
            self.y = y_pos
            self.speed = speed * 0.8  # Giảm tốc độ cho đám mây di chuyển chậm hơn
            self.depth = depth  # Độ sâu để tạo hiệu ứng parallax
            self.time_offset = random.random() * 100  # Offset thời gian để mỗi đám mây có chuyển động riêng
            self.wave_amplitude = random.uniform(0.8, 2.0)  # Biên độ dao động lên xuống
            self.wave_speed = random.uniform(0.3, 0.7)  # Tốc độ dao động lên xuống
        except pygame.error as e:
            print(f"Lỗi khi tải hình ảnh đám mây: {e} - {image_path}")
            # Tạo đám mây mặc định nếu có lỗi
            self.image = pygame.Surface((100, 50), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (200, 200, 200, alpha), (0, 0, 100, 50))
            self.x = random.randint(0, game.screen_width)
            self.y = y_pos
            self.base_y = y_pos
            self.speed = speed * 0.8
            self.depth = depth
            self.time_offset = random.random() * 100
            self.wave_amplitude = random.uniform(0.8, 2.0)
            self.wave_speed = random.uniform(0.3, 0.7)
        
    def update(self, delta_time):
        # Di chuyển đám mây từ trái sang phải với tốc độ phụ thuộc vào delta_time
        self.x += self.speed * delta_time * 60
        
        
        # Nếu đám mây đi ra khỏi màn hình bên phải, đặt lại vị trí bên trái
        if self.x > self.game.screen_width:
            self.x = -self.image.get_width()
            # Thay đổi ngẫu nhiên vị trí y khi đám mây quay lại
            self.base_y = random.randint(0, int(self.game.screen_height * 0.6))
            self.y = self.base_y
            # Thay đổi ngẫu nhiên biên độ và tốc độ dao động
            self.wave_amplitude = random.uniform(0.8, 2.0)
            self.wave_speed = random.uniform(0.3, 0.7)
    
    def draw(self):
        # Vẽ đám mây lên màn hình
        self.game.screen.blit(self.image, (int(self.x), int(self.y)))

class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()  # Khởi tạo hệ thống âm thanh
        except pygame.error:
            print("Không thể khởi tạo âm thanh. Game sẽ chạy mà không có âm thanh.")
        
        pygame.display.set_caption('Wind Stride')
        
        self.screen_width = 1200
        self.screen_height = 700
        # Đặt chế độ video TRƯỚC khi tải hình ảnh
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Thiết lập logo sau khi đã thiết lập chế độ video
        try:
            logo = pygame.image.load('assests/gui/PNG/menu/LogoWindStride.png').convert_alpha()
            logo = pygame.transform.scale(logo, (32, 32))
            pygame.display.set_icon(logo)
        except pygame.error:
            print("Không thể tải icon!")
            
        self.clock = pygame.time.Clock()
        self.last_time = pygame.time.get_ticks()
        self.fps = 60
        
        # Màu sắc
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        
        # Tải hình ảnh
        try:
            # Tải background
            self.background_img = pygame.image.load("assests/background/PNG/game_background_1/game_background_1.png").convert()
            self.background = pygame.transform.scale(self.background_img, (self.screen_width, self.screen_height))
            
            # Tải logo menu
            self.menu_logo = pygame.image.load('assests/gui/PNG/menu/LogoWindStride2.png').convert_alpha()
            self.menu_logo = pygame.transform.scale(self.menu_logo, 
                                                  (int(self.menu_logo.get_width() * 0.8), 
                                                   int(self.menu_logo.get_height() * 0.8)))

            # Tải hình ảnh đám mây để chuẩn bị
            self.cloud_img = pygame.image.load('assests/background/PNG/game_background_2/layers/clouds_3.png').convert_alpha()
            
        except pygame.error as e:
            print(f"Lỗi khi tải hình ảnh: {e}")
            # Tạo background mặc định nếu có lỗi
            self.background = pygame.Surface((self.screen_width, self.screen_height))
            self.background.fill((70, 130, 180))  # Màu xanh da trời
            
        # Tạo các đám mây
        self.create_clouds()
        
        # Tạo nút menu
        self.create_menu_buttons()
        
        # Trạng thái game
        self.state = "menu"  # menu, game, options, about
        
        # Biến để theo dõi trạng thái hộp thoại xác nhận thoát
        self.show_quit_dialog = False
        
        # Font cho text
        self.font_large = pygame.font.Font('assests/font/Arial.ttf', 72)
        self.font_medium = pygame.font.Font('assests/font/Arial.ttf', 48)
        self.font_small = pygame.font.Font('assests/font/Arial.ttf', 36)
        self.font_title = pygame.font.Font('assests/font/Arial.ttf', 50)


    def create_clouds(self):
        # Tạo các đám mây di chuyển với nhiều lớp độ sâu khác nhau
        self.clouds = []
        
        # Danh sách các hình ảnh đám mây
        cloud_images = [
            'assests/background/PNG/game_background_1/layers/clouds_2.png',
            'assests/background/PNG/game_background_1/layers/clouds_2.png',
            'assests/background/PNG/game_background_1/layers/clouds_3.png',
            'assests/background/PNG/game_background_1/layers/clouds_4.png'
        ]
        
        # Lớp đám mây xa nhất (chậm nhất, mờ nhất)
        for i in range(5):
            x_pos = i * (self.screen_width // 5)
            self.clouds.append(Cloud(
                self, 
                cloud_images[0],
                0.10,
                random.randint(20, 150),
                scale=0.5,
                depth=0.2,
                alpha=120
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
                alpha=150
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
                alpha=200
            ))
            
        for i in range(4):
            x_pos = i * (self.screen_width // 4) + (self.screen_width // 8)  # Xen kẽ
            self.clouds.append(Cloud(
                self, 
                cloud_images[3],
                0.35,
                random.randint(150, 300),
                scale=0.75,
                depth=0.7,
                alpha=220
            ))
        
        # Lớp đám mây gần nhất (nhanh nhất, rõ nhất)
        for i in range(4):
            x_pos = i * (self.screen_width // 4)
            self.clouds.append(Cloud(
                self, 
                cloud_images[2],
                0.45,
                random.randint(180, 350),
                scale=0.9,
                depth=1.0,
                alpha=240
            ))
            
        for i in range(4):
            x_pos = i * (self.screen_width // 4) + (self.screen_width // 8)  # Xen kẽ
            self.clouds.append(Cloud(
                self, 
                cloud_images[0],
                0.40,
                random.randint(150, 320),
                scale=0.8,
                depth=0.95,
                alpha=230
            ))

    def create_menu_buttons(self):
        # Tỉ lệ nút
        button_scale = 0.25
        
        button_x = 0 #Vị trí đầu màn hình
        button_y2 = 0
        button_y = self.screen_height * 0.5  # Vị trí y của dòng nút đầu tiên
        button_spacing = 120  # Khoảng cách giữa các nút
        
        # Vị trí trung tâm màn hình
        center_x = self.screen_width // 2
        
        # Thêm faq trên góc trái
        self.faq_button = Button(self, 'assests/gui/PNG/btn/faq.png', button_x+40, button_y2+40, button_scale*1.2)
        
        # Thêm nút quit góc trái dưới tương xứng với nút FAQ
        self.quit_button = Button(self, 'assests/gui/PNG/btn/close.png', button_x+40, self.screen_height-40, button_scale*1.2)


        # Tạo nút Play ở giữa
        self.play_button = Button(self, 'assests/gui/PNG/menu/play.png', center_x*0.82, button_y, button_scale)

        self.shop_button = Button(self, 'assests/gui/PNG/btn/shop.png',center_x*1.17, button_y, button_scale*2.23)
        
        # Tạo các nút khác theo hàng ngang, đều khoảng cách
        button_y += button_spacing + 38  # Dịch xuống cho hàng nút thứ hai + thêm 1cm (38px)
        
        # 3 nút còn lại xếp thành hàng ngang dưới nút Play, cách đều nhau
        self.leader_button = Button(self, 'assests/gui/PNG/menu/leader.png', 
                                    center_x - button_spacing - 30, button_y, button_scale)
        self.setting_button = Button(self, 'assests/gui/PNG/menu/setting.png', 
                                     center_x, button_y, button_scale)
        self.about_button = Button(self, 'assests/gui/PNG/menu/about.png', 
                                  center_x + button_spacing + 30, button_y, button_scale)
    
    def update_clouds(self, delta_time):
        # Cập nhật và vẽ các đám mây theo độ sâu
        sorted_clouds = sorted(self.clouds, key=lambda cloud: cloud.depth)
        for cloud in sorted_clouds:
            cloud.update(delta_time)
            cloud.draw()

    def draw_menu(self):
        # Vẽ logo trên cùng màn hình
        logo_rect = self.menu_logo.get_rect(center=(self.screen_width // 2, self.screen_height * 0.2))
        self.screen.blit(self.menu_logo, logo_rect)
        
        # Vẽ các nút menu
        if self.play_button.draw():
            print("Nút Play được nhấn!")
            # Thay đổi trạng thái game
            self.state = "game"
            
        if self.setting_button.draw():
            print("Nút Setting được nhấn!")
            # Thực hiện hành động khi nhấn Settings
            
        if self.leader_button.draw():
            print("Nút Leaderboard được nhấn!")
            # Thực hiện hành động khi nhấn Leaderboard
            
        if self.shop_button.draw():
            print("Nút Prize được nhấn!")
            # Thực hiện hành động khi nhấn Prize
            
        if self.about_button.draw():
            print("Nút About được nhấn!")
            # Chuyển sang màn hình hướng dẫn
            self.state = "about"
            
        if self.faq_button.draw():
            # Mở trang Facebook khi nhấn nút FAQ
            webbrowser.open("https://www.facebook.com/namdory13")

        if self.quit_button.draw():
            print("Nút Quit được nhấn!")
            # Hiển thị hộp thoại xác nhận thoát
            self.show_quit_dialog = True

    def draw_quit_dialog(self):
        # Làm tối màn hình nền
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Màu đen với độ trong suốt
        self.screen.blit(overlay, (0, 0))
        
        # Tạo hộp thoại
        dialog_width = 650
        dialog_height = 230
        dialog_x = self.screen_width // 2 - dialog_width // 2
        dialog_y = self.screen_height // 2 - dialog_height // 2
        
        # Vẽ hộp thoại
        dialog_surface = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        pygame.draw.rect(dialog_surface, (30, 30, 30, 240), (0, 0, dialog_width, dialog_height), border_radius=10)
        pygame.draw.rect(dialog_surface, (255, 255, 255, 100), (0, 0, dialog_width, dialog_height), 3, border_radius=10)
        self.screen.blit(dialog_surface, (dialog_x, dialog_y))
        
        # Tiêu đề và nội dung
        title_text = self.font_medium.render("Xác nhận", True, self.white)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, dialog_y + 40))
        self.screen.blit(title_text, title_rect)
        
        content_text = self.font_small.render("Bạn có muốn thoát trò chơi không?", True, self.white)
        content_rect = content_text.get_rect(center=(self.screen_width // 2, dialog_y + 100))
        self.screen.blit(content_text, content_rect)
        
        # Tạo nút OK và Cancel
        button_width = 120
        button_height = 40
        padding = 20
        
        # Nút OK
        ok_button_x = dialog_x + (dialog_width // 2) - button_width - padding // 2
        ok_button_y = dialog_y + dialog_height - button_height - 30
        ok_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        pygame.draw.rect(ok_surface, (50, 150, 50, 220), (0, 0, button_width, button_height), border_radius=5)
        pygame.draw.rect(ok_surface, (255, 255, 255, 150), (0, 0, button_width, button_height), 2, border_radius=5)
        self.screen.blit(ok_surface, (ok_button_x, ok_button_y))
        
        ok_text = self.font_small.render("OK", True, self.white)
        ok_text_rect = ok_text.get_rect(center=(ok_button_x + button_width // 2, ok_button_y + button_height // 2))
        self.screen.blit(ok_text, ok_text_rect)
        
        # Nút Cancel
        cancel_button_x = dialog_x + (dialog_width // 2) + padding // 2
        cancel_button_y = ok_button_y
        cancel_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        pygame.draw.rect(cancel_surface, (150, 50, 50, 220), (0, 0, button_width, button_height), border_radius=5)
        pygame.draw.rect(cancel_surface, (255, 255, 255, 150), (0, 0, button_width, button_height), 2, border_radius=5)
        self.screen.blit(cancel_surface, (cancel_button_x, cancel_button_y))
        
        cancel_text = self.font_small.render("Cancel", True, self.white)
        cancel_text_rect = cancel_text.get_rect(center=(cancel_button_x + button_width // 2, cancel_button_y + button_height // 2))
        self.screen.blit(cancel_text, cancel_text_rect)
        
        # Kiểm tra click chuột
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        # Kiểm tra nút OK
        ok_rect = pygame.Rect(ok_button_x, ok_button_y, button_width, button_height)
        if ok_rect.collidepoint(mouse_pos):
            # Hiệu ứng hover
            pygame.draw.rect(self.screen, (100, 200, 100, 150), ok_rect, border_radius=5)
            if mouse_clicked:
                pygame.quit()
                sys.exit()
        
        # Kiểm tra nút Cancel
        cancel_rect = pygame.Rect(cancel_button_x, cancel_button_y, button_width, button_height)
        if cancel_rect.collidepoint(mouse_pos):
            # Hiệu ứng hover
            pygame.draw.rect(self.screen, (200, 100, 100, 150), cancel_rect, border_radius=5)
            if mouse_clicked:
                self.show_quit_dialog = False

    def wrap_text(self, text, font, max_width): #Hàm xuống dòng
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_width = font.size(test_line)[0]  # Lấy chiều rộng từ kết quả size()

            if test_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)  # Thêm dòng cuối cùng
        return lines        
    
    def draw_about(self): #trang hướng dẫn
        button_scale = 0.25
        button_x = 0 #Vị trí đầu màn hình
        
        # Nút quay lại ở góc dưới bên trái
        self.back_btn_bottom = Button(self, 'assests/gui/PNG/btn/prew.png', 
                                     button_x+60, self.screen_height-60, button_scale*1.2)
        
        # Kiểm tra nếu nút quay lại được nhấn
        if self.back_btn_bottom.draw():
            print("Nút quay lại được nhấn!")
            self.state = "menu"

        panel_width = 800
        panel_height = 500
        panel_x = self.screen_width // 2 - panel_width // 2
        panel_y = self.screen_height // 2 - panel_height // 2
        
        # Vẽ panel nền
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (0, 0, 0, 180), (0, 0, panel_width, panel_height))
        pygame.draw.rect(panel_surface, (255, 255, 255, 100), (0, 0, panel_width, panel_height), 3)
        self.screen.blit(panel_surface, (panel_x, panel_y))
        
        # Tiêu đề
        title_text = self.font_title.render("HƯỚNG DẪN", True, self.white)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, panel_y + 60))
        self.screen.blit(title_text, title_rect)
        
        # Các phím điều khiển
        instructions = [
            ["A, D:", "Di chuyển"],
            ["Enter:", "Tấn công"],
            ["Space:", "Nhảy"],
            ["Shop:", "Người chơi dùng tiền để đổi vật phẩm"]
        ]
        
        fixed_x = self.screen_width // 5
        y_pos = panel_y+120 #Cách dòng tiêu đề 20px
        for instruction in instructions:
            # Key
            key_text = self.font_small.render(instruction[0], True, (255, 255, 150))
            key_rect = key_text.get_rect(left=fixed_x, y=y_pos)
            self.screen.blit(key_text, key_rect)
            
            # Action
            action_text = self.font_small.render(instruction[1], True, self.white)
            action_rect = action_text.get_rect(left=fixed_x+120, y=y_pos)
            self.screen.blit(action_text, action_rect)
            
            y_pos += 40
        
        # Mục tiêu trò chơi
        objective_title = self.font_small.render("Mục tiêu:", True, (255, 255, 150))
        objective_rect = objective_title.get_rect(x=panel_x + 40, y=panel_y + 300)
        self.screen.blit(objective_title, objective_rect)
        
        objective_text = "Người chơi sẽ vượt chướng ngại vật và đi tới cánh cổng để tới màn tiếp theo."
        max_text_width = panel_width - 80  # Đảm bảo không bị tràn ra ngoài
        wrapped_lines = self.wrap_text(objective_text, self.font_small, max_text_width)

        y_pos = panel_y + 340
        for line in wrapped_lines:
            line_text = self.font_small.render(line, True, self.white)
            line_rect = line_text.get_rect(x=panel_x + 40, y=y_pos)
            self.screen.blit(line_text, line_rect)
            y_pos += 40  # Khoảng cách giữa các dòng

    def run(self):
        while True:
            # Tính toán delta time
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - self.last_time) / 1000.0
            self.last_time = current_time
            delta_time = min(delta_time, 0.1)  # Giới hạn delta_time

            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "menu":
                            # Hiển thị hộp thoại xác nhận thoát khi nhấn ESC ở menu
                            self.show_quit_dialog = True
                        else:
                            self.state = "menu"

            # Vẽ background
            self.screen.blit(self.background, (0, 0))
            
            # Cập nhật và vẽ đám mây
            self.update_clouds(delta_time)
            
            # Vẽ UI theo trạng thái game
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "game":
                # Phần xử lý game sẽ được thêm sau
                font = pygame.font.Font(None, 72)
                game_text = font.render("GAME SCREEN", True, self.white)
                self.screen.blit(game_text, 
                                (self.screen_width // 2 - game_text.get_width() // 2, 
                                 self.screen_height // 2 - game_text.get_height() // 2))
                
                # Nút back để trở về menu
                back_text = font.render("Nhấn ESC để trở về menu", True, self.white)
                self.screen.blit(back_text, 
                                (self.screen_width // 2 - back_text.get_width() // 2, 
                                 self.screen_height // 2 + 100))
            elif self.state == "about":
                self.draw_about()
            
            # Hiển thị hộp thoại xác nhận thoát nếu cần
            if self.show_quit_dialog:
                self.draw_quit_dialog()

            pygame.display.update()
            self.clock.tick(self.fps)
            
if __name__ == "__main__":
    Game().run()