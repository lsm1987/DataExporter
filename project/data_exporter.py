from openpyxl import load_workbook
import json
import os
from type_node import TypeNode
from header_node import HeaderNode
from loaded_node_object_info import LoadedNodeObjectInfo

# 디렉토리 내 모든 엑셀 파일을 json 으로 변환한다.
def data_export(src_path, dest_path):
    for file_name in os.listdir(src_path):
        # 엑셀 파일이 열려있을 때 생기는 임시파일 제외
        if file_name.endswith('.xlsx') and not file_name.startswith('~'):
            excel_path = os.path.join(src_path, file_name)

            json_file_name = os.path.splitext(file_name)[0] + '.json'
            json_path = os.path.join(dest_path, json_file_name)

            try:
                data_export_file(excel_path, json_path)
            except Exception as e:
                print(excel_path)
                raise e

# 엑셀 파일 하나를 json 으로 변환한다.
def data_export_file(src_path, dest_path):
    wb = load_workbook(src_path, data_only=True)

    ws_define = wb['Define']
    type_info_root = create_type_info(ws_define)
    #print(str(type_info_root))

    ws_data = wb['Data']
    type_max_depth = calc_max_depth(type_info_root, 0)
    header_info_root = create_data_header_info(ws_data, type_max_depth)
    #print(str(header_info_root))

    validate_header_info(type_info_root, header_info_root)

    datas = load_datas(ws_data, type_info_root, header_info_root)
    write_json(datas, dest_path)

def create_type_info(ws):
    # 정의 테이블 헤더 파싱
    row_header = ws[1]
    col_idx_header_name = None
    col_idx_header_type = None

    for cell_header in row_header:
        if cell_header.value == 'Name':
            col_idx_header_name = cell_header.col_idx
        elif cell_header.value == 'Type':
            col_idx_header_type = cell_header.col_idx
    
    #print(col_idx_header_name)
    #print(col_idx_header_type)

    if col_idx_header_name is None:
        raise Exception('Cannot find \'Name\' cell from define header')

    if col_idx_header_type is None:
        raise Exception('Cannot find \'Type\' cell from define header')

    # 타입 정보 노드 트리 구성
    # root 가 depth 0
    max_node_depth = col_idx_header_type - col_idx_header_name
    root = TypeNode('_root', True, '')
    ancestors = [root]

    for row in ws.iter_rows(min_row=2, max_col=max_node_depth):
        for cell in row:
            if cell.value is not None:
                type_string = ws.cell(row=cell.row, column=col_idx_header_type).value
                is_array, type_name = TypeNode.parse_type_string(type_string)
                newNode = TypeNode(cell.value, is_array, type_name)
                
                cell_depth = cell.col_idx
                parent = ancestors[-1]
                parent_depth = len(ancestors) - 1

                if cell_depth == max_node_depth:
                    # 자식 leaf 노드
                    parent.add_member(newNode)
                elif cell_depth == parent_depth + 1:
                    # 자식 중간 노드
                    parent.add_member(newNode)
                    ancestors.append(newNode)
                elif cell_depth == parent_depth:
                    # 부모와 같은 depth 의 중간 노드
                    del ancestors[-1]
                    ancestors[-1].add_member(newNode)
                    ancestors.append(newNode)
                elif cell_depth < parent_depth:
                    # 부모를 거슬러 올라가는 depth 의 중간노드
                    up_depth = cell_depth - parent_depth - 1
                    del ancestors[up_depth:]
                    ancestors[-1].add_member(newNode)
                    ancestors.append(newNode)
                else:
                    raise Exception('Invalid type node depth! Name: {}, Depth: {}, Parent Depth: {}'.format(cell.value, cell_depth, parent_depth))

                # 한 줄에는 노드 하나의 정의만 존재
                break

    return root

# 특정 노드 하위에서 지정한 이름 경로의 타입 정보 노드를 찾는다.
# @param names 예) ['rewards', 'condition', 'firstClear']
def find_node_py_path(node, node_path):
    if len(node_path) == 0:
        return node
        
    member = node.find_member(node_path[0])
    if member is not None:
        return find_node_py_path(member, node_path[1:])

    return None

