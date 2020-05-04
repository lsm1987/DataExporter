cd "$(dirname "$0")"
source ../../.env/bin/activate
python3 ../../project/main.py config.json code
read -n 1 -s -r -p "Press any key to continue..."