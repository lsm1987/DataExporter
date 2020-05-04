import sys
import json
from exporter.data_exporter import DataExporter
from code.code_generator import CodeGenerator

# argv[1]: 설정 파일 경로
# argv[2]: 동작 모드
def main():
    config_file_path = sys.argv[1] if len(sys.argv) >= 2 else ''
    if not config_file_path:
        raise Exception('No config file path')

    run_mode = sys.argv[2] if len(sys.argv) >= 3 else ''
    if not run_mode:
        raise Exception('No run mode')

    with open(config_file_path) as config_file:
        config_data = json.load(config_file)
        #print(config_data)

        if run_mode == 'export':
            exporter = DataExporter(config_data)
            exporter.run()
        elif run_mode == 'code':
            generator = CodeGenerator(config_data)
            generator.run()
        else:
            raise Exception('Invalid run mode: ' + run_mode)

if __name__ == '__main__':
    main()