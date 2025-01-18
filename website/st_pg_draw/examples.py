examples = {
"Default": """
SCREEN.fill(pygame.Color("darkgreen"))

pygame.draw.rect(
    SCREEN, 
    pygame.Color("blue"), 
    pygame.Rect(0, 0, *SCREEN_SIZE), 
    width=50, 
    border_radius=150
)
""",

"Hello World": """
font = pygame.font.SysFont("Roboto", 75)

font_surf = font.render("Hello World!", True, pygame.Color("red"))

font_pos_x = SCREEN_SIZE[0]//2 - font_surf.get_width() // 2
font_pos_y = SCREEN_SIZE[1]//4 - font_surf.get_height() // 2

for i in range(3):
    font_surf = pygame.transform.rotozoom(font_surf, 10, 1)
    SCREEN.blit(font_surf, (font_pos_x, font_pos_y + i*60))
""",

"Gfxdraw":"""
pygame.gfxdraw.rectangle(SCREEN, (50, 50, 200, 100), pygame.Color('white'))

pygame.gfxdraw.ellipse(SCREEN, 400, 100, 100, 50, pygame.Color('red'))

polygon_points = [
    (200, 200), 
    (300, 250), 
    (350, 350), 
    (250, 400), 
    (150, 350), 
    (200, 250),
]
pygame.gfxdraw.filled_polygon(SCREEN, polygon_points, pygame.Color('green'))

pygame.gfxdraw.aacircle(SCREEN, 600, 300, 50, pygame.Color('blue'))
pygame.gfxdraw.filled_circle(SCREEN, 600, 300, 50, pygame.Color('blue'))
""",

"Gradient": """surface = pygame.Surface((255, 255))

ar = pygame.PixelArray(surface)

for y in range(255):
    r, g, b = y, y, y
    ar[:, y] = (r, g, b)
    
del ar

surface = pygame.transform.scale(surface, SCREEN_SIZE)

SCREEN.blit(surface, (0, 0))
""",

"Numpy Pattern": """
def generate_pattern(width, height, shift):
    x = np.arange(width).reshape(1, width)
    y = np.arange(height).reshape(height, 1)

    layer1 = np.sin(x / 16.0 + shift)
    layer2 = np.sin(y / 8.0 + shift)
    layer3 = np.sin((x + y) / 16.0 + shift)
    layer4 = np.sin(np.sqrt((x - width / 2) ** 2 + (y - height / 2) ** 2) / 8.0 + shift)

    # Combine layers and normalize
    arr = layer1 + layer2 + layer3 + layer4
    arr = np.sin(arr * np.pi)

    # Normalize to 0-255 and return as an integer array
    arr = (arr + 1) * 128
    return np.array(arr, dtype=np.uint8)


shift = 0  # Set a constant value for the shift
pattern_arr = generate_pattern(SCREEN_SIZE[0], SCREEN_SIZE[1], shift)

# Map the array values to a Pygame surface
surface = pygame.surfarray.make_surface(np.stack((pattern_arr,) * 3, axis=-1))
surface = pygame.transform.smoothscale(surface, SCREEN_SIZE)

SCREEN.blit(surface, (0, 0))
""",

"Uploaded Image": """
scaled_img_surf = pygame.transform.scale_by(IMAGE_SURFACE, 0.75)

blurred_img_surf = pygame.transform.gaussian_blur(scaled_img_surf, 5)

inverted_blurred_img_surf = pygame.transform.invert(blurred_img_surf)

SCREEN.blit(inverted_blurred_img_surf, (0,0))
"""
}