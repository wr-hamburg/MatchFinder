from flask_sqlalchemy import *
from .. import db

class Verteilung(db.Model):
	__tablename__ = "verteilungen"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), nullable=False)
	thema_list_id = db.Column(db.Integer, db.ForeignKey("thema_lists.id"), nullable=False)
	teilnehmer_list_id = db.Column(db.Integer, db.ForeignKey("teilnehmer_lists.id"), nullable=False)
	editable = db.Column(db.Boolean, default=False)
	max_teilnehmer_per_thema = db.Column(db.Integer, default=1)
	protected = db.Column(db.Boolean, default=True)
	veto_allowed = db.Column(db.Boolean, default=True)
	min_votes = db.Column(db.Integer, default=1)
	praeferenzen = db.relationship("Praeferenz", cascade="all,delete", backref="verteilung", lazy=True)