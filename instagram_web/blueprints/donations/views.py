from flask import Blueprint
import braintree

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

TRANSACTION_SUCCESS_STATUSES = [
	braintree.Transaction.Status.Authorized,
	braintree.Transaction.Status.Authorizing,
	braintree.Transaction.Status.Settled,
	braintree.Transaction.Status.SettlementConfirmed,
	braintree.Transaction.Status.SettlementPending,
	braintree.Transaction.Status.Settling,
	braintree.Transaction.Status.SubmittedForSettlement
]

@donations_blueprint.route('/new', methods=["GET"])
def new_donation():
	client_token = generate_client_token()
	return render_template('new.html', client_token=client_token)

@donations_blueprint.route('/<transaction_id>', methods=['GET'])
def show_checkout(transaction_id):
	transaction = find_transaction(transaction_id)
	result = {}
	if transaction.status in TRANSACTION_SUCCESS_STATUSES:
		result = {
			'header': 'Sweet Success!',
			'icon': 'success',
			'message': 'Your test transaction has been successfully processed. See the Braintree API response and try again.'
		}
	else:
		result = {
			'header': 'Transaction Failed',
			'icon': 'fail',
			'message': 'Your test transaction has a status of ' + transaction.status + '. See the Braintree API response and try again.'
		}

	return render_template('/show.html', transaction=transaction, result=result)

@donations_blueprint.route('/', methods=['POST'])
def create_checkout():
	result = transact({
		'amount': request.form['amount'],
		'payment_method_nonce': request.form['payment_method_nonce'],
		'options': {
			"submit_for_settlement": True
		}
	})

	if result.is_success or result.transaction:
		"""
		Create a donation and save it to database for record
		"""
		# Start of code
		try:
			donor_id = current_user.id
			recipient_id = post.user.id
			new_donation = Donation(
				donor_id = donor_id,
				recipient_id = recipient_id,
				post_id = post_id,
				amount = form.amount.data
			)
		except:
			flash("Error while processing, kindly retry", 'danger')
		else:
			new_donation.save()
			flash('Donation performed', 'success')
		# End of code
		return redirect(url_for('show_checkout',transaction_id=result.transaction.id))
	else:
		for x in result.errors.deep_errors: flash('Error: %s: %s' % (x.code, x.message))
		return redirect(url_for('new_checkout'))

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