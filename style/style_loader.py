import json
import pygame

color_literals = {}
window_style = {}
keyboard_style = {}
gui_style = {}

def color_as_rgb(color: pygame.Color) -> tuple[int, int, int]:
  return (color.r, color.g, color.b)

# loads and initializes colors, fonts, etc. from the provided json file
def load_config(file):
  config = json.load(file)

  global color_literals
  for name, color_string in config['color codes'].items():
    color_literals[name] = pygame.Color(color_string)

  global window_style
  window_style['size'] = config['window']['size']
  window_style['title'] = config['window']['title']
  window_style['background color'] = color_literals[config['window']['background color']]

  global keyboard_style
  keyboard_style['font_name'] = config['keyboard']['font']
  keyboard_style['text_color'] = [
    color_as_rgb(color_literals[i]) for i in config['keyboard']['text colors']
  ]
  keyboard_style['cursor_color'] = (0, 0, 0) # unused
  keyboard_style['selection_color'] = (0, 0, 0) # unused
  keyboard_style['background_color'] = color_as_rgb(
    color_literals[config['keyboard']['background color']])
  keyboard_style['background_key_color'] = [
    color_as_rgb(color_literals[i]) for i in config['keyboard']['key background colors']
  ]
  keyboard_style['background_input_color'] = (0, 0, 0) # unused

  text_box_config = {
    'font': config['gui']['text box']['font'],
    'background color': color_literals[config['gui']['text box']['background color']],
    'focused background color': color_literals[
      config['gui']['text box']['focused background color']],
    'outline color': color_literals[config['gui']['text box']['outline color']],
    'text display color': color_literals[config['gui']['text box']['display text color']],
    'text input color': color_literals[config['gui']['text box']['input text color']]
  }

  global gui_style
  gui_style['text box'] = text_box_config
