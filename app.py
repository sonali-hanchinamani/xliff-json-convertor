from flask import Flask, render_template, request, send_file
import os
import json
import re
import tempfile

app = Flask(__name__)

def xliff_to_json_converter(file_name: str) -> str:
    json_filename = "temp.json"
    json_file_path = os.path.join(tempfile.gettempdir(), json_filename)

    result = {}
    with open(file_name, "r") as fhand:
        for line in fhand:
            if "<unit id=" in line:
                unit_id = re.findall(r'"(.*?)"', line)[0].split(".")[0]
                result[unit_id] = {"defaultMessage": "temp_value"}
            elif "<target>" in line:
                last_unit_id = list(result)[-1]
                s = line.find("<target>")
                e = line.find("</target>")
                default_message = line[s+8:e]
                result[last_unit_id] = {"defaultMessage": default_message.replace("<b>", "").replace("</b>", "")}
                
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
