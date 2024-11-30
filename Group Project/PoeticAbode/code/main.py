import pygame
import sys
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from dotenv import load_dotenv
import os
from pathlib import Path
from openai import OpenAI

# 获取当前脚本所在的文件夹
this_folder = Path(__file__).parent

# 加载 .env 文件
load_dotenv(this_folder / ".env")

# 获取 API 密钥
api_key = os.getenv("GITHUB_TOKEN")
print(f"API Key: {api_key}")

# 设置 OpenAI 客户端配置
#openai.api_key = api_key
# openai.api_base = "https://models.inference.ai.azure.com"

# 检查 API 密钥是否加载成功
if api_key:
    print("GitHub Token loaded successfully.")
else:
    print("GitHub Token is not set. Please check your .env file.")
    exit(1)

# 调试：打印当前工作目录和目录中的文件
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir()}")

# 初始化 Pygame
pygame.init()
pygame.font.init()

# 窗口设置
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 768
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Poetic Abode")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DREAMY_PINK = (255, 182, 193)
DREAMY_PURPLE = (216, 191, 216)
DREAMY_BLUE = (173, 216, 230)

# 字体设置
FONT_SMALL = pygame.font.SysFont('Arial', 18)
FONT_MEDIUM = pygame.font.SysFont('Arial', 24)
FONT_LARGE = pygame.font.SysFont('Arial', 36)
FONT_TITLE = pygame.font.SysFont('Arial', 72)
FONT_POEM = pygame.font.SysFont('Arial', 32)  # 英文字体

# 加载音效
drag_sound = pygame.mixer.Sound("sounds/27976__timkahn__sticker-peel.flac")  # 请确保音频文件在项目文件夹中

# 加载图标
icon_size = (60, 60)
sticker_icon = pygame.transform.scale(pygame.image.load("icon/icon_room.png"), icon_size)
save_icon = pygame.transform.scale(pygame.image.load("icon/icon_music.png"), icon_size)
music_icon = pygame.transform.scale(pygame.image.load("icon/icon_music.png"), icon_size)  # 单一音乐按钮图标
back_icon = pygame.transform.scale(pygame.image.load("icon/icon_back.png"), icon_size)  # 返回按钮图标

# 按钮类
class IconButton:
    def __init__(self, x, y, icon, text):
        self.rect = pygame.Rect(x, y, icon_size[0], icon_size[1])
        self.icon = icon
        self.text = text
        self.text_surface = FONT_SMALL.render(text, True, DREAMY_PINK)
        self.text_rect = self.text_surface.get_rect(center=(x + icon_size[0] // 2, y + icon_size[1] + 15))

    def draw(self, surface):
        surface.blit(self.icon, self.rect.topleft)
        surface.blit(self.text_surface, self.text_rect)

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)

# 图像按钮类
class ImageButton:
    def __init__(self, x, y, image, text=''):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.text = text
        if text:
            self.text_surface = FONT_SMALL.render(text, True, WHITE)
            self.text_rect = self.text_surface.get_rect(center=(self.rect.centerx, self.rect.bottom + 15))
        else:
            self.text_surface = None
            self.text_rect = None

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        if self.text_surface:
            surface.blit(self.text_surface, self.text_rect)

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)

# 贴纸类
class Sticker:
    def __init__(self, image_path, position):
        self.image_path = image_path  # 存储图像路径
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(topleft=position)
        self.dragging = False

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

