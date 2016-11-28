from xml.etree import ElementTree as et

def _subElement(parent, name, value):
	elem = et.SubElement(parent, name)
	elem.text = value

class Spell:

	def __init__(self, name, level, school, ritual, time, range, components, duration, classes, text, rolls):
		self.name = name # String
		self.level = level # Int
		self.school = school # String
		self.ritual = ritual # Bool
		self.time = time # String
		self.range = range # String
		self.components = components # String
		self.duration = duration # String
		self.classes = classes # [String]
		self.text = text # [String]
		self.rolls = rolls # String

	@staticmethod
	def parse(elem):
		name = elem.findtext('name')
		level = elem.findtext('level') or '0'
		school = elem.findtext('school')
		ritual = elem.findtext('ritual') == 'YES'
		time = elem.findtext('time')
		range = elem.findtext('range')
		components = elem.findtext('components')
		duration = elem.findtext('duration')
		classes = elem.findtext('classes') or ''
		classes = [x.strip() for x in classes.split(',')]
		texts = elem.findall('text') or []
		texts = [x.text or '' for x in texts]
		rolls = elem.findall('roll') or []
		rolls = [x.text or '' for x in rolls]
		return Spell(name, int(level), school, ritual, time, range, components, duration, classes, texts, rolls)

	def toXML(self):
		elem = et.Element('spell')
		_subElement(elem, 'name', self.name)
		_subElement(elem, 'level', str(self.level))
		_subElement(elem, 'school', self.school)
		if self.ritual:
			_subElement(elem, 'ritual', 'YES')
		_subElement(elem, 'time', self.time)
		_subElement(elem, 'range', self.range)
		_subElement(elem, 'components', self.components)
		_subElement(elem, 'duration', self.duration)
		_subElement(elem, 'classes', ', '.join(self.classes))
		for text in self.text:
			_subElement(elem, 'text', text)
		for roll in self.rolls:
			_subElement(elem, 'roll', roll)
		return elem

