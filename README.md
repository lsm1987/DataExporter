# DataExporter

엑셀 테이블을 JSON 으로 변환 및 관련 코드를 생성하는 파이썬 툴입니다.

## 기능

### 엑셀 -> JSON 변환

* [JSON Schema](https://json-schema.org/) 로 스키마 정의
* 자료구조
  * 기본 타입
    * int, float, string, bool
  * 배열
    * 열방향, 행방향 입력 가능
  * 구조체
  * 열거형
 
### 코드 생성

* 언어
  * C#
* 자료구조 주석 생성

------------------

## 환경설정

### 가상환경 생성
* Windows
```sh
python -m venv .env
```
* macOS
```sh
python3 -m venv .env
```

### 필요 패키지 설치
```sh
pip install -r requirements.txt
```

------------------

## 사용 방법

### 스키마, 엑셀 테이블, JSON 어셋, 코드 디렉토리 생성
예)
| 용도 | 경로 |
| -- | -- |
| 스키마 | docs/sample/schema |
| 테이블 | docs/sample/tables |
| 어셋 | docs/sample/assets |
| 코드 | docs/sample/code |


### 설정 파일 생성
예) docs/sample/config.json
```json
{
    "schema_dir_path": "schema",
    "table_dir_path": "tables",
    "asset_dir_path": "assets",
    "code_dir_path": "code",
    "code_prefix": "DE"
}
```


### 스키마 정의
예) docs/sample/schema/Enum.schema.json
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "Enum.schema.json",
    
    "definitions" : {
        "DayOfWeek": {
            "description": "요일",
            "type": "string",
            "enum": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        }
    }
}
```

예) docs/sample/schema/SampleSimple.schema.json
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "SampleSimple.table.json",
    "title": "SampleSimple",
    
    "type": "array",
    "items": {
        "description": "단순 샘플 테이블 항목",
        "type": "object",
        "properties": {
            "id": { "type": "integer" },
            "intVal": { "type": "integer" },
            "floatVal": { "type": "number" },
            "strVal": { "type": "string" },
            "boolVal": { "type": "boolean" },
            "enumVal": { "$ref": "Enum.schema.json#/definitions/DayOfWeek" }
        },
        "required": [ "id" ]
    }
}
```


### 엑셀 테이블 Data 시트에 데이터 입력
| id | intVal | floatVal | strVal | boolVal | enumVal |
| -- | ------ | -------- | ------ | ------- | ------- |
| 1 | 10 | 11.1 | row1 | TRUE | Monday |
| 2 | 20 | 22.2 | row2 | FALSE | Tuesday |


### 엑셀 -> JSON 변환 툴 실행
```sh
project\main.py 설정파일.json export
```

예) docs/sample 에서 가상환경을 통해 실행하는 경우
* Windows
```sh
call ..\..\.env\Scripts\activate.bat
python ..\..\project\main.py config.json export
```

* macOS
```sh
source ../../.env/bin/activate
python3 ../../project/main.py config.json export
```


### 엑셀 -> JSON 변환 결과
예) docs/sample/assets/SampleSimple.json
```json
[
    {
        "id": 1,
        "intVal": 10,
        "floatVal": 11.1,
        "strVal": "row1",
        "boolVal": true,
        "enumVal": "Monday"
    },
    {
        "id": 2,
        "intVal": 20,
        "floatVal": 22.2,
        "strVal": "row2",
        "boolVal": false,
        "enumVal": "Tuesday"
    }
]
```


### 코드 생성 툴 실행
```sh
project\main.py 설정파일.json code
```

예) docs/sample 에서 가상환경을 통해 실행하는 경우
* Windows
```sh
call ..\..\.env\Scripts\activate.bat
python ..\..\project\main.py config.json code
```

* macOS
```sh
source ../../.env/bin/activate
python3 ../../project/main.py config.json code
```


### 코드 생성 결과
예) docs/sample/code/DEEnum.generate.cs
```csharp
using System.Collections.Generic;

/// <summary>
/// 요일
/// </summary>
public enum DEDayOfWeek
{
    Sunday,
    Monday,
    Tuesday,
    Wednesday,
    Thursday,
    Friday,
    Saturday,
}
```

예) docs/sample/code/DESampleSimple.generated.cs
```csharp
using System.Collections.Generic;

/// <summary>
/// 단순 샘플 테이블 항목
/// </summary>
public class DESampleSimple
{
    public int id;
    public int intVal;
    public float floatVal;
    public string strVal;
    public bool boolVal;
    public DEDayOfWeek enumVal;
}
```

자세한 사용예는 docs/sample 디렉토리 참고
