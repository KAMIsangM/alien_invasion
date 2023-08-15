import pygame.font
from pygame.sprite import Sprite

class Button(Sprite):
    """为游戏创建按钮的类"""

    def __init__(self, ai_game, msg):
        """初始化按钮的属性"""
        super().__init__()
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.msg = msg

        # 设置按钮颜色（开启/关闭）
        self.highlight_color = (0, 65, 0)
        self.base_color = (0, 135, 0)

        # 设置按钮的尺寸和其他属性
        self.width, self.height = 200, 50
        self.button_color = self.base_color
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 48)

        # 创建按钮的rect对象，并使其居中
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        # 按钮的标签只需创建一次
        self._prep_msg()

    def _prep_msg(self):
        """将msg渲染为图像,并使其在按钮上居中"""
        self.msg_image = self.font.render(self.msg, True, self.text_color,
                self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center =self.rect.center

    def _update_msg(self):
        """当按钮位置改变时，对应移动图像"""
        self.msg_image_rect.center = self.rect.center

    def _prep_highlight(self):
        """开启时对应深色"""
        self.button_color = self.highlight_color
        self._prep_msg()

    def _prep_base(self):
        """关闭时对应浅色（原色）"""
        self.button_color = self.base_color
        self._prep_msg()

    def draw_button(self):
        """绘制一个用颜色填充的按钮，再绘制文本"""
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)