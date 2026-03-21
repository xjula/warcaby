import os
from constants import *

# --- KLASY UI ---
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER if self.rect.collidepoint(mouse_pos) else BUTTON_COLOR

        shadow_rect = self.rect.copy()
        shadow_rect.y += 5
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=30)
        pygame.draw.rect(surface, color, self.rect, border_radius=30)

        text_surf = FONT_BUTTON.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class IconButton:
    def __init__(self, center_x, center_y, size, image_filename, fallback_char):
        self.rect = pygame.Rect(center_x - size // 2, center_y - size // 2, size, size)
        self.fallback_char = fallback_char
        self.image = None

        if os.path.exists(image_filename):
            try:
                img = pygame.image.load(image_filename).convert_alpha()
                self.image = pygame.transform.smoothscale(img, (size, size))
            except Exception as e:
                print(f"Błąd obrazka: {e}")

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)

        if is_hover:
            pygame.draw.circle(surface, SHADOW_COLOR, self.rect.center, self.rect.width // 2 + 5)

        if self.image:
            surface.blit(self.image, self.rect)
        else:
            color = BUTTON_HOVER if is_hover else BUTTON_COLOR
            pygame.draw.circle(surface, color, self.rect.center, self.rect.width // 2)
            text_surf = FONT_BUTTON.render(self.fallback_char, True, WHITE)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)