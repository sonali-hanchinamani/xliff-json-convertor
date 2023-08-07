from flask import Flask, render_template, request, send_file
import os
import xml.etree.ElementTree as ET
import json
import re
import tempfile

app = Flask(__name__)

def xliff_to_json_converter(file_name: str) -> str:
    root = ET.parse(file_name).getroot()
    namespace = re.match(r'{.*}', root.tag).group(0)

    trglang = root.get('trglang')
    json_filename = f"{trglang}.json"
    json_file_path = os.path.join(tempfile.gettempdir(), json_filename)

    result = {}
    for unit in root.iter(f'{namespace}unit'):
        id_value = unit.get("id")
        target_element = unit.find(f'{namespace}segment/{namespace}target')
        if target_element is not None and target_element.text:
            value = target_element.text
            root_key, key = id_value.split('.')
            if root_key not in result:
                result[root_key] = {}
            result[root_key][key] = value

    with open(json_file_path, 'w') as json_file:
        json.dump(result, json_file, indent=4, ensure_ascii=False)

    return json_file_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xliff'):
            json_file_path = xliff_to_json_converter(file)
            return send_file(json_file_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
