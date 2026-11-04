"""Live Pygame view of a running simulation.

Links are drawn on the right-hand side of the road and coloured by how full they
are; vehicles are dots travelling along them and stacking up at the stop lines.
The light at the end of every approach shows its signal (green / amber / red).
Ambulances flash red and blue; in corridor mode the rest of their route is
highlighted while the reservations are active.

Keys: SPACE pause, + / - change speed, L toggle node labels, ESC quit.
"""
from __future__ import annotations

import math
import os
import time
from pathlib import Path

from trafficmas.network.road import VEHICLE_SPACING, Link
from trafficmas.sim.engine import Simulation

BG = (250, 250, 248)
PANEL = (241, 240, 236)
TEXT = (11, 11, 11)
TEXT_2 = (82, 81, 78)
CAR = (60, 60, 60)
GREEN = (0, 150, 60)
AMBER = (237, 161, 0)
RED = (220, 50, 50)
EV_A = (227, 73, 72)
EV_B = (42, 120, 214)
CORRIDOR = (27, 175, 122)
# link occupancy: empty grey -> amber -> red
OCC_STOPS = [(0.0, (200, 199, 194)), (0.5, (237, 161, 0)), (1.0, (200, 40, 40))]


def occupancy_colour(r: float) -> tuple[int, int, int]:
    r = max(0.0, min(1.0, r))
    for (r0, c0), (r1, c1) in zip(OCC_STOPS, OCC_STOPS[1:], strict=False):
        if r <= r1:
            t = (r - r0) / (r1 - r0)
            return tuple(int(a + (b - a) * t) for a, b in zip(c0, c1, strict=True))
    return OCC_STOPS[-1][1]


