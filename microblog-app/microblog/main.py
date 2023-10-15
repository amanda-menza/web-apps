import datetime
import dateutil.tz

from flask import Blueprint, render_template, request

from . import model

bp = Blueprint("main", __name__)
# Define posts and pictures as global variables
posts = []
pictures = []

@bp.route("/")
def index():
    user = model.User(1, "@user1", "static/profile.jpeg", "mary", "1,300", "1,005")
    posts = [
        model.Message(
            1, user, "static/feed1.jpeg", "Beautiful plaza de Espana in Sevilla!",datetime.datetime.now(dateutil.tz.tzlocal())
        ),
        model.Message(
            2, user, "static/feed2.jpeg","Great view of the sunset above Lisbon!", datetime.datetime.now(dateutil.tz.tzlocal())
        ),
        model.Message(
            3, user, "static/feed3.jpeg", "Exploring caves through Albufiera was incredible!", datetime.datetime.now(dateutil.tz.tzlocal())
        ),
    ]
    return render_template("main/index.html", posts=posts)
@bp.route("/profileIndex")
def profileIndex():
    user = model.User(2, "@amandam1102", "static/profile2.jpeg", "amanda", "15,000", "1,200")
    pictures = [
        model.Message(
            4, user, "static/p1.jpeg", "Sandcastles in Mallorca.", datetime.datetime.now(dateutil.tz.tzlocal())
        ),
        model.Message(
            5, user, "static/p2.jpeg","Florence Duomo is stunning in person.", datetime.datetime.now(dateutil.tz.tzlocal())
        ),
        model.Message(
            6, user, "static/p3.jpeg","Yummy pistachio cappaccino.", datetime.datetime.now(dateutil.tz.tzlocal())
        ),
    ]
    return render_template("main/profileIndex.html", pictures=pictures, user=user)

@bp.route("/messageIndex")
def messageIndex():
    # post_id = request.args.get('post_id')
    # # current = get_post_by_id(post_id)
    # current=posts[1]
    user1=model.User(3, "@user3","static/p6.jpeg", "anna","1,400","900")
    user2=model.User(4, "@user4","static/p7.jpeg", "phoebe","1,600","1,300")
    user3=model.User(5, "@user5","static/p8.jpeg", "morgan","1,100","1,000")
    comments=[
        model.Message(
            7, user1, "", "That's a crazy sandcastle:)", datetime.datetime.now(dateutil.tz.tzlocal())
        ),
        model.Message(
            8, user2, "","I kind of want to jump on that thing!", datetime.datetime.now(dateutil.tz.tzlocal())
        ),
        model.Message(
            9, user3, "","I hope it doesn't rain soon!", datetime.datetime.now(dateutil.tz.tzlocal())
        ),
    ]
    return render_template("main/messageIndex.html", comments=comments)
    # return render_template("main/messageIndex.html", comments=comments, current_post=current )

def get_post_by_id(post_id):

    # post_id = int(post_id)

    # Loop through the posts list and find the post with the matching ID
    for post in posts:
        if post.post_id == post_id:
            return post
        
    for picture in pictures:
        if picture.post_id == post_id:
            return post
    
    # If no post with the given ID is found, return None or raise an exception
    return None  # You can change this behavior as needed