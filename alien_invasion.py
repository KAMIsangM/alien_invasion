import sys
from time import sleep
from pathlib import Path
import json

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
import sound_effects as se
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """管理游戏资源和行为的类"""
    
    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.sound = se.Sound()

        self.set_screen(self.settings.full_screen)
        pygame.display.set_caption("Alien Invasion")

        # 创建存储游戏统计信息的实例，并创建计分牌
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # 让游戏在一开始处于非活动状态
        self.game_active = False

        # 创建Play按钮
        self.play_button = Button(self, "Play")

        # 创建难度按钮
        self.easy_button = Button(self, 'Easy')
        self.normal_button = Button(self, 'Normal')
        self.hard_button = Button(self, 'Hard')
        self.make_difficulty_button()

        # 播放背景音乐
        self.sound.play_BGM()

    def set_screen(self, switch):
        """屏幕设置"""
        if switch:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.settings.screen_width = self.screen.get_rect().width
            self.settings.screen_height = self.screen.get_rect().height
        else:
            self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height))
            
    def make_difficulty_button(self):
        """调整难度按钮"""
        self.easy_button.rect.top = (
            self.play_button.rect.top + 1.5 * self.play_button.rect.height)
        self.easy_button._update_msg()
        
        self.normal_button.rect.top = (
            self.easy_button.rect.top + 1.5 * self.easy_button.rect.height)
        self.normal_button._update_msg()

        self.hard_button.rect.top = (
            self.normal_button.rect.top + 1.5 * self.normal_button.rect.height)
        self.hard_button._update_msg()

        # 调整初始难度为normal
        self.normal_button._prep_highlight()

    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()
            self.clock.tick(60)

    def _start_game(self):
        """开始游戏"""
        # 重置游戏的统计信息
        self.stats.reset_stats()
        self.sb.prep_images()
        self.game_active = True

        # 清空外星人列表和子弹列表
        self.bullets.empty()
        self.aliens.empty()

        # 创建一个新的外星舰队，并将飞船放在屏幕底部的中央
        self._create_fleet()
        self.ship.center_ship()
        
        # 隐藏光标
        pygame.mouse.set_visible(False)

        # 还原游戏设置
        self.settings.initialize_dynamic_settings()

        # 开始音效
        self.sound.start.play()

    def _quit_game(self):
        """结束游戏"""
        path = Path(f'highest_score_{self.settings.difficulty_level}.json')
        contents = json.dumps(self.stats.high_score)
        path.write_text(contents)
        sys.exit()

    def _check_events(self):
        """响应按键和鼠标事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                self._check_difficulty_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """在玩家单击Pla按钮时开始游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self._start_game()

    def _check_difficulty_button(self, mouse_pos):
        """在玩家单击难度按钮时调整难度，并显示所选难度"""
        easy_clicked = self.easy_button.rect.collidepoint(mouse_pos)
        normal_clicked = self.normal_button.rect.collidepoint(mouse_pos)
        hard_clicked = self.hard_button.rect.collidepoint(mouse_pos)
        self.sound.switch.play()
        if easy_clicked:
            self.settings.difficulty_level = 'easy'
            self.easy_button._prep_highlight()
            self.normal_button._prep_base()
            self.hard_button._prep_base()
        elif normal_clicked:
            self.settings.difficulty_level = 'normal'
            self.easy_button._prep_base()
            self.normal_button._prep_highlight()
            self.hard_button._prep_base()
        elif hard_clicked:
            self.settings.difficulty_level = 'hard'
            self.easy_button._prep_base()
            self.normal_button._prep_base()
            self.hard_button._prep_highlight()

        self.stats.reset_stats()
        self.stats.remain_highest()
        self.sb.prep_images()

    def _check_keydown_events(self, event):
        """响应按下"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            self._quit_game()
        elif event.key == pygame.K_p:
            self._start_game()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """响应释放"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _create_fleet(self):
        """创建一个外星人舰队"""
        # 创建一个外星人，再不断添加，直到没有空间添加外星人为止
        # 外星人的间距为外星人的宽度和外星人的高度
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        if self.settings.full_screen:
            blank = int(4 * alien_height)
        else:
            blank = int(3 * alien_height)
        while current_y < (self.settings.screen_height - blank):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            # 添加一行外星人后，重置x值并递增y值
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        """创建一个外星人并将其加入外星舰队"""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """在有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """将整个外星舰队向下移动，并改变它们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        """响应飞船和外星人的碰撞"""
        if self.stats.ships_left > 0:
            # 将ships_left减1并更新记分牌
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # 清空外星人列表和子弹列表
            self.bullets.empty()
            self.aliens.empty()

            # 创建一个新的外星舰队，并将飞船放在屏幕底部的中央
            self._create_fleet()
            self.ship.center_ship()

            # 暂停
            self.sound.hit.play()
            sleep(1)
        else:
            self.game_active =False
            pygame.mouse.set_visible(True)

            # 记录最高分
            path = Path(f'highest_score_{self.settings.difficulty_level}.json')
            contents = json.dumps(self.stats.high_score)
            path.write_text(contents)

    def _fire_bullet(self):
        """创建一颗子弹,并将其加入编组bullets"""
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            self.sound.laser.play()

    def _update_bullets(self):
        """更新子弹的位置并删除已消失的子弹"""
        # 更新子弹的位置
        self.bullets.update()

        # 删除已消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """响应子弹和外星人的碰撞"""
        # 删除发生碰撞的子弹和外星人
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
        
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.sound.explosion.play()
            self.sb.prep_score()
            self.sb.check_high_score()
        self._start_new_level()

    def _start_new_level(self):
        """开始新等级"""
        if not self.aliens:
            # 删除现有子弹并创建一个新的外星舰队
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # 提高等级
            self.stats.level += 1
            self.sb.prep_level()
            self.sound.level.play()

    def _check_aliens_bottom(self):
        """检查是否有外星人到达了屏幕的下边缘"""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # 像飞船被撞到一样处理
                self._ship_hit()
                break

    def _update_aliens(self):
        """检查是否有外星人位于屏幕边缘，并更新整个外星舰队的位置"""
        self._check_fleet_edges()
        self.aliens.update()

        # 检测外星人和飞船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # 检查是否有外星人到达下边缘
        self._check_aliens_bottom()

    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕"""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)

        # 显示得分
        self.sb.show_score()

        # 如果游戏处于非活动状态，就绘制Play按钮
        if not self.game_active:
            self.play_button.draw_button()
            self.easy_button.draw_button()
            self.normal_button.draw_button()
            self.hard_button.draw_button()

        pygame.display.flip()

if __name__ == '__main__':
    # 创建游戏实例并运行游戏
    ai = AlienInvasion()
    ai.run_game()