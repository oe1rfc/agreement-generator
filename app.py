from flask import Flask, send_file, redirect, render_template
from jinja2.loaders import FileSystemLoader
from latex.jinja2 import make_env
from latex import build_pdf

import os, requests
app = Flask(__name__)

fahrplanjson_url = "https://fahrplan.privacyweek.at/pw19/schedule/export/schedule.json"

def get_speakerdata():
    speakers = {}
    json = requests.get(fahrplanjson_url).json()
    for d in json['schedule']['conference']['days']:
        for r in d['rooms'].values():
            for t in r:
                for p in t['persons']:
                    if p['code'] not in speakers:
                        speakers[p['code']] = p
                        speakers[p['code']]['talks'] = []
                        speakers[p['code']]['record'] = False
                        speakers[p['code']]['language'] = t['language']
                    speakers[p['code']]['talks'].append(t)
                    if t['do_not_record'] == False:
                        speakers[p['code']]['record'] = True
                    if speakers[p['code']]['language'] == 'de':
                        speakers[p['code']]['language'] = 'de'
    return speakers

def get_speakers(code = None):
    speakers = get_speakerdata()
    if code == 'all' or code == None:
        return sorted(speakers.values(), key=lambda item: item['public_name'])
    if code in speakers:
        return [speakers[code]]

def generate_agreement(speakers):
    tpl = make_env(loader=FileSystemLoader('templates/')).get_template('agreement.tex')
    return build_pdf(tpl.render(speakers=speakers), texinputs=[os.getcwd()+'/templates/', ''])

# views
@app.route('/')
def index():
    return render_template('index.j2', speakers=get_speakers())

@app.route('/<code>')
def agreement(code):
    speakers = get_speakers(code)
    if not speakers:
        return redirect('/')
    pdf = generate_agreement(speakers)
    res = send_file(pdf.stream, attachment_filename="speaker_agreement_%s.pdf" % code)
    res.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    res.headers["Pragma"] = "no-cache"
    res.headers["Expires"] = "0"
    return res

if __name__ == '__main__':
    app.run()
