from __future__ import absolute_import, unicode_literals
from Music.celery import app
import requests, os
import spotify_convert.convert as convert

@app.task
def go(library_url, profile):
    out_file = convert.get_library_file(library_url)
    tree = convert.load_tree(library_url)
    tracks = convert.find_track_info(tree)
    convert.match_apple_to_spotify(tracks, profile)
    send_message("Completed moving songs!", "We're all done moving your songs", profile.email, "Tune Transfer", 'tunes@mikevasiliou.com')


@app.task
def send_message(subject, message, recipients, sender_name, sender_email, attachments = []):
    if type(attachments) is str:
        attachments = [attachments]
    files = []
    for file in attachments:
        files.append(("attachment", open(file)))
    if type(recipients) is str:
        recipients = [recipients]

    domain_name = "mikevasiliou.com"
    api_key = os.environ.get('MAILGUN_KEY')
    return requests.post(
            "https://api.mailgun.net/v3/" + domain_name + "/messages",
            auth = ("api", api_key),
            files = files,
            data = {"from":sender_name + " <" + sender_email + ">",
                    "to":recipients,
                    "subject":subject,
                    "html":message,
            })