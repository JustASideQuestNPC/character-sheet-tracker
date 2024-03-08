''' --- a text entry field --- '''
import pygame
pygame.font.init()

class Text_Box:
  rect: pygame.Rect
  text_font: pygame.font.Font
  text: str = ''
  surface: pygame.Surface

  def __init__(self,
               surface: pygame.Surface,
               rect: tuple[int, int, int, int],
               initial_text: str='') -> None:
    self.surface = surface
    self.rect = pygame.Rect(rect[0], rect[1], rect[2], rect[3])
    self.text_font = pygame.font.Font(size=32)
    self.text = initial_text

  def render(self) -> None:
    pygame.draw.rect(self.surface, (255, 255, 255), self.rect)
    text_surface = self.text_font.render(self.text, True, (0, 0, 0))
    self.surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5, self.rect.w, self.rect.h))

  