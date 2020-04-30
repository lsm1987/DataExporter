import sys
import json
from data_exporter import DataExporter

# argv[1]: 설정 파일 경로
def main():
    config_file_path = sys.argv[1] if len(sys.argv) >= 2 else ''
    if not config_file_path:
        raise Exception('No config file path')

    with open(config_file_path) as config_file:
        config_data = json.load(config_file)
        #print(config_data)

        exporter = DataExporter(config_data)
        exporter.run()

if __name__ == '__main__':
    main()