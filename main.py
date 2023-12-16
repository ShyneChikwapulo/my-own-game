import pygame
import sys
import random
import button

# General setup
pygame.init()

# Game screen
bottom_panel = 170
screen_width = 750
screen_height = 280 + bottom_panel
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Shynes Animation")

#define game variables
current_fighter = 1
total_fighters = 2
action_cooldown = 0
action_wait_time = 200
attack=False
Player_attack = False
potion= False
potion_effect =15
clicked = False

# Define fonts
font = pygame.font.SysFont('Times New Roman', 26)

# Define colors
purple = (128, 0, 128)
green = (0, 255, 0)
red = (255, 0, 0)

# Clock setup
clock = pygame.time.Clock()
FPS = 60

# Scrolling background setup
scroll = 0
ground_image = pygame.image.load("assets/Background/ground.png").convert_alpha()
# panel image
panel_img = pygame.image.load('assets/Background/panel.png').convert_alpha()

#button images
potion_img = pygame.image.load('assets/Icons/potion.png').convert_alpha()

#sword image
sword_img = pygame.image.load('assets/Icons/sword.png').convert_alpha()

# Ground image
ground_width = ground_image.get_width()
ground_height = 235

# create function for drawing text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# function for drawing panel
def draw_panel(player):
    screen.blit(panel_img, (0, screen_height - bottom_panel))
    draw_text(f'{player.name} HP: {player.hp}', font, purple, 100, screen_height - bottom_panel + 10)
    for count, i in enumerate(bandit_list):
        # show name and health
        draw_text(f'{i.name} HP: {i.hp}', font, red, 550, (screen_height - bottom_panel + 10) + count * 60)


bg_images = []
for i in range(1, 11):
    bg_image = pygame.image.load(f"assets/Background/plx-{i}.png").convert_alpha()
    bg_images.append(bg_image)
bg_width = bg_images[0].get_width()


def draw_bg():
    for x in range(25):
        speed = 1
        for i in bg_images:
            screen.blit(i, ((x * bg_width) - scroll * speed, 0))
            speed += 0.2


def draw_ground():
    for x in range(24):
        screen.blit(ground_image, ((x * ground_width) - scroll * 2.5, screen_height - ground_height))


