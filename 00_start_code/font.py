import pygame


def display_text(screen, text, font_size, font_color, position, fadeout_duration=2000):
    font = pygame.font.Font('../graphics/ui/Lyusung-210618.ttf', font_size)
    text_surface = font.render(text, True, font_color)
    text_rect = text_surface.get_rect()
    text_rect.center = position

    start_time = pygame.time.get_ticks()  # 记录开始时间

    running = True
    while running:

        # 计算时间差，计算透明度
        elapsed_time = pygame.time.get_ticks() - start_time
        if elapsed_time >= fadeout_duration:
            alpha = 0  # 完全隐藏文字
            running = False
        else:
            alpha = int(255 - (elapsed_time / fadeout_duration) * 255)

        # 设置文字透明度
        text_surface.set_alpha(alpha)

        screen.blit(text_surface, text_rect)  # 绘制带透明度的文字

        pygame.display.flip()
        pygame.time.Clock().tick(60)
