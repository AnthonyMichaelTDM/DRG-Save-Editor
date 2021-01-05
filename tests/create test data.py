import json
import os
import sys
from pprint import pprint as pp

sys.path.append(r"D:\Programming\Projects\DRG-save-editing\src\main\python")
from main import init_values, get_overclocks

save_num = 0
test_list = list()

for i in os.scandir("tests/"):
    if i.name.endswith(".sav"):
        save_num += 1

for i in range(1, save_num + 1):
    src_file = f"tests/sample_save{str(i)}.sav"
    dummy_save_file = f"tests/save_data{str(i)}.json"
    # dummy_resource_file = f'tests/resource_data{str(save_num)}.json'
    print(src_file, dummy_save_file)
    with open(src_file, "rb") as s:
        data = s.read()

    with open("guids.json", "r") as g:
        guids = json.loads(g.read())

    stats = init_values(data)
    # pp(stats)
    forged_ocs, unacquired_ocs, unforged_ocs = get_overclocks(data, guids)
    stats["unforged"] = unforged_ocs

    # pp(stats)
    with open(dummy_save_file, "w") as d:
        d.write(json.dumps(stats, indent=4))

    test_list.append(
        f'        ("tests/sample_save{i}.sav", "tests/save_data{i}.json"),\n'
    )

test_file_path = "tests/test_editor.py"
with open(test_file_path, "r") as t:
    test_string = t.read()

pos = test_string.find('change_path",\n    [') + 20  # len of find string
end_pos = test_string.find("    ],")

test_string = test_string[:pos] + "".join(test_list) + test_string[end_pos:]

with open(test_file_path, "w") as t:
    t.write(test_string)
