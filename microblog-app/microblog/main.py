import datetime
import dateutil.tz
from . import db
from flask import Blueprint, abort, redirect, render_template, request, url_for
import flask_login
from flask_login import current_user

from . import model

bp = Blueprint("main", __name__)
# Define posts and pictures as global variables
posts = []
pictures = []

@bp.route("/")
@flask_login.login_required
def index():
    followers = db.aliased(model.User)
    query = (
    db.select(model.Message)
    .join(model.User)
    .join(followers, model.User.followers)
    .where(followers.id == flask_login.current_user.id)
    .where(model.Message.response_to == None)
    .order_by(model.Message.timestamp.desc())
    .limit(10)
)
    posts = db.session.execute(query).scalars().all()
    return render_template("main/index.html", posts=posts)
@bp.route("/profileIndex/<int:user_id>")
@flask_login.login_required
def profileIndex(user_id):
    user = db.session.get(model.User, user_id)
    query = db.select(model.Message).where(model.Message.user == user).where(model.Message.response_to==None).order_by(model.Message.timestamp.desc())
    posts = db.session.execute(query).scalars().all()
    if current_user.id==user_id:
        followBtn=None;
    elif flask_login.current_user in user.followers:
        followBtn="unfollow"
    else :
        followBtn="follow"
    return render_template("main/profileIndex.html", posts=posts, user=user, followBtn=followBtn)

@bp.route("/messageIndex/<int:message_id>")
@flask_login.login_required
def messageIndex(message_id):
    message = db.session.get(model.Message, message_id)
    if not message:
        abort(404, "Post id {} doesn't exist.".format(message_id))
    if not message.response_to==None:
        abort(403, "the message to display is a response message.".format(message_id))
    query = db.select(model.Message).where(model.Message.response_to == message).order_by(model.Message.timestamp.desc())
    comments = db.session.execute(query).scalars().all()
    return render_template("main/messageindex.html", post=message, comments=comments)

@bp.route("/new_post", methods=["POST"])
@flask_login.login_required
def new_post():
    newPost = request.form.get("text")
    message=model.Message(
             user=current_user, text=newPost, timestamp=datetime.datetime.now(dateutil.tz.tzlocal())
        )
    db.session.add(message)
    db.session.commit()
    
    return redirect(url_for("main.messageIndex", message_id=message.id))

@bp.route("/new_comment/<int:message_id>", methods=["POST"])
@flask_login.login_required
def new_comment(message_id):
    newComment = request.form.get("text")
    message=db.session.get(model.Message, message_id)
    comment=model.Message(
             user=current_user, text=newComment, response_to=message,timestamp=datetime.datetime.now(dateutil.tz.tzlocal())
        )
    db.session.add(comment)
    db.session.commit()
    
    return redirect(url_for("main.messageIndex", message_id=message.id))

@bp.route("/follow/<int:user_id>", methods=["POST"])
@flask_login.login_required
def follow(user_id):
    user = db.session.get(model.User, user_id)
    if not user:
        abort(404, "User id {} doesn't exist.".format(user_id))
    if user==current_user:
        abort(403, "User id {} is the current user".format(user_id))
    if flask_login.current_user in user.followers:
        abort(403, "The current user is already following User id {}".format(user_id))
    user.followers.append(flask_login.current_user)
    db.session.commit()
    
    return render_template("main/profileIndex.html", posts=posts, user=user)

@bp.route("/unfollow/<int:user_id>", methods=["POST"])
@flask_login.login_required
def unfollow(user_id):
    user = db.session.get(model.User, user_id)
    if not user:
        abort(404, "User id {} doesn't exist.".format(user_id))
    if user==current_user:
        abort(403, "User id {} is the current user".format(user_id))
    if not flask_login.current_user in user.followers:
        abort(403, "The current user is not following User id {}".format(user_id))
    user.followers.remove(flask_login.current_user)
    db.session.commit()
    
    return render_template("main/profileIndex.html", posts=posts, user=user)

@bp.route("/followingView/<int:user_id>")
@flask_login.login_required
def followingView(user_id):
    user=db.session.get(model.User, user_id)
    query = db.select(model.User).where(model.User.followers.contains(user))
    follows = db.session.execute(query).scalars().all()

    return render_template("main/follow.html", follows=follows, user=user)

@bp.route("/followersView/<int:user_id>")
@flask_login.login_required
def followersView(user_id):
    user=db.session.get(model.User, user_id)
    query = db.select(model.User).where(model.User.following.contains(user))
    follows = db.session.execute(query).scalars().all()

    return render_template("main/follow.html", follows=follows, user=user)