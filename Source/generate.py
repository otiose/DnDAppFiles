from dnd.character import *
from dnd.spell import *

from xml.etree import ElementTree as et
from xml.dom import minidom

def read_xml(file, search):
	tree = et.parse(file)
	root = tree.getroot()
	return root.findall(search)

def load_classes():
	xml = read_xml('../Character/Classes.xml', 'class')
	return [CharacterClass.parse(x) for x in xml]

def load_races(root):
	xml = root.findall('race')
	races = {}
	for element in xml:
		race = Race.parse(element)
		races[race.name] = race
	return races

def load_subraces(races, root):
	xml = root.findall('subrace')
	subraces = [Subrace.parse(x) for x in xml]
	for subrace in subraces:
		race = races[subrace.baseRace]
		combined = subrace.inheriting(race)
		races[combined.name] = combined
	return races

def load_backgrounds():
	xml = read_xml('../Character/Backgrounds.xml', 'background')
	return [Background.parse(x) for x in xml]

def load_feats():
	xml = read_xml('../Character/Feats.xml', 'feat')
	return [Feat.parse(x) for x in xml]

def load_spells():
	xml = read_xml('../Spells/PHB Spells.xml', 'spell')
	return [Spell.parse(x) for x in xml]

def run():
	compendium = et.Element('compendium')
	compendium.set('version', '5')

	tree = et.parse("Sources/1. System Reference Document/Races.xml")
	root = tree.getroot()

	# races = load_races(root)
	# races = load_subraces(races, root)
	# races = sorted(races.values(), key=lambda x: x.name)
	classes = load_classes()
	# backgrounds = load_backgrounds()
	# feats = load_feats()
	# spells = load_spells()

	everything = [
		classes,
		# races,
		# backgrounds,
		# feats,
		# spells
		]

	for category in everything:
		for x in category:
			compendium.append(x.toXML())


	roughString = et.tostring(compendium, 'utf-8')
	reparsed = minidom.parseString(roughString)
	print reparsed.toprettyxml(indent='\t', encoding='utf-8')

if __name__ == "__main__":
	run()
	# test()