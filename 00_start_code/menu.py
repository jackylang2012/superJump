import pygame
from pygame.image import load
from main import *

from settings import *


class Menu:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.create_data()
        self.create_buttons()

    def create_data(self):
        self.menu_surfs = {}
        for key, value in EDITOR_DATA.items():
            if value['menu']:
                if not value['menu'] in self.menu_surfs:
                    self.menu_surfs[value['menu']] = [(key, load(value['menu_surf']))]
                else:
                    self.menu_surfs[value['menu']].append((key, load(value['menu_surf'])))

    def create_buttons(self):

        # menu area
        size = 180
        margin = 6
        topleft = (WINDOW_WIDTH - size - margin, WINDOW_HEIGHT - size - margin)
        self.rect = pygame.Rect(topleft, (size, size))

        # button areas
        generic_button_rect = pygame.Rect(self.rect.topleft, (self.rect.width / 2, self.rect.height / 2))
        button_margin = 5
        self.tile_button_rect = generic_button_rect.copy().inflate(-button_margin, -button_margin)
        self.coin_button_rect = generic_button_rect.move(self.rect.height / 2, 0).inflate(-button_margin,
                                                                                          -button_margin)
        self.enemy_button_rect = generic_button_rect.move(self.rect.height / 2, self.rect.width / 2).inflate(
            -button_margin, -button_margin)
        self.palm_button_rect = generic_button_rect.move(0, self.rect.width / 2).inflate(-button_margin, -button_margin)

        # create the buttons
        self.buttons = pygame.sprite.Group()
        Button(self.tile_button_rect, self.buttons, self.menu_surfs['terrain'])
        Button(self.coin_button_rect, self.buttons, self.menu_surfs['coin'])
        Button(self.enemy_button_rect, self.buttons, self.menu_surfs['enemy'])
        Button(self.palm_button_rect, self.buttons, self.menu_surfs['palm fg'], self.menu_surfs['palm bg'])

    def click(self, mouse_pos, mouse_button):
        for sprite in self.buttons:
            if sprite.rect.collidepoint(mouse_pos):
                if mouse_button[1]:  # middle mouse click
                    if sprite.items['alt']:
                        sprite.main_active = not sprite.main_active
                if mouse_button[2]:  # right click
                    sprite.switch()
                return sprite.get_id()

    def highlight_indicator(self, index):
        if EDITOR_DATA[index]['menu'] == 'terrain':
            pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.tile_button_rect.inflate(4, 4), 5, 4)
        if EDITOR_DATA[index]['menu'] == 'coin':
            pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.coin_button_rect.inflate(4, 4), 5, 4)
        if EDITOR_DATA[index]['menu'] == 'enemy':
            pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.enemy_button_rect.inflate(4, 4), 5, 4)
        if EDITOR_DATA[index]['menu'] in ('palm bg', 'palm fg'):
            pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.palm_button_rect.inflate(4, 4), 5, 4)

    def display(self, index):
        self.buttons.update()
        self.buttons.draw(self.display_surface)

        # 在屏幕左上角显示导入和保存图标
        for button in self.buttons:
            button.draw_icons(self.display_surface)
            button.draw_share_icon(self.display_surface, 75, 75)

        self.highlight_indicator(index)


