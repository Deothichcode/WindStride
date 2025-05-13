import sys 
import pygame #type: ignore
from pygame.locals import* #type: ignore
import random
import webbrowser 
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
        self.last_click_time = 0  # Thêm biến theo dõi thời gian click cuối
        
    def draw(self):
        # Lấy vị trí chuột
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        current_time = pygame.time.get_ticks() 
        
        self.game.screen.blit(self.image, self.rect.topleft)
        
        # Kiểm tra sự kiện hover và click
        if self.rect.collidepoint(mouse_pos):
            hover_img = pygame.transform.scale(self.image, 
                                              (int(self.rect.width * 1.1), 
                                               int(self.rect.height * 1.1)))
            hover_rect = hover_img.get_rect(center=self.rect.center)
            self.game.screen.blit(hover_img, hover_rect.topleft)
            
            button_cooldown = 400 
            if mouse_clicked and not self.clicked and current_time - self.last_click_time > button_cooldown:
                self.clicked = True
                self.last_click_time = current_time  # Cập nhật thời gian click cuối
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
            
            width = int(self.image_original.get_width() * scale)
            height = int(self.image_original.get_height() * scale)
            self.image = pygame.transform.scale(self.image_original, (width, height))
            
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
        self.x += self.speed * delta_time * 60
        
        
        # Nếu đám mây đi ra khỏi màn hình bên phải, đặt lại vị trí bên trái
        if self.x > self.game.screen_width:
            self.x = -self.image.get_width()
            
            self.base_y = random.randint(0, int(self.game.screen_height * 0.6))
            self.y = self.base_y
            # Thay đổi ngẫu nhiên biên độ và tốc độ dao động
            self.wave_amplitude = random.uniform(0.8, 2.0)
            self.wave_speed = random.uniform(0.3, 0.7)
    
    def draw(self):
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
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        try:
            logo = pygame.image.load('assests/gui/PNG/menu/LogoWindStride.png').convert_alpha()
            logo = pygame.transform.scale(logo, (32, 32))
            pygame.display.set_icon(logo)
        except pygame.error:
            print("Không thể tải icon!")
            
        self.clock = pygame.time.Clock()
        self.last_time = pygame.time.get_ticks()
        self.fps = 60
        
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        
        # Cài đặt âm thanh
        self.sound_on = True  
        self.volume = 70  
        self.dragging_slider = False  # Trạng thái đang kéo thanh trượt
        
        # Tải nhạc menu và game
        try:
            self.menu_music = pygame.mixer.Sound('assests/sfx/menusfx/WhereWindWhispers.mp3')
            self.game_music = pygame.mixer.Sound('assests/sfx/menusfx/NinjaSchool.mp3')
            self.menu_music.set_volume(self.volume / 100.0)  # Thiết lập âm lượng ban đầu (0.0 - 1.0)
            self.game_music.set_volume(self.volume / 100.0)
            self.music_playing = False  # Trạng thái đang phát nhạc
        except pygame.error as e:
            print(f"Không thể tải nhạc: {e}")
            self.menu_music = None
            self.game_music = None
        
        self.sound_effect_on = True  
        self.effect_volume = 70 
        self.dragging_effect_slider = False  
        
        self.sound_button_last_click = 0
        self.effect_button_last_click = 0
        self.button_cooldown = 500 
        
        # Tải hình ảnh cho màn hình chọn màn chơi
        try:
            self.level_frame = pygame.image.load('assests/gui/PNG/level_select/bg.png').convert_alpha()
            self.level_star = pygame.image.load('assests/gui/PNG/level_select/star_4.png').convert_alpha()
            self.level_lock = pygame.image.load('assests/gui/PNG/level_select/lock.png').convert_alpha()
            self.level_star3 = pygame.image.load('assests/gui/PNG/level_select/star_1.png').convert_alpha()
            self.level_star2 = pygame.image.load('assests/gui/PNG/level_select/star_2.png').convert_alpha()
            self.level_star1 = pygame.image.load('assests/gui/PNG/level_select/star_3.png').convert_alpha()
        except pygame.error as e:
            print(f"Không thể tải hình ảnh cho màn hình chọn màn chơi: {e}")
        
        # Danh sách màn chơi đã mở khóa (ban đầu chỉ mở màn 1)
        self.unlocked_levels = [1]
        # Màn chơi hiện tại
        self.current_level = 1
        
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
            self.background.fill((70, 130, 180))
            
        # Tạo các đám mây
        self.create_clouds()
        
        # Tạo nút menu
        self.create_menu_buttons()
        
        # Trạng thái game
        self.state = "menu"
        self.show_shop_popup = False
        self.show_quit_dialog = False
        
        # Font cho text
        self.font_large = pygame.font.Font('assests/font/Arial.ttf', 72)
        self.font_medium = pygame.font.Font('assests/font/Arial.ttf', 48)
        self.font_small = pygame.font.Font('assests/font/Arial.ttf', 36)
        self.font_title = pygame.font.Font('assests/font/Arial.ttf', 50)
        self.font_small2 = pygame.font.Font('assests/font/Arial.ttf', 20)
        self.font_level = pygame.font.Font('assests/font/Arial.ttf', 70)
        self.font_level.set_bold(True)
        self.font_title.set_bold(True)

    def create_clouds(self):
        self.clouds = []
        
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
            x_pos = i * (self.screen_width // 4) + (self.screen_width // 8)
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
            x_pos = i * (self.screen_width // 4) + (self.screen_width // 8)
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
        button_scale = 0.25
        
        button_x = 0
        button_y = self.screen_height * 0.5  
        button_spacing = 120
        
        # Vị trí trung tâm màn hình
        center_x = self.screen_width // 2
        
        self.faq_button = Button(self, 'assests/gui/PNG/btn/faq.png', self.screen_width-40, self.screen_height-40, button_scale*1.2)
        
        self.quit_button = Button(self, 'assests/gui/PNG/btn/close.png', button_x+40, self.screen_height-40, button_scale*1.2)

        self.play_button = Button(self, 'assests/gui/PNG/menu/play.png', center_x*0.82, button_y, button_scale)

        self.shop_button = Button(self, 'assests/gui/PNG/btn/shop.png',center_x*1.17, button_y, button_scale*2.23)
        
        button_y += button_spacing + 38
        
        self.about_button = Button(self, 'assests/gui/PNG/menu/leader.png', 
                                    center_x - button_spacing - 30, button_y, button_scale)
        self.setting_button = Button(self, 'assests/gui/PNG/menu/setting.png', 
                                     center_x, button_y, button_scale)
        self.leader_button = Button(self, 'assests/gui/PNG/menu/about.png', 
                                  center_x + button_spacing + 30, button_y, button_scale)
    
    def update_clouds(self, delta_time):
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
            self.state = "level_select"
            
        if self.setting_button.draw():
            print("Nút Setting được nhấn!")
            self.state = "setting"

        if self.leader_button.draw():
            print("Nút Leaderboard được nhấn!")
            self.state = "leaderboard"

        if self.shop_button.draw():
            print("Nút Prize được nhấn!")
            self.show_shop_popup = True
            
        if self.about_button.draw():
            print("Nút About được nhấn!")
            self.state = "about"
            
        if self.faq_button.draw():
            webbrowser.open("https://www.facebook.com/namdory13")

        if self.quit_button.draw():
            print("Nút Quit được nhấn!")
            self.show_quit_dialog = True

        if self.show_shop_popup:
            self.draw_shop_popup()

    def draw_level_select(self, score_rs):
        button_scale = 0.25
        button_x = 0 
        
        self.back_btn_level = Button(self, 'assests/gui/PNG/btn/prew.png', 
                                     button_x+100, self.screen_height-100, button_scale*1.2)
        
        if self.back_btn_level.draw():
            print("Nút quay lại từ màn hình chọn màn chơi được nhấn!")
            self.state = "menu"

        # Vẽ tiêu đề
        title_text = self.font_title.render("CHỌN MÀN CHƠI", True, self.white)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Thiết lập kích thước và bố trí màn chơi
        level_width = 200
        level_height = 180
        padding_x = 40
        padding_y = 50
        
        # Tính toán vị trí bắt đầu để căn giữa lưới màn chơi
        total_width = 3 * level_width + 2 * padding_x
        start_x = (self.screen_width - total_width) // 2
        start_y = 150
        
        # Vẽ các màn chơi (2 hàng, mỗi hàng 3 màn)
        for row in range(2):
            for col in range(3):
                level_number = row * 3 + col + 1  # Số màn chơi từ 1-6
                level_x = start_x + col * (level_width + padding_x)
                level_y = start_y + row * (level_height + padding_y)
                
                # Vẽ khung màn chơi
                frame = pygame.transform.scale(self.level_frame, (level_width, level_height))
                self.screen.blit(frame, (level_x, level_y))
                
                # Kiểm tra nếu màn chơi đã mở khóa
                if level_number in self.unlocked_levels:
                    # Vẽ số màn chơi
                    number_text = self.font_level.render(f"{level_number}", True, self.white)
                    number_rect = number_text.get_rect(center=(level_x + level_width // 2 - 5, level_y + 70))
                    self.screen.blit(number_text, number_rect)
                    
                    # Vẽ sao đánh giá
                    if score_rs[level_number-1] == 0:
                        star = pygame.transform.scale(self.level_star, (150, 70))
                        star_rect = star.get_rect(center=(level_x + level_width // 2, level_y + 140))
                        self.screen.blit(star, star_rect)
                    elif score_rs[level_number-1] == 3:
                        star = pygame.transform.scale(self.level_star3, (150, 70))
                        star_rect = star.get_rect(center=(level_x + level_width // 2, level_y + 140))
                        self.screen.blit(star, star_rect)
                    elif score_rs[level_number-1] == 2:
                        star = pygame.transform.scale(self.level_star2, (150, 70))
                        star_rect = star.get_rect(center=(level_x + level_width // 2, level_y + 140))
                        self.screen.blit(star, star_rect)
                    elif score_rs[level_number-1] == 1:
                        star = pygame.transform.scale(self.level_star1, (150, 70))
                        star_rect = star.get_rect(center=(level_x + level_width // 2, level_y + 140))
                        self.screen.blit(star, star_rect)
                else:
                    # Vẽ ổ khóa nếu màn chơi chưa mở
                    lock = pygame.transform.scale(self.level_lock, (80, 80))
                    lock_rect = lock.get_rect(center=(level_x + level_width // 2, level_y + level_height // 2))
                    self.screen.blit(lock, lock_rect)
                
                # Xử lý sự kiện khi nhấn vào màn chơi
                level_rect = pygame.Rect(level_x, level_y, level_width, level_height)
                mouse_pos = pygame.mouse.get_pos()
                mouse_clicked = pygame.mouse.get_pressed()[0]
                
                if level_rect.collidepoint(mouse_pos):
                    # Hiệu ứng hover
                    if level_number in self.unlocked_levels:
                        pygame.draw.rect(self.screen, (255, 255, 255, 50), level_rect, 4, border_radius=10)
                    # Xử lý khi click vào màn đã mở khóa
                    if mouse_clicked and level_number in self.unlocked_levels:
                        print(f"Chọn màn chơi {level_number}")
                        self.current_level = level_number
                        
                         # Cập nhật màn hình lần cuối trước khi chuyển
                        pygame.display.flip()
                        
                        # Pre-load level
                        if self.current_level == 1:
                            import levels.level1 as level1
                            self.preloaded_level = level1
                        elif self.current_level == 2:
                            import levels.level2 as level2
                            self.preloaded_level = level2
                        elif self.current_level == 3:
                            import levels.level3 as level3
                            self.preloaded_level = level3
                        elif self.current_level == 4:
                            import levels.level4 as level4
                            self.preloaded_level = level4
                        elif self.current_level == 5:
                            import levels.level5 as level5
                            self.preloaded_level = level5
                        elif self.current_level == 6:
                            import levels.level6 as level6
                            self.preloaded_level = level6

                        # Hiển thị màn hình loading
                        self.show_loading_screen()
                        self.state = "game"
                        return  # Chuyển sang màn chơi
    def draw_shop_popup(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        dialog_width = 800
        dialog_height = 180
        dialog_x = self.screen_width // 2 - dialog_width // 2
        dialog_y = self.screen_height // 2 - dialog_height // 2

        dialog_surface = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        pygame.draw.rect(dialog_surface, (30, 30, 30, 240), (0, 0, dialog_width, dialog_height), border_radius=10)
        pygame.draw.rect(dialog_surface, (255, 255, 255, 100), (0, 0, dialog_width, dialog_height), 3, border_radius=10)
        self.screen.blit(dialog_surface, (dialog_x, dialog_y))
        
        message = "Tính năng đang được phát triển!"
        text = self.font_medium.render(message, True, self.white)
        text_rect = text.get_rect(center=(self.screen_width // 2, dialog_y + 60))
        self.screen.blit(text, text_rect)
        
        button_width = 120
        button_height = 40
        ok_button_x = self.screen_width // 2 - button_width // 2
        ok_button_y = dialog_y + dialog_height - button_height - 30
        
        ok_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        pygame.draw.rect(ok_surface, (50, 150, 50, 220), (0, 0, button_width, button_height), border_radius=5)
        pygame.draw.rect(ok_surface, (255, 255, 255, 150), (0, 0, button_width, button_height), 2, border_radius=5)
        self.screen.blit(ok_surface, (ok_button_x, ok_button_y))
        
        ok_text = self.font_small.render("OK", True, self.white)
        ok_text_rect = ok_text.get_rect(center=(ok_button_x + button_width // 2, ok_button_y + button_height // 2))
        self.screen.blit(ok_text, ok_text_rect)
        
        ok_rect = pygame.Rect(ok_button_x, ok_button_y, button_width, button_height)
        if ok_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (100, 200, 100, 150), ok_rect, border_radius=5)
            if mouse_clicked:
                self.show_shop_popup = False

    def show_loading_screen(self):
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
        
        bar_width = 600
        bar_height = 40
        
        loadbar_bg = pygame.transform.scale(loadbar_bg, (bar_width, bar_height))
        loadbar_1 = pygame.transform.scale(loadbar_1, (bar_width, bar_height))
        loadbar_2 = pygame.transform.scale(loadbar_2, (bar_width, bar_height))
        loadbar_3 = pygame.transform.scale(loadbar_3, (bar_width, bar_height))
        loading_text = pygame.transform.scale(loading_text, (400, 70))
        
        bar_x = self.screen_width // 2 - bar_width // 2
        bar_y = self.screen_height // 2 - bar_height // 2
        text_x = self.screen_width // 2 - loading_text.get_width() // 2
        text_y = bar_y - loading_text.get_height() - 20
        
        # Thiết lập thời gian loading
        loading_time = 3.0
        start_time = pygame.time.get_ticks()
        current_time = start_time
        
        while (current_time - start_time) / 1000.0 < loading_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
            
            progress = min(100, ((current_time - start_time) / 1000.0) / loading_time * 100)      
            self.screen.fill((0, 0, 0))
            self.screen.blit(loading_text, (text_x, text_y))         
            self.screen.blit(loadbar_bg, (bar_x, bar_y))
            
            if progress < 33:
                # Hiển thị lần lượt 1/3 đầu thanh loading
                progress_width = int(bar_width * progress / 33)
                loadbar_crop = loadbar_1.subsurface((0, 0, progress_width, bar_height))
                self.screen.blit(loadbar_crop, (bar_x, bar_y))
            elif progress < 66:
                # Hiển thị đầy đủ 1/3 đầu và một phần của 1/3 giữa
                self.screen.blit(loadbar_1, (bar_x, bar_y))
                progress_width = int(bar_width * (progress - 33) / 33)
                loadbar_crop = loadbar_2.subsurface((0, 0, progress_width, bar_height))
                self.screen.blit(loadbar_crop, (bar_x, bar_y))
            else:
                # Hiển thị đầy đủ 2/3 đầu và một phần của 1/3 cuối
                self.screen.blit(loadbar_1, (bar_x, bar_y))
                self.screen.blit(loadbar_2, (bar_x, bar_y))
                progress_width = int(bar_width * (progress - 66) / 34)
                loadbar_crop = loadbar_3.subsurface((0, 0, progress_width, bar_height))
                self.screen.blit(loadbar_crop, (bar_x, bar_y))
            
            # Hiển thị % loading
            percent_text = self.font_small.render(f"{int(progress)}%", True, self.white)
            percent_rect = percent_text.get_rect(center=(self.screen_width // 2, bar_y + bar_height + 30))
            self.screen.blit(percent_text, percent_rect)
            
            tips = [
                "Đừng quên thu thập đủ vàng nhé chiến binh!!!"
            ]
            current_tip = random.choice(tips)
            tip_text = self.font_small2.render(current_tip, True, (200, 200, 200))
            self.screen.blit(tip_text, tip_text.get_rect(center=(self.screen_width // 2, self.screen_height - 100)))
            
            pygame.display.flip()
            
            current_time = pygame.time.get_ticks()
            
            self.clock.tick(60)

        self.screen.fill((0, 0, 0))
        self.screen.blit(loading_text, (text_x, text_y))
        self.screen.blit(loadbar_bg, (bar_x, bar_y))
        self.screen.blit(loadbar_1, (bar_x, bar_y))
        self.screen.blit(loadbar_2, (bar_x, bar_y))
        self.screen.blit(loadbar_3, (bar_x, bar_y))
        percent_text = self.font_small.render("100%", True, self.white)
        self.screen.blit(percent_text, percent_rect)
        self.screen.blit(tip_text, tip_text.get_rect(center=(self.screen_width // 2, self.screen_height - 100)))
        pygame.display.flip()
    
    def draw_quit_dialog(self):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) 
        self.screen.blit(overlay, (0, 0))
        
        dialog_width = 650
        dialog_height = 230
        dialog_x = self.screen_width // 2 - dialog_width // 2
        dialog_y = self.screen_height // 2 - dialog_height // 2
    
        dialog_surface = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        pygame.draw.rect(dialog_surface, (30, 30, 30, 240), (0, 0, dialog_width, dialog_height), border_radius=10)
        pygame.draw.rect(dialog_surface, (255, 255, 255, 100), (0, 0, dialog_width, dialog_height), 3, border_radius=10)
        self.screen.blit(dialog_surface, (dialog_x, dialog_y))
        
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
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        # Kiểm tra nút OK
        ok_rect = pygame.Rect(ok_button_x, ok_button_y, button_width, button_height)
        if ok_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (100, 200, 100, 150), ok_rect, border_radius=5)
            if mouse_clicked:
                if self.menu_music:
                    self.menu_music.stop()
                pygame.quit()
                sys.exit()
        
        # Kiểm tra nút Cancel
        cancel_rect = pygame.Rect(cancel_button_x, cancel_button_y, button_width, button_height)
        if cancel_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (200, 100, 100, 150), cancel_rect, border_radius=5)
            if mouse_clicked:
                self.show_quit_dialog = False

    def wrap_text(self, text, font, max_width): #Hàm xuống dòng
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_width = font.size(test_line)[0]  

            if test_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)  
        return lines        
    
    def draw_about(self): #trang hướng dẫn
        button_scale = 0.25
        button_x = 0 
        
        self.back_btn_bottom = Button(self, 'assests/gui/PNG/btn/prew.png', 
                                     button_x+100, self.screen_height-100, button_scale*1.2)
        
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
            ["< >:", "Di chuyển"],
            ["Z X:", "Tấn công"],
            ["^:", "Nhảy"],
            ["Shop:", "Người chơi dùng tiền để đổi vật phẩm"]
        ]
        
        fixed_x = self.screen_width // 5
        y_pos = panel_y+120 
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
        
        objective_text = "Người chơi sẽ vượt chướng ngại vật và đi tới đích để tới màn tiếp theo."
        max_text_width = panel_width - 80 
        wrapped_lines = self.wrap_text(objective_text, self.font_small, max_text_width)

        y_pos = panel_y + 340
        for line in wrapped_lines:
            line_text = self.font_small.render(line, True, self.white)
            line_rect = line_text.get_rect(x=panel_x + 40, y=y_pos)
            self.screen.blit(line_text, line_rect)
            y_pos += 40 

    def draw_setting(self):
        button_scale = 0.25
        button_x = 0 
        
        self.back_btn_setting = Button(self, 'assests/gui/PNG/btn/prew.png', 
                                     button_x+100, self.screen_height-100, button_scale*1.2)
        
        if self.back_btn_setting.draw():
            print("Nút quay lại từ setting được nhấn!")
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
        title_text = self.font_title.render("CÀI ĐẶT", True, self.white)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, panel_y + 60))
        self.screen.blit(title_text, title_rect)
        
        # Phần âm nhạc
        sound_title = self.font_small.render("Âm nhạc:", True, (255, 255, 150))
        sound_rect = sound_title.get_rect(x=panel_x + 50, y=panel_y + 150)
        self.screen.blit(sound_title, sound_rect)
        
        # Tạo nút điều khiển âm nhạc
        sound_icon = 'assests/gui/PNG/btn/sound.png' if self.sound_on else 'assests/gui/PNG/btn/sound_off.png'
        self.sound_button = Button(self, sound_icon, panel_x + 260, panel_y + 165, button_scale*1.5)
        
        # Lấy thời gian hiện tại
        current_time = pygame.time.get_ticks()
        
        if self.sound_button.draw() and current_time - self.sound_button_last_click > self.button_cooldown:
            self.sound_button_last_click = current_time 
            self.sound_on = not self.sound_on  
            if not self.sound_on:
                self.volume = 0
                if self.menu_music:
                    self.menu_music.set_volume(0)
            elif self.volume == 0:
                self.volume = 10
                if self.menu_music:
                    self.menu_music.set_volume(0.1)
            print(f"Âm nhạc: {'Bật' if self.sound_on else 'Tắt'}, Âm lượng: {self.volume}%")
        
        # Vẽ thanh trượt âm lượng nhạc
        slider_x = panel_x + 320
        slider_y = panel_y + 165
        slider_width = 200
        slider_height = 10
        slider_color = (100, 100, 100, 180) 
        slider_fill_color = (80, 180, 80, 220) if self.sound_on else (100, 100, 100, 150)
        
        # Vẽ thanh nền
        slider_surface = pygame.Surface((slider_width, slider_height), pygame.SRCALPHA)
        pygame.draw.rect(slider_surface, slider_color, (0, 0, slider_width, slider_height), border_radius=5)
        self.screen.blit(slider_surface, (slider_x, slider_y))
        
        # Vẽ phần đã điền
        filled_width = int(slider_width * self.volume / 100)
        if filled_width > 0:
            filled_surface = pygame.Surface((filled_width, slider_height), pygame.SRCALPHA)
            pygame.draw.rect(filled_surface, slider_fill_color, (0, 0, filled_width, slider_height), border_radius=5)
            self.screen.blit(filled_surface, (slider_x, slider_y))
        
        # Vẽ núm kéo
        knob_radius = 12
        knob_x = slider_x + filled_width
        knob_y = slider_y + slider_height // 2
        knob_color = (200, 200, 200, 255)  
        pygame.draw.circle(self.screen, knob_color, (knob_x, knob_y), knob_radius)
        pygame.draw.circle(self.screen, (80, 80, 80, 150), (knob_x, knob_y), knob_radius, 2)
        
        # Xử lý kéo thanh trượt
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Kiểm tra xem chuột có đang ở gần núm kéo không
        knob_rect = pygame.Rect(knob_x - knob_radius, knob_y - knob_radius, knob_radius*2, knob_radius*2)
        slider_rect = pygame.Rect(slider_x, slider_y - 10, slider_width, slider_height + 20)
        
        # Xử lý sự kiện khi bắt đầu kéo
        if mouse_pressed and knob_rect.collidepoint(mouse_pos) and not self.dragging_slider and not self.dragging_effect_slider:
            self.dragging_slider = True
        
        # Xử lý sự kiện khi click trực tiếp vào thanh trượt
        elif mouse_pressed and slider_rect.collidepoint(mouse_pos) and not self.dragging_slider and not self.dragging_effect_slider:
            rel_x = min(max(0, mouse_pos[0] - slider_x), slider_width)
            self.volume = int((rel_x / slider_width) * 100)
            self.sound_on = self.volume > 0
            if self.menu_music:
                self.menu_music.set_volume(self.volume / 100.0)
            self.dragging_slider = True
        
        # Xử lý sự kiện khi đang kéo
        elif self.dragging_slider and mouse_pressed:
            rel_x = min(max(0, mouse_pos[0] - slider_x), slider_width)
            self.volume = int((rel_x / slider_width) * 100)
            self.sound_on = self.volume > 0
            if self.menu_music:
                self.menu_music.set_volume(self.volume / 100.0)
        
        # Xử lý sự kiện khi kết thúc kéo
        elif not mouse_pressed and self.dragging_slider:
            self.dragging_slider = False
        
        # Hiển thị phần trăm âm lượng
        volume_text = self.font_small.render(f"{self.volume}%", True, self.white)
        volume_rect = volume_text.get_rect(x=slider_x + slider_width + 20, y=slider_y - 10)
        self.screen.blit(volume_text, volume_rect)
        
        # ----- PHẦN ÂM THANH HIỆU ỨNG -----
        effect_y_offset = 80
        
        # Tiêu đề âm thanh hiệu ứng
        effect_title = self.font_small.render("Âm thanh:", True, (255, 255, 150))
        effect_rect = effect_title.get_rect(x=panel_x + 50, y=panel_y + 165 + effect_y_offset)
        self.screen.blit(effect_title, effect_rect)
        
        # Tạo nút điều khiển âm thanh hiệu ứng
        effect_icon = 'assests/gui/PNG/btn/misic.png' if self.sound_effect_on else 'assests/gui/PNG/btn/music_off.png'
        self.effect_button = Button(self, effect_icon, panel_x + 260, panel_y + 180 + effect_y_offset, button_scale*1.5)
        
        # Kiểm tra nếu nút âm thanh hiệu ứng được nhấn và đã qua thời gian cooldown
        if self.effect_button.draw() and current_time - self.effect_button_last_click > self.button_cooldown:
            self.effect_button_last_click = current_time  
            self.sound_effect_on = not self.sound_effect_on  
            if not self.sound_effect_on:
                self.effect_volume = 0
            elif self.effect_volume == 0:
                self.effect_volume = 10 
            print(f"Âm thanh hiệu ứng: {'Bật' if self.sound_effect_on else 'Tắt'}, Âm lượng: {self.effect_volume}%")
        
        effect_slider_x = panel_x + 320
        effect_slider_y = panel_y + 180 + effect_y_offset
        effect_slider_width = 200
        effect_slider_height = 10
        effect_slider_color = (100, 100, 100, 180)  
        effect_slider_fill_color = (80, 180, 80, 220) if self.sound_effect_on else (100, 100, 100, 150)
        
        # Vẽ thanh nền
        effect_slider_surface = pygame.Surface((effect_slider_width, effect_slider_height), pygame.SRCALPHA)
        pygame.draw.rect(effect_slider_surface, effect_slider_color, (0, 0, effect_slider_width, effect_slider_height), border_radius=5)
        self.screen.blit(effect_slider_surface, (effect_slider_x, effect_slider_y))
        
        # Vẽ phần đã điền
        effect_filled_width = int(effect_slider_width * self.effect_volume / 100)
        if effect_filled_width > 0:
            effect_filled_surface = pygame.Surface((effect_filled_width, effect_slider_height), pygame.SRCALPHA)
            pygame.draw.rect(effect_filled_surface, effect_slider_fill_color, (0, 0, effect_filled_width, effect_slider_height), border_radius=5)
            self.screen.blit(effect_filled_surface, (effect_slider_x, effect_slider_y))
        
        # Vẽ núm kéo
        effect_knob_x = effect_slider_x + effect_filled_width
        effect_knob_y = effect_slider_y + effect_slider_height // 2
        pygame.draw.circle(self.screen, knob_color, (effect_knob_x, effect_knob_y), knob_radius)
        pygame.draw.circle(self.screen, (80, 80, 80, 150), (effect_knob_x, effect_knob_y), knob_radius, 2)
        
        # Kiểm tra tương tác với thanh trượt hiệu ứng
        effect_knob_rect = pygame.Rect(effect_knob_x - knob_radius, effect_knob_y - knob_radius, knob_radius*2, knob_radius*2)
        effect_slider_rect = pygame.Rect(effect_slider_x, effect_slider_y - 10, effect_slider_width, effect_slider_height + 20)
        
        # Xử lý sự kiện khi bắt đầu kéo thanh hiệu ứng
        if mouse_pressed and effect_knob_rect.collidepoint(mouse_pos) and not self.dragging_slider and not self.dragging_effect_slider:
            self.dragging_effect_slider = True
        
        # Xử lý sự kiện khi click trực tiếp vào thanh trượt hiệu ứng
        elif mouse_pressed and effect_slider_rect.collidepoint(mouse_pos) and not self.dragging_slider and not self.dragging_effect_slider:
            rel_x = min(max(0, mouse_pos[0] - effect_slider_x), effect_slider_width)
            self.effect_volume = int((rel_x / effect_slider_width) * 100)
            self.sound_effect_on = self.effect_volume > 0
            self.dragging_effect_slider = True
        
        # Xử lý sự kiện khi đang kéo thanh hiệu ứng
        elif self.dragging_effect_slider and mouse_pressed:
            rel_x = min(max(0, mouse_pos[0] - effect_slider_x), effect_slider_width)
            self.effect_volume = int((rel_x / effect_slider_width) * 100)
            self.sound_effect_on = self.effect_volume > 0
        
        # Xử lý sự kiện khi kết thúc kéo
        elif not mouse_pressed and self.dragging_effect_slider:
            self.dragging_effect_slider = False
        
        # Hiển thị phần trăm âm lượng hiệu ứng
        effect_volume_text = self.font_small.render(f"{self.effect_volume}%", True, self.white)
        effect_volume_rect = effect_volume_text.get_rect(x=effect_slider_x + effect_slider_width + 20, y=effect_slider_y - 10)
        self.screen.blit(effect_volume_text, effect_volume_rect)

    def draw_leaderboard(self):
        button_scale = 0.25
        button_x = 0 
        
        self.back_btn_leader = Button(self, 'assests/gui/PNG/btn/prew.png', 
                                     button_x+100, self.screen_height-100, button_scale*1.2)
        
        # Kiểm tra nếu nút quay lại được nhấn
        if self.back_btn_leader.draw():
            print("Nút quay lại từ màn hình giới thiệu được nhấn!")
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
        title_text = self.font_title.render("GIỚI THIỆU DỰ ÁN", True, self.white)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, panel_y + 60))
        self.screen.blit(title_text, title_rect)
        
        # Nội dung giới thiệu dự án
        project_desc = "WindStride – Sải Bước Của Gió là một dự án game phiêu lưu được phát triển với mục tiêu mang đến trải nghiệm hấp dẫn và đầy thử thách. Người chơi sẽ hóa thân thành một chiến binh dũng cảm, vượt qua chướng ngại vật và khám phá thế giới rộng lớn."
        
        max_text_width = panel_width - 80 
        project_lines = self.wrap_text(project_desc, self.font_small2, max_text_width)
        
        y_pos = panel_y + 120
        for line in project_lines:
            line_text = self.font_small2.render(line, True, self.white)
            line_rect = line_text.get_rect(x=panel_x + 40, y=y_pos)
            self.screen.blit(line_text, line_rect)
            y_pos += 30  
        
        y_pos += 20
        
        thanks_text = self.font_small2.render("Chúng em xin gửi lời cảm ơn chân thành đến Giảng Viên:", True, (255, 255, 150))
        thanks_rect = thanks_text.get_rect(x=panel_x + 40, y=y_pos)
        self.screen.blit(thanks_text, thanks_rect)
        
        y_pos += 30  
        teacher_text = self.font_small2.render("Ninh Thị Thu Trang", True, self.white)
        teacher_rect = teacher_text.get_rect(x=panel_x + 40, y=y_pos)
        self.screen.blit(teacher_text, teacher_rect)
        
        y_pos += 40  

        student_title = self.font_small2.render("Sinh viên thực hiện:", True, (255, 255, 150))
        student_title_rect = student_title.get_rect(x=panel_x + 40, y=y_pos)
        self.screen.blit(student_title, student_title_rect)
        
        students = [
            "Nguyễn Đức Hải(C) - B22DCAT107",
            "Đỗ Duy Nam - B22DCAT199",
            "Nguyễn Quang Huy - B22DCAT143"
        ]
        
        y_pos += 30 
        for student in students:
            student_text = self.font_small2.render(student, True, self.white)
            student_rect = student_text.get_rect(x=panel_x + 40, y=y_pos)
            self.screen.blit(student_text, student_rect)
            y_pos += 30  
    
    def run(self):
        # Phát nhạc menu khi bắt đầu game
        if self.menu_music and not self.music_playing:
            self.menu_music.play(-1)  # -1 nghĩa là lặp vô hạn
            self.music_playing = True
            
        # Khởi tạo biến để lưu trữ level đã pre-load
        self.preloaded_level = None
        self.score_rs = [0,0,0,0,0,0]
        
        while True:
            # Tính toán delta time
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - self.last_time) / 1000.0
            self.last_time = current_time
            delta_time = min(delta_time, 0.1)  # Giới hạn delta_time

            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.menu_music:
                        self.menu_music.stop()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "menu":
                            # Hiển thị hộp thoại xác nhận thoát khi nhấn ESC ở menu
                            self.show_quit_dialog = True
                        elif self.state == "level_select":
                            # Quay lại menu khi nhấn ESC ở màn hình chọn level
                            self.state = "menu"
                        else:
                            self.state = "menu"
                if event.type == pygame.MOUSEBUTTONUP:
                    # Khi thả chuột, đảm bảo dừng việc kéo cả hai thanh trượt
                    self.dragging_slider = False
                    self.dragging_effect_slider = False

            # Vẽ background
            self.screen.blit(self.background, (0, 0))
            
            # Cập nhật và vẽ đám mây
            self.update_clouds(delta_time)
            
            # Vẽ UI theo trạng thái game
            if self.state == "menu":
                self.draw_menu()
                # Đảm bảo nhạc menu đang phát khi ở màn hình menu
                if self.menu_music and not self.music_playing:
                    self.menu_music.play(-1)
                    self.music_playing = True
            elif self.state == "level_select":
                self.draw_level_select(self.score_rs)
            elif self.state == "game":
                # Dừng nhạc menu khi vào game
                if self.menu_music and self.music_playing:
                    self.menu_music.stop()
                    self.music_playing = False
                
                # Sử dụng level đã pre-load nếu có
                if self.preloaded_level and self.current_level >= 1:
                    # Chạy level1 và nhận kết quả
                    return_to_select_level, score_tmp, check_continue = self.preloaded_level.run_level(self.screen, self.screen_width, self.screen_height)
                    if score_tmp != 0:
                        if self.score_rs[self.current_level-1] < score_tmp:
                            self.score_rs[self.current_level-1] = score_tmp
                        self.current_level += 1
                        if self.unlocked_levels.count(self.current_level) == 0: self.unlocked_levels.append(self.current_level)
                    if check_continue:
                        if self.current_level == 1:
                            import levels.level1 as level1
                            self.preloaded_level = level1
                        elif self.current_level == 2:
                            import levels.level2 as level2
                            self.preloaded_level = level2
                        elif self.current_level == 3:
                            import levels.level3 as level3
                            self.preloaded_level = level3
                        elif self.current_level == 4:
                            import levels.level4 as level4
                            self.preloaded_level = level4
                        elif self.current_level == 5:
                            import levels.level5 as level5
                            self.preloaded_level = level5
                        elif self.current_level == 6:
                            import levels.level6 as level6
                            self.preloaded_level = level6    
                        self.show_loading_screen()
                        self.state = "game"
                    if return_to_select_level:
                        # Quay về menu
                        self.state = "level_select"
                        # Phát lại nhạc menu
                        if self.menu_music and not self.music_playing:
                            self.menu_music.play(-1)
                            self.music_playing = True
                        # Reset pre-loaded level
                        self.preloaded_level = None
                else:
                    # Đoạn mã này sẽ được thực thi nếu chưa có level tương ứng
                    font = pygame.font.Font(None, 72)
                    game_text = font.render(f"MÀN CHƠI {self.current_level}", True, self.white)
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
            elif self.state == "setting":
                self.draw_setting()
            elif self.state == "leaderboard":
                self.draw_leaderboard()
            
            # Hiển thị hộp thoại xác nhận thoát nếu cần
            if self.show_quit_dialog:
                self.draw_quit_dialog()

            pygame.display.update()
            self.clock.tick(self.fps)
            
if __name__ == "__main__":
    Game().run()