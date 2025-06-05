# flappy_game.py (Revised with scoring fix)

import pygame
import sys
import random

# --- Constants ---
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 620
# BIRD_START_X, etc., are fine unless assets require adjustment
BIRD_START_X = 70
BIRD_START_Y = SCREEN_HEIGHT // 2
GRAVITY = 0.25
FLAP_STRENGTH = 6.5
PIPE_GAP = 150 # Adjust based on your pipe image and desired difficulty
PIPE_FREQUENCY = 1500 # Milliseconds
PIPE_SPEED = 3
# Example heights - Adjust based on your pipe image height and PIPE_GAP
PIPE_HEIGHTS = [200, 275, 350, 425]
FLOOR_HEIGHT = 100 # Make sure this matches your floor image height if using one
# FLOOR_SPEED should match PIPE_SPEED for visual consistency
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# --- Asset Loading Function ---
def load_assets():
    """Loads game images and handles potential errors."""
    assets = {}
    try:
        # --- Bird ---
        bird_img = pygame.image.load('assets/bird.png').convert_alpha()
        # Scale if needed (example: make 1.5 times bigger)
        assets['bird'] = pygame.transform.scale(bird_img, (int(bird_img.get_width() * 1.5), int(bird_img.get_height() * 1.5)))

        # --- Pipe ---
        pipe_img = pygame.image.load('assets/pipe.png').convert_alpha()
        # Scale if needed
        assets['pipe'] = pygame.transform.scale(pipe_img, (int(pipe_img.get_width() * 1.2), int(pipe_img.get_height() * 1.2)))

        # --- Background ---
        bg_img = pygame.image.load('assets/background.png').convert()
        assets['background'] = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # --- Floor ---
        floor_img = pygame.image.load('assets/floor.png').convert()
        # Ensure floor scaling matches FLOOR_HEIGHT constant if overridden by image
        actual_floor_height = floor_img.get_height()
        scale_factor = FLOOR_HEIGHT / actual_floor_height
        assets['floor'] = pygame.transform.scale(floor_img, (int(floor_img.get_width() * scale_factor), FLOOR_HEIGHT))
        # OR just scale width to screen width if aspect ratio should be kept:
        # assets['floor'] = pygame.transform.scale(floor_img, (SCREEN_WIDTH, FLOOR_HEIGHT))


        # --- Sounds (Optional Example) ---
        # pygame.mixer.init() # Initialize the mixer (call once before loading sounds)
        # assets['sound_flap'] = pygame.mixer.Sound('assets/flap.wav')
        # assets['sound_hit'] = pygame.mixer.Sound('assets/hit.wav')
        # assets['sound_point'] = pygame.mixer.Sound('assets/point.wav')

        print("Assets loaded successfully.")
        assets['use_images'] = True # Flag to indicate images are loaded

    except pygame.error as e:
        print(f"Error loading assets: {e}. Using basic shapes.")
        assets['use_images'] = False
        # Define fallback sizes if images fail
        assets['bird_rect_size'] = (34, 24)
        assets['pipe_rect_size'] = (70, 500) # Example default height
        assets['floor_height'] = FLOOR_HEIGHT # Use constant
        # Define fallback colors
        assets['background_color'] = (135, 206, 235)
        assets['bird_color'] = (255, 200, 0)
        assets['pipe_color'] = (0, 150, 0)
        assets['floor_color'] = (222, 184, 135)

    return assets

# --- Initialization ---
pygame.init()
# pygame.mixer.init() # Call if using sounds
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Flappy Bird Clone")
clock = pygame.time.Clock()
FPS = 60
game_font = pygame.font.Font(None, 40) # Use default font, size 40

# --- Load Assets ---
assets = load_assets() # Load everything into the assets dictionary

# --- Bird Setup ---
if assets['use_images']:
    bird_surface = assets['bird'] # The loaded image surface
    bird_rect = bird_surface.get_rect(center=(BIRD_START_X, BIRD_START_Y))
else:
    bird_surface = None # No surface needed for drawing rects
    bird_rect = pygame.Rect(BIRD_START_X, BIRD_START_Y - assets['bird_rect_size'][1] // 2,
                            assets['bird_rect_size'][0], assets['bird_rect_size'][1])
bird_movement = 0

# --- Pipe Setup ---
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, PIPE_FREQUENCY)

# --- Floor Setup ---
floor_x_pos = 0 # X position for scrolling the floor

