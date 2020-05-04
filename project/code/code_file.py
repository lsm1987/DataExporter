class CodeFileFormatting:
    def __init__(self):
        self.indent_string = '   '
        self.line_sep = '\r\n'  # 플랫폼 무관하게 같은 문서 생성되어야 하므로 os.linesep 사용하지 않음

class CodeFile:
    def __init__(self):
        self.name = ''
        self.blocks = [] # CodeBlock[]
        self.formatting = CodeFileFormatting()
    
    def to_code(self):
        text = 'using System.Collections.Generic;' + self.formatting.line_sep
        text += self.formatting.line_sep

        for idx, block in enumerate(self.blocks):
            text += block.to_code(0, self.formatting)
            
            if idx < len(self.blocks) - 1:
                text += self.formatting.line_sep

        return text