# 타입 정보 트리에서 가장 깊은 depth 값을 구한다.
def calc_max_depth(node, cur_depth):
    if node is None:
        return cur_depth
    
    max_depth = cur_depth
    for member in node.members:
        member_depth = calc_max_depth(member, cur_depth + 1)
        
        if member_depth > max_depth:
            max_depth = member_depth
    
    return max_depth

def calc_node_col_end(ws, row_idx, col_idx_start, col_idx_max):
    # 시작 컬럼은 항상 유효하다고 가정
    # start + 1 ~ max 순회
    # 값이 있는 다음 셀 찾아 그 전까지를 노드 마지막 col 로 구함
    for col_idx in range(col_idx_start + 1, col_idx_max + 1):
        if ws.cell(row=row_idx, column=col_idx).value is not None:
            return col_idx - 1
    
    return col_idx_max

def calc_node_row_end(ws, col_idx, row_idx_start, row_idx_max):
    # 시작 행은 항상 유효하다고 가정
    # start + 1 ~ max 순회
    # 값이 있는 다음 셀 찾아 그 전까지를 노드 마지막 row 로 구함
    for row_idx in range(row_idx_start + 1, row_idx_max + 1):
        if ws.cell(row=row_idx, column=col_idx).value is not None:
            return row_idx - 1
    
    return row_idx_max

def is_empty_row(ws, row_idx, col_idx_start, col_idx_max):
    for row in ws.iter_rows(min_row=row_idx, max_row=row_idx, min_col=col_idx_start, max_col=col_idx_max):
        for cell in row:
            if cell.value is not None:
                return False
    
    return True

def create_data_header_info(ws, max_depth):
    root = HeaderNode('_root', 1, ws.max_column)
    ancestors = [root]

    for col in ws.iter_cols(max_row=max_depth):
        for cell in col:
            if cell.value is not None:
                parent = ancestors[-1]
                parent_depth = len(ancestors) - 1
                cell_depth = cell.row

                node_name = cell.value
                node_col_start = cell.col_idx

                if cell_depth == max_depth:
                    # 자식 leaf 노드
                    node_col_end = calc_node_col_end(ws, cell.row, node_col_start, parent.col_end)
                    newNode = HeaderNode(node_name, node_col_start, node_col_end)
                    parent.add_member(newNode)
                
                elif cell_depth == parent_depth + 1:
                    # 자식 중간 노드
                    node_col_end = calc_node_col_end(ws, cell.row, node_col_start, parent.col_end)
                    newNode = HeaderNode(node_name, node_col_start, node_col_end)
                    parent.add_member(newNode)
                    ancestors.append(newNode)
                
                elif cell_depth == parent_depth:
                    # 부모와 같은 depth 의 중간 노드
                    del ancestors[-1]
                    newParent = ancestors[-1]
                    node_col_end = calc_node_col_end(ws, cell.row, node_col_start, newParent.col_end)
                    newNode = HeaderNode(node_name, node_col_start, node_col_end)
                    newParent.add_member(newNode)
                    ancestors.append(newNode)
                
                elif cell_depth < parent_depth:
                    # 부모를 거슬러 올라가는 depth 의 중간노드
                    up_depth = cell_depth - parent_depth - 1
                    del ancestors[up_depth:]
                    newParent = ancestors[-1]
                    node_col_end = calc_node_col_end(ws, cell.row, node_col_start, newParent.col_end)
                    newNode = HeaderNode(node_name, node_col_start, node_col_end)
                    newParent.add_member(newNode)
                    ancestors.append(newNode)
    
    return root

def validate_header_info(type_root, header_root):
    # 모든 타입 노드가 헤더 노드에도 있어야 함
    # 헤더 노드에는 주석 컬럼 등도 있을 수 있으므로 반대는 체크하지 않음
    validate_type_node_exist_in_header(type_root, header_root, [])

def validate_type_node_exist_in_header(type_node, header_root, parent_node_path):
    for member in type_node.members:
        node_path = parent_node_path + [member.name]
        
        if find_node_py_path(header_root, node_path) is None:
            raise Exception('Node {} is not exist in data header'.format(node_path))

        validate_type_node_exist_in_header(member, header_root, node_path)

def parse_cell(type_name, cell):
    try:
        # 타입 무관하게 셀이 비어있으면 None 취급
        if cell.value is None:
            return None

        if type_name == 'int':
            return int(cell.value)
        elif type_name == 'float':
            return float(cell.value)
        elif type_name == 'bool':
            return bool(cell.value)
        elif type_name == 'string':
            return str(cell.value) if cell.value is not None else ''
        else:
            raise Exception('Invalid type name to parse. type_name:{}'.format(type_name))
    except Exception as e:
        print('Exception on parse_cell(). coordinate:{}'.format(cell.coordinate))
        raise e

