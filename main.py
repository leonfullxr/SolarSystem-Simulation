import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 1500, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Simulation with Elliptical Orbits")

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (169, 169, 169)
BROWN = (165, 42, 42)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
LIGHT_BROWN = (210, 180, 140)

# Celestial body class
class CelestialBody:
    def __init__(self, name, semi_major_axis, eccentricity, color, radius, mass, orbit_speed):
        self.name = name
        self.semi_major_axis = semi_major_axis
        self.eccentricity = eccentricity
        self.color = color
        self.radius = radius
        self.mass = mass
        self.orbit_speed = orbit_speed
        self.angle = random.uniform(0, 2 * math.pi)
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.hit_count = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def update_position(self, sun_x, sun_y):
        # Calculate position based on elliptical orbit
        r = self.semi_major_axis * (1 - self.eccentricity**2) / (1 + self.eccentricity * math.cos(self.angle))
        self.x = sun_x + r * math.cos(self.angle)
        self.y = sun_y + r * math.sin(self.angle)
        
        # Update angle for next frame
        self.angle += self.orbit_speed
        
        # Apply additional velocity from collisions
        self.x += self.vx
        self.y += self.vy
        
        # Dampen the velocity
        self.vx *= 0.98
        self.vy *= 0.98

    def check_collision(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance < self.radius + other.radius

    def apply_sun_gravity(self, sun_x, sun_y):
        dx = sun_x - self.x
        dy = sun_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        force = 2.0 / (distance ** 2)
        self.vx += force * dx / distance
        self.vy += force * dy / distance

class Asteroid:
    def __init__(self, x, y, radius=None, color=GRAY, vx=None, vy=None):
        self.x = x
        self.y = y
        self.radius = radius if radius else random.randint(2, 10)
        self.color = color
        self.vx = vx if vx else random.uniform(-0.5, 0.5)
        self.vy = vy if vy else random.uniform(-0.5, 0.5)
        self.mass = self.radius ** 2

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def update_position(self, sun_x, sun_y):
        self.x += self.vx
        self.y += self.vy
        self.apply_sun_gravity(sun_x, sun_y)

    def check_collision(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance < self.radius + other.radius

    def apply_sun_gravity(self, sun_x, sun_y):
        dx = sun_x - self.x
        dy = sun_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        force = 0.5 / (distance ** 2)
        self.vx += force * dx / distance
        self.vy += force * dy / distance

def collide_objects(obj1, obj2):
    nx = obj2.x - obj1.x
    ny = obj2.y - obj1.y
    d = math.sqrt(nx**2 + ny**2)
    nx /= d
    ny /= d

    dvx = obj2.vx - obj1.vx
    dvy = obj2.vy - obj1.vy

    impulse = 2 * (dvx * nx + dvy * ny) / (obj1.mass + obj2.mass)

    obj1.vx += impulse * obj2.mass * nx
    obj1.vy += impulse * obj2.mass * ny
    obj2.vx -= impulse * obj1.mass * nx
    obj2.vy -= impulse * obj1.mass * ny

    overlap = (obj1.radius + obj2.radius - d) / 2
    obj1.x -= overlap * nx
    obj1.y -= overlap * ny
    obj2.x += overlap * nx
    obj2.y += overlap * ny

# Create celestial bodies
sun = CelestialBody("Sun", 0, 0, YELLOW, 60, 1000, 0)
sun.x, sun.y = WIDTH // 2, HEIGHT // 2
planets = [
    CelestialBody("Mercury", 120, 0.206, GRAY, 10, 0.055, 0.02),
    CelestialBody("Venus", 170, 0.007, BROWN, 15, 0.815, 0.015),
    CelestialBody("Earth", 220, 0.017, BLUE, 16, 1, 0.01),
    CelestialBody("Mars", 270, 0.093, RED, 14, 0.107, 0.008),
    CelestialBody("Jupiter", 350, 0.048, ORANGE, 40, 317.8, 0.004),
    CelestialBody("Saturn", 450, 0.054, LIGHT_BROWN, 35, 95.2, 0.003),
    CelestialBody("Uranus", 550, 0.047, LIGHT_BLUE, 25, 14.5, 0.002),
    CelestialBody("Neptune", 650, 0.009, DARK_BLUE, 24, 17.1, 0.001)
]

asteroids = []
sun_glow = 0

def explode_planet(planet):
    fragments = []
    for _ in range(planet.radius * 2):
        fragment = Asteroid(
            planet.x + random.uniform(-planet.radius, planet.radius),
            planet.y + random.uniform(-planet.radius, planet.radius),
            radius=random.randint(2, 6),
            color=planet.color,
            vx=random.uniform(-1, 1),
            vy=random.uniform(-1, 1)
        )
        fragments.append(fragment)
    return fragments

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    # Update positions
    for planet in planets:
        planet.update_position(sun.x, sun.y)
        planet.apply_sun_gravity(sun.x, sun.y)

    # Update asteroids and check for collisions
    for i, asteroid in enumerate(asteroids):
        asteroid.update_position(sun.x, sun.y)
        
        if asteroid.check_collision(sun):
            asteroids.pop(i)
            sun_glow = 20
            continue
        
        for planet in planets[:]:
            if asteroid.check_collision(planet):
                collide_objects(asteroid, planet)
                planet.hit_count += asteroid.radius
                print(f"Asteroid hit {planet.name}! Hit count: {planet.hit_count}")
                
                if planet.hit_count >= planet.radius:
                    print(f"{planet.name} has exploded!")
                    planets.remove(planet)
                    asteroids.extend(explode_planet(planet))
                break
        
        for j, other_asteroid in enumerate(asteroids[i+1:], i+1):
            if asteroid.check_collision(other_asteroid):
                collide_objects(asteroid, other_asteroid)

    # Add new asteroids
    if random.random() < 0.05:
        x = random.choice([0, WIDTH])
        y = random.randint(0, HEIGHT)
        asteroids.append(Asteroid(x, y))

    # Remove asteroids that are far outside the screen
    asteroids = [ast for ast in asteroids if -WIDTH < ast.x < WIDTH*2 and -HEIGHT < ast.y < HEIGHT*2]

    # Draw orbits
    for planet in planets:
        points = []
        for angle in range(0, 360, 5):
            rad_angle = math.radians(angle)
            r = planet.semi_major_axis * (1 - planet.eccentricity**2) / (1 + planet.eccentricity * math.cos(rad_angle))
            x = sun.x + r * math.cos(rad_angle)
            y = sun.y + r * math.sin(rad_angle)
            points.append((int(x), int(y)))
        pygame.draw.lines(screen, (50, 50, 50), False, points, 1)
    
    # Draw sun with glow effect
    if sun_glow > 0:
        pygame.draw.circle(screen, (255, 255, 100), (int(sun.x), int(sun.y)), sun.radius + sun_glow)
        sun_glow -= 1
    sun.draw(screen)

    for planet in planets:
        planet.draw(screen)

    for asteroid in asteroids:
        asteroid.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
