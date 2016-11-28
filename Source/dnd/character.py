from xml.etree import ElementTree as et

class Abilities(object):

	def __init__(self, str=0, dex=0, con=0, int=0, wis=0, cha=0):
		self.str = str
		self.dex = dex
		self.con = con
		self.int = int
		self.wis = wis
		self.cha = cha

	@staticmethod
	def parse(element):
		if element is None:
			return Abilities()

		text = element.text or ""
		strings = [s.strip() for s in text.split(',')]
		# strings = [s.strip() for s in strings]
		a = {
			"str": 0,
			"dex": 0,
			"con": 0,
			"int": 0,
			"wis": 0,
			"cha": 0
		}

		for string in strings:
			values = string.split(' ')
			name = values[0].lower()
			a[name] = int(values[1])

		return Abilities(
			a["str"],
			a["dex"],
			a["con"],
			a["int"],
			a["wis"],
			a["cha"])

	def toXML(self):
		element = et.Element('ability')
		abilities = []
		if self.str > 0:
			abilities += ["Str %s" % self.str]
		if self.dex > 0:
			abilities += ["Dex %s" % self.dex]
		if self.con > 0:
			abilities += ["Con %s" % self.con]
		if self.int > 0:
			abilities += ["Int %s" % self.int]
		if self.wis > 0:
			abilities += ["Wis %s" % self.wis]
		if self.cha > 0:
			abilities += ["Cha %s" % self.cha]
		element.text = ', '.join(abilities)
		return element

	def adding(self, abilities):
		stren = self.str + abilities.str
		dex = self.dex + abilities.dex
		con = self.con + abilities.con
		intel = self.int + abilities.int
		wis = self.wis + abilities.wis
		cha = self.cha + abilities.cha
		return Abilities(stren, dex, con, intel, wis, cha)


class Trait(object):

	def __init__(self, name, texts):
		self.name = name
		self.texts = texts

	@staticmethod
	def parse(element):
		name = element.findtext('name')
		textElements = element.findall('text')
		texts = [s.text or '' for s in textElements]
		return Trait(name, texts)

	def toXML(self):
		element = et.Element('trait')
		name = et.SubElement(element, 'name')
		name.text = self.name
		for text in self.texts:
			textElement = et.SubElement(element, 'text')
			textElement.text = text
		return element


class Race:

	def __init__(self, name=None, size=None, speed=None, abilities=None, proficiencies=None, traits=None):
		self.name = name or ""
		self.size = size or "M"
		self.speed = speed or 30
		self.abilities = abilities or Abilities()
		self.proficiencies = proficiencies or []
		self.traits = traits or []

	@staticmethod
	def parse(element):
		name = element.findtext('name')
		size = element.findtext('size')
		speed = int(element.findtext('speed') or 0)
		abilityElement = element.find('ability')
		abilities = Abilities.parse(abilityElement)
		proficienciesString = element.findtext('proficiency') or ""
		if len(proficienciesString) > 0:
			proficiencies = [s.strip() for s in proficienciesString.split(',')]
		else:
			proficiencies = []
		traits = [Trait.parse(e) for e in element.findall('trait')]
		return Race(name, size, speed, abilities, proficiencies, traits)

	def toXML(self):
		element = et.Element('race')
		name = et.SubElement(element, 'name')
		name.text = self.name
		size = et.SubElement(element, 'size')
		size.text = self.size
		speed = et.SubElement(element, 'speed')
		speed.text = str(self.speed)
		abilities = self.abilities.toXML()
		element.append(abilities)
		proficiencies = et.SubElement(element, 'proficiency')
		proficiencies.text = ', '.join(self.proficiencies)
		traits = [t.toXML() for t in self.traits]
		for trait in traits:
			element.append(trait)
		return element

	def copy(self):
		return Race(self.name, self.size, self.speed, self.abilities, list(self.proficiencies), list(self.traits))

