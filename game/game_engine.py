#edited code
import json
import pygame
import time
from collections import deque

from game.maze import generate_maze, CELL
from game.player import Player


FPS = 60

BG = (240, 235, 220)
WALL_COLOR = (40, 40, 60)
EXIT_COLOR = (80, 200, 80)

DIFFICULTIES = {
    "Easy": (10, 8),
    "Medium": (15, 13),
    "Hard": (20, 16),
}

LEADERBOARD_FILE = "leaderboard.json"
FOG_RADIUS = 120


class GameEngine:

    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont(
            "monospace", 36, bold=True
        )
        self.small_font = pygame.font.SysFont("monospace", 18)

        self.difficulty = None
        self.won = False

        self.path = []
        self.show_path = False

        self.leaderboard = self.load_leaderboard()

        self.run()

    # ---------------------------------------------------------
    # LEADERBOARD
    # ---------------------------------------------------------

    def load_leaderboard(self):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                data = json.load(f)

            if not isinstance(data, list):
                return []

            return sorted(
                [float(time_value) for time_value in data]
            )[:5]

        except (
            FileNotFoundError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ):
            return []

    def save_leaderboard(self):
        self.leaderboard = sorted(
            self.leaderboard
        )[:5]

        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(
                self.leaderboard,
                f,
                indent=2
            )

    def save_time(self):
        self.leaderboard.append(
            round(self.elapsed, 2)
        )

        self.leaderboard = sorted(
            self.leaderboard
        )[:5]

        self.save_leaderboard()

    # ---------------------------------------------------------
    # DIFFICULTY SELECTION
    # ---------------------------------------------------------

    def show_difficulty_screen(self):

        screen = pygame.display.set_mode(
            (800, 600)
        )

        pygame.display.set_caption(
            "Maze Runner - Select Difficulty"
        )

        buttons = {}

        for i, difficulty in enumerate(DIFFICULTIES):

            buttons[difficulty] = pygame.Rect(
                0,
                0,
                260,
                60
            )

            buttons[difficulty].center = (
                400,
                230 + i * 90
            )

        while True:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):

                    for difficulty, rect in buttons.items():

                        if rect.collidepoint(event.pos):
                            return difficulty

            screen.fill(BG)

            title = self.big_font.render(
                "Select Difficulty",
                True,
                WALL_COLOR
            )

            screen.blit(
                title,
                (
                    400 - title.get_width() // 2,
                    100
                )
            )

            for difficulty, rect in buttons.items():

                pygame.draw.rect(
                    screen,
                    WALL_COLOR,
                    rect,
                    border_radius=8
                )

                label = self.font.render(
                    difficulty,
                    True,
                    (240, 240, 240)
                )

                screen.blit(
                    label,
                    (
                        rect.centerx
                        - label.get_width() // 2,
                        rect.centery
                        - label.get_height() // 2
                    )
                )

            pygame.display.flip()
            self.clock.tick(FPS)

    # ---------------------------------------------------------
    # RESET / NEW MAZE
    # ---------------------------------------------------------

    def reset(self):

        self.cols, self.rows = DIFFICULTIES[
            self.difficulty
        ]

        self.width = self.cols * CELL
        self.maze_height = self.rows * CELL
        self.height = self.maze_height + 60

        self.screen = pygame.display.set_mode(
            (self.width, self.height)
        )

        pygame.display.set_caption(
            f"Maze Runner - {self.difficulty}"
        )

        # Existing maze generation system
        self.walls = generate_maze(
            self.cols,
            self.rows
        )

        self.player = Player(0, 0)

        self.exit_rect = pygame.Rect(
            (self.cols - 1) * CELL + 5,
            (self.rows - 1) * CELL + 5,
            CELL - 10,
            CELL - 10
        )

        self.start_time = time.time()
        self.elapsed = 0

        self.won = False

        # BFS path state
        self.path = []
        self.show_path = False

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                # Generate a new maze
                if event.key == pygame.K_r:
                    self.reset()

                # Toggle BFS shortest path
                elif (
                    event.key == pygame.K_h
                    and not self.won
                ):

                    self.show_path = not self.show_path

                    if self.show_path:
                        self.path = (
                            self.find_shortest_path()
                        )

        return True

    # ---------------------------------------------------------
    # GAME UPDATE
    # ---------------------------------------------------------

    def update(self):

        if self.won:
            return

        keys = pygame.key.get_pressed()

        # Existing movement system
        self.player.move(
            keys,
            self.walls,
            self.rows,
            self.cols
        )

        self.elapsed = (
            time.time() - self.start_time
        )

        # Exit detection
        if self.player.rect.colliderect(
            self.exit_rect
        ):

            self.won = True

            # Save completion time
            self.save_time()

    # ---------------------------------------------------------
    # BFS SOLVER
    # ---------------------------------------------------------

    def find_shortest_path(self):

        start = (0, 0)

        target = (
            self.rows - 1,
            self.cols - 1
        )

        queue = deque([start])

        previous = {
            start: None
        }

        while queue:

            r, c = queue.popleft()

            if (r, c) == target:
                break

            # -------------------------
            # NORTH
            # -------------------------

            if (
                r > 0
                and not self.walls[r][c][0]
            ):

                neighbor = (
                    r - 1,
                    c
                )

                if neighbor not in previous:

                    previous[neighbor] = (
                        r,
                        c
                    )

                    queue.append(
                        neighbor
                    )

            # -------------------------
            # SOUTH
            # -------------------------

            if (
                r < self.rows - 1
                and not self.walls[r][c][1]
            ):

                neighbor = (
                    r + 1,
                    c
                )

                if neighbor not in previous:

                    previous[neighbor] = (
                        r,
                        c
                    )

                    queue.append(
                        neighbor
                    )

            # -------------------------
            # EAST
            # -------------------------

            if (
                c < self.cols - 1
                and not self.walls[r][c][2]
            ):

                neighbor = (
                    r,
                    c + 1
                )

                if neighbor not in previous:

                    previous[neighbor] = (
                        r,
                        c
                    )

                    queue.append(
                        neighbor
                    )

            # -------------------------
            # WEST
            # -------------------------

            if (
                c > 0
                and not self.walls[r][c][3]
            ):

                neighbor = (
                    r,
                    c - 1
                )

                if neighbor not in previous:

                    previous[neighbor] = (
                        r,
                        c
                    )

                    queue.append(
                        neighbor
                    )

        # No path found
        if target not in previous:
            return []

        # Reconstruct shortest path
        path = []

        current = target

        while current is not None:

            path.append(current)

            current = previous[current]

        path.reverse()

        return path

    # ---------------------------------------------------------
    # DRAW MAZE
    # ---------------------------------------------------------

    def draw_maze(self):

        wall_w = 3

        for r in range(self.rows):

            for c in range(self.cols):

                x = c * CELL
                y = r * CELL

                w = self.walls[r][c]

                # North
                if w[0]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x + CELL, y),
                        wall_w
                    )

                # South
                if w[1]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        wall_w
                    )

                # East
                if w[2]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        wall_w
                    )

                # West
                if w[3]:
                    pygame.draw.line(
                        self.screen,
                        WALL_COLOR,
                        (x, y),
                        (x, y + CELL),
                        wall_w
                    )

    # ---------------------------------------------------------
    # DRAW BFS PATH
    # ---------------------------------------------------------

    def draw_path(self):

        if not self.show_path:
            return

        for r, c in self.path:

            rect = pygame.Rect(
                c * CELL + 7,
                r * CELL + 7,
                CELL - 14,
                CELL - 14
            )

            pygame.draw.rect(
                self.screen,
                (255, 210, 70),
                rect,
                border_radius=4
            )

    # ---------------------------------------------------------
    # FOG OF WAR
    # ---------------------------------------------------------

    def draw_fog(self):

        fog = pygame.Surface(
            (
                self.width,
                self.maze_height
            ),
            pygame.SRCALPHA
        )

        # Dark overlay over entire maze
        fog.fill(
            (0, 0, 0, 220)
        )

        # Transparent circular visibility area
        pygame.draw.circle(
            fog,
            (0, 0, 0, 0),
            self.player.rect.center,
            FOG_RADIUS
        )

        self.screen.blit(
            fog,
            (0, 0)
        )

    # ---------------------------------------------------------
    # LEADERBOARD ON WIN SCREEN
    # ---------------------------------------------------------

    def draw_leaderboard(self):

        title = self.font.render(
            "Leaderboard",
            True,
            (240, 240, 240)
        )

        self.screen.blit(
            title,
            (
                self.width // 2
                - title.get_width() // 2,
                self.maze_height // 2 + 5
            )
        )

        if not self.leaderboard:

            text = self.small_font.render(
                "No times yet",
                True,
                (220, 220, 220)
            )

            self.screen.blit(
                text,
                (
                    self.width // 2
                    - text.get_width() // 2,
                    self.maze_height // 2 + 45
                )
            )

            return

        for i, score in enumerate(
            self.leaderboard
        ):

            text = self.small_font.render(
                f"{i + 1}. {score:.2f}s",
                True,
                (220, 220, 220)
            )

            self.screen.blit(
                text,
                (
                    self.width // 2
                    - text.get_width() // 2,
                    self.maze_height // 2
                    + 40
                    + i * 25
                )
            )

    # ---------------------------------------------------------
    # DRAW EVERYTHING
    # ---------------------------------------------------------

    def draw(self):

        self.screen.fill(BG)

        # Maze
        self.draw_maze()

        # BFS solution
        self.draw_path()

        # Exit
        pygame.draw.rect(
            self.screen,
            EXIT_COLOR,
            self.exit_rect,
            border_radius=4
        )

        ex_label = self.font.render(
            "EXIT",
            True,
            (20, 80, 20)
        )

        self.screen.blit(
            ex_label,
            (
                self.exit_rect.x + 2,
                self.exit_rect.y + 4
            )
        )

        # Player
        self.player.draw(
            self.screen
        )

        # Fog
        self.draw_fog()

        # HUD
        hud = pygame.Rect(
            0,
            self.maze_height,
            self.width,
            60
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 50),
            hud
        )

        time_surf = self.small_font.render(
            f"Time: {self.elapsed:.1f}s   H = Path   R = New Maze",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            time_surf,
            (
                10,
                self.maze_height + 18
            )
        )

        # Win screen
        if self.won:

            overlay = pygame.Surface(
                (
                    self.width,
                    self.maze_height
                ),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 180)
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            msg = self.big_font.render(
                f"Solved in {self.elapsed:.1f}s!",
                True,
                (80, 240, 80)
            )

            self.screen.blit(
                msg,
                (
                    self.width // 2
                    - msg.get_width() // 2,
                    55
                )
            )

            self.draw_leaderboard()

            sub = self.small_font.render(
                "Press R for a new maze",
                True,
                (200, 200, 200)
            )

            self.screen.blit(
                sub,
                (
                    self.width // 2
                    - sub.get_width() // 2,
                    self.maze_height - 45
                )
            )

        pygame.display.flip()

    # ---------------------------------------------------------
    # MAIN GAME LOOP
    # ---------------------------------------------------------

    def run(self):

        self.difficulty = (
            self.show_difficulty_screen()
        )

        if self.difficulty is None:
            return

        self.reset()

        running = True

        while running:

            running = self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()
