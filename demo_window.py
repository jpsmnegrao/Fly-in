"""Pygame-based interactive demo window for the Fly-In simulation.

Renders the map, animates drone movement, and provides controls for stepping
through the simulation and inspecting zones and connections.
"""


import pygame
from typing import Any
from data import MapData, Zone, Connection
from map_renderer import MapRenderer
from simulation import Simulation


class DemoWindow:
    """Interactive pygame window for visualizing the Fly-In simulation.

    Handles rendering, user interaction, and animation while coordinating
    simulation steps with the Simulation object.
    """

    def __init__(self, map_data: MapData, simulation: Simulation) -> None:
        """Initialize the demo window.

        Creates the pygame window, initializes rendering resources, UI state,
        animation state, and simulation-related data.
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
        self.simulation = simulation
        self.last_step_time = 0
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
        self.drone_anim: dict[str, dict[str, Any]] = {
            d.id: {
                "start_pos": self.map_renderer.zone_position(
                    self.map_renderer.zone_dict[d.current_zone]),
                "end_pos": self.map_renderer.zone_position(
                    self.map_renderer.zone_dict[d.current_zone]),
                "progress": 1.0
            }
            for d in simulation.drones
        }
        # Animation state
        self.auto_play: bool = True
        self.step_requested: bool = False
        self.reset_requested: bool = False
        self.frame_height = self.walk.get_height() // 15
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_direction = 1

    def run(self) -> bool:
        """Run the main application loop until the window is closed or reset.

        Loops at 60 FPS, processes input, updates the simulation and animation,
        then shuts down pygame before returning whether a reset was requested.
        """
        while self.running:
            pygame.event.pump()
            self.handle_events()
            dt = self.clock.tick(60)
            self.last_step_time += dt
            should_step = (
                (self.auto_play and self.running_animation and
                 self.last_step_time > 1000) or (not self.auto_play and
                                                 self.step_requested)
            )
            if should_step:
                self.step_requested = False
                pre_positions = {
                    d.id: self.map_renderer.zone_position(
                        self.map_renderer.zone_dict[d.current_zone])
                    for d in self.simulation.drones
                }
                completed_transit, arriving = self.simulation.step()
                for drone in self.simulation.drones:
                    end_pos = self.map_renderer.zone_position(
                        self.map_renderer.zone_dict[drone.current_zone])
                    self.drone_anim[drone.id]["start_pos"] = pre_positions.get(
                        drone.id, end_pos)
                    self.drone_anim[drone.id]["end_pos"] = end_pos
                    self.drone_anim[drone.id]["progress"] = 0.0
                for drone in self.simulation.drones:
                    if drone.in_transit and not drone.arriving:
                        dest_zone = self.map_renderer.zone_dict[
                            drone.destination_zone]
                        dest_pos = self.map_renderer.zone_position(dest_zone)
                        origin_pos = pre_positions.get(drone.id, dest_pos)
                        mid_x = (origin_pos[0] + dest_pos[0]) // 2
                        mid_y = (origin_pos[1] + dest_pos[1]) // 2
                        self.drone_anim[drone.id]["end_pos"] = (mid_x, mid_y)
                for drone in arriving:
                    dest_pos = self.map_renderer.zone_position(
                        self.map_renderer.zone_dict[drone.current_zone])
                    origin_name = drone.current_connection.split("-")[0]
                    origin_pos = self.map_renderer.zone_position(
                        self.map_renderer.zone_dict[origin_name])
                    mid_x = (origin_pos[0] + dest_pos[0]) // 2
                    mid_y = (origin_pos[1] + dest_pos[1]) // 2
                    self.drone_anim[drone.id]["start_pos"] = (mid_x, mid_y)
                    self.drone_anim[drone.id]["end_pos"] = dest_pos
                    self.drone_anim[drone.id]["progress"] = 0.0
                self.last_step_time = 0
            self.update_animation(dt)
            self.draw()
        pygame.quit()
        return self.reset_requested

    def handle_events(self) -> None:
        """Process pygame events.

        Handles window close events, keyboard input for controlling the
        simulation, and mouse clicks for selecting zones or connections.
        """
        simulation_finished = all(d.finished for d in self.simulation.drones)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_m:
                    self.auto_play = not self.auto_play
                elif event.key == pygame.K_SPACE and not simulation_finished:
                    if self.auto_play:
                        self.running_animation = not self.running_animation
                    else:
                        if all(a["progress"] >= 1.0
                                for a in self.drone_anim.values()):
                            self.step_requested = True
                            self.running_animation = True
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
        """Render a complete frame.

        Draws the map, UI panels, and all active drones at their current
        animated positions, then updates the display.
        """
        self.screen.fill("black")
        self.screen.blit(self.title, self.title_pos)
        pygame.draw.rect(self.screen, "gray", self.map_area)
        self.map_renderer.draw_connections()
        self.map_renderer.draw_zones()
        self.draw_info_panel()
        for drone in self.simulation.drones:
            anim = self.drone_anim[drone.id]
            if drone.finished and anim["progress"] >= 1.0:
                continue
            t = anim["progress"]
            sx, sy = anim["start_pos"]
            ex, ey = anim["end_pos"]
            x = int(sx + (ex - sx) * t)
            y = int(sy + (ey - sy) * t)
            zone = self.map_renderer.zone_dict[drone.current_zone]
            path = self.simulation.scheduler.paths.get(drone.id, [])
            if len(path) >= 2:
                next_zone = self.map_renderer.zone_dict[path[1]]
                dy = next_zone.y - zone.y
                if dy < 0:
                    current_sprite = self.walk_up
                elif dy > 0:
                    current_sprite = self.walk_down
                else:
                    current_sprite = self.walk
            else:
                current_sprite = self.walk
            frame_area = pygame.Rect(
                0, self.current_frame * self.frame_height,
                current_sprite.get_width(), self.frame_height)
            self.screen.blit(
                current_sprite,
                (x - current_sprite.get_width() // 2,
                 y - self.frame_height // 2),
                frame_area)
        pygame.display.flip()

    def draw_info_panel(self) -> None:
        """Draw all bottom information panels."""
        self.draw_simulation_panel()
        self.draw_selection_panel()
        self.draw_help_panel()

    def draw_simulation_panel(self) -> None:
        """Draw the bottom-left panel showing simulation status."""
        rect = self.bottoml_panel
        font = pygame.font.SysFont(None, 20)
        if all(d.finished for d in self.simulation.drones):
            state = "Finished"
        elif not self.running_animation:
            state = "Paused"
        else:
            state = "Running"
        lines = [
            "SIMULATION:",
            f"Map: {self.map_data.map_name}",
            f"State: {state}",
            f"Number of drones: {self.map_data.nb_drones}",
            f"Ended: {sum(1 for d in self.simulation.drones if d.finished)}",
            f"Turn: {self.simulation.turn}",
            f"Simulation mode: {'Auto' if self.auto_play else 'Turn-based'}"
        ]
        x = rect.x + 10
        y = rect.y + 10
        line_height = font.get_linesize()
        for i, line in enumerate(lines):
            text = font.render(line, True, "white")
            self.screen.blit(
                text, text.get_rect(topleft=(x, y + i * line_height)))

    def draw_selection_panel(self) -> None:
        """Draw information about the selected zone or connection.

        Displays a prompt when no object is selected.
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
        interaction instructions.
        """
        rect = self.bottomr_panel
        font = pygame.font.SysFont(None, 20)
        lines = [
            "CONTROLS:",
            "M: Simulation playback mode (turn by turn or continuous)",
            "SPACE: start / pause simulation",
            "0: reset simulation (relaunches pygame)",
            "ESC / Q: quit window",
            "",
            "INTERACTIONS:",
            "Click on a zone or connection to see their information"
        ]
        x = rect.x + 10
        y = rect.y + 10
        line_height = font.get_linesize()
        for i, line in enumerate(lines):
            text = font.render(line, True, "white")
            self.screen.blit(text, (x, y + i * line_height))

    def update_animation(self, dt: int) -> None:
        """Update drone animations and advance the walking sprite animation.

        Args:
            dt: Milliseconds elapsed since the last frame.
        """
        if self.running_animation:
            self.frame_timer += dt
            if self.frame_timer > 100:
                self.current_frame += self.frame_direction
                if self.current_frame >= 14 or self.current_frame <= 0:
                    self.frame_direction *= -1
                self.frame_timer = 0
            for drone_id, anim in self.drone_anim.items():
                if anim["progress"] < 1.0:
                    anim["progress"] = min(1.0, anim["progress"] + dt / 1000.0)
            if all(d.finished for d in self.simulation.drones):
                if all(a["progress"] >= 1.0 for a in
                        self.drone_anim.values()):
                    self.running_animation = False
            elif (not self.auto_play and
                    all(a["progress"] >= 1.0
                        for a in self.drone_anim.values())):
                self.running_animation = False

    def reset_animation(self) -> None:
        """Request a simulation reset and close the current demo window."""
        self.reset_requested = True
        self.running = False
