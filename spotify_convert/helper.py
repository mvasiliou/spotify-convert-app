from django.conf import settings

def get_callback():
    if settings.PRODUCTION:
        callback = "https%3A%2F%2Fshrouded-bastion-15188.herokuapp.com%2Fspotify_convert%2Fregister%2F"
    else:
        callback = "http%3A%2F%2F127.0.0.1%3A8000%2Fspotify_convert%2Fregister%2F"
    return callback