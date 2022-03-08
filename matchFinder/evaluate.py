from flask import (
    Blueprint, session, render_template, request, redirect, url_for,
    send_file, after_this_request, current_app as app)
from . import database_helper
from . import matchCalculator
from . import helper
import json
import os

bp = Blueprint('evaluate', __name__, url_prefix='/evaluate')

@bp.route('/')
def index():
    """
    loads all verteilungen, so one can be selected.
    """

    verteilungen = database_helper.get_all_verteilungen()
    return render_template('evaluate.html', verteilungen=verteilungen)

@bp.route('/from_id/<int:verteilung_id>')
def from_id(verteilung_id):
    """
    Evaluates a verteilung from database data.
    First, it gathers data from the request form.
    Then, it loads the teilnehmer and themen from the database that belong to
    this verteilung.
    If a thema allows 2 or more teilnehmer, the name of the thema needs to
    be duplicated to account for the higher number of teilnehmer per thema.
    In the end, the calculated data is passed to the matchCalculator for the
    calculation.
    It then renders the results.
    """
    if session.get('is_authenticated') != True:
        return redirect(url_for('home.index'))

    verteilung = database_helper.get_verteilung_by_id(verteilung_id)
    max_per = verteilung.max_teilnehmer_per_thema
    teilnehmer = verteilung.teilnehmer.teilnehmer
    thema_list = database_helper.get_thema_list_by_id(verteilung.thema_list_id)
    themen = list(map(lambda x: x.thema_name + " (Betr: " + x.betreuer + ")", thema_list.themen))
    themen = helper.duplicate_themen(themen, max_per)
    teilnehmer_pref = []
    for teil in teilnehmer:
        praeferenz = database_helper.get_praeferenz(teil.id, verteilung.id)
        if (praeferenz == None):
            praeferenzen = list(map(lambda x: "Keine Präferenz", thema_list.themen))
            praeferenz = helper.convert_preferences(praeferenzen)
        else:
            praeferenz = praeferenz.praeferenzen
        praeferenz = praeferenz.split(',')
        censored_matr_nr = helper.build_cencored_matr(teil.matr_nr)
        name = teil.first_name + " " + teil.last_name if teil.last_name != "" else teil.first_name
        #for now don't display matr_nr at all
        concat_name = name #+ " " + censored_matr_nr
        local_teilnehmer_pref = helper.duplicate_teilnehmer_praefs(
            [concat_name] + praeferenz, max_per)
        teilnehmer_pref.append(local_teilnehmer_pref)
    assignments = matchCalculator.calculateMatchFromList(teilnehmer_pref, themen)
    assignments = helper.sort_by_median(assignments)
    return render_template('results.html', data=assignments, name=verteilung.name)

@bp.route('csv_upload', methods=['POST'])
def csv_upload():
    """
    handles calculations from files.
    Checks if file is valid, then processes it in matchCalculator
    """

    file = request.files['file']
    if helper.validate_file(file, app):
        assignments = matchCalculator.calculateFromCSV(file)
        assignments = helper.sort_by_median(assignments)
    else:
        abort(400)
    return render_template('results.html', data=assignments, name=file.filename)


@bp.route('export', methods=['GET', 'POST'])
def export():
    """
    Handles file export.
    saves a temp file for calculations, deletes it afterwards
    """

    data_string = request.form.get('data', None)
    if data_string != None:
        data_string = data_string.replace('\'', '\"')
        data_json = json.loads(data_string)
        name = data_json["name"]
        data = data_json["data"]
        filename = "auswertung_von_" + name
        with open("verteilung.txt", 'w') as f:
            if data_json["type"] == "csv":
                filename += ".csv"
                f.write(helper.create_csv(data["studis"]))
            else:
                filename += ".txt"
                f.write(helper.create_txt(data["studis"]))
        path = "../verteilung.txt"

        @after_this_request
        def remove_file(response):
            try:
                dirname = os.path.dirname(__file__)
                filename = os.path.join(dirname, path)
                os.remove(filename)
            except Exception as error:
                print("Error removing or closing downloaded file handle", error)
            return response
        return send_file(path, attachment_filename=filename, as_attachment=True)
    return redirect(url_for("home.index"))