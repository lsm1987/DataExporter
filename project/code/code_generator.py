import json
import os
from code.code_block import EnumCodeMember, EnumCodeBlock, ObjectCodeMember, ObjectCodeBlock
from code.code_file import CodeFile

class CodeGeneratorConfig:
    def __init__(self, config_json):
        self.schema_dir_path = config_json['schema_dir_path']
        self.code_dir_path = config_json['code_dir_path']
        self.code_prefix = config_json['code_prefix']

class CodeGenerator:
    def __init__(self, config_json):
        self.config = CodeGeneratorConfig(config_json)
        self.cached_schema_files = {} # { 파일명 : 스키마 파일 }
    
    def run(self):
        for schema_file_name in os.listdir(self.config.schema_dir_path):
            print(schema_file_name)

        return
        