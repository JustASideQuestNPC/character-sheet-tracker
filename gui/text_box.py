''' --- a text entry field --- '''
import pygame
from style.style_loader import gui

class Text_Box:
  rect: pygame.Rect
  text_font: pygame.font.Font
  text: str = ''
  type: str = 'text box'
  focused: bool = False

  def __init__(self,
               rect: tuple[int, int, int, int],
               initial_text: str='') -> None:
    self.rect = pygame.Rect(rect[0], rect[1], rect[2], rect[3])
    self.text_font = pygame.font.Font(size=32)
    self.text = initial_text

  def render(self, surface: pygame.Surface) -> None:
    pygame.draw.rect(surface, (255, 255, 255), self.rect)
    text_surface = self.text_font.render(self.text, True, (0, 0, 0))
    surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5, self.rect.w, self.rect.h))