# 오브젝트 노드 데이터를 읽었을 때 구한 정보들
class LoadedNodeObjectInfo:
    def __init__(self, data, row_end):
        self.data = data
        self.row_end = row_end