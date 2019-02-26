from app import app
from flask import render_template, redirect, url_for
from flask_login import LoginManager
from flask_assets import Environment, Bundle
from instagram_web.blueprints.users.views import users_blueprint
from instagram_web.blueprints.posts.views import posts_blueprint
from .util.assets import bundles

from models.user import User
from models.post import Post

assets = Environment(app)
assets.register(bundles)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(posts_blueprint, url_prefix="/posts")

@login_manager.user_loader
def load_user(user_id):
	return User.get_or_none(User.id == user_id)

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.route("/")
def home():
	# return render_template('home.html')
	return redirect(url_for('users.index'))
