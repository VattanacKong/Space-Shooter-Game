import pygame
import os
import time
import random
pygame.font.init()
pygame.mixer.init()

#width height size
W, H = 750, 750
WIN = pygame.display.set_mode((W, H))
pygame.display.set_caption("Space Invaders")


assets = "assets"
# load images
RED_SPACE_SHIP = pygame.image.load(os.path.join(assets,"enemy_ship_red.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join(assets,"big_enemy_ship.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join(assets, "enemy_ship_red.png"))


# Load sound effects
LASER_SOUND = pygame.mixer.Sound(os.path.join(assets,"sounds", "alienshoot1.ogg"))
EXPLOSION_SOUND = pygame.mixer.Sound(os.path.join(assets,"sounds", "explosion.ogg"))
GAME_SOUND = pygame.mixer.Sound(os.path.join(assets,"sounds", "game.ogg"))

# Player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join(assets,"player_ship.png"))

# Lasers
BLUE_LASER = pygame.image.load(os.path.join(assets, "blue_laser.png"))
# background
BG = pygame.transform.scale(pygame.image.load(os.path.join(assets,"background-black.png")), (W, H))
#explosion frames
folder = 'assets/explosion frames'
sprites=[]
for i in range(24):
    frame = pygame.image.load(os.path.join(folder,f'explosion_{i}.png'))
    sprites.append(frame)

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y < height and self.y >= 0)
    
    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30 #cooldown time for shooting
    def __init__(self, x, y, health=100): 
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(H):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 10 

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 35 , self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            LASER_SOUND.play()

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=50):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = BLUE_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) # mask tell us where pixels are and where they are not in the image
        self.max_health = health
    
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(H):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        EXPLOSION_SOUND.play()
    
    def explode(self):
        EXPLOSION_SOUND.play()
        for i in range(24):
            WIN.blit(sprites[i], (self.x-10, self.y))
            pygame.display.update()
            pygame.time.delay(30)
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
    
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))
        

class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, BLUE_LASER),
        "green": (GREEN_SPACE_SHIP, BLUE_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }
    def __init__(self, x,y, color, health = 100):
        super().__init__(x,y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 35    , self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


#check collision
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    if obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None:
        return True
    return False

    
def main():
    execute = True
    FPS = 60
    level = 0
    # lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1 #enemy velocity
    laser_vel = 40 #laser velocity

    player_vel = 30 #playyer velocityy

    player = Player(300, 650)

    clock = pygame.time.Clock()

#auto shoot
    auto_shoot = False

    lost = False

    def redraw_window():
        WIN.blit(BG, (0, 0))
        # draw text
        # lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        health_label = main_font.render(f"Health: {player.health}", 1, (255, 255, 255))

        # WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (W - level_label.get_width() - 10, 10))
        WIN.blit(health_label, (10, 10))

        #draw all enemies
        for ememy in enemies:
            ememy.draw(WIN)

        #draw player
        player.draw(WIN)

        #check if lost, print text
        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (W/2 - lost_label.get_width()/2, 350)) 
            
        pygame.display.update()

    while execute:
        clock.tick(FPS)
        redraw_window()

        # if lives <= 0 or player.health <= 0:
        #     lost = True
        
        if player.health <= 0:
            lost = True
            player.explode()
            pygame.time.delay(500)
            execute = False

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, W-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"])) 
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()  

        
        #event controls
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player.x - player_vel > 0:
            player.x -= player_vel
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.x + player_vel +player.get_width() < W:
            player.x += player_vel
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and player.y - player_vel > 0:
            player.y -= player_vel
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player.y + player_vel + player.get_height() + 15< H:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            
        #set auto_shoot key
        if keys[pygame.K_z]:
            if auto_shoot == False: 
                auto_shoot = True
            else:
                auto_shoot = False
                
        #handle auto shoot if key pressed  
        if auto_shoot == True:
            player.shoot()
        
        #make enemies move and shoot randomly and remove if shot or collided
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 60) >= 55:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                # lives -= 1
                enemies.remove(enemy)
            
            for laser in enemy.lasers:
                if laser.off_screen(H):
                    enemy.lasers.remove(laser)
                if collide(laser, player):
                    player.health -= 10
                    # lives -= 1
                    enemy.lasers.remove(laser)

            if enemy.y + enemy.get_height() > H:
                # lives -= 1
                enemies.remove(enemy)
            
        #move player laser faster than enemy
        player.move_lasers(-(laser_vel + 10), enemies)


def main_menu():    
    #define font
    title_font = pygame.font.SysFont("comicsans", 50)   
    #play lobby music
    GAME_SOUND.play()    
    run = True
    while run:
        #render background and start text
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Press any key to begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (W/2 - title_label.get_width()/2, 350))
        pygame.display.update()

        #get user event
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                #stop sound
                GAME_SOUND.stop()           
                #run main if mouse clicked     
                main()
                run = True

main_menu()