# 贴纸选择栏类
class StickerSelectionBar:
    def __init__(self, stickers, width, height):
        self.stickers = stickers  # 贴纸列表
        self.width = width
        self.height = height
        self.surface = pygame.Surface((self.width, self.height))
        self.rect = pygame.Rect(WINDOW_WIDTH - self.width, 0, self.width, self.height)
        self.scroll_y = 0
        self.sticker_spacing = 10
        self.sticker_size = 80  # 贴纸显示大小

        # 垂直排列贴纸
        for idx, sticker in enumerate(self.stickers):
            sticker.image = pygame.transform.scale(sticker.image, (self.sticker_size, self.sticker_size))
            sticker.rect = sticker.image.get_rect()
            sticker.rect.topleft = (10, idx * (self.sticker_size + self.sticker_spacing))

        # 所有贴纸的总高度
        self.content_height = len(self.stickers) * (self.sticker_size + self.sticker_spacing)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 检查点击是否在选择栏内
            if self.rect.collidepoint(event.pos):
                x, y = event.pos
                x -= self.rect.left
                y += self.scroll_y - self.rect.top  # 考虑滚动偏移
                for sticker in self.stickers:
                    if sticker.rect.collidepoint((x, y)):
                        # 返回被点击的贴纸
                        return sticker
        elif event.type == pygame.MOUSEWHEEL:
            # 滚动上下移动
            self.scroll_y -= event.y * 20  # 调整滚动速度
            # 限制滚动范围
            max_scroll = max(self.content_height - self.height, 0)
            self.scroll_y = max(0, min(self.scroll_y, max_scroll))
        return None

    def draw(self, surface):
        # 清空选择栏表面
        self.surface.fill(DREAMY_BLUE)

        # 创建一个新的 Surface，用于绘制所有贴纸
        content_surface = pygame.Surface((self.width, self.content_height))
        content_surface.fill(DREAMY_BLUE)

        # 绘制贴纸到 content_surface
        for sticker in self.stickers:
            content_surface.blit(sticker.image, sticker.rect.topleft)

        # 创建一个裁剪区域，用于滚动效果
        clip_rect = pygame.Rect(0, self.scroll_y, self.width, self.height)

        # 将 content_surface 的一部分（根据 scroll_y）绘制到选择栏表面
        self.surface.blit(content_surface, (0, 0), area=clip_rect)

        # 将选择栏表面绘制到主屏幕上
        surface.blit(self.surface, self.rect.topleft)

# 主菜单类
class MainMenu:
    def __init__(self):
        self.title_font = FONT_TITLE
        self.button_font = FONT_LARGE

        # 加载背景图片
        self.background = pygame.image.load("bg/firstbg.jpg")  # 假设背景图为 "main_menu_bg.jpg"
        self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))

        self.start_button = IconButton(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, pygame.Surface((200, 50)), "Start Game")
        self.start_button.rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, 200, 50)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button.rect.collidepoint(event.pos):
                        running = False
                        return True
            screen.blit(self.background, (0, 0))  # 绘制背景图
            # 绘制开始按钮
            pygame.draw.rect(screen, DREAMY_BLUE, self.start_button.rect)
            start_text_surface = self.button_font.render("Start Game", True, WHITE)
            start_text_rect = start_text_surface.get_rect(center=self.start_button.rect.center)
            screen.blit(start_text_surface, start_text_rect)
            pygame.display.flip()

