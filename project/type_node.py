import os
from enum import Enum

# 셀 값 텍스트 파싱 유형
class TypeNodeParseType(Enum):
    NONE = 0
    INT = 1
    FLOAT = 2
    BOOL = 3
    STRING = 4

class TypeNode:
    def __init__(self):
        self.name = None    # 필드명
        self.is_array = False
        self.parse_type = TypeNodeParseType.NONE
        self.members = []    # [TypeNode]

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

        text += '{} - isArray: {}, ParseType: {}'.format(self.name, self.is_array, self.parse_type)

        for member in self.members:
            text += os.linesep + member.to_string(depth + 1)
        
        return text
    
    def __str__(self):
        return self.to_string(0)