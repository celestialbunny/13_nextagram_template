from flask import Blueprint

# importing related to Donation & it's forms
from models.post import Post
from models.donation import Donation
from instagram_web.blueprints.donations.forms import CreateDonateForm

# Common import that shares with the posts.py
from flask import render_template, redirect, url_for, flash, request, session, escape, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import app

from instagram_web.util.gateway import generate_client_token, transact, find_transaction

donations_blueprint = Blueprint('donations',
							__name__,
							template_folder='templates/donations')

# from instagram_web.blueprints.posts.views import posts_blueprint

@donations_blueprint.route('/', methods=["GET"])
def view_donation():
	form = CreateDonateForm()
	return render_template('create_donation.html', form=form)

# @donations_blueprint.route('<int:post_id>/donate', methods=["POST"])
# @login_required
# def create_donation(post_id):
# 	form = CreateDonateForm()
# 	if form.validate_on_submit():
# 		try:
# 			donor_id = current_user.id
# 			post = Post.get_or_none(Post.id == post_id)
# 			recipient_id = post.user.id
# 			new_donation = Donation(
# 				donor_id = donor_id,
# 				recipient_id = recipient_id,
# 				post_id = post_id,
# 				amount = form.amount.data
# 			)
# 		except:
# 			flash("Error while processing, kindly retry", 'danger')
# 		else:
# 			new_donation.save()
# 			flash('Donation performed', 'success')
# 			return redirect(url_for('users.index'))
# 	return render_template('create_donation.html', form=form)