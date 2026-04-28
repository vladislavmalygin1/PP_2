import pygame
import random

WIDTH, HEIGHT, BLOCK_SIZE = 600, 400, 20

class SnakeGame:
    def __init__(self, color):
        self.snake_color = color
        self.reset()

    # game.py

    def reset(self):
        self.snake = [[WIDTH//2, HEIGHT//2]]
        self.dx, self.dy = BLOCK_SIZE, 0
        self.score, self.level, self.fps = 0, 1, 10
        self.shield = False
        self.effects = {"speed": 0, "slow": 0}
        
        # Initialize empty lists so spawn_item doesn't crash
        self.obstacles = []
        self.powerup = None
        
        # Create a temporary dummy for poison so food doesn't spawn on a null attribute
        self.poison = [-100, -100] 
        
        # Now spawn the real items
        self.poison = self.spawn_item("poison")
        self.food = self.spawn_item("food")

    # Inside game.py
    def spawn_item(self, itype):
        while True:
            pos = [random.randrange(0, WIDTH-BLOCK_SIZE, BLOCK_SIZE), 
                random.randrange(0, HEIGHT-BLOCK_SIZE, BLOCK_SIZE)]
        
        # Ensure it doesn't spawn on top of the snake or existing obstacles
            if pos not in self.snake and pos not in self.obstacles:
                if itype == "food":
                # Food returns a dictionary
                    t = random.choice([{"w":1,"c":(255,0,0),"l":10000}, {"w":3,"c":(255,215,0),"l":5000}])
                    return {"pos": pos, "weight": t["w"], "color": t["c"], "exp": pygame.time.get_ticks() + t["l"]}
            
            # Poison and Obstacles just return the [x, y] list
                return pos

    def update(self):
        now = pygame.time.get_ticks()
        
        # 1. Logic to spawn power-up
        if not self.powerup and random.random() < 0.02:
            self.powerup = {
                "pos": self.spawn_item("powerup"), 
                "type": random.choice(["speed", "slow", "shield"]), 
                "exp": now + 7000 
            }
        
        if now > self.food["exp"]: self.food = self.spawn_item("food")
        if self.powerup and now > self.powerup["exp"]: self.powerup = None

        new_head = [self.snake[-1][0] + self.dx, self.snake[-1][1] + self.dy]

        # 2. Collision Logic with Wall
        if new_head[0] >= WIDTH or new_head[0] < 0 or new_head[1] >= HEIGHT or new_head[1] < 0:
            return "DEAD" # Walls are still deadly even with a shield

        # 3. Collision Logic with Obstacles (The Barrier)
        if new_head in self.obstacles:
            if self.shield:
                self.shield = False
                self.obstacles.remove(new_head) # Barrier disappears
                # We continue movement so the snake doesn't get stuck
            else:
                return "DEAD"

        # 4. Collision with Self
        if new_head in self.snake:
            return "DEAD"

        self.snake.append(new_head)

        # 5. Eating Items
        if new_head == self.food["pos"]:
            self.score += self.food["weight"]
            # Check for Level Up
            if self.score // 5 + 1 > self.level:
                self.level += 1
                self.fps += 1
                # Spawn a new obstacle every level after level 2
                if self.level >= 2:
                    self.obstacles.append(self.spawn_item("obstacle"))
            self.food = self.spawn_item("food")
            
        elif self.powerup and new_head == self.powerup["pos"]:
            if self.powerup["type"] == "shield": self.shield = True
            else: self.effects[self.powerup["type"]] = now + 5000
            self.powerup = None
            
        elif new_head == self.poison:
            if self.shield:
                self.shield = False # Shield protects against poison too
            else:
                if len(self.snake) <= 3: return "DEAD"
                self.snake.pop(0); self.snake.pop(0); self.snake.pop(0) 
            self.poison = self.spawn_item("poison") # Relocate poison
        else:
            self.snake.pop(0)

        return "ALIVE"