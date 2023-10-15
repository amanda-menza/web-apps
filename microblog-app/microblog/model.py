class Message:
    def __init__(self, post_id, user, imgPost, text,timestamp):
        self.post_id = post_id
        self.user = user
        self.imgPost=imgPost
        self.text=text
        self.timestamp = timestamp


class User:
    def __init__(self, user_id, handle, imgProf, name, followers, following):
        self.user_id = user_id
        self.handle = handle
        self.imgProf = imgProf
        self.name = name
        self.followers=followers
        self.following=following
