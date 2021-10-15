from flask import (
	Blueprint, redirect, render_template, request,
    session, url_for, abort, current_app as app)
from werkzeug.utils import secure_filename
from matchFinder.forms import themen_form
from matchFinder.forms import teilnehmer_form
from . import database_helper
from . import txt_parser
from . import helper
import os

bp = Blueprint('upload', __name__, url_prefix='/upload')

@bp.before_request
def check_status():
    """
    If the user is unauthenticated,
    this method redirects to the homepage.
    Called before each request to this subdomain
    """
    if session.get('is_authenticated') != True:
        return redirect(url_for('home.index'))

@bp.route('/')
def index():
    return render_template('upload.html')

@bp.route('/', methods=['POST'])
def file():
    """
    This function takes a file and a name and saves the entries
    into the database after parsing the file contents to arrays.
    """

    uploaded_file = request.files['file']
    if helper.validate_file(uploaded_file, app):
        teilnehmer_name = request.form.get('teilnehmer_name', None)
        themen_name = request.form.get('themen_name', None)
        if teilnehmer_name:
            teilnehmer = txt_parser.array_from_teilnehmer(uploaded_file)
            number_saved, error = database_helper.save_teilnehmer(teilnehmer, teilnehmer_name)
        elif themen_name:
            themen = txt_parser.array_from_themen(uploaded_file)
            number_saved = database_helper.save_themen(themen, themen_name)
        return redirect(url_for('upload.index', items_saved=number_saved))
    else:
        abort(400)
    return redirect(url_for('upload.index', items_saved=False))


@bp.route('/themen_manually', methods=['POST'])
def themen_manually():
    """
    handles the manual creates of themen.
    Uses WTForms to look for valid forms.
    """

    themenform = themen_form.ThemenForm()
    if themenform.validate_on_submit():
        # form is filled out and valid
        # save data to database

        rtn = database_helper.save_themen(
            themenform.themen.data,
            themenform.themen_name.data)
        return redirect(url_for('upload.index', items_saved=rtn))

    # form is not filled, present form to user
    number_of_themen = request.form.get('number_themen', None)
    if number_of_themen != None and int(number_of_themen) > 0:
        for i in range(int(number_of_themen)):
            thema_form = themen_form.ThemaEntryForm()
            themenform.themen.append_entry(thema_form)
        return render_template('upload_themen.html', form=themenform)
    return redirect(url_for('upload.index'))

@bp.route('/teilnehmer_manually', methods=['POST'])
def teilnehmer_manually():
    """
    handles the manual creates of teilnehmer.
    Uses WTForms to look for valid forms.
    """

    teilnehmerform = teilnehmer_form.TeilnehmerForm()
    if teilnehmerform.validate_on_submit():
        # form is filled out and valid
        # save data to database

        number_saved, error = database_helper.save_teilnehmer(
            teilnehmerform.teilnehmer.data,
            teilnehmerform.teilnehmer_name.data)
        if error == None:
            return redirect(url_for('upload.index', items_saved=number_saved))
        else:
            return redirect(url_for('upload.index', error=error))

    # form is not filled, present form to user
    number_of_teilnehmer = request.form.get('number_teilnehmer', None)
    if number_of_teilnehmer != None and int(number_of_teilnehmer) > 0:
        for i in range(int(number_of_teilnehmer)):
            single_teilnehmer_form = teilnehmer_form.TeilnehmerEntryForm()
            teilnehmerform.teilnehmer.append_entry(single_teilnehmer_form)
        return render_template('upload_teilnehmer.html', form=teilnehmerform)
    return redirect(url_for('upload.index'))
