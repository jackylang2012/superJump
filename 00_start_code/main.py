import threading
from random import choice, randint

import pygame
import django
from pygame.math import Vector2 as vector
from settings import *
from support import *

from pygame.image import load

from editor import Editor
from level import Level

from os import walk
from sprites import Player
from start_menu import StartMenu


class Singleton(object):
    _instance_lock = threading.Lock()

    def __init__(self, cls):
        self._cls = cls
        self.uniqueInstance = None

    def __call__(self):
        if self.uniqueInstance is None:
            with self._instance_lock:
                if self.uniqueInstance is None:
                    self.uniqueInstance = self._cls()
        return self.uniqueInstance


# @Singleton
class Main:
    menu_ie = True
    music_ie = 0

    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.imports()

        self.editor_active = False
        self.transition = Transition(self.toggle)
        self.editor = Editor(self.land_tiles, self.switch)
        self.menu_ = StartMenu()

        # cursor
        surf = load('../graphics/cursors/mouse.png').convert_alpha()
        cursor = pygame.cursors.Cursor((0, 0), surf)
        pygame.mouse.set_cursor(cursor)

        self.level = None

    def imports(self):
        # terrain
        self.land_tiles = import_folder_dict('../graphics/terrain/land')
        self.water_bottom = load('../graphics/terrain/water/water_bottom.png').convert_alpha()
        self.water_top_animation = import_folder('../graphics/terrain/water/animation')

        # coins
        self.gold = import_folder('../graphics/items/gold')
        self.silver = import_folder('../graphics/items/silver')
        self.diamond = import_folder('../graphics/items/diamond')
        self.particle = import_folder('../graphics/items/particle')

        # palm trees
        self.palms = {folder: import_folder(f'../graphics/terrain/palm/{folder}') for folder in
                      list(walk('../graphics/terrain/palm'))[0][1]}

        # enemies
        self.spikes = load('../graphics/enemies/spikes/spikes.png').convert_alpha()
        self.tooth = {folder: import_folder(f'../graphics/enemies/tooth/{folder}') for folder in
                      list(walk('../graphics/enemies/tooth'))[0][1]}
        self.shell = {folder: import_folder(f'../graphics/enemies/shell_left/{folder}') for folder in
                      list(walk('../graphics/enemies/shell_left/'))[0][1]}
        self.pearl = load('../graphics/enemies/pearl/pearl.png').convert_alpha()

        # player
        self.player_graphics = {folder: import_folder(f'../graphics/player/{folder}') for folder in
                                list(walk('../graphics/player/'))[0][1]}

        self.clouds = import_folder('../graphics/clouds')

        self.level_sounds = {
            'coin': pygame.mixer.Sound('../audio/coin.wav'),
            'hit': pygame.mixer.Sound('../audio/hit.wav'),
            'jump': pygame.mixer.Sound('../audio/jump.wav'),
            'stomp': pygame.mixer.Sound('../audio/smb_stomp.wav'),
            'music': pygame.mixer.Sound('../audio/SuperHero.ogg'),
            'music1': pygame.mixer.Sound('../audio/EGGSTREME DUCK PHONK.mp3'),
            'music2': pygame.mixer.Sound('../audio/Dream Speedrun Music.mp3')
        }

    def toggle(self):
        self.editor_active = not self.editor_active
        if self.editor_active:
            if randint(1, 2) == 1:
                self.editor.editor_music.play()
            else:
                self.editor.editor_music1.play()

    def switch(self, grid=None):
        self.transition.active = True
        Player.xue = 10
        if grid:
            self.level = Level(
                grid,
                self.switch, {
                    'land': self.land_tiles,
                    'water bottom': self.water_bottom,
                    'water top': self.water_top_animation,
                    'gold': self.gold,
                    'silver': self.silver,
                    'diamond': self.diamond,
                    'particle': self.particle,
                    'palms': self.palms,
                    'spikes': self.spikes,
                    'tooth': self.tooth,
                    'shell': self.shell,
                    'player': self.player_graphics,
                    'pearl': self.pearl,
                    'clouds': self.clouds, },
                self.level_sounds)

    def run(self):
        if not self.menu_ie:
            self.editor_active = True
            while True:
                dt = self.clock.tick() / 1000
                if self.editor_active:
                    self.editor.run(dt)
                elif self.level is not None:
                    self.level.run(dt)
                self.transition.display(dt)
                pygame.display.update()
        else:
            start_menu = StartMenu()
            start_menu.run()


class Transition:
    def __init__(self, toggle):
        self.display_surface = pygame.display.get_surface()
        self.toggle = toggle
        self.active = False

        self.border_width = 0
        self.direction = 1
        self.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.radius = vector(self.center).magnitude()
        self.threshold = self.radius + 100

    def display(self, dt):
        if self.active:
            self.border_width += 1000 * dt * self.direction
            if self.border_width >= self.threshold:
                self.direction = -1
                self.toggle()

            if self.border_width < 0:
                self.active = False
                self.border_width = 0
                self.direction = 1
            pygame.draw.circle(self.display_surface, 'black', self.center, self.radius, int(self.border_width))


if __name__ == '__main__':
    main = Main()
    main.run()
