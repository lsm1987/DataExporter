import os

class TypeNode:
    def __init__(self, name, is_array, type_name):
        self.name = name
        self.is_array = is_array
        self.type_name = type_name
        self.members = []    # [TypeNode]
    
    @staticmethod
    def parse_type_string(type_string):
        is_array = False
        type_name = ''

        is_not_empty = type_string is not None and len(type_string) > 0

        if is_not_empty and type_string[0] == '[':
            is_array = True
            type_name = type_string[1:]
        else:
            is_array = False
            type_name = type_string if type_string is not None else ''
        
        return is_array, type_name

    @staticmethod
    def generate_type_string(is_array, type_name):
        type_string = ''

        if is_array == True:
            type_string += '['

        type_string += type_name
        return type_string
    
    def add_member(self, member):
        self.members.append(member)

    def find_member(self, name):
        for member in self.members:
            if member.name == name:
                return member
        return None

    def is_leaf(self):
        return len(self.members) == 0

    def to_string(self, depth):
        text = ''
        
        for i in range(depth):
            text += ' '

        text += '{} {}'.format(self.name, self.generate_type_string(self.is_array, self.type_name))

        for member in self.members:
            text += os.linesep + member.to_string(depth + 1)
        
        return text
    
    def __str__(self):
        return self.to_string(0)

"""
# TypeNode 테스트용
root = TypeNode('_root', True, '')
root_id = TypeNode('id', False, 'string')
root_numArr = TypeNode('numArr', True, 'number')
root_numNull = TypeNode('numNull', False, 'number')

openTimes = TypeNode('openTimes', True, '')
openTimes_dayOfWeek = TypeNode('dayOfWeek', False, 'string')

condition = TypeNode('condition', False, '')
condition_firstClear = TypeNode('condition', False, 'bool')
openTimes.add_member(condition_firstClear)

openTimes.add_member(openTimes_dayOfWeek)
openTimes.add_member(condition)

event = TypeNode('event', False, '')
event_name = TypeNode('name', False, 'string')
event.add_member(event_name)

option = TypeNode('option', False, '')
option_name = TypeNode('name', False, 'string')
option.add_member(option_name)

root.add_member(root_id)
root.add_member(root_numArr)
root.add_member(root_numNull)
root.add_member(openTimes)
root.add_member(event)
root.add_member(option)

print(str(root))
"""

"""
# parse_type_string 테스트용
is_array, type_name = TypeNode.parse_type_string('[num')
print('is_array: {}, type_name: {}'.format(is_array, type_name))
"""