# 房间选择菜单类
class RoomSelectionMenu:
    def __init__(self):
        self.button_font = FONT_LARGE
        self.room_buttons = []
        room_names = ['Room 1', 'Room 2', 'Room 3', 'Room 4', 'Room 5', 'Room 6']

        for idx, room_name in enumerate(room_names):
            image_path = f'bg/room{idx + 1}.png'
            if os.path.exists(image_path):
                image = pygame.image.load(image_path)
                image = pygame.transform.scale(image, (200, 150))
            else:
                print(f"Room image '{image_path}' not found.")
                image = pygame.Surface((200, 150))
                image.fill(DREAMY_BLUE)

            # 计算按钮位置，排列成两行三列
            x = (idx % 3) * (WINDOW_WIDTH // 3) + (WINDOW_WIDTH // 6 - 100)
            y = (idx // 3) * 250 + WINDOW_HEIGHT // 4

            button = ImageButton(x, y, image)
            self.room_buttons.append(button)

    def run(self):
        running = True
        selected_room = None
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for idx, button in enumerate(self.room_buttons):
                        if button.is_hovered(event.pos):
                            selected_room = idx
                            running = False  # 直接进入游戏，不需要额外的按钮或确认
                            break
            screen.fill(WHITE)
            # 绘制房间按钮
            for button in self.room_buttons:
                button.draw(screen)
            pygame.display.flip()
        return selected_room

# 诗句显示界面类
class PoemDisplay:
    def __init__(self, poem):
        self.poem = poem
        # 加载并缩放背景图像
        self.background = pygame.image.load("poem_bg/poem_bg.png")
        self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.font = FONT_POEM

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        return
            screen.blit(self.background, (0, 0))
            # 渲染诗句文本
            self.render_text(self.poem, screen, 50, 100)
            pygame.display.flip()

    def render_text(self, text, surface, x, y):
        lines = []
        paragraphs = text.split('\n')
        for paragraph in paragraphs:
            words = paragraph.split(' ')
            current_line = ''
            for word in words:
                test_line = current_line + ' ' + word if current_line else word
                # 渲染当前行的文本
                text_surface = self.font.render(test_line, True, WHITE)
                # 如果当前行的宽度超过了设定的宽度，开始换行
                if text_surface.get_width() < (WINDOW_WIDTH // 2 - 50):  # 缩小宽度限制
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            # 添加空行以分隔段落
            lines.append('')

        # 移除最后一个不必要的空行
        if lines and lines[-1] == '':
            lines.pop()

        # 现在渲染每一行，动态调整字体大小
        for idx, line in enumerate(lines):
            # 获取字体的宽度和高度
            font_size = self.font.size(line)[0]
            
            # 确保font_size不为零，避免除零错误
            if font_size == 0:
                font_size = 1  # 设置为最小值，避免除零

            # 动态调整字体大小，缩小到原来大小的两倍小
            scale_factor = 0.3  # 缩小到三分之一
            if font_size > (WINDOW_WIDTH // 2 - 50):  # 缩小宽度限制
                new_font_size = int(self.font.get_height() * (WINDOW_WIDTH // 2 - 50) / font_size * scale_factor)
                self.font = pygame.font.Font(None, new_font_size)  # 重新设置字体大小

            text_surface = self.font.render(line, True, WHITE)
            text_x = WINDOW_WIDTH // 2 + 50  # 调整位置
            line_height = 30  # 缩小行间距
            surface.blit(text_surface, (text_x, y + idx * line_height))  # 调整行间距

# 主游戏类
class Game:
    def __init__(self):
        # 初始化 Pygame 和音频模块
        pygame.mixer.init()

        # 加载背景音乐
        pygame.mixer.music.load("sounds/久石让 - いつも何度でも (与你同在) (Inst_).flac")  # 请确保音频文件路径正确
        pygame.mixer.music.set_volume(0.5)  # 设置音量（0.0 到 1.0）
        pygame.mixer.music.play(-1)  # 循环播放背景音乐，-1 表示无限循环
        self.music_playing = True  # 初始状态为播放

        self.running = True
        self.stickers = []
        self.available_stickers = []
        self.selected_sticker = None
        self.buttons = []
        self.background = None  # 背景将在选择房间后加载
        global client
        #base_url = "https://models.inference.ai.azure.com"
        base_url = "http://localhost:11434/v1"
        client = OpenAI(
            base_url = base_url,
            api_key = os.getenv("GITHUB_TOKEN")
        )

        # 初始化 GPT-4o API
        #openai.api_key = os.getenv("GITHUB_TOKEN")  # 请将您的 GitHub Token 设置为环境变量 GITHUB_TOKEN
        #openai.api_base = "http://localhost:11311/v1"  # GPT-4o 的 API 端点

        # 初始化英文 BLIP 模型用于图像描述
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)

        # 加载贴纸和按钮
        self.load_stickers()
        self.create_buttons()

    def load_stickers(self):
        # 加载所有贴纸
        self.available_stickers = []
        stickers_dir = 'stickers'
        for filename in os.listdir(stickers_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(stickers_dir, filename)
                sticker = Sticker(path, (0, 0))
                self.available_stickers.append(sticker)

    def create_buttons(self):
        # 创建按钮
        self.sticker_button = IconButton(50, 50, sticker_icon, "Stickers")
        self.save_button = IconButton(150, 50, save_icon, "Save")
        self.music_button = IconButton(250, 50, music_icon, "Music")  # 添加音乐按钮
        self.back_button = IconButton(350, 50, back_icon, "Back")  # 添加返回按钮
        self.buttons = [self.sticker_button, self.save_button, self.music_button, self.back_button]

    def load_room_background(self, room_index):
        # 假设房间背景图片命名为 'room1.png', 'room2.png', 等
        background_path = f'bg/room{room_index + 1}.png'
        if os.path.exists(background_path):
            self.background = pygame.image.load(background_path)
        else:
            print(f"Background image '{background_path}' not found.")
            self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.background.fill(WHITE)

    def run(self):
        while True:
            # 主菜单
            main_menu = MainMenu()
            proceed = main_menu.run()
            if not proceed:
                break

            # 房间选择
            room_menu = RoomSelectionMenu()
            selected_room = room_menu.run()
            if selected_room is None:
                break

            # 加载房间背景
            self.load_room_background(selected_room)
            self.stickers = []  # 清空贴纸

            # 游戏主循环
            self.running = True
            while self.running:
                self.handle_events()
                self.draw()
                pygame.display.flip()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 1:
                    # 检查按钮点击
                    if self.sticker_button.is_hovered(pos):
                        self.open_sticker_menu()
                    elif self.save_button.is_hovered(pos):
                        self.save_canvas()
                    elif self.music_button.is_hovered(pos):
                        # 控制音乐播放和暂停
                        if self.music_playing:
                            pygame.mixer.music.pause()
                            self.music_playing = False
                        else:
                            pygame.mixer.music.unpause()
                            self.music_playing = True
                    elif self.back_button.is_hovered(pos):
                        # 返回主页
                        self.running = False
                        return
                    else:
                        # 检查是否点击到贴纸
                        for sticker in reversed(self.stickers):
                            if sticker.rect.collidepoint(pos):
                                sticker.dragging = True
                                self.selected_sticker = sticker
                                drag_sound.play()
                                break
                elif event.button == 3:
                    # 右键删除贴纸
                    for sticker in self.stickers:
                        if sticker.rect.collidepoint(pos):
                            self.stickers.remove(sticker)
                            break
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.selected_sticker:
                    self.selected_sticker.dragging = False
                    self.selected_sticker = None
            elif event.type == pygame.MOUSEMOTION:
                if self.selected_sticker and self.selected_sticker.dragging:
                    self.selected_sticker.rect.move_ip(event.rel)

    def draw(self):
        screen.fill(WHITE)
        screen.blit(self.background, (0, 0))  # 绘制房间背景

        # 绘制贴纸
        for sticker in self.stickers:
            sticker.draw(screen)

        # 绘制按钮
        for button in self.buttons:
            button.draw(screen)

    def open_sticker_menu(self):
        # 创建贴纸选择栏
        selection_bar_width = WINDOW_WIDTH // 5
        selection_bar_height = WINDOW_HEIGHT
        sticker_selection_bar = StickerSelectionBar(self.available_stickers, selection_bar_width, selection_bar_height)
        selecting = True
        while selecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    selecting = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        selecting = False
                else:
                    # 传递事件给选择栏
                    selected_sticker = sticker_selection_bar.handle_event(event)
                    if selected_sticker:
                        # 添加贴纸到画布
                        pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)  # 默认位置为屏幕中心
                        new_sticker = Sticker(selected_sticker.image_path, pos)
                        self.stickers.append(new_sticker)
                        selecting = False
                        break

            # 绘制界面
            screen.fill(WHITE)
            screen.blit(self.background, (0, 0))
            for sticker in self.stickers:
                sticker.draw(screen)
            sticker_selection_bar.draw(screen)
            pygame.display.flip()

    def save_canvas(self):
        # 将当前屏幕保存为图片
        pygame.image.save(screen, "saved_artwork.png")
        print("Artwork saved as 'saved_artwork.png'")
        # 调用图像描述函数
        poem = self.image_to_text("saved_artwork.png")
        print(f"Generated Poem:\n{poem}")
        # 显示诗句界面
        poem_display = PoemDisplay(poem)
        poem_display.run()

    def image_to_text(self, image_path):
        try:
            # 使用 BLIP 模型生成图像描述
            raw_image = Image.open(image_path).convert('RGB')
            inputs = self.processor(raw_image, return_tensors="pt").to(self.device)
            out = self.model.generate(**inputs, max_new_tokens=50)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            print(f"Generated caption: {caption}")

            # 确保已设置 API 密钥
            if api_key is None:
                print("GitHub Token is not set. Please check your .env file.")
                return "抱歉，生成诗歌时出现问题。"

            # 构建提示信息
            prompt = f"Based on the following description, write a warm and healing poem in the style of Tagore, describing a person's inner world:\n\n{caption}\n\nPoem:"

            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]

            # 调用 GPT-4o 的 API
            completion = client.chat.completions.create(
                
                model="llama3.2",
                messages=messages,
                temperature=1.0,
                max_tokens=100,
            )
            print(completion)

            # 正确访问 message content
            poem = completion.choices[0].message.content.strip()
            print(f"Generated Poem:\n{poem}")
        except Exception as e:
            print(f"An error occurred: {e}")
            poem = "sorry, I was unable to generate the poem. Please try again later."

        return poem

if __name__ == "__main__":
    game = Game()
    game.run()