# --- Game State Variables ---
game_active = True
score = 0
high_score = 0
# Use a set to efficiently track IDs of pipes we've scored from
score_counted_pipes = set()

# --- Helper Functions ---

def get_pipe_dimensions():
    """Returns width and height, either from image or fallback."""
    if assets['use_images']:
        return assets['pipe'].get_width(), assets['pipe'].get_height()
    else:
        return assets['pipe_rect_size'][0], assets['pipe_rect_size'][1]

def create_pipe():
    pipe_width, pipe_height = get_pipe_dimensions()
    random_pipe_y = random.choice(PIPE_HEIGHTS) # Y position of the TOP of the bottom pipe image

    bottom_pipe_rect = pygame.Rect(SCREEN_WIDTH + 10, random_pipe_y, pipe_width, pipe_height)

    top_pipe_y = random_pipe_y - PIPE_GAP - pipe_height
    top_pipe_rect = pygame.Rect(SCREEN_WIDTH + 10, top_pipe_y, pipe_width, pipe_height)

    return bottom_pipe_rect, top_pipe_rect

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= PIPE_SPEED
    visible_pipes = [pipe for pipe in pipes if pipe.right > -50]
    # Also remove pipes from the score_counted_pipes set if they are removed from screen
    # This prevents the set from growing indefinitely
    visible_pipe_ids = {id(p) for p in visible_pipes}
    global score_counted_pipes
    score_counted_pipes = {pipe_id for pipe_id in score_counted_pipes if pipe_id in visible_pipe_ids}

    return visible_pipes

def draw_pipes(pipes):
    pipe_width, pipe_height = get_pipe_dimensions() # Needed to check position
    current_floor_height = assets.get('floor_height', FLOOR_HEIGHT) # Get floor height safely
    for pipe_rect in pipes:
        if assets['use_images']:
            pipe_surface = assets['pipe']
            # Determine if it's a top or bottom pipe based on its position
            # A simple check: bottom pipes are usually lower on the screen
            if pipe_rect.top >= SCREEN_HEIGHT - pipe_height - current_floor_height:
                 screen.blit(pipe_surface, pipe_rect)
            else: # It's a top pipe, needs to be flipped vertically
                flip_pipe = pygame.transform.flip(pipe_surface, False, True)
                screen.blit(flip_pipe, pipe_rect)
        else:
            pygame.draw.rect(screen, assets['pipe_color'], pipe_rect)

def check_collision(pipes):
    global bird_rect
    floor_level = SCREEN_HEIGHT - assets.get('floor_height', FLOOR_HEIGHT)
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            # if assets['use_images'] and 'sound_hit' in assets: assets['sound_hit'].play()
            return False
    if bird_rect.top <= -50 or bird_rect.bottom >= floor_level:
        # if assets['use_images'] and 'sound_hit' in assets: assets['sound_hit'].play()
        return False
    return True

# --- SCORING FIX APPLIED HERE ---
def update_score(pipes):
    global score, high_score, score_counted_pipes, bird_rect
    # Identify bottom pipes (more robust check might be needed depending on assets)
    # Check if bird's center passed pipe's center and pipe ID not counted
    potential_score_pipes = [p for p in pipes if p.height > PIPE_GAP and # Basic check for bottom pipe
                             p.centerx < bird_rect.centerx and
                             id(p) not in score_counted_pipes] # <-- Check using id()

    for pipe in potential_score_pipes:
        score += 1
        score_counted_pipes.add(id(pipe)) # <-- Add the id() to the set
        # if assets['use_images'] and 'sound_point' in assets: assets['sound_point'].play()
        print(f"Score! Current score: {int(score)}")

    high_score = max(score, high_score)
# --- END OF SCORING FIX ---

def display_score(game_state):
    """Displays the current score or final score."""
    if game_state == 'main_game':
        score_surface = game_font.render(f"Score: {int(score)}", True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH / 2, 50))
        screen.blit(score_surface, score_rect)
    elif game_state == 'game_over':
        # Display final score
        score_surface = game_font.render(f"Score: {int(score)}", True, WHITE)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH / 2, 50))
        screen.blit(score_surface, score_rect)
        # Display high score
        high_score_surface = game_font.render(f"High Score: {int(high_score)}", True, WHITE)
        high_score_rect = high_score_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))
        screen.blit(high_score_surface, high_score_rect)

