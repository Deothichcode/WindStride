import pygame # type: ignore
import pickle
from os import path, makedirs

# Create levels data directory if it doesn't exist
level_data_dir = 'levels/level.data'
if not path.exists(level_data_dir):
	makedirs(level_data_dir)

pygame.init()

clock = pygame.time.Clock()
fps = 60

#game window
tile_size = 60
cols = 20
rows = 12  # 700/60 = ~11.7, so we use 12 rows
screen_width = 1200  # Match game dimensions
screen_height = 700  # Match game dimensions

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('WindStride Level Editor')

try:
	logo = pygame.image.load('assests/gui/PNG/menu/LogoWindStride.png').convert_alpha()
	logo = pygame.transform.scale(logo, (32, 32))
	pygame.display.set_icon(logo)
except pygame.error:
	print("Không thể tải icon!")

#load images
bg_img = pygame.image.load('assests/background/PNG/game_background_2/game_background_2.png')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))
# Ground tile
ground_img = pygame.image.load('assests/tileset/Forest Tileset/1 Tiles/Tile_12.png')
# Other tiles
dirt_img = pygame.image.load('assests/tileset/Forest Tileset/1 Tiles/Tile_02.png')
grass_img = pygame.image.load('assests/objects/Plant Animations/Plant 1/Plant1_00000.png')
plant2_img = pygame.image.load('assests/objects/Plant Animations/Plant 2/Plant2_00000.png')
plant3_img = pygame.image.load('assests/objects/Plant Animations/Plant 3/Plant3_00000.png')
plant4_img = pygame.image.load('assests/objects/Plant Animations/Plant 4/Plant4_00000.png') if path.exists('assests/objects/Plant Animations/Plant 4/Plant4_00000.png') else grass_img
plant5_img = pygame.image.load('assests/objects/Plant Animations/Plant 5/Plant5_00000.png') if path.exists('assests/objects/Plant Animations/Plant 5/Plant5_00000.png') else grass_img
plant6_img = pygame.image.load('assests/objects/Plant Animations/Plant 6/Plant6_00000.png') if path.exists('assests/objects/Plant Animations/Plant 6/Plant6_00000.png') else grass_img
# Blue flowers
blue_flower1_img = pygame.image.load('assests/objects/Plant Animations/BlueFlower1/BlueFlower_00000.png')
blue_flower2_img = pygame.image.load('assests/objects/Plant Animations/BlueFlower2/BluePlantClosed_00000.png')
#creep
blue_slime_img = pygame.image.load('assests/objects/Creep/Blue_Slime/idle/1.png')
green_slime_img = pygame.image.load('assests/objects/Creep/Green_Slime/idle/1.png')
skeleton_img = pygame.image.load('assests/objects/Creep/Skeleton/idle/1.png')
#others
platform_x_img = pygame.image.load('assests/tileset/Forest Tileset/1 Tiles/Tile_08.png')
lava_img = pygame.image.load('assests/tileset/Forest Tileset/1 Tiles/Tile_20.png')
coin_img = pygame.image.load('assests/objects/Item/coin/1.png')
rune_img = pygame.image.load('assests/objects/Item/rune/1.png')
exit_img = pygame.image.load('assests/objects/Item/flag/1.png')

# Button images
save_img = pygame.image.load('assests/gui/PNG/btn/ok.png')
cancel_img = pygame.image.load('assests/gui/PNG/btn/close.png')
up_img = pygame.image.load('assests/gui/PNG/btn/next.png')
down_img = pygame.image.load('assests/gui/PNG/btn/prew.png')

# Scale button images
save_img = pygame.transform.scale(save_img, (40, 40))
cancel_img = pygame.transform.scale(cancel_img, (40, 40))
up_img = pygame.transform.scale(up_img, (30, 30))
down_img = pygame.transform.scale(down_img, (30, 30))

#define game variables
clicked = False
level = 1

#define colours
white = (255, 255, 255)
green = (144, 201, 120)
red = (200, 50, 50)
blue = (50, 50, 200)

font = pygame.font.SysFont('Futura', 24)

#create empty tile list
world_data = []
for row in range(rows):
	r = [0] * cols
	world_data.append(r)

# Add ground tiles at the bottom
for tile in range(cols):
	world_data[rows-1][tile] = 1

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_grid():
	# Draw vertical lines
	for c in range(cols + 1):
		pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, rows * tile_size))
	# Draw horizontal lines
	for r in range(rows + 1):
		pygame.draw.line(screen, white, (0, r * tile_size), (cols * tile_size, r * tile_size))