class Subrace:

	def __init__(self, baseRace=None, name=None, size=None, speed=None, abilities=None, proficiencies=None, traits=None):
		self.baseRace = baseRace
		self.name = name
		self.size = size
		self.speed = speed
		self.abilities = abilities or Abilities()
		self.proficiencies = proficiencies or []
		self.traits = traits or []

	@staticmethod
	def parse(element):
		baseRace = element.get('base') or ''
		name = element.findtext('name')
		size = element.findtext('size')
		speed = int(element.findtext('speed') or 0)
		abilityElement = element.find('ability')
		abilities = Abilities.parse(abilityElement)

		proficienciesString = element.findtext('proficiency') or ""
		if len(proficienciesString) > 0:
			proficiencies = [s.strip() for s in proficienciesString.split(',')]
		else:
			proficiencies = []

		traits = [Trait.parse(e) for e in element.findall('trait')]
		return Subrace(baseRace, name, size, speed, abilities, proficiencies, traits)

	def inheriting(self, race):
		return Race(
			self.name or race.name,
			self.size or race.size,
			self.speed or race.speed,
			self.abilities.adding(race.abilities),
			race.proficiencies + self.proficiencies,
			race.traits + self.traits)


class Modifier(object):

	def __init__(self, category, value):
		self.category = category
		self.value = value

	@staticmethod
	def parse(element):
		category = element.get("category")
		text = element.text
		if category is None or text is None:
			return None

		return Modifier(category, text)


	def toXML(self):
		element = et.Element('modifier')
		element.text = self.value
		if self.category is not None:
			element.set('category', self.category)
		return element

class Feature(object):

	def __init__(self, name=None, text=None, optional=False, modifiers=None):
		self.optional = optional
		self.name = name or ""
		self.text = text or []
		self.modifiers = modifiers or []

	def toString(self, indent=0):
		desc = [
			"Feature{}: {}".format((" (Optional)" if self.optional else ""), self.name),
		]
		desc += self.text
		desc = map(lambda x: x or "", desc)

		# tabs = "\t" * indent
		# desc = map(lambda x: tabs + x, desc)
		return '\n'.join(desc)

	@staticmethod
	def parse(element):
		featureName = element.findtext('name') or ''
		optional = element.get('optional', 'NO') == 'YES'
		textElements = element.findall('text') or []
		texts = [e.text or "" for e in textElements]
		modifierElements = element.findall('modifier') or []
		modifiers = [Modifier.parse(element) for element in modifierElements]
		return Feature(featureName, texts, optional, modifiers)

	def toXML(self):
		element = et.Element('feature')
		name = et.SubElement(element, 'name')
		name.text = self.name

		if self.optional:
			element.set('optional', 'YES')

		for text in self.text:
			textElement = et.SubElement(element, 'text')
			textElement.text = text

		for modifier in self.modifiers:
			modifierElement = modifier.toXML()
			element.append(modifierElement)

		return element


