import json
import os
from code.code_block import EnumCodeMember, EnumCodeBlock, ObjectCodeMember, ObjectCodeBlock
from code.code_file import CodeFile
from jsonschema import Draft7Validator

class CodeGeneratorConfig:
    def __init__(self, config_json):
        self.schema_dir_path = config_json['schema_dir_path']
        self.code_dir_path = config_json['code_dir_path']
        self.code_prefix = config_json['code_prefix']

class CodeGenerator:
    def __init__(self, config_json):
        self.config = CodeGeneratorConfig(config_json)
        self.cached_file_schemas = {} # { 파일명 : 파일 스키마 }
    
    def run(self):
        for schema_file_name in os.listdir(self.config.schema_dir_path):
            if schema_file_name.endswith('.json'):
                print(schema_file_name)
                
                file_schema = self.load_file_schema(schema_file_name)
                code_file = self.create_code_file(schema_file_name, file_schema)
                print(code_file.to_code())
        
        return
    
    def load_file_schema(self, schema_file_name):
        if schema_file_name in self.cached_file_schemas:
            return self.cached_file_schemas[schema_file_name]
        
        schema_file_path = os.path.join(self.config.schema_dir_path, schema_file_name)

        file_schema = None
        with open(schema_file_path, 'r', encoding='UTF8') as fp:
            file_schema = json.load(fp)
        
        Draft7Validator.check_schema(file_schema)

        self.cached_file_schemas[schema_file_name] = file_schema

        return file_schema
    
    def create_code_file(self, schema_file_name, file_schema):
        context = CodeGenerateContext()
        context.schema_file_name = schema_file_name

        code_file = CodeFile()

        # 예) Enum.schema.json -> DEEnum.generated.cs
        file_keyword = schema_file_name.split('.', 1)[0]
        code_file.name = '{}{}.generated.cs'.format(self.config.code_prefix, file_keyword)
        
        if 'definitions' in file_schema:
            for block_name, block_schema in file_schema['definitions'].items():
                self.parse_code_block(block_name, block_schema, context)

        code_file.blocks = context.blocks
        return code_file
    
    def parse_code_block(self, block_name, block_schema, context):
        if block_schema['type'] == 'string' and 'enum' in block_schema:
            self.parse_enum_code_block(block_name, block_schema, context)
        elif block_schema['type'] == 'object':
            self.parse_object_code_block(block_name, block_schema, context)
        elif block_schema['type'] == 'array':
            self.parse_code_block(block_name, block_schema['items'], context)
    
    def parse_enum_code_block(self, block_name, block_schema, context):
        context.push_path(block_name)

        enum_code_block = EnumCodeBlock()
        enum_code_block.name = '{}{}'.format(self.config.code_prefix, context.get_block_code_name())
        enum_code_block.comment = block_schema['description'] if 'description' in block_schema else ''

        for enum_member_name in block_schema['enum']:
            enum_member = EnumCodeMember()
            enum_member.name = enum_member_name

            enum_code_block.members.append(enum_member)

        context.blocks.append(enum_code_block)
        context.pop_path()

    def parse_object_code_block(self, block_name, block_schema, context):
        context.push_path(block_name)

        object_code_block = ObjectCodeBlock()
        object_code_block.name = '{}{}'.format(self.config.code_prefix, context.get_block_code_name())
        object_code_block.comment = block_schema['description'] if 'description' in block_schema else ''

        for object_property_name, object_property_schema in block_schema['properties'].items():
            # Object property 가 block 화 가능하다면 수행
            self.parse_code_block(object_property_name, object_property_schema, context)

            object_member = ObjectCodeMember()
            object_member.name = object_property_name
            object_member.type, object_member.is_array = self.determine_block_member_type(object_property_name, object_property_schema, context)
            object_member.comment = object_property_schema['description'] if 'description' in object_property_schema else ''

            object_code_block.members.append(object_member)
        
        context.blocks.append(object_code_block)
        context.pop_path()
    
    def determine_block_member_type(self, property_name, property_schema, context):
        member_type = ''
        member_is_array = False

        property_type = property_schema['type']

        if property_type == 'array':
            member_is_array = True

            item_schema = property_schema['items']
            item_type = item_schema['type']

            if item_type == 'array':
                raise Exception('Nested array schema is not supported!')
            elif item_type == 'object':
                context.push_path(property_name)
                member_type = '{}{}'.format(self.config.code_prefix, context.get_block_code_name())
                context.pop_path()
            elif item_type == 'string' and 'enum' in item_schema:
                context.push_path(property_name)
                member_type = '{}{}'.format(self.config.code_prefix, context.get_block_code_name())
                context.pop_path()
            else:
                member_type = self.determine_leaf_block_member_type(item_schema)
        
        elif property_type == 'object':
            context.push_path(property_name)
            member_type = '{}{}'.format(self.config.code_prefix, context.get_block_code_name())
            context.pop_path()
        
        elif property_type == 'string' and 'enum' in property_schema:
            context.push_path(property_name)
            member_type = '{}{}'.format(self.config.code_prefix, context.get_block_code_name())
            context.pop_path()

        else:
            member_type = self.determine_leaf_block_member_type(property_schema)
        
        return member_type, member_is_array
    
    def determine_leaf_block_member_type(self, property_schema):
        property_type = property_schema['type']
        if property_type == 'integer':
            return 'int'
        elif property_type == 'number':
            return 'float'
        elif property_type == 'boolean':
            return 'bool'
        elif property_type == 'string':
            return 'string'
        else:
            raise Exception('Not supported leaf property type! type: {}'.format(property_type))

class CodeGenerateContext:
    def __init__(self):
        self.schema_file_name = ''
        self.current_block_path = [] #예) ['ContentsOpenTime', 'structVal']
        self.blocks = [] # CodeBlock[]
    
    def push_path(self, node):
        self.current_block_path.append(node)
    
    def pop_path(self):
        self.current_block_path.pop()
    
    def get_block_code_name(self):
        text = ''

        for idx, node in enumerate(self.current_block_path):
            if idx != 0:
                text += '_'
            
            text += node[:1].upper() + node[1:]
        
        return text