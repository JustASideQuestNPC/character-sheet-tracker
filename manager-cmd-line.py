from argparse import ArgumentParser
import json
from math import floor
from time import sleep
from rich import box
from rich.console import Group, Console
from rich.theme import Theme
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel

console = Console(
  theme=Theme({
  "black": "#282A36",
  "dark gray": "#44475A",
  "white": "#F8F8F2",
  "light gray": "#6272A4",
  "cyan": "#8BE9FD",
  "green": "#50FA7B",
  "orange": "#FFB86C",
  "pink": "#FF79C6",
  "purple": "#BD93F9",
  "red": "#FF5555",
  "yellow": "#F1FA8C"
  }),
  height = 30
)

def ordinal(n: int) -> str:
  if n % 10 == 1:
    return f'{n}st'
  elif n % 10 == 2:
    return f'{n}nd'
  elif n % 10 == 3:
    return f'{n}rd'
  else:
    return f'{n}th'
  
def format_modifier(n: int) -> str:
  return f'+{n}' if n >= 0 else f'{n}'

class Character:
  def load_sheet(self, path) -> None:
    with open(path) as file:
      sheet = json.load(file)
      self.sheet = {}
      for k, v in sheet.items():
        self.sheet[k] = v

      self.max_hp = self.sheet['max hp']
      self.current_hp = self.sheet['current hp']
      self.temp_hp = self.sheet['temp hp']

      self.ability_scores = {}
      for name, score in self.sheet['ability scores'].items():
        self.ability_scores[name] = [score, floor((score - 10) / 2)]

      self.initiative = self.sheet['initiative bonus'] + self.ability_scores['dex'][1]
      self.armor_class = self.sheet['base armor class'] + self.sheet['other ac modifiers']

      if self.sheet['armor type'] == 'light':
        self.armor_class += self.ability_scores['dex'][1]
      elif self.sheet['armor type'] == 'medium':
        self.armor_class += min(2, self.ability_scores['dex'][1])

      self.proficiency_bonus = self.sheet['proficiency bonus']
      self.passive_perception = 10 + self.ability_scores['wis'][1]
      self.passive_insight = 10 + self.ability_scores['wis'][1]
      self.passive_investigation = 10 + self.ability_scores['int'][1]

  def format_personal_info(self) -> Panel:
    blocks = [
      f'[pink]Name:[/pink] {self.sheet["name"]}',
      f'[pink]Race:[/pink] {self.sheet["race"]}'
    ]

    buffer = f'{ordinal(self.sheet["level"])}-level {self.sheet["class"]}'
    if 'subclass' in self.sheet:
      buffer += f' ({self.sheet["subclass"]})'
    blocks.append(buffer)

    return Panel(Group(*[i for i in blocks]), title='[orange]Personal Info')
  
  def format_combat_stats(self) -> Panel:
    blocks = [
      f'[pink]Size:[/pink] {self.sheet["size"]}',
      f'[pink]Initiative:[/pink] {format_modifier(self.initiative)}',
      f'[pink]Speed:[/pink] {self.sheet["speed"]}ft',
      f'[pink]Armor Class:[/pink] {self.armor_class}',
      f'[pink]Max HP:[/pink] {self.max_hp}'
    ]

    buffer = f'[pink]Current HP:[/pink] {self.current_hp}'
    if self.temp_hp > 0:
      buffer += f' + [cyan]{self.temp_hp}[/cyan] = [orange]{self.current_hp + self.temp_hp}'
    blocks.append(buffer)

    return Panel(Group(*[i for i in blocks]), title='[orange]Combat Stats')

  def format_ability_scores(self) -> Panel:
    root_table = Table(show_header=False, box=box.SIMPLE, show_lines=False)
    root_table.add_column()
    root_table.add_column()

    left_table = Table(show_header=False, box=box.MINIMAL, padding=(0, 0, 0, 0))
    left_table.add_column(style='cyan')
    left_table.add_column()
    right_table = Table(show_header=False, box=box.MINIMAL, padding=(0, 0, 0, 0))
    right_table.add_column(style='cyan')
    right_table.add_column()
    for i, (ability, (raw, modifier)) in enumerate(self.ability_scores.items()):
      if i < 3:
        left_table.add_row(
          ability.upper(),
          f'{raw} '.rjust(3, '0') + f'({format_modifier(modifier)})'
        )
      else:
        right_table.add_row(
          ability.upper(),
          f'{raw} '.rjust(3, '0') + f'({format_modifier(modifier)})'
        )

    root_table.add_row(left_table, right_table)
    return Panel(root_table, title='[orange]Ability Scores')
  
  def format_passive_scores(self) -> Panel:
    passive_scores = Table(show_header=False, box=box.MINIMAL)
    passive_scores.add_column(style='cyan')
    passive_scores.add_column()
    
    passive_scores.add_row('Perception', f'{self.passive_perception}')
    passive_scores.add_row('Insight', f'{self.passive_insight}')
    passive_scores.add_row('Investigation', f'{self.passive_investigation}')

    return Panel(
      Group(
        f'[pink]Proficiency Bonus:[/pink] {self.proficiency_bonus}',
        passive_scores
      ),
      title='[orange]Passive Scores'
    )


parser = ArgumentParser()
parser.add_argument('file_path')
args = parser.parse_args()

character = Character()
character.load_sheet(args.file_path)

layout = Layout()
layout.split_row(
  Layout(name='left'),
  Layout(name='proficiencies'),
  Layout(name='actions')
)
layout['left'].split_column(
  Layout(name='personal info', size=5),
  Layout(name='combat stats'),
  Layout(name='ability scores'),
  Layout(name='passive scores')
)

with Live(layout, console=console, refresh_per_second=4):  # update 4 times a second to feel fluid
  layout['left']['personal info'].update(
    character.format_personal_info()
  )
  layout['left']['combat stats'].update(
    character.format_combat_stats()
  )
  layout['left']['ability scores'].update(
    character.format_ability_scores()
  )
  layout['left']['passive scores'].update(
    character.format_passive_scores()
  )