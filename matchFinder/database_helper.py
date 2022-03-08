from matchFinder.models import teilnehmer_model
from matchFinder.models import thema_model
from matchFinder.models import thema_list_model
from matchFinder.models import teilnehmer_list_model
from matchFinder.models import verteilung_model
from matchFinder.models import password_model
from matchFinder.models import praeferenz_model
from sqlalchemy.exc import IntegrityError
from . import db
import hashlib

"""
This file capsules the database and provides a clean interface
to other files and classes.
It features your typical get, delete and save operations.
At the bottom, is has more sophisticated functions that handle more
complex save operations.
"""

def init_db():
	"""
	Initialized the databasy by dropping all passwords and inserting
	new ones.
	Optionally, it drops all tables and recreates them.
	BE CAREFUL WHEN USING THIS IN PRODUCTION AS ALL DATA IS LOST AFTERWARDS.
	"""

	# reset_db() # <-- DANGER

	rows = password_model.Password.query.count()
	if rows == 0:
		password_model.Password.query.delete()
		from . import password_helper
		password_helper.create_passwords()

def reset_db():
	"""
	drops and recreates all database tables.
	BE CAREFUL WHEN USING THIS IN PRODUCTION AS ALL DATA IS LOST AFTERWARDS.
	"""
	db.drop_all()
	db.create_all()

def get_all_teilnehmer():
	return teilnehmer_model.Teilnehmer.query.all()

def get_all_teilnehmer_lists():
	return teilnehmer_list_model.Teilnehmer_List.query.all()

def get_all_themen():
	return thema_model.Thema.query.all()

def get_all_thema_lists():
	return thema_list_model.Thema_List.query.all()

def get_all_verteilungen():
	return verteilung_model.Verteilung.query.all()

def get_all_passwords():
	return password_model.Password.query.all()

def get_teilnehmer_by_id(id):
	return teilnehmer_model.Teilnehmer.query.filter_by(id=id).first()

def get_teilnehmer_list_by_id(id):
	return teilnehmer_list_model.Teilnehmer_List.query.filter_by(id=id).first()

def get_thema_by_id(id):
	return thema_model.Thema.query.filter_by(id=id).first()

def get_thema_list_by_id(id):
	return thema_list_model.Thema_List.query.filter_by(id=id).first()

def get_verteilung_by_id(id):
	return verteilung_model.Verteilung.query.filter_by(id=id).first()

def get_verteilung_by_hashed_id(hashed_id):
	verteilungen = get_all_verteilungen()
	for vert in verteilungen:
		hashed_db_id = hashlib.sha256(str(vert.id).encode()).hexdigest()
		if hashed_db_id == hashed_id:
			return vert
	return None

def get_praeferenz(teilnehmer_id, verteilung_id):
	return praeferenz_model.Praeferenz.query.filter_by(
		teilnehmer_id=teilnehmer_id, verteilung_id=verteilung_id
		).first()

def delete_teilnehmer_by_id(id):
	db.session.delete(get_teilnehmer_by_id(id))
	db.session.commit()

def delete_teilnehmer_list_by_id(id):
	db.session.delete(get_teilnehmer_list_by_id(id))
	db.session.commit()

def delete_thema_by_id(id):
	db.session.delete(get_thema_by_id(id))
	db.session.commit()

def delete_thema_list_by_id(id):
	db.session.delete(get_thema_list_by_id(id))
	db.session.commit()

def delete_verteilung_by_id(id):
	db.session.delete(get_verteilung_by_id(id))
	db.session.commit()

def insert_password(password):
	db.session.add(password)
	db.session.commit()

def insert_praeferenz(praeferenz):
	db.session.add(praeferenz)
	db.session.commit()

def insert_teilnehmer(teilnehmer):
	db.session.add(teilnehmer)
	db.session.commit()

def update_praef(praef, preafs):
	praef.praeferenzen = preafs
	db.session.commit()

def save_teilnehmer(teilnehmer_liste, list_name):
	"""
	saves a teilnehmerList by saving a list of Teilnehmer and
	a teilnehmerList that references the before saved list of teilnehmer

	Parameters
	----------
	teilnehmer_liste : [Teilnehmer]
    	the teilnehmerList to save
	list_name : str
    	name of the teilnehmerlist
    Returns
	-------
	int
    	returns the number of teilnehmer that where saved
	"""
	memberlist = []
	for mem in teilnehmer_liste:
		matr_nr = mem['matr_nr'] if isinstance(mem['matr_nr'], int) else mem['matr_nr'].item()
		local_member = teilnehmer_model.Teilnehmer(
        	matr_nr = matr_nr,
        	last_name = mem['last_name'],
        	first_name = mem['first_name'])
		db.session.add(local_member)
		memberlist.append(local_member)

	list = teilnehmer_list_model.Teilnehmer_List(
		name = list_name,
		teilnehmer = memberlist)
	db.session.add(list)

	try:
		db.session.commit()
	except IntegrityError as e:
		db.session.rollback()
		return 0, "Eine der Matrikelnummern ist bereits vergeben."
    	# unique constraint error, matr_nr already exists

	return len(teilnehmer_liste), None

def save_themen(themen, list_name):
	"""
	saves a themenList by saving a list of themen and
	a themenList that references the before saved list of teilnehmer

	Parameters
	----------
	themen : [Themen]
    	the themenlist to save
	list_name : str
    	name of the themenLsit
    Returns
	-------
	int
    	returns the number of teilnehmer that where saved
	"""
	list_of_themen = []
	for top in themen:
		local_thema = thema_model.Thema(
        	thema_name = top['thema_name'],
        	betreuer = top['betreuer'],
        	zeit = top['zeit'])
		db.session.add(local_thema)
		list_of_themen.append(local_thema)

	list = thema_list_model.Thema_List(
		name = list_name,
		themen = list_of_themen)
	db.session.add(list)
	db.session.commit()

	return len(themen)

def save_verteilung(data):
	"""
	Saves a verteilung.
	if the verteilung will be unprotected, an empty teilnehmerList
	is created to store the teilnehmer that will register by entering their
	name before setting their präferenzen

	Parameters
	----------
	data : object
    	key-value object holding information about the verteilung
	y : str
    	name of the teilnehmerlist
    Returns
	-------
	int
    	returns the id of the saved verteilung
	"""

	thema_list = get_thema_list_by_id(data["thema_list_id"])
	if data["protected"]:
		teiln_list = get_teilnehmer_list_by_id(data["teilnehmer_list_id"])
	else:
		teiln_list = teilnehmer_list_model.Teilnehmer_List(
			name="Teilnehmer der offenen Verteilung mit Themenname '"
			+ str(thema_list.id) + "'",
			is_for_unprotected=True)
		db.session.add(teiln_list)
		db.session.commit()

	local_verteilung = verteilung_model.Verteilung(
		name=data["name"],
		thema_list_id = thema_list.id,
		teilnehmer_list_id = teiln_list.id,
		protected = data["protected"],
		editable = data["editable"],
		max_teilnehmer_per_thema = data["max_per_thema"],
		min_votes = data["min_votes"],
		veto_allowed = data["veto_allowed"])
	db.session.add(local_verteilung)
	try:
		db.session.commit()
	except IntegrityError as e:
		db.session.rollback()
		return 0, "Es existiert bereits eine Verteilung mit diesem Namen."
    	# unique constraint error, matr_nr already exists
	return local_verteilung.id, None