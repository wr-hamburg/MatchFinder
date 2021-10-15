from flask_sqlalchemy import *
from .. import db

class Teilnehmer(db.Model):
	"""
	Database scheme for the teilnehmer table.
	It references the list of teilnehmer it belongs to via the list_id,
	has a convenience backref to its präferenzen.
	"""

	__tablename__ = "teilnehmer"
	id = db.Column(db.Integer, primary_key=True)
	list_id = db.Column(db.Integer, db.ForeignKey("teilnehmer_lists.id"), nullable=False)
	praeferenzen = db.relationship("Praeferenz", cascade="all,delete", backref="teilnehmer", lazy=True)
	first_name = db.Column(db.String(80), nullable=False)
	last_name = db.Column(db.String(80))
	# since all students are collected within a single table, the Matrikel may not be unique, since students may use this tool for different courses
	matr_nr = db.Column(db.Integer, unique=False)