import json
from math import floor
from rich import box
from rich.table import Table, Column
from rich.panel import Panel
from rich.console import Group
from rich.columns import Columns

SKILLS = {
  'str': ['athletics'],
  'dex': ['acrobatics', 'sleight of hand', 'stealth'],
  'con': [],
  'int': ['arcana', 'history', 'investigation', 'nature', 'religion'],
  'wis': ['animal handling', 'insight', 'medicine', 'perception', 'survival'],
  'cha': ['deception', 'intimidation', 'performance', 'persuasion']
}

ABILITY_NAMES = (
  ('str', 'strength'),
  ('dex', 'dexterity'),
  ('con', 'constitution'),
  ('int', 'intelligence'),
  ('wis', 'wisdom'),
  ('cha', 'charisma')
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
  if n == 0:  return '+0'
  elif n > 0: return f'[green]+{n}[/green]'
  else:       return f'[red]{n}[/red]'

class Character:
  def load_sheet(self, path) -> None:
    with open(path) as file:
      sheet = json.load(file)
      
      self.name = sheet['name']
      self.level = sheet['level']
      self.character_class = sheet['class']
      self.character_subclass = sheet['subclass']
      self.background = sheet['background']
      self.alignment = sheet['alignment']
      self.race = sheet['race']

      self.ability_scores = {}
      for name, score in sheet['ability scores'].items():
        self.ability_scores[name[:3]] = [score, floor((score - 10) / 2)]

      self.proficiency_bonus = floor((self.level - 1) / 4) + 2

      self.save_modifiers = {}
      self.skill_modifiers = {}
      for short_name, long_name in ABILITY_NAMES:
        modifier = self.ability_scores[short_name][1]
        if long_name in sheet['proficiencies']['saving throws']:
          self.save_modifiers[short_name] = [modifier + self.proficiency_bonus, True]
        else:
          self.save_modifiers[short_name] = [modifier, False]
        
        self.skill_modifiers[short_name] = {}
        for skill in SKILLS[short_name]:
          if skill in sheet['proficiencies']['skills']:
            self.skill_modifiers[short_name][skill] = [modifier + self.proficiency_bonus, True]
          else:
            self.skill_modifiers[short_name][skill] = [modifier, False]

      self.death_saves = [
        [False, False, False], # successes
        [False, False, False]  # failures
      ]

      self.max_hp = sheet['hp']['max']
      self.current_hp = sheet['hp']['current']
      self.temp_hp = sheet['hp']['temp']
      self.hit_die = sheet['hp']['hit die']
      self.hit_dice_remaining = self.level - sheet['hp']['hit dice used']

      self.base_ac = sheet['ac']['base']
      self.armor_type = sheet['ac']['armor type']

      self.ac_dex_bonus = 0
      if self.armor_type == 'light':
        self.ac_dex_bonus = self.ability_scores['dex'][1]
      elif self.armor_type == 'medium':
        self.ac_dex_bonus = min(self.ability_scores['dex'][1], 2)

      self.shield_equipped = sheet['ac']['shield equipped']
      self.shield_ac_bonus = sheet['ac']['shield bonus']

      self.misc_ac_bonuses = sheet['ac']['other bonuses']

      self.total_ac = self.base_ac + self.ac_dex_bonus +\
                      (self.shield_ac_bonus if self.shield_equipped else 0) +\
                      sum([i for i in self.misc_ac_bonuses.values()])
      
      self.size = sheet['size']
      self.initiative = self.ability_scores['dex'][1] + sheet['initiative bonus']
      self.speed = sheet['movement speed']

      self.proficiencies = {
        'simple weapons': sheet['proficiencies']['simple weapons'],
        'martial weapons': sheet['proficiencies']['martial weapons'],
        'light armor': sheet['proficiencies']['light armor'],
        'medium armor': sheet['proficiencies']['medium armor'],
        'heavy armor': sheet['proficiencies']['heavy armor'],
        'shields': sheet['proficiencies']['shields'],
        'languages': sheet['proficiencies']['languages'],
        'tools': sheet['proficiencies']['tools'],
        'other': sheet['proficiencies']['other']
      }

      self.racial_traits = sheet['racial traits']


  def format_skill_modifiers(self) -> Panel:
    skill_tables = {}
    for short_name, long_name in ABILITY_NAMES:
      table = Table(Column(style='cyan'), '', title=f'{long_name.capitalize()}',
                    title_style='orange', show_header=False, box=box.ROUNDED, expand=True)

      buffer = ''
      if self.save_modifiers[short_name][1]:
        buffer = f'[green][P][/green] {format_modifier(self.save_modifiers[short_name][0])}'
      else:
        buffer = f'[dark gray][ ][/dark gray] {format_modifier(self.save_modifiers[short_name][0])}'
      table.add_row('[pink]Saving Throws', buffer)

      num_rows = 0
      for skill_name, [modifier, has_proficiency] in self.skill_modifiers[short_name].items():
        buffer = ''
        if has_proficiency:
          buffer = f'[green][P][/green] {format_modifier(modifier)}'
        else:
          buffer = f'[dark gray][ ][/dark gray] {format_modifier(modifier)}'
        
        # sleight of hand is an edge case and will become "Sleight Of Hand" without this
        if skill_name == 'sleight of hand':
          table.add_row('Sleight of Hand', buffer)
        else:
          table.add_row(skill_name.title(), buffer)

        num_rows += 1

      while num_rows < 5:
        table.add_row('', '')
        num_rows += 1

      skill_tables[short_name] = table

    grid = Table.grid('', '')

    grid.add_row(skill_tables['str'], skill_tables['dex'])
    grid.add_row(skill_tables['con'], skill_tables['int'])
    grid.add_row(skill_tables['wis'], skill_tables['cha'])

    return Panel(grid, title='[orange]Skill Modifiers', border_style='purple')  
  
  def format_combat_stats(self) -> Panel:
    death_save_display = Table('', '', show_header=False, box=None)
    death_save_display.add_row(
      'Successes',
      ' '.join(['[green][■][/green]' if s else '[dark gray][ ][/dark gray]'\
                for s in self.death_saves[0]])
    )
    death_save_display.add_row(
      'Failures',
      ' '.join(['[red][■][/red]' if s else '[dark gray][ ][/dark gray]'\
                for s in self.death_saves[1]])
    )
    death_save_display = Panel(death_save_display, title='[orange]Death Saves', height=4)
    
    hp_display_rows = [
      f'[cyan]Max:[/cyan] {self.max_hp}',
      f'[cyan]Current:[/cyan] ',
      f'[cyan]Hit Dice:[/cyan] {self.hit_dice_remaining}d{self.hit_die}[light gray]/'+\
        f'{self.level}d{self.hit_die}'
    ]
    
    if self.temp_hp > 0:
      hp_display_rows[1] += f'[red]{self.current_hp}[/red] + [cyan]{self.temp_hp}[/cyan] = '
    else:
      hp_display_rows[1] += f'[light gray]{self.current_hp} + 0 = [/light gray]'
    hp_display_rows[1] += f'[red]{self.current_hp + self.temp_hp}'

    left_grid_rows = (
      ('Size', f'{self.size}'),
      ('Initiative', f'{format_modifier(self.initiative)}'),
      ('Armor Class', f'{self.total_ac}'),
      ('Shield', f'Yes (+{self.shield_ac_bonus} AC)' if self.shield_equipped else 'No')
    )

    left_grid = Table.grid(Column(style='pink'), '', padding=(0, 2))
    for row in left_grid_rows: left_grid.add_row(*row)

    movement_speed_table = Table('', '', show_header=False, box=None)
    movement_speed_table_rows = (
      (('[cyan]Walking',f'{self.speed["walking"]}'.rjust(2)+' ft.') if self.speed['walking'] > 0
       else ('[dark gray]Walking', '[dark gray] 0 ft.')),
      (('[cyan]Swimming',f'{self.speed["swimming"]}'.rjust(2)+' ft.') if self.speed['swimming'] > 0
       else ('[dark gray]Swimming', '[dark gray] 0 ft.')),
      (('[cyan]Flying',f'{self.speed["flying"]}'.rjust(2)+' ft.') if self.speed['flying'] > 0
       else ('[dark gray]Flying', '[dark gray] 0 ft.'))
    )
    for row in movement_speed_table_rows: movement_speed_table.add_row(*row)

    left_group = Group(
      left_grid,
      Panel(Group(*[i for i in hp_display_rows]), title='[orange]Hit Points')
    )

    right_group = Group(
      Panel(movement_speed_table, title='[orange]Movement Speed'),
      death_save_display
    )

    grid = Table.grid(Column(ratio=1), Column(ratio=1), expand=True)
    grid.add_row(left_group, right_group)


    return Panel(grid, title='[orange]Combat Stats', border_style='purple')
  
  def format_personal_info(self) -> Panel:
    table_rows = (
      ('Name', f'[cyan]{self.name}'),
      ('Class', f'[cyan]{self.character_class} {self.level}[/cyan] ({self.character_subclass})'),
      ('Race', self.race),
      ('Background', self.background),
      ('Alignment', self.alignment)
    )

    table = Table(Column(style='pink'), '', show_header=False, box=None)
    for row in table_rows: table.add_row(*row)
    
    return Panel(table, title='[orange]Personal Info', border_style='purple')
  
  def format_ability_scores(self) -> Panel:
    ability_table_rows = (
      ('Strength', f'{self.ability_scores["str"][0]}'.rjust(2)+\
       f' ({format_modifier(self.ability_scores["str"][1])})'),
      ('Dexterity', f'{self.ability_scores["dex"][0]}'.rjust(2)+\
       f' ({format_modifier(self.ability_scores["dex"][1])})'),
      ('Constitution', f'{self.ability_scores["con"][0]}'.rjust(2)+\
       f' ({format_modifier(self.ability_scores["con"][1])})'),
      ('Intelligence', f'{self.ability_scores["int"][0]}'.rjust(2)+\
       f' ({format_modifier(self.ability_scores["int"][1])})'),
      ('Wisdom', f'{self.ability_scores["wis"][0]}'.rjust(2)+\
       f' ({format_modifier(self.ability_scores["wis"][1])})'),
      ('Charisma', f'{self.ability_scores["cha"][0]}'.rjust(2)+\
       f' ({format_modifier(self.ability_scores["cha"][1])})')
    )
    ability_table = Table(Column(style='orange'), '', box=None, show_header=False)
    for row in ability_table_rows: ability_table.add_row(*row)
    
    passive_table_rows = (
      ('Proficiency Bonus', format_modifier(self.proficiency_bonus)),
      ('Passive Perception', f'{10 + self.skill_modifiers["wis"]["perception"][0]}'),
      ('Passive Insight', f'{10 + self.skill_modifiers["wis"]["insight"][0]}'),
      ('Passive Investigation', f'{10 + self.skill_modifiers["int"]["investigation"][0]}')
    )
    passive_table = Table(Column(style='pink'), '', box=None, show_header=False)
    for row in passive_table_rows: passive_table.add_row(*row)

    return Panel(Group(
      ability_table,
      '',
      passive_table
    ), title='[orange]Game Stats', border_style='purple')
  
  def format_proficiencies(self) -> Panel:
    weapons_table_rows = (
      ('Simple' if self.proficiencies['simple weapons'] else '[dark gray]Simple',
       '[■]' if self.proficiencies['simple weapons'] else '[dark gray][ ]'),
      ('Martial' if self.proficiencies['martial weapons'] else '[dark gray]Martial',
       '[■]' if self.proficiencies['martial weapons'] else '[dark gray][ ]'),
    )
    weapons_table = Table(Column(style='cyan'), Column(style='green'), box=None, show_header=False)
    for row in weapons_table_rows: weapons_table.add_row(*row)
    weapons_table = Panel(weapons_table, title='[orange]Weapons', expand=True)

    armor_table_rows = (
      ('Light' if self.proficiencies['light armor'] else '[dark gray]Light',
       '[■]' if self.proficiencies['light armor'] else '[dark gray][ ]'),
      ('Medium' if self.proficiencies['medium armor'] else '[dark gray]Medium',
       '[■]' if self.proficiencies['medium armor'] else '[dark gray][ ]'),
      ('Heavy' if self.proficiencies['heavy armor'] else '[dark gray]Heavy',
       '[■]' if self.proficiencies['heavy armor'] else '[dark gray][ ]'),
      ('Shields' if self.proficiencies['shields'] else '[dark gray]Shields',
       '[■]' if self.proficiencies['shields'] else '[dark gray][ ]'),
    )
    armor_table = Table(Column(style='cyan'), Column(style='green'), box=None, show_header=False)
    for row in armor_table_rows: armor_table.add_row(*row)
    armor_table = Panel(armor_table, title='[orange]Armor', expand=True)

    languages_list = Panel(Group(
      # a space is added in front to match the weapons and armor tables
      *[f'[cyan] {i}' for i in self.proficiencies['languages']]
    ), title='[orange]Languages', expand=True)

    tools_list = Panel(Group(
      # a space is added in front to match the weapons and armor tables
      *[f'[cyan] {i}' for i in self.proficiencies['tools']]
    ), title='[orange]Tools', expand=True)
    
    display_grid = Table.grid(Column(ratio=1), Column(ratio=1), expand=True)
    display_grid.add_row(Group(
      weapons_table,
      tools_list
    ), Group(
      armor_table,
      languages_list
    ))

    return Panel(Group(
      display_grid
    ), title='[orange]Proficiencies', border_style='purple')

  def format_racial_traits(self) -> Panel:
    rows = []

    for name in self.racial_traits:
      rows.append(f'[cyan]{name}')

    return Panel(Group(
      *[i for i in rows]
    ), title='[orange]Racial Traits', border_style='purple')