def load_datas(ws, type_info_root, header_info_root):
    header_row_count = calc_max_depth(type_info_root, 0)
    data_row_start = header_row_count + 1
    data_row_max = max(ws.max_row, data_row_start)

    return load_node_array(ws, type_info_root, header_info_root, data_row_start, data_row_max)

def load_node_object(ws, type_node, header_node, row_start, row_max):
    data = {}
    row_end = row_max
    
    for member_header_node in header_node.members:
        member_name = member_header_node.name
        member_type_node = type_node.find_member(member_header_node.name)

        # 주석 컬럼은 타입 정보에 없음. 오류 아님
        if member_type_node is None:
            continue
        
        # 배열은 여러 행에 걸쳐 있을 수 있으므로
        # 배열이 아닌 타입을 기준으로 노드 마지막 행을 갱신한다.
        if not member_type_node.is_array:
            row_end = calc_node_row_end(ws, member_header_node.col_start, row_start, row_end)

        if member_type_node.is_leaf():
            if not member_type_node.is_array:
                # 단일값
                data_value = load_leaf_value(ws, member_type_node, member_header_node, row_start)
                if not data_value is None:
                    data[member_name] = data_value
            else:
                # 단일값 배열
                data_values = load_leaf_array(ws, member_type_node, member_header_node, row_start, row_end)
                if not data_values is None:
                    if not member_name in data:
                        data[member_name] = []
                    data[member_name].extend(data_values)
        else:
            if not member_type_node.is_array:
                # 구조체
                data_value = load_node_object(ws, member_type_node, member_header_node, row_start, row_end).data
                if not data_value is None:
                    data[member_name] = data_value
            else:
                # 구조체 배열
                data_values = load_node_array(ws, member_type_node, member_header_node, row_start, row_end)
                if not data_values is None:
                    if not member_name in data:
                        data[member_name] = []
                    data[member_name].extend(data_values)

    if len(data) == 0:
        data = None
    return LoadedNodeObjectInfo(data, row_end)

def load_node_array(ws, type_node, header_node, row_start, row_max):
    datas = []
    row_idx = row_start

    while row_idx <= row_max:
        # 빈 줄을 만나면 다음 줄로 넘어감
        # 데이터 구분 위해 의도적으로 빈 줄 남기는 경우 위함
        if is_empty_row(ws, row_idx, header_node.col_start, header_node.col_end):
            row_idx += 1
            continue
        
        loaded_info = load_node_object(ws, type_node, header_node, row_idx, row_max)
        if not loaded_info.data is None:
            datas.append(loaded_info.data)
        row_idx = loaded_info.row_end + 1

    if len(datas) > 0:
        return datas
    else:
        return None

# 리프노드 단일값 구하기
def load_leaf_value(ws, type_node, header_node, row_start):
    cell = ws.cell(column=header_node.col_start, row=row_start)
    return parse_cell(type_node.type_name, cell)

# 리프노드 배열 구하기
def load_leaf_array(ws, type_node, header_node, row_start, row_max):
    datas = []
    
    for col in ws.iter_cols(min_col=header_node.col_start, max_col=header_node.col_start, min_row=row_start, max_row=row_max):
        for cell in col:
            # 빈 줄을 만나면 다음 줄로 넘어감
            # load_node_array() 와 동작 맞추기 위함
            if cell.value is None:
                continue
            
            data_value = parse_cell(type_node.type_name, cell)
            if not data_value is None:
                datas.append(data_value)
    
    if len(datas) > 0:
        return datas
    else:
        return None

def write_json(data, path):
    old_dump = None

    try:
        with open(path, 'r', encoding='utf8') as datafile:
            old_dump = datafile.read()
    except FileNotFoundError:
        pass

    new_dump = json.dumps(data, indent=4, ensure_ascii=False)

    write_status = ''
    
    if old_dump != new_dump:
        with open(path, 'w', encoding='utf8') as datafile:
            datafile.write(new_dump)
        write_status = 'Written'
    else:
        write_status = 'Skipped'

    print('{}: {}'.format(path, write_status))