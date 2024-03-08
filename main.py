import pygame
from pygame_vkeyboard import *
from style.style_loader import load_config, window_style, keyboard_style
from gui.manager import GUI_Manager


with open('style/style_config.json') as file:
  load_config(file)

pygame.init()
pygame.font.init()

pygame.display.set_caption(window_style['title'])
window = pygame.display.set_mode(window_style['size'])

gui_manager = GUI_Manager()

keyboard_surface = pygame.Surface(window_style['size'])
keyboard_surface.set_colorkey((0, 0, 0))
keyboard = VKeyboard(
  keyboard_surface,
  lambda text: gui_manager.update_text(text),
  VKeyboardLayout(VKeyboardLayout.QWERTY),
  renderer=VKeyboardRenderer(**keyboard_style)
)

clock = pygame.time.Clock()
is_running = True

pygame.event.set_blocked(pygame.FINGERDOWN)
pygame.event.set_blocked(pygame.FINGERUP)
pygame.event.set_blocked(pygame.FINGERMOTION)

while is_running:
  time_delta = clock.tick(60)/1000.0
  events = pygame.event.get()
  for event in events:
    if event.type == pygame.QUIT:
      is_running = False

  keyboard.update(events)

  window.fill(window_style['background color'])

  keyboard.draw(keyboard_surface)
  window.blit(keyboard_surface, (0, 0))

  pygame.display.flip()
