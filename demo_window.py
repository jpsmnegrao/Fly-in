"""Pygame-based interactive demo window for the Fly-In simulation.

Renders the map, zones, and connections, and provides a placeholder
walking-sprite animation and click-to-inspect UI for zones/connections.
"""


import pygame
from data import MapData, Zone, Connection
from map_renderer import MapRenderer


class DemoWindow():
    """mambo"""

    def __init__(self, map_data: MapData) -> None:
        """Interactive pygame window for map and demo animation visualization.

        Handles window setup, user input (clicks and key presses), rendering
        of the map/zones/connections, an info panel, and a placeholder sprite
        animation used to preview movement along the map area.
        """
        # pygame initialization
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("==== Fly-In ====")
        # window
        self.screen = pygame.display.set_mode((1600, 800))
        self.clock = pygame.time.Clock()
        # Data
        self.map_data = map_data
        self.start_zone = next(
           z for z in self.map_data.zones if z.hub_type == "start"
        )
        self.map_area = pygame.Rect(
                self.map_data.map_x,
                self.map_data.map_y,
                self.map_data.map_width,
                self.map_data.map_height
            )
        # Rendering
        self.map_renderer = MapRenderer(map_data, self.screen)
        self.start_pos = self.map_renderer.zone_position(self.start_zone)
        # UI
        self.font = pygame.font.SysFont(None, 25)
        self.title = self.font.render(" ====  Fly-In  ==== ", True, "gray")
        self.title_pos = self.title.get_rect(center=(800, 25))
        self.bottoml_panel = pygame.Rect(95, 670, 400, 130)
        self.bottomc_panel = pygame.Rect(495, 670, 600, 130)
        self.bottomr_panel = pygame.Rect(1095, 670, 400, 130)
        # Application state
        self.running = True
        self.running_animation = False
        self.selected_object: Zone | Connection | None = None
        # Animation assets
        self.walk = pygame.transform.flip(
            pygame.image.load("assets/wwalk.png"), True, False)
        self.walk.set_colorkey((128, 128, 192))
        self.walk_down = pygame.transform.flip(
            pygame.image.load("assets/wwalkd.png"), True, False)
        self.walk_down.set_colorkey((128, 128, 192))
        self.walk_up = pygame.transform.flip(
            pygame.image.load("assets/wwalku.png"), True, False)
        self.walk_up.set_colorkey((128, 128, 192))
        # Animation state
        self.frame_height = self.walk.get_height() // 15
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_direction = 1
        self.speed: float = 590 / 5000
        self.x = float(self.start_pos[0] - self.walk.get_width() // 2)
        self.y = float(self.start_pos[1] - self.frame_height // 2)

    def run(self) -> None:
        """Run the main loop: handle input, update animation, draw, repeat.

        Loops at 60 FPS until the window is closed or the user quits, then
        shuts down pygame.
        """
        while self.running:
            self.handle_events()
            dt = self.clock.tick(60)
            self.update_animation(dt)
            self.draw()
        pygame.quit()

    def handle_events(self) -> None:
        """Process pygame events: quit, key presses, and mouse clicks.

        Handles window close, Q/ESC to quit, SPACE to start/pause the
        placeholder animation, 0 to reset it, and left-click to select a zone
        or connection.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if not self.running_animation:
                        self.running_animation = True
                        self.frame_timer = 0
                        self.frame_direction = 1
                    else:
                        self.running_animation = False
                elif event.key == pygame.K_0 or event.key == pygame.K_KP0:
                    self.reset_animation()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                self.handle_click(mx, my)

    def handle_click(self, mx: int, my: int) -> None:
        """Select the zone or connection under the given click position.

        Checks zones first (circular hit area), then connections (rectangular
        hit area centered on the connection's midpoint). Sets
        self.selected_object to the first match found, if any.

        Args:
            mx: X coordinate of the click, in screen pixels.
            my: Y coordinate of the click, in screen pixels.
        """
        for zone in self.map_data.zones:
            x, y = self.map_renderer.zone_position(zone)
            r = self.map_renderer.zone_radius

            dx = mx - x
            dy = my - y

            if dx * dx + dy * dy <= r * r:
                self.selected_object = zone
                return
        for connection in self.map_data.connections:
            start = self.map_renderer.zone_position(
                self.map_renderer.zone_dict[connection.zone_a]
            )
            end = self.map_renderer.zone_position(
                self.map_renderer.zone_dict[connection.zone_b]
            )
            rect = pygame.Rect(
                0, 0,
                max(1, self.map_renderer.zone_radius),
                max(1, self.map_renderer.zone_radius // 2)
            )
            rect.center = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
            if rect.collidepoint(mx, my):
                self.selected_object = connection
                return

    def draw(self) -> None:
        """Render one full frame: background, map, panels, and sprite.

        Clears the screen, draws the title, map area, connections, zones, info
        panels, and the current animation frame, then flips the display buffer.
        """
        self.screen.fill("black")
        self.screen.blit(self.title, self.title_pos)
        pygame.draw.rect(self.screen, "gray", self.map_area)
        self.map_renderer.draw_connections()
        self.map_renderer.draw_zones()
        self.draw_info_panel()
        current_sprite = self.walk
        frame_area = pygame.Rect(
            0, self.current_frame * self.frame_height,
            current_sprite.get_width(), self.frame_height)
        self.screen.blit(current_sprite, (self.x, self.y), frame_area)
        pygame.display.flip()

    def draw_info_panel(self) -> None:
        """Draw all three bottom info panels: simulation, selection, help."""
        self.draw_simulation_panel()
        self.draw_selection_panel()
        self.draw_help_panel()

    def draw_simulation_panel(self) -> None:
        """Draw the bottom-left panel showing simulation status.

        Note:
            "Total drone moves", "Turn", and "Stat 4" are placeholder labels
            with no value rendered yet. TODO: wire these up once simulation
            state is tracked/exposed here.
        """
        rect = self.bottoml_panel
        font = pygame.font.SysFont(None, 20)
        lines = [
            "SIMULATION:",
            "",
            "State: ",
            f"Number of drones: {self.map_data.nb_drones}",
            "Total drone moves: ",
            "Turn: ",
            "Stat 4: "
        ]
        x = rect.x + 10
        y = rect.y + 10
        line_height = font.get_linesize()
        for i, line in enumerate(lines):
            text = font.render(line, True, "white")
            self.screen.blit(
                text, text.get_rect(topleft=(x, y + i * line_height)))

    def draw_selection_panel(self) -> None:
        """Draw the bottom-center panel showing the currently selected zone or
        connection's details, or a prompt if nothing is selected.
        """
        rect = self.bottomc_panel
        font = pygame.font.SysFont(None, 20)
        x = rect.x + 10
        y = rect.y + 10
        line_height = font.get_linesize()
        if self.selected_object is None:
            lines = ["Click on a zone or connection node"]
        elif isinstance(self.selected_object, Zone):
            lines = [
                "ZONE:",
                "",
                f"Name: {self.selected_object.name}",
                f"Type: {self.selected_object.zone_type}",
                f"Current drones: {self.selected_object.drone_count}",
                f"Max capacity: {self.selected_object.max_drones}",
            ]
        elif isinstance(self.selected_object, Connection):
            c = self.selected_object
            lines = [
                "CONNECTION:",
                "",
                f"Source: {c.zone_a}",
                f"Destination: {c.zone_b}",
                f"Drones: {c.drone_count}",
                f"Max capacity: {c.max_capacity}",
            ]
        for i, line in enumerate(lines):
            text = font.render(line, True, "white")
            self.screen.blit(text, (x, y + i * line_height))

    def draw_help_panel(self) -> None:
        """Draw the bottom-right panel showing keyboard controls and
        interaction hints.
        """
        rect = self.bottomr_panel
        font = pygame.font.SysFont(None, 20)
        lines = [
            "CONTROLS:",
            "SPACE: start / pause simulation",
            "0: reset animation",
            "ESC / Q: quit window",
            "",
            "INTERACTIONS:",
            "Click on a zone or connection to",
            "see their information"
        ]
        x = rect.x + 10
        y = rect.y + 10
        line_height = font.get_linesize()
        for i, line in enumerate(lines):
            text = font.render(line, True, "white")
            self.screen.blit(text, (x, y + i * line_height))

    def update_animation(self, dt: int) -> None:
        """Advance the placeholder walking animation by one frame step.

        Args:
            dt: Milliseconds elapsed since the last frame, used to time frame
                advancement and horizontal movement.

        Note:
            This animates a single sprite walking left-to-right across the map
            area; it is not yet driven by actual drone positions or simulation
            state. TODO: replace with real drone rendering.
        """
        if self.running_animation:
            self.frame_timer += dt
            if self.frame_timer > 100:
                self.current_frame += self.frame_direction
                if self.current_frame >= 14 or self.current_frame <= 0:
                    self.frame_direction *= -1
                self.frame_timer = 0
            self.x += self.speed * dt
            if self.x > self.map_data.map_x + self.map_data.map_width \
                    - 110:
                self.x = (
                    self.map_data.map_x + self.map_data.map_width - 110)
                self.running_animation = False

    def reset_animation(self) -> None:
        """Reset the placeholder animation to its starting position and frame,
        and stop it if running.
        """
        self.x = float(
            self.start_pos[0] - self.walk.get_width() // 2)
        self.y = float(
            self.start_pos[1] - self.frame_height // 2)
        self.current_frame = 0
        self.frame_timer = 0
        self.running_animation = False