class Button(pygame.sprite.Sprite):
    active = False
    load_ie = False
    # can new an object/F is can't new an object
    can_click = True
    share = False

    def __init__(self, rect, group, items, items_alt=None):
        super().__init__(group)
        self.image = pygame.Surface(rect.size)
        self.rect = rect

        # items
        self.items = {'main': items, 'alt': items_alt}
        self.index = 0
        self.main_active = True

        # 加载图标图片
        self.import_pic = pygame.image.load("../graphics/start_menu/load (2).png").convert_alpha()  # 导入出市导入图片
        self.save_pic = pygame.image.load("../graphics/start_menu/save1.png").convert_alpha()  # 导入初始保存图片
        self.share_pic = pygame.image.load("../graphics/start_menu/share_pic.png").convert_alpha()  # 导入初始分享图片

        # Load button sounds
        self.button_sound = pygame.mixer.Sound('../audio/Click button.wav')
        self.button_sound.set_volume(0.3)

        # 将图片缩放到所需大小
        icon_width = 66  # 使用按钮宽度的一半作为图标的宽度
        icon_height = 33  # 使用按钮高度的一半作为图标的高度
        self.import_pic = pygame.transform.scale(self.import_pic, (icon_width, icon_height))
        self.save_pic = pygame.transform.scale(self.save_pic, (icon_width, icon_height))

        # 记录上一次的鼠标点击状态，初始为False表示未被点击
        self.last_mouse_pressed = False

    def get_id(self):
        return self.items['main' if self.main_active else 'alt'][self.index][0]

    def switch(self):
        self.index += 1
        self.index = 0 if self.index >= len(self.items['main' if self.main_active else 'alt']) else self.index

    def get_icon_position(self, icon):
        # 将图标垂直居中放置在按钮的左上角
        # 将图标居中放置在按钮的右下角，并留有一些空隙
        x = (self.rect.width + icon.get_width()) * 8
        y = 450
        return x, y

    def draw_icons(self, display_surface):
        # 绘制导入图标
        import_pos = self.get_icon_position(self.import_pic)
        display_surface.blit(self.import_pic, import_pos)

        # 绘制保存图标
        save_pos = self.get_icon_position(self.save_pic)
        save_pos = (save_pos[0], save_pos[1] + self.rect.height // 2)  # 将保存图标位置下移一半按钮高度
        display_surface.blit(self.save_pic, save_pos)

    def draw_share_icon(self, display_surface, new_width, new_height):
        self.share_pic = pygame.transform.scale(self.share_pic, (new_width, new_height))
        x = (self.rect.width + self.share_pic.get_width()) * 7.5
        share_pos = (x, -5)  # Position for the top-left corner
        display_surface.blit(self.share_pic, share_pos)

    def update(self):
        self.image.fill(BUTTON_BG_COLOR)
        surf = self.items['main' if self.main_active else 'alt'][self.index][1]
        rect = surf.get_rect(center=(self.rect.width / 2, self.rect.height / 2))
        self.image.blit(surf, rect)

        # 检查当前鼠标点击状态
        mouse_pressed = pygame.mouse.get_pressed()[0]

        # 检查鼠标点击事件是否发生在导入图标上，并处理相应的内容
        mouse_pos = pygame.mouse.get_pos()
        import_pos = self.get_icon_position(self.import_pic)
        import_rect = pygame.Rect(import_pos, self.import_pic.get_size())

        if import_rect.collidepoint(mouse_pos):
            self.import_pic = pygame.image.load("../graphics/start_menu/load (1).png").convert_alpha()
            Button.can_click = False
            if mouse_pressed and not self.last_mouse_pressed:
                self.button_sound.play()
                self.import_pic = pygame.image.load("../graphics/start_menu/load (3).png").convert_alpha()
                Button.load_ie = True
                Button.can_click = False
        else:
            self.import_pic = pygame.image.load("../graphics/start_menu/load (2).png").convert_alpha()
            Button.load_ie = False
            Button.can_click = True

        # 检查鼠标点击事件是否发生在保存图标上，并处理相应的内容
        save_pos = self.get_icon_position(self.save_pic)
        save_pos = (save_pos[0], save_pos[1] + self.rect.height // 2 + 10)
        save_rect = pygame.Rect(save_pos, self.save_pic.get_size())

        if save_rect.collidepoint(mouse_pos):
            self.save_pic = pygame.image.load('../graphics/start_menu/save2.png').convert_alpha()
            Button.can_click = False
            if mouse_pressed and not self.last_mouse_pressed:
                self.button_sound.play()
                self.save_pic = pygame.image.load('../graphics/start_menu/save.png').convert_alpha()
                Button.active = True
                Button.can_click = False
        else:
            self.save_pic = pygame.image.load("../graphics/start_menu/save1.png").convert_alpha()
            Button.active = False
            Button.can_click = True

        x = (self.rect.width + self.share_pic.get_width()) * 7.5
        share_pos = (x, -5)  # Position for the top-left corner
        share_rect = pygame.Rect(share_pos, self.share_pic.get_size())

        if share_rect.collidepoint(mouse_pos):
            Button.can_click = False
            if mouse_pressed and not self.last_mouse_pressed:
                self.button_sound.play()
                Button.share = True
                Button.can_click = False

        else:
            Button.share = False
            Button.can_click = True

        # 更新上一次的鼠标点击状态
        self.last_mouse_pressed = mouse_pressed
