import yaml
import itertools as it
import json

with open("templates.yaml", "r") as input_file:
    data = yaml.safe_load(input_file)

output_data = []

cur_id = 0

for shape_key in data:
    shape = data[shape_key]
    combinations = it.product(*(shape[key] for key in shape))
    for combination in combinations:
        output_data.append({
            "id": cur_id,
            "shape_name": f"{shape_key}_{'_'.join(map(str, combination))}"
            })
        cur_id += 1

with open("templates_output.json", "w+") as output_file:
    json.dump(output_data, output_file)