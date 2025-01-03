import pygame
import numpy as np


pygame.init()

width, height = 1280, 720
screen = pygame.display.set_mode((width, height))

# Paramètres du pendule
g = 9.81
l = 200 # longueur du pendule
b = 0.042 # frottements
dt = 0.1 # intervalle de temps

# Conditions initiales
theta = np.pi-0.04 # angle
omega = 0.0 # vitesse angulaire

# Centre du pendule
origin_x = width // 2
origin_y = height // 2

def update_pendulum(theta, omega, dt, l, g, b):
    alpha = -(g/l) * np.sin(theta) - b * omega # acceleration angulaire
    omega += alpha * dt # intégration de l'accélération = vitesse angulaire
    theta += omega * dt # intégration de la vitesse angulaire = angle
    theta = (theta + np.pi) % (2 * np.pi) - np.pi # normalisation de l'angle entre -pi et pi
    return theta, omega

# Pendulum equation : theta'' = -(g/l) * sin(theta) - b * theta'

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        

    absolute_angle = abs(theta)

    theta, omega = update_pendulum(theta, omega, dt, l, g, b)

    screen.fill((0, 0, 0))
    pygame.draw.line(screen, (255, 255, 255), (origin_x, origin_y), (origin_x + l * np.sin(theta), origin_y + l * np.cos(theta)), 2) # axis
    pygame.draw.circle(screen, (255, 255, 255), (origin_x + l * np.sin(theta), origin_y + l * np.cos(theta)), 10) # bob

    pygame.display.flip() # update the screen

    clock.tick(120) # 120 fps