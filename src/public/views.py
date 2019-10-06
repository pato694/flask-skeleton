"""
Logic for dashboard related routes
"""
from flask import Blueprint, render_template
from .forms import LogUserForm, secti,masoform, vstupnitestform, ValidateParent, ValidateDite
from ..data.database import db
from ..data.models import LogUser
blueprint = Blueprint('public', __name__)

@blueprint.route('/', methods=['GET'])
def index():
    return render_template('public/index.tmpl')

@blueprint.route('/loguserinput',methods=['GET', 'POST'])
def InsertLogUser():
    form = LogUserForm()
    if form.validate_on_submit():
        LogUser.create(**form.data)
    return render_template("public/LogUser.tmpl", form=form)

@blueprint.route('/loguserlist',methods=['GET'])
def ListuserLog():
    pole = db.session.query(LogUser).all()
    return render_template("public/listuser.tmpl",data = pole)

@blueprint.route('/secti', methods=['GET','POST'])
def scitani():
    form = secti()
    if form.validate_on_submit():
        return render_template('public/vystup.tmpl',hod1=form.hodnota1.data,hod2=form.hodnota2.data,suma=form.hodnota1.data+form.hodnota2.data)
    return render_template('public/secti.tmpl', form=form)

@blueprint.route('/maso', methods=['GET','POST'])
def masof():
    form = masoform()
    if form.validate_on_submit():
        return render_template('public/masovystup.tmpl',hod1=form.hodnota1.data,hod2=form.hodnota2.data,suma=form.hodnota1.data+form.hodnota2.data)
    return render_template('public/maso.tmpl', form=form)

@blueprint.route('/vstupni_test', methods=['GET','POST'])
def vstupnitest():
    from ..data.models import Vysledky
    from flask import flash
    form = vstupnitestform()
    if form.validate_on_submit():
        # vyhodnoceni vysledku z formulare
        vysledek = 0
        if form.otazka1.data == 2:
            vysledek = vysledek + 1
        if form.otazka2.data == 0:
            vysledek = vysledek + 1
        if form.otazka3.data.upper() == "ELEPHANT":
            vysledek = vysledek + 1
        # ukladani vysledku do databazove vety
        i = Vysledky(username=form.Jmeno.data,hodnoceni=vysledek)
        db.session.add(i)
        db.session.commit()
        dotaz = db.session.query(Vysledky.username,func.count(Vysledky.hodnoceni).label("suma")).group_by(Vysledky.username).all()
        return render_template('public/vysledekvystup.tmpl',data=dotaz)
        flash("Vysledek ulozen")
    return render_template('public/vstupnitest.tmpl', form=form)

@blueprint.route('/testvystup', methods=['GET','POST'])
def testvystup():
    from ..data.models.vysledky import Vysledky
    from sqlalchemy import func
    dotaz = db.session.query(Vysledky.username, func.count(Vysledky.hodnoceni).label("suma")).group_by(Vysledky.username).all()
    return render_template('public/vysledekvystup.tmpl', data=dotaz)

#@blueprint.route('/vysledekvystup', methods=['GET','POST'])
#def testvystupuzivatel(username):
 #   from ..data.models.vysledky import Vysledky
  #  dotaz = db.session.query(Vysledky.username, Vysledky.hodnoceni.filter(Vysledky.username == username).all()
   # return render_template('public/vysledekvystupuzivatel.tmpl', form=form)


@blueprint.route('/vystupjson', methods=['GET'])
def testvystupjson():
    from ..data.models.vysledky import Vysledky
    from flask import jsonify
    dotaz = db.session.query("username", Vysledky.username, Vysledky.username, Vysledky.hodnoceni).all()
    return jsonify(dotaz)

@blueprint.route('/nactenijson', methods=['GET'])
def nactenijson():
    from flask import jsonify
    import requests, os
    os.environ['NO_PROXY'] = '127.0.0.1'
    proxies = {
        "http": None,
        "https": "http://192.168.1.1:800"
    }
    response = requests.get("http://192.168.10.1:5000/nactenijson")
    json_res = response.json()
    data = []
    for radek in json_res["list"]:
        data.append(radek["main"]["temp"])
    #return render_template("public/dataprint.tmpl",data=data)
    return jsonify(json_res)

#@blueprint.route('/chart', methods=['GET'])
#def chart():
 #   legend = 'Temperatures'
  #  temperatures = [73.7, 73.4, 73.8, 72.8, 68.7, 65.2,
   #                 61.8, 58.7, 58.2, 58.3, 60.5, 65.7,
    #                70.2, 71.4, 71.2, 70.9, 71.3, 71.1]
    #times = ['12:00PM', '12:10PM', '12:20PM', '12:30PM', '12:40PM', '12:50PM',
     #        '1:00PM', '1:10PM', '1:20PM', '1:30PM', '1:40PM', '1:50PM',
      #       '2:00PM', '2:10PM', '2:20PM', '2:30PM', '2:40PM', '2:50PM']
    #return render_template('public/chart.tmpl', values=temperatures, labels=times, legend=legend)

@blueprint.route('/chart', methods=['GET'])
def chart():
    legend = 'Monthly Data'
    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]
    from flask import jsonify
    import requests, os
    os.environ['NO_PROXY'] = '127.0.0.1'
    proxies = {
        "http": None,
        "https": "http://192.168.1.1:800"
    }
    response = requests.get("http://192.168.10.1:5000/nactenijson")
    json_res = response.json()
    data = []
    for radek in json_res["list"]:
        data.append(radek["main"]["temp"])
    return render_template('public/chart.tmpl', values=data, labels=data, legend=legend)

@blueprint.route('/vstup_rodic', methods=['GET','POST'])
def rodic():
    from flask import flash
    from ..data.models.loguzivatele import Child, Parent
    form = ValidateParent()
    if form.is_submitted():
        Parent.create(**form.data)
        flash(message="Ulozeno", category= "infor")
    return render_template('public/rodic.tmpl', form=form)

@blueprint.route('/vstup_dite', methods=['GET','POST'])
def dite():
    from flask import flash
    from ..data.models.loguzivatele import Child, Parent
    form = ValidateDite()
    form.parent_id.choices = db.session.query(Parent.id, Parent.prijmeni).all()
    if form.is_submitted():
        Child.create(**form.data)
        flash(message="Ulozeno", category= "infor")
    return render_template('public/dite.tmpl', form=form)

