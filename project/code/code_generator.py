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
                #print(schema_file_name)
                
                file_schema = self.load_file_schema(schema_file_name)
                code_file = self.create_code_file(schema_file_name, file_schema)
                self.write_code_file(code_file)
        
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
        code_file = CodeFile()

        # 예) Enum.schema.json -> DEEnum.generated.cs
        file_keyword = schema_file_name.split('.', 1)[0]
        code_file.name = '{}{}.generated.cs'.format(self.config.code_prefix, file_keyword)
        
        if 'definitions' in file_schema:
            for block_name, block_schema in file_schema['definitions'].items():
                self.parse_code_block(block_name, block_schema, context)
        
        self.parse_code_block(file_keyword, file_schema, context)

        code_file.blocks = context.blocks
        return code_file
    
    def parse_code_block(self, block_name, block_schema, context):
        if not 'type' in block_schema:
            return

        block_type = block_schema['type']

        if block_type == 'string' and 'enum' in block_schema:
            self.parse_enum_code_block(block_name, block_schema, context)
        elif block_type == 'object':
            is_struct = 'is_struct' in block_schema and block_schema['is_struct']
            self.parse_object_code_block(block_name, block_schema, is_struct, context)
        elif block_type == 'array':
            self.parse_code_block(block_name, block_schema['items'], context)
    
    def parse_enum_code_block(self, block_name, block_schema, context):
        context.push_path(block_name)

        enum_code_block = EnumCodeBlock()
        enum_code_block.name = '{}{}'.format(self.config.code_prefix, CodeGenerator.block_path_to_type(context.current_block_path))
        enum_code_block.comment = block_schema['description'] if 'description' in block_schema else ''

        for enum_member_name in block_schema['enum']:
            enum_member = EnumCodeMember()
            enum_member.name = enum_member_name

            enum_code_block.members.append(enum_member)

        context.blocks.append(enum_code_block)
        context.pop_path()

    def parse_object_code_block(self, block_name, block_schema, is_struct, context):
        context.push_path(block_name)

        object_code_block = ObjectCodeBlock()
        object_code_block.name = '{}{}'.format(self.config.code_prefix, CodeGenerator.block_path_to_type(context.current_block_path))
        object_code_block.comment = block_schema['description'] if 'description' in block_schema else ''
        object_code_block.is_struct = is_struct

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

        property_type = property_schema['type'] if 'type' in property_schema else ''

        if property_type == 'array':
            # TODO: array 는 값 미지정 시 빈 array 생성하면 되므로 nullable 대응하지 않음. schema 로 체크할 수 있다면 수정 - lsm1987
            member_is_array = True

            item_schema = property_schema['items']
            item_type = item_schema['type'] if 'type' in item_schema else ''

            if item_type == 'array':
                raise Exception('Nested array schema is not supported!')
            elif item_type == 'object':
                member_type = self.determine_object_block_member_type(property_name, item_schema, context)
            elif item_type == 'string' and 'enum' in item_schema:
                member_type = self.determine_object_block_member_type(property_name, item_schema, context)
            else:
                member_type = self.determine_leaf_block_member_type(item_schema)
        
        elif property_type == 'object':
            member_type = self.determine_object_block_member_type(property_name, property_schema, context)

        elif property_type == 'string' and 'enum' in property_schema:
            member_type = self.determine_object_block_member_type(property_name, property_schema, context)

        else:
            member_type = self.determine_leaf_block_member_type(property_schema)
        
        return member_type, member_is_array
    
    def determine_leaf_block_member_type(self, property_schema):
        type_name = ''

        if 'type' in property_schema:
            property_type_value = property_schema['type']
            if property_type_value == 'integer':
                type_name = 'int'
            elif property_type_value == 'number':
                type_name = 'float'
            elif property_type_value == 'boolean':
                type_name = 'bool'
            elif property_type_value == 'string':
                type_name = 'string'
            else:
                raise Exception('Not supported leaf property type! property_type_value: {}'.format(property_type_value))
        
        elif '$ref' in property_schema:
            type_name = '{}{}'.format(self.config.code_prefix, CodeGenerator.ref_to_type(property_schema['$ref']))
        
        else:
            raise Exception('Not supported leaf block member type!')

        # TODO: C# 에서 string 에는 '?' 붙일 수 없음. schema 로 체크할 수 있다면 수정 - lsm1987
        if 'nullable' in property_schema and property_schema['nullable']:
            type_name += '?'
        
        return type_name

    def determine_object_block_member_type(self, property_name, property_schema, context):
        context.push_path(property_name)
        
        type_name = '{}{}'.format(self.config.code_prefix, CodeGenerator.block_path_to_type(context.current_block_path))
        
        if 'nullable' in property_schema and property_schema['nullable']:
            type_name += '?'
        
        context.pop_path()

        return type_name

    @staticmethod
    def block_path_to_type(block_path):
        text = ''

        for idx, node in enumerate(block_path):
            if idx != 0:
                text += '_'
            
            text += node[:1].upper() + node[1:]
        
        return text

    @staticmethod
    def ref_to_type(ref_uri):
        # ref_uri: Enum.schema.json#/definitions/dayOfWeek
        ref_schema_path = ref_uri.split('#')[1]  # '/definitions/dayOfWeek'
        paths = ref_schema_path.split('/') # ['', 'definitions', 'dayOfWeek']

        block_paths = []
        for path in paths:
            if len(path) == 0 or path == 'definitions' or path == 'properties' or path == 'items':
                continue
            block_paths.append(path)
        
        return CodeGenerator.block_path_to_type(block_paths)

    def write_code_file(self, code_file):
        code_file_path = os.path.join(self.config.code_dir_path, code_file.name)

        old_code = None

        try:
            with open(code_file_path, 'r', encoding='UTF8', newline='') as fp:
                old_code = fp.read()
        except FileNotFoundError:
            pass

        new_code = code_file.to_code()

        write_status = ''

        if old_code != new_code:
            with open(code_file_path, 'w', encoding='UTF8', newline='') as fp:
                fp.write(new_code)
            write_status = 'Written'
        else:
            write_status = 'Skipped'

        print('{}: {}'.format(code_file_path, write_status))


class CodeGenerateContext:
    def __init__(self):
        self.current_block_path = [] #예) ['ContentsOpenTime', 'structVal']
        self.blocks = [] # CodeBlock[]
    
    def push_path(self, node):
        self.current_block_path.append(node)
    
    def pop_path(self):
        self.current_block_path.pop()