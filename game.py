import arcade
import os
from typing import List, Dict
import json

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Платформер"
GRAVITY = 980
JUMP_IMPULSE = 480

class Settings:
    def __init__(self):
        self.fullscreen = False
        self.volume = 1.0
        self.difficulty = "normal"
    
    def save(self):
        with open('settings.json', 'w') as f:
            json.dump(self.__dict__, f)
    
    def load(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                self.__dict__.update(json.load(f))

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("player.png", center_x=SCREEN_WIDTH // 4, center_y=SCREEN_HEIGHT // 2)
        self.velocity = arcade.Vector(0, 0)
        self.on_ground = False
        self.score = 0
        self.health = 100
    
    def update(self):
        # Применяем гравитацию
        if not self.on_ground:
            self.velocity.y -= GRAVITY * 1/60
        
        # Обновляем позицию
        self.center_x += self.velocity.x * 1/60
        self.center_y += self.velocity.y * 1/60
        
        # Проверка столкновений с полом
        if self.center_y < SCREEN_HEIGHT // 2:
            self.center_y = SCREEN_HEIGHT // 2
            self.velocity.y = 0
            self.on_ground = True
    
    def jump(self):
        if self.on_ground:
            self.velocity.y = JUMP_IMPULSE
            self.on_ground = False
    
    def move_left(self):
        self.velocity.x = -300
    
    def move_right(self):
        self.velocity.x = 300
    
    def stop(self):
        self.velocity.x = 0

class Enemy(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("enemy.png", center_x=x, center_y=y)
        self.patrol_range = 200
        self.start_x = x
        self.direction = 1
    
    def update(self):
        # Патрулирование
        self.center_x += 2 * self.direction
        
        if abs(self.center_x - self.start_x) > self.patrol_range:
            self.direction *= -1

class Shop:
    def __init__(self):
        self.items = {
            "heart": {"price": 100, "description": "Восстановить здоровье"},
            "speed_boost": {"price": 200, "description": "Ускорение на 30 секунд"},
            "jump_boost": {"price": 150, "description": "Усиленное прыжание на 45 секунд"}
        }
    
    def buy_item(self, player, item_name):
        if item_name in self.items and player.score >= self.items[item_name]["price"]:
            player.score -= self.items[item_name]["price"]
            return True
        return False

class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)
        
        # Инициализация объектов
        self.player = Player()
        self.enemies: List[Enemy] = [Enemy(600, SCREEN_HEIGHT // 2)]
        self.shop = Shop()
        self.settings = Settings()
        self.settings.load()
        
        # Состояние игры
        self.game_state = "playing"
        self.show_shop = False
        
        # Физика
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, 
            [], 
            gravity_constant=GRAVITY
        )
    
    def on_draw(self):
        arcade.start_render()
        
        if self.game_state == "playing":
            self.player.draw()
            for enemy in self.enemies:
                enemy.draw()
            
            # Отображение очков и здоровья
            arcade.draw_text(
                f"Очки: {self.player.score}", 
                10, SCREEN_HEIGHT - 30, 
                arcade.color.BLACK, 
                20
            )
            arcade.draw_text(
                f"Здоровье: {self.player.health}", 
                10, SCREEN_HEIGHT - 60, 
                arcade.color.BLACK, 
                20
            )
        
        elif self.show_shop:
            self._draw_shop()
    
    def _draw_shop(self):
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT // 2, 
            SCREEN_WIDTH * 0.8, 
            SCREEN_HEIGHT * 0.6, 
            arcade.color.LIGHT_BLUE
        )
        
        arcade.draw_text("Магазин", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, arcade.color.BLACK, 30)
        
        y = SCREEN_HEIGHT // 2
        for item_name, item_data in self.shop.items.items():
            arcade.draw_text(
                f"{item_name}: {item_data['price']} очков\n{item_data['description']}", 
                SCREEN_WIDTH // 2, 
                y, 
                arcade.color.BLACK, 
                15,
                anchor_x="center"
            )
            y -= 60
    
    def update(self, delta_time):
        if self.game_state == "playing":
            self.physics_engine.update()
            self.player.update()
            
            # Обновление врагов
            for enemy in self.enemies:
                enemy.update()
                
                # Проверка столкновения с игроком
                if abs(enemy.center_x - self.player.center_x) < 30 and \
                   abs(enemy.center_y - self.player.center_y) < 30:
                    self.player.health -= 1
                    if self.player.health <= 0:
                        self.game_state = "game_over"
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.move_left()
        elif key == arcade.key.RIGHT:
            self.player.move_right()
        elif key == arcade.key.SPACE:
            self.player.jump()
        elif key == arcade.key.ESCAPE:
            arcade.close_window()
        elif key == arcade.key.TAB:
            self.show_shop = not self.show_shop
        
        # Покупка предметов
        if self.show_shop:
            if key == arcade.key.KEY_1:
                self.shop.buy_item(self.player, "heart")
            elif key == arcade.key.KEY_2:
                self.shop.buy_item(self.player, "speed_boost")
            elif key == arcade.key.KEY_3:
                self.shop.buy_item(self.player, "jump_boost")

def main():
    window = Game()
    arcade.run()

if __name__ == "__main__":
    main()                  