def draw_world():
	for row in range(rows):
		for col in range(cols):
			if world_data[row][col] > 0:
				if world_data[row][col] == 1:
					# Ground blocks (Tile_12)
					img = pygame.transform.scale(ground_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 2:
					# Dirt blocks
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 3:
					# Plant1 - scaled 1.5x larger
					img = pygame.transform.scale(grass_img, (tile_size*3, tile_size*3))
					screen.blit(img, (col * tile_size - tile_size, row * tile_size - tile_size + 6))
				if world_data[row][col] == 5:
					# Blue slime enemy - scaled 3x larger
					img = pygame.transform.scale(blue_slime_img, (int(tile_size * 0.6), int(tile_size * 0.6)))
					screen.blit(img, (col * tile_size + 15, row * tile_size + 26))
				if world_data[row][col] == 6:
					# Horizontally moving platform - at top of tile
					img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 2.5))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 17:
					# Platform at bottom of tile
					img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 2.5))
					screen.blit(img, (col * tile_size, row * tile_size + tile_size // 2 + 5))
				if world_data[row][col] == 8:
					
					img = pygame.transform.scale(lava_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size // 2)))
				if world_data[row][col] == 9:
					# Coin - scaled 1.5x larger
					img = pygame.transform.scale(coin_img, (int(tile_size * 0.5), int(tile_size * 0.5)))
					# Center coin in its grid cell
					coin_x = col * tile_size + (tile_size - int(tile_size * 0.5)) // 2
					coin_y = row * tile_size + (tile_size - int(tile_size * 0.5)) // 2
					screen.blit(img, (coin_x, coin_y))
				if world_data[row][col] == 10:
					# Exit - scaled 1.5x larger
					img = pygame.transform.scale(exit_img, (int(tile_size*1.5), int(tile_size * 2.25)))
					screen.blit(img, (col * tile_size - tile_size//4, row * tile_size - (tile_size * 0.75)))
				# New plants
				if world_data[row][col] == 11:
					# Plant2 - scaled 1.5x larger
					img = pygame.transform.scale(plant2_img, (tile_size*3, tile_size*3))
					screen.blit(img, (col * tile_size - tile_size, row * tile_size - tile_size + 6))
				if world_data[row][col] == 12:
					# Plant3 - scaled 1.5x larger
					img = pygame.transform.scale(plant3_img, (tile_size*3, tile_size*3))
					screen.blit(img, (col * tile_size - tile_size, row * tile_size - tile_size + 6))
				if world_data[row][col] == 13:
					# Plant4 - scaled 1.5x larger
					img = pygame.transform.scale(plant4_img, (tile_size*3, tile_size*3))
					screen.blit(img, (col * tile_size - tile_size, row * tile_size - tile_size + 6))
				if world_data[row][col] == 14:
					# Plant5 - scaled 1.5x larger
					img = pygame.transform.scale(plant5_img, (tile_size*3, tile_size*3))
					screen.blit(img, (col * tile_size - tile_size, row * tile_size - tile_size + 6))
				if world_data[row][col] == 15:
					# Plant6 - scaled 1.5x larger
					img = pygame.transform.scale(plant6_img, (tile_size*3, tile_size*3))
					screen.blit(img, (col * tile_size - tile_size, row * tile_size - tile_size + 6))
				# Blue Flowers
				if world_data[row][col] == 18:
					# BlueFlower1 - scaled 1.5x larger
					img = pygame.transform.scale(blue_flower1_img, (tile_size*3, tile_size*3))
					screen.blit(img, (col * tile_size - tile_size, row * tile_size - tile_size + 6))
				if world_data[row][col] == 19:
					# BlueFlower2 - scaled 1.5x larger
					img = pygame.transform.scale(blue_flower2_img, (tile_size*3, tile_size*3))
					screen.blit(img, (col * tile_size - tile_size, row * tile_size - tile_size + 6))
				if world_data[row][col] == 16:
					# Rune - centered in tile
					img = pygame.transform.scale(rune_img, (int(tile_size * 0.5), int(tile_size * 0.5)))
					# Center rune in its grid cell
					rune_x = col * tile_size + (tile_size - int(tile_size * 0.5)) // 2
					rune_y = row * tile_size + (tile_size - int(tile_size * 0.5)) // 2
					screen.blit(img, (rune_x, rune_y))
				if world_data[row][col] == 20:
					# Green slime enemy - scaled to fit one tile
					img = pygame.transform.scale(green_slime_img, (tile_size*0.6, tile_size*0.6))
					screen.blit(img, (col * tile_size + 15, row * tile_size + 26))
				if world_data[row][col] == 21:
					# Skeleton - scaled to fit one tile
					img = pygame.transform.scale(skeleton_img, (tile_size*0.8, tile_size*1.3))
					screen.blit(img, (col * tile_size + 6, row * tile_size - 17))
class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self):
		action = False

		# Get mouse position
		pos = pygame.mouse.get_pos()

		# Check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		# Draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action

# Create buttons
save_button = Button(cols * tile_size - 150, (rows-1) * tile_size + 10, save_img)
cancel_button = Button(cols * tile_size - 80, (rows-1) * tile_size + 10, cancel_img)
level_up_button = Button(130, (rows-1) * tile_size + 10, up_img)
level_down_button = Button(80, (rows-1) * tile_size + 10, down_img)

# Function to initialize or reset level data
def reset_level():
	data = []
	for row in range(rows):
		r = [0] * cols
		data.append(r)
	
	# Add ground tiles at the bottom
	for tile in range(cols):
		data[rows-1][tile] = 1
		
	return data

# Function to load level data
def load_level(level):
	# Get path to level data file in the specific folder
	level_file = path.join(level_data_dir, f'level{level}_data')
	if path.exists(level_file):
		pickle_in = open(level_file, 'rb')
		data = pickle.load(pickle_in)
		print(f"Loaded level {level}")
		return data
	else:
		print(f"Level {level} not found, creating new")
		return reset_level()

# Initialize world_data for current level
world_data = load_level(level)

# Main game loop
run = True
while run:

	clock.tick(fps)

	# Draw background
	screen.blit(bg_img, (0, 0))

	# Show the grid and draw the level tiles
	draw_grid()
	draw_world()

	# Text showing current level and instructions
	draw_text(f'Level: {level}', font, white, 10, (rows-1) * tile_size + 10)
	
	# Draw level navigation buttons
	if level_up_button.draw():
		level += 1
		print(f"Changed to level {level}")
		world_data = load_level(level)
	
	if level_down_button.draw() and level > 1:
		level -= 1
		print(f"Changed to level {level}")
		world_data = load_level(level)
	
	# Draw save & cancel buttons
	if save_button.draw():
		# Save level data to the specific folder
		level_file = path.join(level_data_dir, f'level{level}_data')
		pickle_out = open(level_file, 'wb')
		pickle.dump(world_data, pickle_out)
		pickle_out.close()
		print(f"Saved level {level} to {level_file}")
	
	if cancel_button.draw():
		# Reload level or clear if no file exists
		world_data = load_level(level)
	
	# Draw instructions
	draw_text('LMB: Place/Cycle Tiles  |  RMB: Remove Tiles', font, white, 200, (rows-1) * tile_size + 10)

	# Event handler
	for event in pygame.event.get():
		# Quit game
		if event.type == pygame.QUIT:
			run = False
		# Mouseclicks to change tiles
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
			pos = pygame.mouse.get_pos()
			x = pos[0] // tile_size
			y = pos[1] // tile_size
			# Check that the coordinates are within the tile area
			if x < cols and y < rows:
				# Update tile value
				if pygame.mouse.get_pressed()[0] == 1:
					# Don't change the bottom row tiles
					if y == rows - 1:
						continue
					world_data[y][x] += 1
					# Skip values 4 (green slime) and 7 (platform_y)
					if world_data[y][x] == 4:
						world_data[y][x] = 5
					if world_data[y][x] == 7:
						world_data[y][x] = 8
					if world_data[y][x] > 22:
						world_data[y][x] = 0
				elif pygame.mouse.get_pressed()[2] == 1:
					# Don't change the bottom row tiles
					if y == rows - 1:
						continue
					world_data[y][x] = 0
		if event.type == pygame.MOUSEBUTTONUP:
			clicked = False
		# Key presses
		if event.type == pygame.KEYDOWN:
			# Load level data with L key
			if event.key == pygame.K_l:
				if path.exists(f'level{level}_data'):
					pickle_in = open(f'level{level}_data', 'rb')
					world_data = pickle.load(pickle_in)
					print(f"Đã tải level {level}")
				else:
					print(f"Không tìm thấy level {level}")

	# Update game display window
	pygame.display.update()

pygame.quit()