import pygame
from pygame_vkeyboard import *
from gui.text_box import Text_Box

pygame.init()

pygame.display.set_caption('Quick Start')
window = pygame.display.set_mode((800, 600))

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#000000'))

test_text = Text_Box(window, (0, 0, 200, 100), 'test')

clock = pygame.time.Clock()
is_running = True

pygame.event.set_blocked(pygame.FINGERDOWN)
pygame.event.set_blocked(pygame.FINGERUP)
pygame.event.set_blocked(pygame.FINGERMOTION)

def consumer(text):
  print('Current text : %s' % text)

keyboard = VKeyboard(window, consumer, VKeyboardLayout(VKeyboardLayout.QWERTY))
screen_touched = False

while is_running:
  time_delta = clock.tick(60)/1000.0
  events = pygame.event.get()
  for event in events:
    if event.type == pygame.QUIT:
      is_running = False
    elif event.type == pygame.MOUSEBUTTONDOWN:
      print('mouse clicked')
    # elif event.type == pygame.FINGERDOWN:
    #   screen_touched = True
    # elif event.type == pygame.FINGERUP:
    #   screen_touched = False

  keyboard.update(events)

  # window.blit(background, (0, 0))
  keyboard.draw(window)

  # if screen_touched:
  #   pygame.draw.circle(window, (0, 0, 0), ())

  # test_text.render()

  pygame.display.flip()