class LiveView:
    def __init__(self, sim: Simulation, width: int = 1280, height: int = 820, speed: float = 8.0,
                 fps: int = 30, record: str | None = None, record_seconds: float = 120.0,
                 headless: bool = False, start_at: float = 0.0) -> None:
        if headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        import pygame
        self.pg = pygame
        pygame.init()
        self.sim = sim
        self.W, self.H = width, height
        self.panel_w = 300
        self.speed = speed
        self.fps = fps
        self.paused = False
        self.labels = False
        self.record = record
        self.record_seconds = record_seconds
        self.frames: list = []
        self.start_at = start_at
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(f"TrafficMAS+ - {sim.name} - {sim.controller_name}")
        self.font = pygame.font.SysFont("segoeui,arial", 15)
        self.small = pygame.font.SysFont("segoeui,arial", 12)
        self.big = pygame.font.SysFont("segoeui,arial", 22, bold=True)
        x0, y0, x1, y1 = sim.net.bbox()
        margin = 40
        sx = (width - self.panel_w - 2 * margin) / max(1.0, x1 - x0)
        sy = (height - 2 * margin) / max(1.0, y1 - y0)
        self.scale = min(sx, sy)
        self.ox = margin - x0 * self.scale + (width - self.panel_w - 2 * margin - (x1 - x0) * self.scale) / 2
        self.oy = height - margin + y0 * self.scale - (height - 2 * margin - (y1 - y0) * self.scale) / 2
        self.offset = max(2.5, min(6.0, 6.0 * self.scale / 1.2))

    # ------------------------------------------------------------------ geometry
    def to_screen(self, x: float, y: float) -> tuple[float, float]:
        return self.ox + x * self.scale, self.oy - y * self.scale

    def link_geom(self, link: Link):
        a = self.sim.net.nodes[link.u]
        b = self.sim.net.nodes[link.v]
        ax, ay = self.to_screen(a.x, a.y)
        bx, by = self.to_screen(b.x, b.y)
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy) or 1.0
        ux, uy = dx / length, dy / length
        nx, ny = -uy, ux                      # right-hand side of travel on screen
        off = self.offset
        trim = min(10.0, length * 0.2)
        p0 = (ax + nx * off + ux * trim, ay + ny * off + uy * trim)
        p1 = (bx + nx * off - ux * trim, by + ny * off - uy * trim)
        return p0, p1

    @staticmethod
    def along(p0, p1, f: float) -> tuple[float, float]:
        return p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f

    # ------------------------------------------------------------------ drawing
    def draw(self) -> None:
        pg = self.pg
        sim = self.sim
        now = sim.env.now
        scr = self.screen
        scr.fill(BG)
        corridor_links = set()
        for v in sim.vehicles.values():
            if v.is_emergency and v.link is not None and getattr(v, "mode", "") == "corridor":
                corridor_links.update(link.id for link in v.route[v.idx:])
        for link in sim.net.links.values():
            p0, p1 = self.link_geom(link)
            if link.id in corridor_links:
                pg.draw.line(scr, CORRIDOR, p0, p1, int(2 + link.lanes * 2.5))
            colour = (120, 120, 120) if link.closed else occupancy_colour(link.occupancy_ratio)
            pg.draw.line(scr, colour, p0, p1, max(2, link.lanes + 1))
        # vehicles
        blink = int(now * 2) % 2 == 0
        for link in sim.net.links.values():
            p0, p1 = self.link_geom(link)
            px_len = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1.0
            per_veh = VEHICLE_SPACING * self.scale / link.lanes
            queued = link.queued
            tail = max(0.0, 1.0 - queued * per_veh / px_len)
            k = 0
            for q in link.queues.values():
                for veh in q:
                    f = max(0.0, 1.0 - (k + 0.5) * per_veh / px_len)
                    self._dot(veh, self.along(p0, p1, f), blink)
                    k += 1
            for veh in link.travellers.values():
                span = max(1e-6, veh.stopline_at - veh.entered_at)
                f = min(tail, (now - veh.entered_at) / span)
                self._dot(veh, self.along(p0, p1, f), blink)
        # signals
        for agent in sim.agents.values():
            if not agent.signalized:
                continue
            for link in agent.in_links:
                _, p1 = self.link_geom(link)
                movs = [m for m in agent.node.movements if m.inbound is link]
                if agent.in_intergreen and any(agent.node.phase_of[m.key] == agent.phase for m in movs):
                    c = AMBER
                elif any(agent.is_green(m) for m in movs):
                    c = GREEN
                else:
                    c = RED
                pg.draw.circle(scr, c, (int(p1[0]), int(p1[1])), 4)
            if agent.ev_hold:
                x, y = self.to_screen(agent.node.x, agent.node.y)
                pg.draw.circle(scr, CORRIDOR, (int(x), int(y)), 12, 2)
        if self.labels:
            for node in sim.net.nodes.values():
                x, y = self.to_screen(node.x, node.y)
                scr.blit(self.small.render(node.id, True, TEXT_2), (x + 6, y - 16))
        self._panel()

    def _dot(self, veh, pos, blink: bool) -> None:
        if veh.is_emergency:
            self.pg.draw.circle(self.screen, EV_A if blink else EV_B, (int(pos[0]), int(pos[1])), 6)
        else:
            self.pg.draw.circle(self.screen, CAR, (int(pos[0]), int(pos[1])), 2)

    def _panel(self) -> None:
        pg = self.pg
        sim = self.sim
        m = sim.metrics
        x = self.W - self.panel_w
        pg.draw.rect(self.screen, PANEL, (x, 0, self.panel_w, self.H))
        y = 18
        self.screen.blit(self.big.render("TrafficMAS+", True, TEXT), (x + 18, y))
        y += 36
        trips = m.trips
        avg_tt = sum(t["travel_time"] for t in trips) / len(trips) if trips else 0.0
        evs = [v for v in sim.vehicles.values() if v.is_emergency]
        t = sim.env.now
        rows = [
            ("scenario", sim.name),
            ("controller", sim.controller_name),
            ("emergency mode", sim.emergency_mode),
            ("time", f"{int(t // 60):02d}:{int(t % 60):02d}"),
            ("speed", f"{self.speed:g}x" + ("  (paused)" if self.paused else "")),
            ("", ""),
            ("vehicles in network", str(len(m.active))),
            ("completed trips", str(len(trips))),
            ("avg. travel time", f"{avg_tt:.0f} s"),
            ("queued at signals", str(m.samples[-1]["queued"] if m.samples else 0)),
            ("messages sent", str(sim.bus.sent)),
            ("ambulances driving", str(len(evs))),
            ("ambulances arrived", str(len(m.ev_trips))),
        ]
        for k, v in rows:
            if k:
                self.screen.blit(self.font.render(k, True, TEXT_2), (x + 18, y))
                self.screen.blit(self.font.render(v, True, TEXT), (x + 165, y))
            y += 24
        y += 10
        legend = [(GREEN, "green light"), (AMBER, "amber / all-red"), (RED, "red light"),
                  (EV_A, "ambulance"), (CORRIDOR, "reserved corridor")]
        for c, label in legend:
            pg.draw.circle(self.screen, c, (x + 26, y + 9), 6)
            self.screen.blit(self.small.render(label, True, TEXT_2), (x + 42, y + 1))
            y += 22
        y += 6
        self.screen.blit(self.small.render("link colour: empty -> full", True, TEXT_2), (x + 18, y))
        for i in range(120):
            pg.draw.line(self.screen, occupancy_colour(i / 119), (x + 18 + i, y + 22), (x + 18 + i, y + 32))
        y += 50
        for line in ("SPACE pause   + / - speed", "L labels   ESC quit"):
            self.screen.blit(self.small.render(line, True, TEXT_2), (x + 18, y))
            y += 18

    # ------------------------------------------------------------------ loop
    def run(self) -> dict:
        pg = self.pg
        sim = self.sim
        clock = pg.time.Clock()
        t0 = time.perf_counter()
        if self.start_at > 0:
            sim.env.run(until=self.start_at)
        watcher = sim.env.process(sim._watch(sim.env))
        record_start = sim.env.now
        running = True
        while running and not watcher.triggered:
            for ev in pg.event.get():
                if ev.type == pg.QUIT or (ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE):
                    running = False
                elif ev.type == pg.KEYDOWN:
                    if ev.key == pg.K_SPACE:
                        self.paused = not self.paused
                    elif ev.key in (pg.K_PLUS, pg.K_EQUALS, pg.K_KP_PLUS):
                        self.speed = min(200.0, self.speed * 1.5)
                    elif ev.key in (pg.K_MINUS, pg.K_KP_MINUS):
                        self.speed = max(0.5, self.speed / 1.5)
                    elif ev.key == pg.K_l:
                        self.labels = not self.labels
            if not self.paused:   # a recording advances one simulated second per frame
                sim.env.run(until=sim.env.now + (1.0 if self.record else self.speed / self.fps))
            self.draw()
            pg.display.flip()
            if self.record:
                if not self.paused:
                    self._capture()
                if sim.env.now - record_start >= self.record_seconds:
                    break
            else:
                clock.tick(self.fps)
        if self.record and self.frames:
            self._save_gif()
        pg.quit()
        sim.wall_time = time.perf_counter() - t0
        return sim.summary()

    def _capture(self) -> None:
        from PIL import Image
        raw = self.pg.image.tobytes(self.screen, "RGB")
        img = Image.frombytes("RGB", (self.W, self.H), raw)
        self.frames.append(img.resize((int(self.W * 0.6), int(self.H * 0.6)), Image.LANCZOS))

    def _save_gif(self) -> None:
        out = Path(self.record)
        out.parent.mkdir(parents=True, exist_ok=True)
        frames = [f.quantize(colors=128, method=2) for f in self.frames]
        frames[0].save(out, save_all=True, append_images=frames[1:], duration=80, loop=0, optimize=True)
        print(f"saved {len(frames)} frames to {out}")
