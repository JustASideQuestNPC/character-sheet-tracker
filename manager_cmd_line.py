from argparse import ArgumentParser
import json
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.theme import Theme
from character import Character

with open('style_config.json') as file:
  style_config = json.load(file)
  console = Console(
  theme=Theme(style_config['theme']),
  width=style_config['width'],
  height=style_config['height']
)

parser = ArgumentParser()
parser.add_argument('file_path')
args = parser.parse_args()

character = Character()
character.load_sheet(args.file_path)

layout = Layout()
layout.split_row(
  Layout(name='left', size=45),
  Layout(name='center', size=60),
  Layout(name='right column', size=45)
)
layout['left'].split_column(
  Layout(name='personal info', size=7),
  Layout(name='ability scores', size=13),
  Layout(name='proficiencies', size=12),
  Layout(name='racial traits')
)
layout['center'].split_column(
  Layout(name='combat stats', size=11),
  Layout(name='skill modifiers')
)

with Live(layout, console=console, screen=False, auto_refresh=False):
  layout['personal info'].update(character.format_personal_info())
  layout['ability scores'].update(character.format_ability_scores())
  layout['proficiencies'].update(character.format_proficiencies())
  layout['racial traits'].update(character.format_racial_traits())
  layout['combat stats'].update(character.format_combat_stats())
  layout['skill modifiers'].update(character.format_skill_modifiers())