import datetime
import dateutil.tz
from . import db, bcrypt
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
import flask_login
from flask_login import current_user

from . import model

bp = Blueprint("main", __name__)



@bp.route("/")

def home():
    followerFeed=None;
    bookmarkFeed=None;
    if flask_login:
        followers = db.aliased(model.User)
        query1 = (
        db.select(model.Recipe)
        .join(model.User)
        .join(followers, model.User.followers)
        .where(followers.id == flask_login.current_user.id)
        .order_by(model.Recipe.timestamp.desc())
        .limit(10)
        )
        followerFeed = db.session.execute(query1).scalars().all()
        query2=(
        db.select(model.Recipe).where(model.Recipe.bookmarks.user.id==flask_login.current_user.id)
        .order_by(model.Recipe.timestamp.desc())
        .limit(10)
        )
        bookmarkFeed = db.session.execute(query2).scalars().all()
    query3= (
    db.select(model.Recipe).order_by(model.Recipe.timestamp.desc())
    .limit(10)
    )
    timeFeed=db.session.execute(query3).scalars().all()
    query4= (
    db.select(model.Recipe).order_by(model.Recipe.ratings.value==True)
    .limit(10)
    )
    ratingFeed=db.session.execute(query4).scalars().all()

## would each of these feeds be part of different controllers or html templates
    return render_template("main/home.html", timeFeed=timeFeed, ratingFeed=ratingFeed, followerFeed=followerFeed, bookmarkFeed=bookmarkFeed)

@bp.route("/recipeView/<int:recipe_id>")
def recipeView(recipe_id):
    recipe = db.session.get(model.Recipe, recipe_id)
    if not recipe:
        abort(404, "Recipe id {} doesn't exist.".format(recipe_id))
    query = db.select(model.Photo).where(model.Photo.recipe == recipe).order_by(model.Photo.timestamp.desc())
    photos = db.session.execute(query).scalars().all()
    authenticated=False;
    if flask_login:
        authenticated=True

    return render_template("main/recipeView.html", recipe=recipe, photos=photos, authenticated=authenticated)

@bp.route("/photo_upload/<int:recipe_id>", methods=["POST"])
@flask_login.login_required
def photo_upload(recipe_id):
    recipe = db.session.get(model.Recipe, recipe_id)
    if not recipe:
        abort(404, "Recipe id {} doesn't exist.".format(recipe_id))
    uploaded_file = request.files['photo']
    if uploaded_file.filename != '':
        content_type = uploaded_file.content_type
        if content_type == "image/png":
            file_extension = "png"
        elif content_type == "image/jpeg":
            file_extension = "jpg"
        else:
            abort(400, f"Unsupported file type {content_type}")
        photo = model.Photo(
        user=flask_login.current_user,
        recipe=recipe,
        file_extension=file_extension
        )
        db.session.add(photo)
        db.session.commit()
    else:
        abort(400,f"Missing file")
    
    return redirect(url_for("main.recipeView", recipe_id=recipe.id))

@bp.route("/rate/<int:recipe_id>", methods=["POST"])
@flask_login.login_required
def rate(recipe_id):
    rateVal = request.form.get("value")#should be boolean up or down
    recipe=db.session.get(model.recipe, recipe_id)
    rating=model.Rating(user=current_user, value=rateVal, recipe=recipe,)
    db.session.add(rating)
    db.session.commit()
    
    return redirect(url_for("main.recipeView", recipe_id=recipe.id))

@bp.route("/bookmark/<int:recipe_id>", methods=["POST"])
@flask_login.login_required
def bookmark(recipe_id):
    recipe=db.session.get(model.recipe, recipe_id)
    bookmark=model.Rating(user=current_user, recipe=recipe,)
    db.session.add(bookmark)
    db.session.commit()
    
    return redirect(url_for("main.recipeView", recipe_id=recipe.id))

@bp.route("/userView/<int:user_id>")
def userView(user_id):
    user = db.session.get(model.User, user_id)
    if not user:
        abort(404, "User id {} doesn't exist.".format(user_id))
    query1 = db.select(model.Photo).where(model.Photo.user == user).order_by(model.Photo.timestamp.desc())
    photos = db.session.execute(query1).scalars().all()
    query2 = db.select(model.Recipe).where(model.Recipe.user == user).order_by(model.Recipe.timestamp.desc())
    recipes = db.session.execute(query2).scalars().all()
    authenticated=False
    selfProfile=False
    followBtn=None;
    bookmarks=None;
    if flask_login:
        authenticated=True
        if current_user.id==user_id:
            query3 = db.select(model.Recipe).where(model.Recipe.bookmarks.user == user).order_by(model.Recipe.timestamp.desc())
            bookmarks = db.session.execute(query3).scalars().all()
            followBtn=None;
        elif flask_login.current_user in user.followers:
            followBtn="unfollow"
        else :
            followBtn="follow"
    
    return render_template("main/userView.html", recipes=recipes, photos=photos, authenticated=authenticated, followBtn=followBtn, bookmarks=bookmarks)

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
    
    return render_template("main/userView.html", user=user)

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
    
    return render_template("main/userView.html", user=user)

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

@bp.route("/recipeForm")
@flask_login.login_required
def recipeForm():
    return render_template("main/recipeForm.html")


@bp.route("/recipeForm", methods=["POST"])
@flask_login.login_required
def recipeForm_post():
    title = request.form.get("title")
    description = request.form.get("description")
    servings = request.form.get("servings")
    cookTime=request.form.get("cooking-time")
    new_recipe = model.Recipe(title=title, user=current_user,description=description, servings=servings, cooktime=cookTime)
    db.session.add(new_recipe)
    db.session.commit()
    recipe_id=new_recipe.id
    
    ingredient_fields = request.form.getlist("ingredient")
    ingredient_amt_fields = request.form.getlist("ingredient-amt")
    ingredient_measure_fields = request.form.getlist("ingredient-measure")

    for i in range(len(ingredient_fields)):
        ingredient_name = ingredient_fields[i]
        ingredient_amt=ingredient_amt_fields[i]
        ingredient_measure=ingredient_measure_fields[i]
        # Create and save the Ingredient entity
        query = db.select(model.Ingredient).where(model.Ingredient.name == ingredient_name)
        old_ingredient = db.session.execute(query).scalar_one_or_none()
        if not old_ingredient:
            new_ingredient = model.Ingredient(name=ingredient_name)
            db.session.add(new_ingredient)
            db.session.commit()
            ingredient_id=new_ingredient.id
        else:
            ingredient_id=old_ingredient.id
        new_qingredient = model.Qingredient(
            ingredient_id=ingredient_id,
            recipe_id=recipe_id, amount=ingredient_amt,measure=ingredient_measure)
        db.session.add(new_qingredient)
        db.session.commit()
    step_fields = request.form.getlist("step")
    for step_text in step_fields:
        # Create and save the Step entity, linking it to the Recipe
        new_step = model.Step(
        text=step_text,
        recipe_id=recipe_id
        )
        db.session.add(new_step)
        db.session.commit()
    return redirect(url_for("main.home"))