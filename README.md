# DataExporter

엑셀 테이블을 JSON 으로 변환하는 파이썬 툴입니다.

## 기능

* 기본 타입
  * int, float, string, bool
* 배열
  * 열방향, 행방향 입력 지원
* 구조체

------------------

## 환경설정

### 가상환경 생성
```sh
python -m venv .env
```

### 필요 패키지 설치
```sh
pip install -r requirements.txt
```

------------------

## 사용 방법

### 엑셀 테이블, JSON 어셋 디렉토리 생성
예) 테이블: docs/sample/tables  
예) 어셋: docs/sample/assets

### 설정 파일 생성
예) docs/sample/config.json
```json
{
    "table_dir_path": "tables",
    "asset_dir_path": "assets"
}
```

### 엑셀 테이블 Define 시트에 구조 정의
예) docs/sample/tables/sample_simple.xlsx
| Name | Type | Descripion |
| ---- | ---- | ---------- |
| id | int | ID |
| intVal | int | 정수 |
| floatVal | float | 부동소수 |
| strVal | string | 문자열 |
| boolVal | bool | boolean |


### 엑셀 테이블 Data 시트에 데이터 입력
| id | intVal | floatVal | strVal | boolVal |
| -- | ------ | -------- | ------ | ------- |
| 1 | 10 | 11.1 | row1 | TRUE |
| 2 | 20 | 22.2 | row2 | FALSE |

### 변환 툴 실행
```sh
project\main.py 설정파일.json
```

예) docs/sample 에서 가상환경을 통해 실행하는 경우
```sh
call ..\..\.env\Scripts\activate.bat
python ..\..\project\main.py config.json
```

### 변환 결과
예) docs/sample/assets/sample_simple.json
```json
[
    {
        "id": 1,
        "intVal": 10,
        "floatVal": 11.1,
        "strVal": "row1",
        "boolVal": true
    },
    {
        "id": 2,
        "intVal": 20,
        "floatVal": 22.2,
        "strVal": "row2",
        "boolVal": false
    }
]
```

자세한 사용예는 docs/sample 디렉토리 참고
