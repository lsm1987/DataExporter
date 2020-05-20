def to_indentation(indent_depth, formatting):
    indentation = ''
    for i in range(indent_depth):
            indentation += formatting.indent_string
    return indentation

def to_comment(comment, indent_depth, formatting):
    indentation = to_indentation(indent_depth, formatting)
    
    text = indentation + '/// <summary>' + formatting.line_sep
    text += indentation + '/// {}'.format(comment) + formatting.line_sep
    text += indentation + '/// </summary>' + formatting.line_sep
    return text

class CodeBlock:
    def __init__(self):
        self.name = ''
        self.comment = ''
    
    def to_code(self, indent_depth, formatting):
        raise Exception('CodeBlock.to_code() is abstract method!')
        return ''


class EnumCodeMember():
    def __init__(self):
        self.name = ''
        self.comment = ''
    
    def to_code(self, indent_depth, formatting):
        text = ''
        
        if len(self.comment) != 0:
            text += to_comment(self.comment, indent_depth, formatting)

        indentation = to_indentation(indent_depth, formatting)
        
        text += indentation + '{},'.format(self.name) + formatting.line_sep

        return text


class EnumCodeBlock(CodeBlock):
    def __init__(self):
        super().__init__()
        self.members = []   # EnumCodeMember[]
    
    def to_code(self, indent_depth, formatting):
        text = ''

        if len(self.comment) != 0:
            text += to_comment(self.comment, indent_depth, formatting)
        
        indentation = to_indentation(indent_depth, formatting)

        text += indentation + 'public enum {}'.format(self.name) + formatting.line_sep
        text += indentation + '{' + formatting.line_sep

        for idx, member in enumerate(self.members):
            # 이번 멤버나 이전 멤버가 주석을 갖고 있다면 줄바꿈 추가
            if idx != 0 and (len(member.comment) != 0 or len(self.members[idx - 1].comment) != 0):
                text += formatting.line_sep

            text += member.to_code(indent_depth + 1, formatting)
        
        text += indentation + '}' + formatting.line_sep

        return text

class ObjectCodeMember():
    def __init__(self):
        self.name = ''
        self.type = ''
        self.is_array = False
        self.comment = ''

    def to_code(self, indent_depth, formatting):
        text = ''
        
        if len(self.comment) != 0:
            text += to_comment(self.comment, indent_depth, formatting)

        indentation = to_indentation(indent_depth, formatting)
        
        result_type = 'List<{}>'.format(self.type) if self.is_array else self.type

        text += indentation + 'public {} {};'.format(result_type, self.name) + formatting.line_sep

        return text

class ObjectCodeBlock(CodeBlock):
    def __init__(self):
        super().__init__()
        self.is_struct = False   # True: struct
        self.members = []   # ObjectCodeMember[]
    
    def to_code(self, indent_depth, formatting):
        text = ''
        
        if len(self.comment) != 0:
            text += to_comment(self.comment, indent_depth, formatting)

        indentation = to_indentation(indent_depth, formatting)

        result_object_category = 'struct' if self.is_struct else 'class'

        text += indentation + 'public {} {}'.format(result_object_category, self.name) + formatting.line_sep
        text += indentation + '{' + formatting.line_sep

        for idx, member in enumerate(self.members):
            # 이번 멤버나 이전 멤버가 주석을 갖고 있다면 줄바꿈 추가
            if idx != 0 and (len(member.comment) != 0 or len(self.members[idx - 1].comment) != 0):
                text += formatting.line_sep

            text += member.to_code(indent_depth + 1, formatting)
        
        text += indentation + '}' + formatting.line_sep

        return text