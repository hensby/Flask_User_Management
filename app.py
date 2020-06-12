import sys
import random

from flask import Flask
import os
from flask import Flask, request, redirect, url_for
from flask.templating import render_template
import csv
from datetime import timedelta
from werkzeug.utils import secure_filename

port = int(os.getenv('PORT', '3000'))
PIC_folder = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PIC_folder
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
all_data_dict = {}

def updateData():
    with open('data/names.csv', encoding='utf8') as r:
        d = csv.reader(r, delimiter=',', skipinitialspace=True)
        name = []
        new_data = {}
        for k, line in enumerate(d):
            if k == 0:
                continue
            if line[0] not in new_data.keys():
                new_data[line[0]] = line
                name.append(line[0])
    writeCSV(new_data)
    return new_data


@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        all_data_dict = updateData()
        i = 0
        if request.form['type'] == 'searchByState':
            print(request.form)
            tmp_data = {}
            if request.form['State'] == '':
                return render_template('home.html', result=all_data_dict)
            for _, all_data_item in all_data_dict.items():
                if all_data_item[3] == request.form['State']:
                    tmp_data[i] = all_data_item
                    i += 1
            # print(tmp_data)
            return render_template('home.html', result=tmp_data)
        if request.form['type'] == 'searchByName':
            print(request.form)
            tmp_data = {}
            if request.form['Name'] == '':
                return render_template('home.html', result=all_data_dict)
            for _, all_data_item in all_data_dict.items():
                if all_data_item[0].lower() == request.form['Name'].lower():
                    tmp_data[i] = all_data_item
                    i += 1
            return render_template('home.html', result=tmp_data)
        if request.form['type'] == 'edit':
            print(request.form)
            tmp_data = {}
            upload_file = request.files["files"]
            size = len(upload_file.read())
            upload_file.seek(0)
            if 2097152 < size:
                print("larger than 2M")
                return render_template('home.html', result=all_data_dict)
            for _, all_data_item in all_data_dict.items():
                if all_data_item[0].lower() == request.form['Name'].lower():
                    print(all_data_item)
                    tmp = []
                    tmp.append(request.form["Name"])
                    tmp.append(request.form["ID"])
                    tmp.append(request.form["Room"])
                    tmp.append(request.form["State"])
                    # tmp.append(request.form["Picture"])
                    upload_file = request.files["files"]
                    size = len(upload_file.read())
                    upload_file.seek(0)
                    if size > 2:
                        img = request.files.get('files')
                        # if allowed_file(img.filename):
                        flag = str(random.randint(0, 999))
                        path = "static/" + request.form["Name"] + flag + ".jpg"
                        img.save(path)
                        tmp.append(request.form["Name"] + flag + ".jpg")

                        path = os.path.join(PIC_folder, 'static', all_data_item[4])
                        if os.path.exists(path):
                            os.remove(path)
                        else:
                            print("no")
                    else:
                        print(22222)
                        tmp.append(all_data_item[4])
                    tmp.append(request.form["Caption"])
                    tmp_data[i] = tmp
                    i += 1
                    print(tmp)
                    continue
                tmp_data[i] = all_data_item
                i += 1
                writeCSV(tmp_data)
            return render_template('home.html', result=tmp_data)
    else:
        all_data_dict = updateData()
        return render_template('home.html', result=all_data_dict)


@app.route("/all_pictures", methods=["GET"])
def all_picture():
    updateData()
    filename = os.path.join(PIC_folder, 'static')
    sl_pictures = os.listdir(filename)
    result = []
    for p in sl_pictures:
        result.append([p])
        print(result)
    return render_template('all_pictures.html', result=result)


@app.route("/edit_page", methods=["POST"])
def edit():
    print(request.form)
    # name = request.form[]
    result = request.form["edit"].replace("'", "").replace("]", "").replace("[", "").split(",")
    return render_template("edit.html", result=result)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def writeCSV(tmp_data):
    f = open('data/names.csv', 'w', encoding='utf-8')

    csv_writer = csv.writer(f)

    csv_writer.writerow(["Name", "Grade", "Room", "State", "Picture", "Caption"])

    for _, item in tmp_data.items():
        print(item)
        csv_writer.writerow(item)

    f.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
