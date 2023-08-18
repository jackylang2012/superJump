from font import *
import pygame, sys
from pygame.math import Vector2 as vector

from settings import *
from support import *

from sprites import Generic, Block, Animated, Particle, Coin, Player, Spikes, Tooth, Shell, Cloud
from timer import Timer
from ui import UI

from random import choice, randint

last_stomp_time = 0
clock = pygame.time.Clock()


class Level:
    def __init__(self, grid, switch, asset_dict, audio):

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.display_surface = pygame.display.get_surface()
        self.switch = switch

        # groups
        self.all_sprites = CameraGroup()
        self.coin_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.shell_sprites = pygame.sprite.Group()

        self.build_level(grid, asset_dict, audio['jump'])

        self.level_limits = {
            'left': -WINDOW_WIDTH,
            'right': None
        }

        try:
            self.level_limits['right'] = sorted(list(grid['terrain'].keys()), key=lambda pos: pos[0])[-1][0] + 500
        except TypeError as e:
            self.switch()
            # 在这里处理异常
            error_message = f"存档码错误: {e}"
            display_text(self.display_surface, error_message, 36, (0, 0, 0), (640, 50))
        except IndexError as e:
            self.switch()
            # 在这里处理异常
            error_message = f"未放置方块/土地: {e}"
            display_text(self.display_surface, error_message, 36, (0, 0, 0), (640, 50))

        # additional stuff
        self.particle_surfs = asset_dict['particle']
        self.cloud_surfs = asset_dict['clouds']
        self.cloud_timer = pygame.USEREVENT + 2
        pygame.time.set_timer(self.cloud_timer, 2000)
        self.startup_clouds()

        self.ui = UI(self.display_surface)
        self.coin_p = 0

        self.bg_music = audio['music']
        self.bg_music.set_volume(0.4)

        self.bg_music2 = audio['music1']
        self.bg_music2.set_volume(1)

        self.bg_music3 = audio['music2']
        self.bg_music3.set_volume(0.2)

        sam = randint(0, 2)

        if sam == 1:
            self.bg_music.play(loops=-1)
        elif sam == 0:
            self.bg_music2.play(loops=-1)
        else:
            self.bg_music3.play(loops=-1)

        self.coin_sound = audio['coin']
        self.coin_sound.set_volume(0.3)

        self.hit_sound = audio['hit']
        self.hit_sound.set_volume(0.3)

        self.stomp_sound = audio['stomp']

    def build_level(self, grid, asset_dict, jump_sound):
        try:
            for layer_name, layer in grid.items():
                for pos, data in layer.items():
                    Timer(100)
                    if layer_name == 'terrain':
                        Generic(pos, asset_dict['land'][data], [self.all_sprites, self.collision_sprites])
                    if layer_name == 'water':
                        if data == 'top':
                            Animated(asset_dict['water top'], pos, self.all_sprites, LEVEL_LAYERS['water'])
                        else:
                            Generic(pos, asset_dict['water bottom'], self.all_sprites, LEVEL_LAYERS['water'])

                    match data:
                        case 0:
                            self.player = Player(pos, asset_dict['player'],
                                                 self.all_sprites, self.collision_sprites, jump_sound)
                        case 1:
                            self.horizon_y = pos[1]
                            self.all_sprites.horizon_y = pos[1]

                        # coins
                        case 4:
                            Coin('gold', asset_dict['gold'], pos, [self.all_sprites, self.coin_sprites])
                        case 5:
                            Coin('silver', asset_dict['silver'], pos, [self.all_sprites, self.coin_sprites])
                        case 6:
                            Coin('diamond', asset_dict['diamond'], pos, [self.all_sprites, self.coin_sprites])

                        # enemies
                        case 7:
                            Spikes(asset_dict['spikes'], pos, [self.all_sprites, self.damage_sprites])
                        case 8:
                            Tooth(asset_dict['tooth'], pos, [self.all_sprites, self.damage_sprites]
                                  , self.collision_sprites)
                        case 9:
                            Shell(
                                orientation='left',
                                assets=asset_dict['shell'],
                                pos=pos,
                                group=[self.all_sprites, self.collision_sprites, self.shell_sprites],
                                pearl_surf=asset_dict['pearl'],
                                damage_sprites=self.damage_sprites)
                        case 10:
                            Shell(
                                orientation='right',
                                assets=asset_dict['shell'],
                                pos=pos,
                                group=[self.all_sprites, self.collision_sprites, self.shell_sprites],
                                pearl_surf=asset_dict['pearl'],
                                damage_sprites=self.damage_sprites)

                        # palm trees
                        case 11:
                            Animated(asset_dict['palms']['small_fg'], pos, self.all_sprites)
                            Block(pos, (76, 50), self.collision_sprites)
                        case 12:
                            Animated(asset_dict['palms']['large_fg'], pos, self.all_sprites)
                            Block(pos, (76, 50), self.collision_sprites)
                        case 13:
                            Animated(asset_dict['palms']['left_fg'], pos, self.all_sprites)
                            Block(pos, (76, 50), self.collision_sprites)
                        case 14:
                            Animated(asset_dict['palms']['right_fg'], pos, self.all_sprites)
                            Block(pos + vector(50, 0), (76, 50), self.collision_sprites)

                        case 15:
                            Animated(asset_dict['palms']['small_bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
                        case 16:
                            Animated(asset_dict['palms']['large_bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
                        case 17:
                            Animated(asset_dict['palms']['left_bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
                        case 18:
                            Animated(asset_dict['palms']['right_bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
        except AttributeError:
            display_text(self.display_surface, "存档码错误not found", 36, (0, 0, 0), (640, 50))

        for sprite in self.shell_sprites:
            sprite.player = self.player

    def get_coins(self):
        collided_coins = pygame.sprite.spritecollide(self.player, self.coin_sprites, True)
        for sprite in collided_coins:
            self.coin_p += 1
            self.coin_sound.play()
            Particle(self.particle_surfs, sprite.rect.center, self.all_sprites)

    def get_damage(self):
        global last_stomp_time
        collision_sprites = pygame.sprite.spritecollide(self.player, self.damage_sprites, False,
                                                        pygame.sprite.collide_mask)
        for sprite in collision_sprites:
            if isinstance(sprite, Tooth):
                # 碰到牙齿后先检查玩家状态
                if self.player.direction.y > 0.5:  # 玩家正在下落
                    # 玩家处于下落状态，可以踩踏牙齿
                    sprite.shrink()
                    self.stomp_sound.play()
                    current_time = pygame.time.get_ticks()
                    last_stomp_time = current_time
                    self.player.direction.y = -1.5
                    self.coin_p += 5
                    sprite.kill()
                else:
                    # 玩家没有处于下落状态，受到伤害
                    self.hit_sound.play()
                    self.player.damage()
            else:
                # 玩家没有处于下落状态，受到伤害
                self.hit_sound.play()
                self.player.damage()

    def event_loop(self):
        xue = Player.xue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or xue <= 0:
                self.switch()
                self.bg_music.stop()
                self.bg_music2.stop()
                self.bg_music3.stop()

            if event.type == self.cloud_timer:
                surf = choice(self.cloud_surfs)
                surf = pygame.transform.scale2x(surf) if randint(0, 5) > 3 else surf
                x = self.level_limits['right'] + randint(100, 300)
                y = self.horizon_y - randint(-50, 600)
                Cloud((x, y), surf, self.all_sprites, self.level_limits['left'])

    def startup_clouds(self):
        for i in range(35):
            surf = choice(self.cloud_surfs)
            surf = pygame.transform.scale2x(surf) if randint(0, 5) > 3 else surf
            if self.level_limits['right'] is not None:
                x = randint(self.level_limits['left'], self.level_limits['right'])
                y = self.horizon_y - randint(100, 500)
                Cloud((x, y), surf, self.all_sprites, self.level_limits['left'])
            else:
                pass

    def run(self, dt):
        # update
        self.event_loop()
        self.all_sprites.update(dt)
        self.get_coins()
        self.get_damage()

        # drawing
        self.display_surface.fill(SKY_COLOR)
        self.all_sprites.custom_draw(self.player)
        self.ui.show_health(Player.xue, 10)
        self.ui.show_coins(self.coin_p)


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()

    def draw_horizon(self):
        horizon_pos = self.horizon_y - self.offset.y

        if horizon_pos < WINDOW_HEIGHT:
            sea_rect = pygame.Rect(0, horizon_pos, WINDOW_WIDTH, WINDOW_HEIGHT - horizon_pos)

            pygame.draw.rect(self.display_surface, SEA_COLOR, sea_rect)
            horizon_rect1 = pygame.Rect(0, horizon_pos - 10, WINDOW_WIDTH, 10)
            horizon_rect2 = pygame.Rect(0, horizon_pos - 16, WINDOW_WIDTH, 4)
            horizon_rect3 = pygame.Rect(0, horizon_pos - 20, WINDOW_WIDTH, 2)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect1)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect2)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect3)

            pygame.draw.line(self.display_surface, HORIZON_COLOR, (0, horizon_pos), (WINDOW_WIDTH, horizon_pos), 3)

        if horizon_pos < 0:
            self.display_surface.fill(SEA_COLOR)

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
        self.offset.y = player.rect.centery - WINDOW_HEIGHT / 2

        for sprite in self:
            if sprite.z == LEVEL_LAYERS['clouds']:
                offset_rect = sprite.rect.copy()
                offset_rect.center -= self.offset
                self.display_surface.blit(sprite.image, offset_rect)

        self.draw_horizon()
        for sprite in self:
            for layer in LEVEL_LAYERS.values():
                if sprite.z == layer and sprite.z != LEVEL_LAYERS['clouds']:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
