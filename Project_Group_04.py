import pygame
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Archery Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

# Global variables for game logic
teer_pos = [100, HEIGHT // 2]  # Initial position of the arrow
BOW_POSITION = [100, HEIGHT // 2]
teer_angle = 0  # Angle of the arrow in degrees
teer_speed = 20
teer_fired = False

# Target settings
TARGET_RADIUS = 50
TARGET_SCORES = {
    GREEN: 10,
    BLUE: 20,
    YELLOW: 30,
    RED: 50
}
SCORE = 0
CHANCES = 3
GAME_OVER = False
PAUSED = False
drop_speed = 3
# List to hold targets
targets = []

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Midpoint line algorithm
def draw_line(surface, x1, y1, x2, y2, color):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    if x1 < x2:
        step_x = 1
    else:
        step_x = -1
    if y1 < y2:
        step_y = 1
    else:
        step_y = -1
    err = dx - dy

    while (x1, y1) != (x2, y2):
        surface.set_at((x1, y1), color)
        e2 = 2 * err

        # Adjust x1 and error term if necessary
        if e2 > -dy:
            err -= dy
            x1 += step_x

        # Adjust y1 and error term if necessary
        if e2 < dx:
            err += dx
            y1 += step_y

    # Ensure the last point is drawn
    surface.set_at((x2, y2), color)

# Midpoint circle algorithm for the target
def draw_circle(surface, xc, yc, r, color):
    x, y = 0, r
    d = 1 - r
    while x <= y:
        for point in [(x, y), (y, x), (-x, y), (-y, x), (-x, -y), (-y, -x), (x, -y), (y, -x)]:
            surface.set_at((xc + point[0], yc + point[1]), color)
        x += 1
        if d < 0:
            d += 2 * x + 1
        else:
            y -= 1
            d += 2 * (x - y) + 1

# Function to draw the target with filled colors
def draw_filled_circle(surface, xc, yc, r, color):
    for radius in range(r, 0, -1):  # Fill the circle by drawing smaller circles inside
        draw_circle(surface, xc, yc, radius, color)

# Target class
class Target:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.colors = random.sample([GREEN, BLUE, YELLOW, RED], 4)  # Randomize colors

    def draw(self):
        for i, radius in enumerate(range(TARGET_RADIUS, 0, -TARGET_RADIUS // len(self.colors))):
            draw_filled_circle(screen, self.x, self.y, radius, self.colors[i])

    def update(self, drop_speed):
        self.y += drop_speed  # Move down the screen
        if self.y - TARGET_RADIUS > HEIGHT:  # Check if the target moves off-screen
            targets.remove(self)  # Remove the target when off-screen

# Calculate the score based on arrow position
def calculate_score(teer_tip_x, teer_tip_y):
    global SCORE
    for target in targets[:]:
        distance = math.sqrt((teer_tip_x - target.x) ** 2 + (teer_tip_y - target.y) ** 2)
        if distance <= TARGET_RADIUS:
            for i, radius in enumerate(range(TARGET_RADIUS, 0, -TARGET_RADIUS // len(target.colors))):
                if distance <= radius:
                    color = target.colors[i]
                    SCORE += TARGET_SCORES[color]
                    targets.remove(target)
                    return True  # Indicate a hit
    return False

# Function to draw the arrow
def draw_arrow(surface, pos, angle, color):
    x, y = pos
    length = 80
    radians = math.radians(angle)
    end_x = x + int(length * math.cos(radians))
    end_y = y - int(length * math.sin(radians))

    for offset in range(-2, 3):
        draw_line(surface, x + offset, y, end_x + offset, end_y, color)

    head_length = 15
    head_width = 10
    tip_x = end_x
    tip_y = end_y
    left_x = tip_x - int(head_length * math.cos(radians + math.pi / 6))
    left_y = tip_y + int(head_length * math.sin(radians + math.pi / 6))
    right_x = tip_x - int(head_length * math.cos(radians - math.pi / 6))
    right_y = tip_y + int(head_length * math.sin(radians - math.pi / 6))

    draw_line(surface, tip_x, tip_y, left_x, left_y, color)
    draw_line(surface, tip_x, tip_y, right_x, right_y, color)
    draw_line(surface, left_x, left_y, right_x, right_y, color)

# Draw the bow
def draw_bow(surface, teer_pos, color):
    x, y = teer_pos
    bow_radius = 60
    bow_width = 5

    for angle in range(90, 270):
        radians = math.radians(angle)
        bow_x = x - int(bow_radius * math.cos(radians))
        bow_y = y - int(bow_radius * math.sin(radians))
        for offset in range(-bow_width // 2, bow_width // 2 + 1):
            surface.set_at((bow_x + offset, bow_y), color)

    draw_arrow(surface, teer_pos, teer_angle, WHITE)
    string_start_x = x - int(bow_radius * math.cos(math.radians(90)))
    string_start_y = y - int(bow_radius * math.sin(math.radians(90)))
    string_end_x = x - int(bow_radius * math.cos(math.radians(270)))
    string_end_y = y - int(bow_radius * math.sin(math.radians(270)))
    draw_line(surface, string_start_x, string_start_y, string_end_x, string_end_y, color)

# Restart the game
def restart_game():
    global SCORE, CHANCES, GAME_OVER, teer_pos, teer_angle, targets
    SCORE = 0
    CHANCES = 3
    GAME_OVER = False
    teer_pos = [100, HEIGHT // 2]
    teer_angle = 0
    targets.clear()  # Clear existing targets

# Update arrow position
def update_arrow():
    global teer_pos, teer_fired, CHANCES, GAME_OVER
    if teer_fired:
        radians = math.radians(teer_angle)
        teer_pos[0] += int(teer_speed * math.cos(radians))
        teer_pos[1] -= int(teer_speed * math.sin(radians))
        teer_length = 50
        teer_tip_x = teer_pos[0] + int(teer_length * math.cos(radians))
        teer_tip_y = teer_pos[1] - int(teer_length * math.sin(radians))
        hit_target = calculate_score(teer_tip_x, teer_tip_y)

        if (teer_tip_x < 0 or teer_tip_x > WIDTH or teer_tip_y < 0 or teer_tip_y > HEIGHT or hit_target):
            if not hit_target:
                CHANCES -= 1
            teer_fired = False
            teer_pos[:] = [100, HEIGHT // 2]
            if CHANCES == 0:
                GAME_OVER = True

# Function to handle keyboard events
def handle_keyboard_event(event):
    global teer_angle, teer_fired, GAME_OVER, PAUSED

    if event.type == pygame.KEYDOWN:
        if not GAME_OVER and not PAUSED:
            if event.key == pygame.K_UP:  # Rotate arrow up
                teer_angle = min(teer_angle + 5, 90)
            elif event.key == pygame.K_DOWN:  # Rotate arrow down
                teer_angle = max(teer_angle - 5, -90)
            elif event.key == pygame.K_SPACE:  # Fire the arrow
                if not teer_fired:
                    teer_fired = True

        if event.key == pygame.K_p:  # Toggle pause
            PAUSED = not PAUSED

        if event.key == pygame.K_r:  # Restart the game
            restart_game()

        if event.key == pygame.K_ESCAPE:  # Exit the game
            pygame.quit()
            exit()
def can_spawn_target(new_x, new_y):
    """Check if a target can be spawned at the given coordinates."""
    for target in targets:
        distance = math.sqrt((new_x - target.x) ** 2 + (new_y - target.y) ** 2)
        if distance < 2 * TARGET_RADIUS:  # Ensure no overlap
            return False
    return True

# Main game loop
def main():
    global GAME_OVER
    running = True
    spawn_timer = 0  # Timer for spawning targets
    while running:
        screen.fill((BLACK))  # Updated background color

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            handle_keyboard_event(event)

        if not GAME_OVER and not PAUSED:
            update_arrow()

            # Spawn a new target if the timer condition is met
            spawn_timer += 1
            if spawn_timer >= 30:
                potential_x = WIDTH - 150
                potential_y = random.randint(100, HEIGHT - 100)

                if can_spawn_target(potential_x, potential_y):
                    targets.append(Target(potential_x, potential_y))
                    spawn_timer = 0  # Reset spawn timer only if a target is added

            # Update and draw each target
            for target in targets[:]:
                target.update(drop_speed)
                target.draw()

            draw_bow(screen, BOW_POSITION, WHITE)

            if teer_fired:
                draw_arrow(screen, teer_pos, teer_angle, YELLOW)

        # Display score, chances, paused state, and game over message
        font = pygame.font.SysFont(None, 36)
        screen.blit(font.render(f"Score: {SCORE}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Chances: {CHANCES}", True, WHITE), (10, 50))

        if PAUSED:
            screen.blit(font.render("Paused! Press P to Resume", True, WHITE), (WIDTH // 2 - 150, HEIGHT // 2))

        if GAME_OVER:
            screen.blit(font.render("Game Over! Press R to Restart or ESC to Exit", True, WHITE), (WIDTH // 2 - 250, HEIGHT - 50))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