def display_game_over():
    """Displays the 'Game Over' message and restart instructions."""
    display_score('game_over') # Show final score and high score

    game_over_text = game_font.render("GAME OVER", True, RED)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40))
    screen.blit( game_over_text, game_over_rect)

    restart_text = game_font.render("Press SPACE to Play Again", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20))
    screen.blit(restart_text, restart_rect)

def draw_floor():
    """Draws the floor and handles scrolling."""
    global floor_x_pos
    floor_y = SCREEN_HEIGHT - assets.get('floor_height', FLOOR_HEIGHT)
    if assets['use_images']:
        screen.blit(assets['floor'], (floor_x_pos, floor_y))
        screen.blit(assets['floor'], (floor_x_pos + SCREEN_WIDTH, floor_y))
    else:
        pygame.draw.rect(screen, assets['floor_color'], (0, floor_y, SCREEN_WIDTH, assets['floor_height']))

def rotate_bird(bird_surf, movement):
    """Rotates the bird surface based on its vertical movement."""
    rotation_angle = max(min(-movement * 3, 25), -90)
    rotated_surface = pygame.transform.rotozoom(bird_surf, rotation_angle, 1)
    return rotated_surface

# --- Main Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False # Exit the main loop entirely
            pygame.quit()   # Clean up pygame
            sys.exit()      # Exit script

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_active: # Only flap if the game is currently active
                    bird_movement = 0
                    bird_movement -= FLAP_STRENGTH
                    # if assets['use_images'] and 'sound_flap' in assets: assets['sound_flap'].play()
                else: # If game is NOT active (game over state), restart
                    print("Restarting game...")
                    game_active = True
                    pipe_list.clear() # Remove all existing pipes
                    score_counted_pipes.clear() # Reset scored pipes set
                    # Reset bird position
                    if assets['use_images']:
                        bird_rect = assets['bird'].get_rect(center=(BIRD_START_X, BIRD_START_Y))
                    else:
                        bird_rect.center = (BIRD_START_X, BIRD_START_Y)
                    bird_movement = 0 # Reset bird speed
                    score = 0 # Reset score to 0

        if event.type == SPAWNPIPE and game_active: # Only spawn pipes if game active
            pipe_list.extend(create_pipe())

    # --- Drawing Background ---
    if assets['use_images']:
        screen.blit(assets['background'], (0, 0))
    else:
        screen.fill(assets.get('background_color', (135, 206, 235))) # Use get for safety

    # --- Game Logic & Drawing (Active Game) ---
    if game_active:
        # Bird Movement
        bird_movement += GRAVITY
        bird_rect.centery += bird_movement

        # Pipe Movement & Drawing
        pipe_list = move_pipes(pipe_list) # Update pipe positions and remove old ones
        draw_pipes(pipe_list) # Now draws images or rects

        # Update Score
        update_score(pipe_list) # Check for scoring opportunities
        display_score('main_game') # Show score during gameplay

        # Bird Drawing (with rotation if using images)
        if assets['use_images']:
            rotated_bird_surface = rotate_bird(assets['bird'], bird_movement)
            rotated_bird_rect = rotated_bird_surface.get_rect(center=bird_rect.center)
            screen.blit(rotated_bird_surface, rotated_bird_rect)
        else:
            pygame.draw.rect(screen, assets.get('bird_color', (255, 200, 0)), bird_rect)

        # Check Collisions (Must be AFTER drawing pipes/bird for the current frame)
        game_active = check_collision(pipe_list) # Update game_active based on collision check

    # --- Game Over State ---
    else:
        # Keep drawing the pipes where they were when the game ended
        draw_pipes(pipe_list)
        # Keep drawing the bird where it crashed
        if assets['use_images']:
             screen.blit(assets['bird'], bird_rect) # No rotation on game over
        else:
             pygame.draw.rect(screen, assets.get('bird_color', (255, 200, 0)), bird_rect)
        # Display the Game Over message
        display_game_over()


    # --- Floor Scrolling and Drawing (Always draw floor) ---
    if assets['use_images']:
        floor_x_pos -= PIPE_SPEED # Scroll floor
        if floor_x_pos <= -SCREEN_WIDTH: # Reset position for seamless loop
            floor_x_pos = 0
    draw_floor() # Call the function to draw the (potentially scrolling) floor

    # --- Update Display and Control FPS ---
    pygame.display.update()
    clock.tick(FPS)

# --- Quit (This part might not be reached if sys.exit() was called in the loop) ---
pygame.quit()
sys.exit()