from flask import Blueprint
from peewee import IntegrityError
from werkzeug.utils import secure_filename

# importing related to User & it's forms
from models.post import Post
from instagram_web.blueprints.posts.forms import CreatePostForm

# Common import that shares with the posts.py
from flask import render_template, redirect, url_for, flash, request, session, escape, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import app

from instagram_web.util.s3_helper import upload_file_to_s3, random_file_name

posts_blueprint = Blueprint('posts',
							__name__,
							template_folder='templates/posts')

@posts_blueprint.route('/create', methods=["GET"])
def show_post():
	form = CreatePostForm()
	return render_template('create_post.html', form=form)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@posts_blueprint.route('/create', methods=["POST"])
@login_required
def create_post():
	form = CreatePostForm()
	# Start here
	if "picture" not in request.files:
		flash("No picture key in request.files", 'danger')
		return redirect(url_for('users.update_user'))
	file = request.files['picture']
	if file.filename == '':
		flash("Please select a file", 'danger')
		return redirect(url_for('users.update_user'))
	if file and allowed_file(file.filename):
		file.filename = secure_filename(file.filename)
		output = upload_file_to_s3(file, app.config['S3_BUCKET'])
		flash('Data saved', 'success')
		# Break here
		if form.validate_on_submit():
			try:
				new_post = Post(
					user=current_user.id,
					picture=output,
					title=form.title.data,
					content=form.content.data
				)
			except:
				flash('Error while creating post', 'danger')
			else:
				new_post.save()
				flash('New post created', 'success')
				return redirect(url_for('users.index'))
		return render_template('create_post.html', form=form)
	else:
		return redirect("/")
	# End here
	user = current_user

@posts_blueprint.route('/post/<int:post_id>')
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post=post)

@posts_blueprint.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	# How to execute the delete command???
	flash('Post has been deleted!', 'info')
	return redirect(url_for('home'))