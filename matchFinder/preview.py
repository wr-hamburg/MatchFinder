from flask import (
	Blueprint, redirect, render_template, request, url_for, session)
from . import database_helper
from . import helper

bp = Blueprint('preview', __name__, url_prefix='/preview')

@bp.before_request
def check_status():
	"""
	If the user is unauthenticated,
	this method redirects to the homepage.
	Called before each request to this subdomain
	"""
	if session.get('is_authenticated') != True:
		return redirect(url_for('home.index'))


@bp.route('/index/<int:verteilung_id>')
def index(verteilung_id):
	verteilung = database_helper.get_verteilung_by_id(verteilung_id)
	print(verteilung.praeferenzen)
	array = []
	for teilnehmer in verteilung.teilnehmer.teilnehmer:
		local_object = {}
		#for now dont show matr_nr at all
		local_object["name"] = teilnehmer.first_name + " " + teilnehmer.last_name# + " " + helper.build_cencored_matr(teilnehmer.matr_nr)
		praeferenz = database_helper.get_praeferenz(teilnehmer.id, verteilung.id)
		local_object["praeferenz"] = praeferenz.praeferenzen.split(",") if praeferenz != None else " "
		array.append(local_object)

	print(array)
	return render_template('preview.html', praeferenzen=array, themen=verteilung.thema_list)