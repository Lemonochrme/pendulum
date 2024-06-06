import pygame
import numpy as np

# Initialisation de Pygame
pygame.init()

# Paramètres de la fenêtre
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pendule Simple")

# Couleurs
BACKGROUND = (30, 31, 38)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Paramètres du pendule
g = 9.81  # Accélération due à la gravité (m/s^2)
l = 150   # Longueur du pendule en pixels
b = 0.05  # Coefficient de friction augmenté
dt = 0.1 # Pas de temps augmenté
move_speed = 5  # Vitesse de déplacement de l'axe horizontal

# Paramètres du contrôleur PID
Kp = 5.0   # Gain proportionnel réduit
Ki = 0.1   # Gain intégral réduit
Kd = 2.0   # Gain dérivé réduit

# Conditions initiales
theta = 0.0  # Angle initial (rad)
omega = 0.0  # Vitesse angulaire initiale (rad/s)

# Centre du pendule (initial)
origin_x = width // 2
origin_y = height // 2

# Limites d'excursion
min_x = 100
max_x = width - 100

# Vitesse horizontale initiale de l'axe
v_origin_x = 0

# État du contrôleur PID
integral = 0
previous_error = 0

# Mode de contrôle
manual_control = True

# Angle seuil pour activer le contrôle PID automatique (en radians)
threshold_angle = 2.0

def update_pendulum(theta, omega, dt, l, g, b, v_origin_x):
    alpha = -(g / l) * np.sin(theta) - b * omega - (v_origin_x * np.cos(theta) / l)
    omega += alpha * dt
    theta += omega * dt
    theta = (theta + np.pi) % (2 * np.pi) - np.pi  # Normaliser l'angle entre -π et π
    return theta, omega

def pid_control(theta, dt, Kp, Ki, Kd):
    global integral, previous_error
    error = np.arctan2(np.sin(np.pi - theta), np.cos(np.pi - theta))  # Correction de l'erreur pour tenir compte de la nature cyclique
    integral += error * dt
    derivative = (error - previous_error) / dt
    output = Kp * error + Ki * integral + Kd * derivative
    previous_error = error
    return np.clip(output, -move_speed, move_speed), error, integral, derivative  # Retourner l'erreur, l'intégrale et la dérivée

# Initialisation de la police pour afficher les métriques
font = pygame.font.SysFont(None, 24)

# Fonction pour afficher du texte à l'écran
def draw_text(surface, text, pos, color=WHITE):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

# Boucle principale
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Calculer l'angle absolu du pendule
    absolute_angle = abs(theta)

    # Basculer automatiquement entre le mode de contrôle manuel et le contrôle PID
    if absolute_angle > threshold_angle:
        manual_control = False
    else:
        manual_control = True

    # Gestion des événements de clavier pour déplacer l'axe horizontalement
    keys = pygame.key.get_pressed()
    previous_origin_x = origin_x
    if manual_control:
        if keys[pygame.K_LEFT] and origin_x > min_x:
            origin_x -= 0.2*move_speed # Factor to ease manual control 
        elif keys[pygame.K_RIGHT] and origin_x < max_x:
            origin_x += 0.2*move_speed
        error = integral = derivative = 0  # Réinitialiser les métriques PID en mode manuel
    else:
        pid_output, error, integral, derivative = pid_control(theta, dt, Kp, Ki, Kd)
        origin_x += pid_output  # Ajuster l'origine du pendule en fonction de la sortie PID
        
        # Ajouter une perturbation basée sur la position de la souris
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_y < height:
            theta -= (mouse_x - width // 2) * 0.00001  # Influence légère basée sur la position x de la souris

    # Appliquer les limites d'excursion
    if origin_x < min_x:
        origin_x = min_x
    elif origin_x > max_x:
        origin_x = max_x

    # Calculer la vitesse horizontale de l'axe
    v_origin_x = (origin_x - previous_origin_x) / dt

    # Mise à jour du pendule
    theta, omega = update_pendulum(theta, omega, dt, l, g, b, v_origin_x)
    
    # Calcul de la position du pendule
    x = origin_x + l * np.sin(theta)
    y = origin_y + l * np.cos(theta)

    # Dessiner tout
    screen.fill(BACKGROUND)
    pygame.draw.line(screen, WHITE, (min_x, origin_y), (max_x, origin_y), 2)  # Dessiner l'axe horizontal
    pygame.draw.line(screen, RED, (origin_x, origin_y - 10), (origin_x, origin_y + 10), 2)  # Marquer la position actuelle sur l'axe
    pygame.draw.line(screen, WHITE, (origin_x, origin_y), (x, y), 2)
    pygame.draw.circle(screen, WHITE, (int(x), int(y)), 10)

    # Afficher les métriques
    draw_text(screen, f"Theta angle (deg): {theta:.2f}", (10, 10))
    draw_text(screen, f"Angular velocity (rad/s): {omega:.2f}", (10, 50))
    draw_text(screen, f"Position on x axis (px): {origin_x}", (10, 90))
    draw_text(screen, f"Mode: {'Manual' if manual_control else 'PID'}", (10, 130))
    draw_text(screen, f"PID Error: {error:.2f}", (10, 170))
    draw_text(screen, f"Integral PID: {integral:.2f}", (10, 210))
    draw_text(screen, f"Derivative PID: {derivative:.2f}", (10, 250))

    pygame.display.flip()
    
    clock.tick(120)  # Limite à 120 FPS

pygame.quit()
