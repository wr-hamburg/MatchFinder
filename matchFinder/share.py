from flask import (Blueprint, redirect, render_template, request, session, url_for)
from . import database_helper
from io import BytesIO
from PIL import Image
import hashlib
import qrcode
import base64

bp = Blueprint('share', __name__, url_prefix='/share')

@bp.before_request
def check_status():
    if session.get('is_authenticated') != True:
        return redirect(url_for('home.index'))

#make database entry, return link to enter site
@bp.route('/', methods=['POST'])
def index():
	teilnehmer_list_id = request.form.get('teilnehmer', None)
	name = request.form.get('name', None)
	thema_list_id = request.form.get('thema', None)
	protected = request.form.get('protected', False)
	editable = request.form.get('editable', False)
	max_per_thema = request.form.get('max_per', 1)
	min_votes = request.form.get('min_votes', 1)
	veto_allowed = request.form.get('veto_allowed', True)
	protected = True if protected == "on" else False
	editable = True if editable == "on" else False
	veto_allowed = True if veto_allowed == "on" else False

	id = database_helper.save_verteilung(
		name, teilnehmer_list_id, thema_list_id,
		protected, editable, max_per_thema,
		min_votes, veto_allowed)

	hashed_verteilung_id = hashlib.sha256(str(id).encode()).hexdigest()

	return redirect(url_for('share.show', verteilung_id=hashed_verteilung_id))

@bp.route('/show/<verteilung_id>')
def show(verteilung_id):
	root_url = request.url_root
	url = root_url + 'preference?id=' + str(verteilung_id)
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_H,
		box_size=4,
		border=4)

	qr.add_data(url)
	qr.make(fit=True)
	img = qr.make_image()

	buffered = BytesIO()
	img.save(buffered, format="PNG")
	img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
	return render_template('share.html', id=verteilung_id, img=img_str)