class Slots(object):

	def __init__(self, optional=False, slots=None):
		self.optional = optional
		self.slots = slots or [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

	def hasSlots(self):
		return reduce(lambda x, y: x+y, self.slots) > 0

	@staticmethod
	def parse(element):
		optional = element.get('optional', 'NO') == 'YES'
		slotText = element.text or ''
		slotNumbers = map(int, slotText.split(','))
		return Slots(optional, slotNumbers)

	def toXML(self):
		element = et.Element('slots')
		slots = map(str, self.slots)
		element.text = ','.join(slots)
		if self.optional:
			element.attrib["optional"] = "YES"

		return element


class Level(object):

	def __init__(self, level=None, slots=None, features=None):
		self.level = level or 0
		self.slots = slots or Slots()
		self.features = features or []

	def toString(self, indent=None):
		indent = indent or 0
		desc = [
			"Level: %s" % self.level,
			"Slots{}: {}".format(("  (Optional)" if self.slots.optional else ""), self.slots),
		]
		features = map(lambda x: x.toString(indent - 1), self.features)
		desc += features
		tabs = '\t' * indent
		desc = map(lambda x: tabs + x, desc)
		return '\n'.join(desc)

	@staticmethod
	def parse(elements):
		levels = {}

		for element in elements:
			number = element.get('level', '0')
			if number == '0':
				continue

			# Get an existing level if it exists, or create a new one
			level = levels.get(number) or Level(int(number))

			# Get the slots if they exist
			slotElement = element.find('slots')
			if slotElement is not None:
				level.slots = Slots.parse(slotElement)

			# Get the features if they exist
			featureElements = element.findall('feature') or []
			for featureElement in featureElements:
				feature = Feature.parse(featureElement)
				level.features.append(feature)

			levels[str(level.level)] = level

		return sorted(levels.values(), key=lambda x: x.level)


	def slotsXML(self):
		element = et.Element('autolevel')
		element.attrib['level'] = str(self.level)
		slots = self.slots.toXML()
		element.append(slots)
		return element

	def toXML(self):
		element = et.Element('autolevel')
		element.set('level', str(self.level))

		for feature in self.features:
			featureElement = feature.toXML()
			element.append(featureElement)

		return element


class CharacterClass(object):

	def __init__(self, name, hitDie, proficiencies, spellAbility, levels):
		self.name = name
		self.hitDie = hitDie
		self.proficiencies = proficiencies
		self.spellAbility = spellAbility
		self.levels = levels

	def hasSlots(self):
		for level in self.levels:
			if level.slots.hasSlots():
				return True
		return False

	@staticmethod
	def parse(element):
		name = element.findtext('name') or ''
		hitDie = int(element.findtext('hd') or '0')
		proficiency = element.findtext('proficiency') or ''
		proficiencies = [skill.strip() for skill in proficiency.split(',')]
		spellAbility = element.findtext('spellAbility') or ''
		levelElements = element.findall('autolevel') or []

		levels = Level.parse(levelElements)

		return CharacterClass(name, hitDie, proficiencies, spellAbility, levels)

	def toXML(self):
		element = et.Element('class')
		name = et.SubElement(element, 'name')
		name.text = self.name
		hd = et.SubElement(element, 'hd')
		hd.text = str(self.hitDie)
		proficiency = et.SubElement(element, 'proficiency')
		proficiency.text = ', '.join(self.proficiencies)
		spellAbility = et.SubElement(element, 'spellAbility')
		spellAbility.text = self.spellAbility

		# First make the slots levels
		if self.hasSlots():
			for level in self.levels:
				levelSlotsElement = level.slotsXML()
				element.append(levelSlotsElement)

		# Then go again and do the features
		for level in self.levels:
			levelElement = level.toXML()
			element.append(levelElement)

		return element

class Background:

	def __init__(self, name=None, proficiencies=None, traits=None):
		self.name = name or ''
		self.proficiencies = proficiencies or []
		self.traits = traits or []

	@staticmethod
	def parse(element):
		name = element.findtext('name')
		proficiencyString = element.findtext('proficiency') or ''
		proficiencies = [s.strip() for s in proficiencyString.split(',')]
		traitElements = element.findall('trait')
		traits = [Trait.parse(e) for e in traitElements]
		return Background(name, proficiencies, traits)

	def toXML(self):
		element = et.Element('background')
		name = et.SubElement(element, 'name')
		name.text = self.name
		proficiencies = et.SubElement(element, 'proficiency')
		proficiencies.text = ', '.join(self.proficiencies)
		for trait in self.traits:
			element.append(trait.toXML())
		return element


class Feat:

	def __init__(self, name=None, prerequisite=None, text=None, modifiers=None):
		self.name = name or ''
		self.prerequisite = prerequisite or ''
		self.text = text or []
		self.modifiers = modifiers or []

	@staticmethod
	def parse(element):
		featureName = element.findtext('name') or ''
		prerequisite = element.findtext('prerequisite') or ''
		textElements = element.findall('text') or []
		texts = [e.text or "" for e in textElements]
		modifierElements = element.findall('modifier') or []
		modifiers = [Modifier.parse(element) for element in modifierElements]
		return Feat(featureName, prerequisite, texts, modifiers)

	def toXML(self):
		element = et.Element('feat')
		name = et.SubElement(element, 'name')
		name.text = self.name

		if self.prerequisite:
			prerequisite = et.SubElement(element, 'prerequisite')
			prerequisite.text = self.prerequisite

		for text in self.text:
			textElement = et.SubElement(element, 'text')
			textElement.text = text

		for modifier in self.modifiers:
			modifierElement = modifier.toXML()
			element.append(modifierElement)

		return element
