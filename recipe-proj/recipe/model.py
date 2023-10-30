#ideas for extra functionality:
#have followers for users, show followers in profile
#can switch main view from main feed(maybe latest), to highest rated, to bookmarked, to followers only
# show bookmarked recipes from profile

from . import db
import flask_login

class FollowingAssociation(db.Model):
    follower_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False
    )
    followed_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False
    )
class User(flask_login.UsaerMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    recipes = db.relationship('Recipe', back_populates='user')
    following = db.relationship(
        "User",
        secondary=FollowingAssociation.__table__,
        primaryjoin=FollowingAssociation.follower_id == id,
        secondaryjoin=FollowingAssociation.followed_id == id,
        back_populates="followers",
    )
    followers = db.relationship(
        "User",
        secondary=FollowingAssociation.__table__,
        primaryjoin=FollowingAssociation.followed_id == id,
        secondaryjoin=FollowingAssociation.follower_id == id,
        back_populates="following",
    )
    photos=db.relationship('Photo', back_populates='user')
    bookmarks=db.relationship('Bookmark', back_populates='user')

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='recipes')
    title=db.Column(db.String(128),nullable=False)
    description = db.Column(db.String(512), nullable=False)
    timestamp = db.Column(db.DateTime(), nullable=False)
    portion=db.Column(db.Integer, nullable=False)
    qingredients=db.relationship('Qingredient', back_populates='recipe')
    cooktime=db.Column(db.Integer, nullable=False)
    steps=db.relationship('Step', back_populates='recipe')
    responses = db.relationship('Photo', back_populates='recipe')
    bookmarks=db.relationship('Bookmark', back_populates='recipe')
    ratings=db.relationship('Rating', back_populates='recipe')
    
class Ingredient(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(64), nullable=False)
    qingredients=db.relationship("Qingredient", back_populates="ingredient")    

class Qingredient(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    ingredient=db.relationship("Ingredient", back_populates="qingredients")
    recipe_id=db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe=db.relationship('Recipe', back_populates='qingredients')

class Step(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    recipe_id=db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe=db.relationship('Recipe', back_populates='steps')
    text=db.Column(db.String(512), nullable=False)

class Rating(db.model):
    id=db.Column(db.Integer, primary_key=True)
    recipe_id=db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe=db.relationship('Recipe', back_populates='ratings')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    value=db.Column(db.Boolean, nullable=False)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipe', back_populates='responses')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='photos')
    file_extension = db.Column(db.String(8), nullable=False)

class Bookmark(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='bookmarks')
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe = db.relationship('Recipe', back_populates='bookmarks')