class Player(pygame.sprite.Sprite):
    GRAVITY = 0.5

    def __init__(self, pos_x, pos_y, name, max_hp, strength, potions):
        super().__init__()
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potions = potions
        self.P_alive = True
        self.potions = potions

        self.idle_sprites = [pygame.image.load(f"assets/idle/idle{i}.png") for i in range(1, 5)]
        self.run_sprites = [pygame.image.load(f"assets/run/run{i}.png") for i in range(1, 12)]
        self.punch_sprites = [pygame.image.load(f"assets/punch/punch{i}.png") for i in range(1, 50)]
        self.jump_image = [pygame.image.load(f"assets/jump/jump{i}.png") for i in range(1, 18)]
        self.fall_image = [pygame.image.load(f"assets/fall/fall{i}.png") for i in range(1, 10)]
        self.transform_sprites = [pygame.image.load(f"assets/transform/transform{i}.png") for i in range(1, 70)]
        self.Hurt_sprites = [pygame.image.load(f"assets/Hurt/{i}.png") for i in range(1, 8)]


        self.is_animating = False
        self.is_punching = False
        self.is_transforming = False
        self.is_hurt = False
        self.is_falling = False
        self.is_jumping = False


        self.current_sprite = 0
        self.image = self.idle_sprites[0]  # Set the initial image
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x, pos_y]
        self.direction = 1  # 1 for right, -1 for left
        
        self.jump_height = 200
        self.fall_count = 0
        self.x_vel = 0
        self.y_vel = 0
        self.original_y = pos_y

    def P_Hurt(self):
        self.is_hurt = True
        self.is_animating = False
        self.is_punching = False
        self.current_sprite = 0

    def hurt_animation(self):
        self.is_hurt = True
        self.is_animating = False
        self.is_punching = False
        self.current_sprite = 0
        self.rect.y=125


    def fall(self):
        if self.is_jumping:
            self.is_jumping = False
            self.is_falling = True  # Add this line to indicate that the player is falling
            self.fall_count = 0
            self.current_sprite = 0  # Reset the sprite index
            self.image = self.fall_image[0]  # Set the initial fall image
           

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1

    def animate(self):
        self.is_animating = True
        self.is_transforming = False

    def punch(self, Player_Target):
        self.is_punching = True
        self.is_animating = False
        self.is_transforming = False
        self.current_sprite = 0

        
        #deal damage to enemy
        rand = random.randint(-5, 5)
        damage = self.strength + rand
        Player_Target.hp -= damage
        Player_Target.hurt()



        
            #check if target has died
        if Player_Target.hp < 1:
            Player_Target.hp = 0
            Player_Target.alive = False
            Player_Target.death()


            # Check for collision with bandits when punchinga
        for bandit in bandit_list:
            if check_collision(self, bandit):
                bandit.hp -= self.strength
                if bandit.hp <= 0:
                    bandit.dead = True



    def transform(self):
        self.is_transforming = True
        self.is_animating = False
        self.is_punching = False
        self.current_sprite = 0
        self.image = pygame.transform.flip(self.transform_sprites[0], self.direction == -1, False)
        # Store the original Y-coordinate before transformation
        
        
        

    def jump(self):
        if not self.is_jumping and not self.is_falling:
            self.is_jumping = True
            self.y_vel = -self.jump_height
            self.rect.y = self.rect.y  # Adjust the starting position when jumping


    def move(self, direction):
        self.direction = direction
        new_rect = self.rect.move(5 * direction, 0)
        for bandit in bandit_list:
            if new_rect.colliderect(bandit.rect):
                return  # Do not move if there is a collision with any bandit
        if 0 <= new_rect.x < screen_width - self.rect.width:
            self.rect.x += 5 * direction
            self.rect.y = 127

    def update(self):

        if self.is_jumping:
            self.current_sprite += 0.2
            if self.current_sprite >= len(self.jump_image):       
                self.is_jumping = False
                self.image = self.idle_sprites[0]  # Set the default image after jumping animation
                self.rect.y = self.original_y  # Reset the Y-coordinate after jumping

            else:
                self.image = self.jump_image[int(self.current_sprite)]
                self.rect.y = self.original_y  # Adjust this value based on your requirements               
       
        if self.is_falling:
            if self.fall_count < len(self.fall_image) * 3:  # Adjust the multiplier for the fall speed
                self.image = self.fall_image[self.fall_count // 3]  # Use integer division to index the images
                self.fall_count += 1
            else:
                self.is_falling = False
                self.image = self.idle_sprites[0]  # Set the default image after falling animation
                self.rect.y = self.original_y  # Reset the Y-coordinate after falling

        elif self.is_hurt:
            self.current_sprite += 0.2

            if self.current_sprite >= len(self.Hurt_sprites):
                self.is_hurt = False
                self.current_sprite = 0

            self.image = self.Hurt_sprites[int(self.current_sprite)]

                
        else:
            if not self.is_punching and not self.is_animating and not self.is_jumping and not self.is_transforming:
                self.current_sprite += 0.2

                if self.current_sprite >= len(self.idle_sprites):
                    self.current_sprite = 0

                self.image = pygame.transform.flip(self.idle_sprites[int(self.current_sprite)], self.direction == -1,
                                                   False)
                self.rect.y = self.original_y 

            elif self.is_animating and not self.is_jumping and not self.is_transforming:
                self.current_sprite += 0.2

                if self.current_sprite >= len(self.run_sprites):
                    self.current_sprite = 0

                self.image = pygame.transform.flip(self.run_sprites[int(self.current_sprite)], self.direction == -1,
                                                   False)
            elif self.is_punching and not self.is_jumping and not self.is_transforming:
                self.current_sprite += 0.2

                if self.current_sprite >= len(self.punch_sprites):
                    self.is_punching = False
                    self.current_sprite = 0

                self.image = pygame.transform.flip(self.punch_sprites[int(self.current_sprite)],
                                                   self.direction == -1, False)
            elif self.is_transforming:
                self.current_sprite += 0.2

                if self.current_sprite >= len(self.transform_sprites):
                    self.is_transforming = False
                    self.current_sprite = 0

            

                self.image = pygame.transform.flip(self.transform_sprites[int(self.current_sprite)],
                                                   self.direction == -1, False)
                self.original_y = self.rect.y

            elif self.is_hurt:
                self.current_sprite += 0.2

                if self.current_sprite >= len(self.Hurt_sprites):
                    self.is_hurt = False
                    self.current_sprite = 0

                self.image = self.Hurt_sprites[int(self.current_sprite)]

    
               
# fighter class
class Fighter():
    def __init__(self, x, y, name, max_hp, strength, potions):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potions = potions
        self.potions = potions
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 # 0:idle, 1:attack, 2:hurt, 3:dead
        self.update_time = pygame.time.get_ticks()

        self.dead = False  # Flag to track whether the bandit is dead
        self.death_sprites = [pygame.image.load(f'assets/Bandit/Death/{i}.png') for i in range(10)]
        self.death_frame_index = 0
        self.death_update_time = pygame.time.get_ticks()

        # load idle images
        temp_list = []
        for i in range(25):
            img = pygame.image.load(f'assets/Bandit/Idle/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 0.90, img.get_height() * 0.90))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        # load attack1 images
        temp_list = []
        for i in range(20):
            img = pygame.image.load(f'assets/Bandit/Attack1/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 0.90, img.get_height() * 0.90))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # load Hurt images
        temp_list = []
        for i in range(3):
            img = pygame.image.load(f'assets/Bandit/Hurt/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 0.90, img.get_height() * 0.90))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # load Death images
        temp_list = []
        for i in range(41):
            img = pygame.image.load(f'assets/Bandit/Death/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 0.90, img.get_height() * 0.90))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


    def flip_sprites(self):
        for i in range(len(self.animation_list)):
            for j in range(len(self.animation_list[i])):
                self.animation_list[i][j] = pygame.transform.flip(self.animation_list[i][j], True, False)




    def fighter_update(self):
        animation_cooldown = 100
        # handle animation
        # update image

        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # if the animation has run out then reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

        if self.action == 1:  # Only update x-coordinate during the attack animation
            self.rect.x -= 2  # Adjust the value based on the desired speed

        self.image = self.animation_list[self.action][self.frame_index]

    def idle(self):
        #set variables to idle animation
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()



    def attack(self, target):
        #deal damagge to enemy
        rand = random.randint(-5, 5)
        damage =self.strength + rand
        target.hp -= damage
        #run enemy hurt animation
        

        # check for collision with player when attacking
        # if check_collision(target, self):
        

      
        #check if target has died
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            
        #set variables to attack animation
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        #set variables to hurt animation
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        

    def death(self):
		#set variables to death animation
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        

    



    def draw(self):
        screen.blit(self.image, self.rect)


class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        # update with new health
        self.hp = hp
        # calculate health ratio
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))


Sasuke = Player(100, 100, 'Sasuke', 100, 10, 5)
bandit1 = Fighter(550, 170, 'Bandit', 100, 6, 1)
bandit1.flip_sprites()


bandit_list = []
bandit_list.append(bandit1)


Sasuke_health_bar = HealthBar(100, screen_height - bottom_panel + 40, Sasuke.hp, Sasuke.max_hp)
bandit1_health_bar = HealthBar(550, screen_height - bottom_panel + 40, bandit1.hp, bandit1.max_hp)
# bandit2_health_bar = HealthBar(550, screen_height - bottom_panel + 100, bandit2.hp, bandit2.max_hp)

# create buttons
potion_button = button.Button(screen, 100, screen_height - bottom_panel + 63, potion_img, 70, 70)



def check_collision(player, bandit):
    return player.rect.colliderect(bandit.rect)

# Game loop
run = True
moving_sprites = pygame.sprite.Group()
moving_sprites.add(Sasuke)

while run:
    clock.tick(FPS)
    

    # Event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Get keypresses
    key = pygame.key.get_pressed()

    if key[pygame.K_LEFT]:
        if scroll > 0:
            scroll -= 5
            Sasuke.move(-1)
            Sasuke.animate()
    elif key[pygame.K_RIGHT]:
        if scroll < 3000:
            scroll += 5
            Sasuke.move(1)
            Sasuke.animate()
    else:
        Sasuke.is_animating = False

    

    if key[pygame.K_SPACE]:
        Sasuke.jump()


    if key[pygame.K_p]:
        Sasuke.punch(bandit1)
        # Check for collision with bandits when punching
        
        for bandit in bandit_list:
            if Sasuke.is_punching and check_collision(Sasuke, bandit):
                bandit.hp -= Sasuke.strength

    if key[pygame.K_t]:
        Sasuke.transform()
        # Check for collision with bandits while transforming
        if Sasuke.is_transforming:
            for bandit in bandit_list:
                if check_collision(Sasuke, bandit):
                    bandit.hp -= Sasuke.strength

    # Clear the screen
    screen.fill((0, 0, 0))

    #draw background
    draw_bg()
    draw_ground()

    # Draw world
    draw_panel(Sasuke)
    Sasuke_health_bar.draw(Sasuke.hp)
    bandit1_health_bar.draw(bandit1.hp)
    # bandit2_health_bar.draw(bandit2.hp)

    #draw fighters
    

    for bandit in bandit_list:
        bandit.fighter_update()
        bandit.draw()

    potion=False
    attack = False


    pygame.mouse.set_visible(True)
    pos = pygame.mouse.get_pos()
    for count, bandit in enumerate(bandit_list):
        if bandit.rect.collidepoint(pos):
			#hide mouse
            pygame.mouse.set_visible(False)
			#show sword in place of mouse cursor
            screen.blit(sword_img, pos)
            if clicked == True and bandit.alive == True:
                attack = True
                target = bandit_list[count]
    if potion_button.draw():
        potion = True


 
    #show number of potions remaining
    draw_text(str(Sasuke.potions), font, purple, 150, screen_height - bottom_panel + 70)
    draw_text('Health Potion', font, purple, 70, screen_height - bottom_panel + 130)
    
    #player action
    if Sasuke.alive == True:
        if current_fighter ==1: 
            action_cooldown += 0.5
            if action_cooldown >= action_wait_time :       #use this code to create punch attack for sasuke and copy code for bandits 0idle 1attack 2 dead
                #look for player action
                #attack
                    Sasuke.punch(bandit)
                    current_fighter += 1
                    action_cooldown=0   

            if potion == True:
                if Sasuke.potions > 0:
                    #check if the potion would heal the player beyond the max health
                    if Sasuke.max_hp - Sasuke.hp > potion_effect:
                        heal_amount = potion_effect
                    else:
                        heal_amount= Sasuke.max_hp - Sasuke.hp
                        Sasuke.hp += heal_amount
                        Sasuke.potions -= 1
                        current_fighter+= 1
                        action_cooldown =0



    if bandit.alive == True:
            if current_fighter == 1  :
            
                action_cooldown += 0.5
                if action_cooldown >= action_wait_time:       #use this code to create punch attack for sasuke and copy code for bandits 0idle 1attack 2 dead
                #look for player action
                #attack
                    bandit.attack(Sasuke)
                    # Trigger hurt animation for the player
                    Sasuke.hurt_animation()
                    
                    current_fighter += 1
                    action_cooldown=0
                    
            else:
                current_fighter = 1

    #if all fighters have had a turn then reset
    if current_fighter > total_fighters:
        current_fighter = 1


        
    
    # Update and draw sprites
    moving_sprites.update()
    moving_sprites.draw(screen)  # Draw the sprite on top of the background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False

    
    
    pygame.display.flip()

pygame.quit()
sys.exit()
