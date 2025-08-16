import pygame
import sys
import os
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Screen setup
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Game")

# ---------------- Load Images ----------------
bg_image_raw = pygame.image.load(os.path.join(script_dir, "bg image.png")).convert()
bg_image = pygame.transform.scale(bg_image_raw, (screen_width, screen_height))

start_btn = pygame.image.load(os.path.join(script_dir, "start button.png")).convert_alpha()
start_btn_pressed = pygame.image.load(os.path.join(script_dir, "start button pressed.png")).convert_alpha()
start_btn_rect = start_btn.get_rect(center=(screen_width // 2, screen_height // 2))

restart_btn = pygame.image.load(os.path.join(script_dir, "restart button.png")).convert_alpha()
restart_btn_rect = restart_btn.get_rect(center=(screen_width // 2, screen_height // 2))

pipe_bottom = pygame.image.load(os.path.join(script_dir, "down side rod.png")).convert_alpha()
pipe_top = pygame.transform.flip(pipe_bottom, False, True)

bird_img = pygame.image.load(os.path.join(script_dir, "bird.png")).convert_alpha()
bird_img = pygame.transform.scale(bird_img, (90, 70))
bird_x = 150
bird_y = 150
bird_rect = bird_img.get_rect(center=(bird_x, bird_y))

# ---------------- Load Sounds ----------------
start_sound = pygame.mixer.Sound(os.path.join(script_dir, "start.mp3"))
point_sound = pygame.mixer.Sound(os.path.join(script_dir, "point.mp3"))
bg_music = pygame.mixer.Sound(os.path.join(script_dir, "background.mp3"))
death_sound = pygame.mixer.Sound(os.path.join(script_dir, "death.mp3"))

# ---------------- Game Setup ----------------
pipe_gap = 200
pipe_speed = 3
pipe_distance = 300
num_pipe_sets = 3

bg_x = 0
bg_speed = 2
soil_height = 50  # height of soil

def create_pipe_pair(gap_override=None):
    gap_size = gap_override if gap_override else pipe_gap
    y_offset = random.randint(150, screen_height - gap_size - 150 - soil_height)
    pipes_list = []
    pipes_list.append({"rect": pipe_top.get_rect(midbottom=(0, y_offset)), "image": pipe_top, "passed": False})
    pipes_list.append({"rect": pipe_bottom.get_rect(midtop=(0, y_offset + gap_size)), "image": pipe_bottom, "passed": False})
    return pipes_list

def reset_game():
    global bird_rect, bird_velocity, score, pipes, pipe_gap, pipes_passed, game_state, bg_x
    bird_rect = bird_img.get_rect(center=(bird_x, bird_y))
    bird_velocity = 1
    score = 0
    pipe_gap = 200
    pipes_passed = 0
    pipes = []
    for i in range(num_pipe_sets):
        pair = create_pipe_pair()
        for p in pair:
            p["rect"].x = screen_width + i * pipe_distance
            pipes.append(p)
    bg_x = 0
    game_state = "playing"
    bg_music.play(-1)

# Initial pipes
pipes = []
for i in range(num_pipe_sets):
    pair = create_pipe_pair()
    for p in pair:
        p["rect"].x = screen_width + i * pipe_distance
        pipes.append(p)

gravity = 0.2
bird_velocity = 1
flap_strength = -6

score = 0
pipes_passed = 0

clock = pygame.time.Clock()
game_state = "menu"

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn_rect.collidepoint(event.pos):
                    screen.fill((0, 0, 0))
                    screen.blit(start_btn_pressed, start_btn_pressed.get_rect(center=start_btn_rect.center))
                    pygame.display.flip()
                    start_sound.play()
                    pygame.time.delay(int(start_sound.get_length() * 1000))
                    reset_game()

        elif game_state == "playing":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird_velocity = flap_strength
            if event.type == pygame.MOUSEBUTTONDOWN:
                bird_velocity = flap_strength

        elif game_state == "game_over":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn_rect.collidepoint(event.pos):
                    reset_game()

    if game_state == "menu":
        screen.fill((0, 0, 0))
        screen.blit(start_btn, start_btn_rect)
        pygame.display.flip()

    elif game_state == "playing":
        bird_velocity += gravity
        bird_rect.y += bird_velocity

        bg_x -= bg_speed
        if bg_x <= -screen_width:
            bg_x = 0

        for i in range(0, len(pipes), 2):
            pipes[i]["rect"].x -= pipe_speed
            pipes[i+1]["rect"].x -= pipe_speed

            if pipes[i]["rect"].centerx < bird_rect.centerx and not pipes[i]["passed"]:
                score += 1
                pipes[i]["passed"] = True
                point_sound.play()
                pipes_passed += 2
                if pipes_passed % 4 == 0:
                    pipe_gap = max(50, pipe_gap - 5)

            if pipes[i]["rect"].right < 0:
                farthest_x = max(p["rect"].x for p in pipes)
                new_pair = create_pipe_pair(gap_override=pipe_gap)
                pipes[i] = new_pair[0]
                pipes[i]["rect"].x = farthest_x + pipe_distance
                pipes[i+1] = new_pair[1]
                pipes[i+1]["rect"].x = farthest_x + pipe_distance

        # ---- Precise Collision Detection ----
        bird_hitbox = bird_rect.inflate(-30, -25)  # smaller bird hitbox
        for i in range(0, len(pipes), 2):
            top_pipe = pipes[i]
            bottom_pipe = pipes[i+1]

            top_hitbox = top_pipe["rect"].inflate(-15, -15)
            bottom_hitbox = bottom_pipe["rect"].inflate(-15, -15)

            if bird_hitbox.right > top_hitbox.left and bird_hitbox.left < top_hitbox.right:
                if bird_hitbox.colliderect(top_hitbox) or bird_hitbox.colliderect(bottom_hitbox):
                    bg_music.stop()
                    death_sound.play()
                    game_state = "game_over"
                    break

        # Soil and ceiling collision
        if bird_rect.top < 0 or bird_rect.bottom > screen_height - soil_height:
            bg_music.stop()
            death_sound.play()
            game_state = "game_over"

        # Draw background
        screen.blit(bg_image, (bg_x, 0))
        screen.blit(bg_image, (bg_x + screen_width, 0))

        # Draw bird
        screen.blit(bird_img, bird_rect)

        # Draw pipes
        for pipe in pipes:
            screen.blit(pipe["image"], pipe["rect"])

        # Draw soil
        pygame.draw.rect(screen, (139, 69, 19), (0, screen_height - soil_height, screen_width, soil_height))

        # Draw score
        font = pygame.font.Font(None, 48)
        score_text = font.render(f"SCORE : {int(score)}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    elif game_state == "game_over":
        screen.fill((0, 0, 0))

        # Centered Scoreboard
        font_big = pygame.font.Font(None, 72)
        score_text = font_big.render(f"Score: {score}", True, (255, 255, 255))
        score_x = screen_width // 2 - score_text.get_width() // 2
        score_y = screen_height // 2 - restart_btn.get_height() // 2 - 60
        screen.blit(score_text, (score_x, score_y))

        # Restart button centered
        restart_btn_rect.center = (screen_width // 2, screen_height // 2 + 50)
        screen.blit(restart_btn, restart_btn_rect)

        pygame.display.flip()

pygame.quit()
sys.exit()


# skjkkdkjkhkjhkdjfhhfkjhksdfhjdfhksfhkhjkdfkhkjdffdhdushiuhuihui usdiuusfuiguidfudsugsdfiugiudgfgidgfuggiugigugugfigsiugfifxnmmbnxcbnbxcnbnxbmnnbvxbnvxs            ifugsgi giugd iugsiu gdsif iusg igsdiu gig iusdiusd gisggsiugisggf uggsuggsdgyfsubf dgfgjsgd7sdfsdfguygayygauygfgsvbviuyuyrtwet gusyygsdyufs gsfsgf gfysgyfgsyg sfsuygfuygg vxtvhrggstfk sgdggfygbnycgury gsgyudguydsgyugsdf ygysfggygfs sgfgsuyfgb dsgfuggyugfgsu dgygsdgfuygygs vxvuyvcyvtutcxytuxtcytctytytxcsghgsdfgg durga durga durga durga durga  durga durga durg durga durga durga durga durga durga   iu huudiuhdfguhduidu uh dfuhuududhfudfu hdfiugdfgduguduhudfgudhfgdfudfuhudhdhuhiud uer tert        jgdfgdfgdj kd dfjdfkkjdhfk kjkfkjhd jshkg kkdfkjdgkkjkf dgkjkjk      ete rterre terterweiwueefueufufsdfusdisdufhusduui9tetertyerteruiiyiurtetertyertrtetuerteiuteriuuf iusds gsggsgfguydgug                  tsyygygbc vurga khjjjzhkjzkhcjhkjzkhjjhzkjhhzchjzhcjkhhjhjh hhkjhhzjhkjzkjhzkjhhxhhxhkjhhhhkjjcjvgvggbccvnbvnbdurga durga durga durga durga furga durga durga durga dugr durga durga durga dsgfiugsdigiugisdgusdggiufgsdiufgsdifgsiufgsdifsdiufgsidfudfgsdfgiugfisdgiusdgfisdfiugsdfsdufgsdufgsdfsdf
