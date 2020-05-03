import os

# 데이터 시트의 헤더 정보 노드
class HeaderNode:
    def __init__(self, name, col_start, col_end):
        self.name = name
        self.col_start = col_start
        self.col_end = col_end
        self.members = []    # [HeaderNode]

    def add_member(self, member):
        self.members.append(member)

    def find_member(self, name):
        for member in self.members:
            if member.name == name:
                return member
        return None

    def to_string(self, depth):
        text = ''
        
        for i in range(depth):
            text += '.'

        text += '{} ({}~{})'.format(self.name, self.col_start, self.col_end)

        for member in self.members:
            text += os.linesep + member.to_string(depth + 1)
        
        return text
    
    def __str__(self):
        return self.to_string(0)