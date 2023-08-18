import pygame
import sys
from settings import *

pygame.init()


class StartMenu:
    def __init__(self):

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        # Create game window
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        # Load background image and button images
        self.background_image = pygame.image.load("../graphics/start_menu/back.png")
        self.button_image1 = pygame.image.load("../graphics/start_menu/play.png")
        self.button_image2 = pygame.image.load("../graphics/start_menu/make.png")
        self.title_image = pygame.image.load('../graphics/start_menu/tile.png')

        # Load button sounds
        self.button_sound = pygame.mixer.Sound('../audio/Click button.wav')

        # Adjust background image size to fit the window
        self.background_image = pygame.transform.scale(self.background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

        # Button size
        self.button_width = 293
        self.button_height = 100

        self.title_width = 384
        self.title_height = 384

        # Adjust button image size to fit the window
        self.button_image1 = pygame.transform.scale(self.button_image1, (self.button_width, self.button_height))
        self.button_image2 = pygame.transform.scale(self.button_image2, (self.button_width, self.button_height))
        self.title_image = pygame.transform.scale(self.title_image, (self.title_width, self.title_height))

        # Button coordinates
        self.button1_x = 50
        self.button1_y = 400
        self.button2_x = 50
        self.button2_y = 550
        self.button3_x = 30
        self.button3_y = 0

    def change_brightness(self, image, factor):
        pixels = pygame.surfarray.pixels3d(image)
        pixels = pixels * factor
        pixels = pixels.clip(0, 255)
        return pygame.surfarray.make_surface(pixels)

    def run(self):
        button1_clicked = False
        button2_clicked = False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Draw the background
            self.screen.blit(self.background_image, (0, 0))

            # Draw black fill area
            self.screen.fill(self.BLACK, rect=(0, 0, WINDOW_WIDTH // 4 + 70, WINDOW_HEIGHT))

            self.screen.blit(self.title_image, (self.button3_x, self.button3_y))

            # Get mouse button state
            mouse_buttons = pygame.mouse.get_pressed()

            # Check if button1 is clicked
            button1_rect = pygame.Rect(self.button1_x, self.button1_y, self.button_width, self.button_height)
            if button1_rect.collidepoint(pygame.mouse.get_pos()):
                if mouse_buttons[0] and not button1_clicked:
                    self.button_sound.set_volume(3)
                    self.button_sound.play()
                    print("按钮1被点击！")
                    button1_clicked = True
                else:
                    self.screen.blit(self.change_brightness(self.button_image1, 2), (self.button1_x, self.button1_y))
            else:
                button1_clicked = False
                self.screen.blit(self.button_image1, (self.button1_x, self.button1_y))

            # Check if button2 is clicked
            button2_rect = pygame.Rect(self.button2_x, self.button2_y, self.button_width, self.button_height)
            if button2_rect.collidepoint(pygame.mouse.get_pos()):
                if mouse_buttons[0] and not button2_clicked:
                    self.button_sound.set_volume(3)
                    self.button_sound.play()
                    from main import Main
                    Main.menu_ie = False
                    main = Main()
                    main.run()
                    button2_clicked = True
                else:
                    self.screen.blit(self.change_brightness(self.button_image2, 2), (self.button2_x, self.button2_y))
            else:
                button2_clicked = False
                self.screen.blit(self.button_image2, (self.button2_x, self.button2_y))

            # Refresh display
            pygame.display.flip()


if __name__ == "__main__":
    start_menu = StartMenu()
    start_menu.run()
