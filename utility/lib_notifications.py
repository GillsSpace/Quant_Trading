import smtplib
import json
import time
import datetime
import schwabdev as sd

def send_token_update_email(to_email):

    with open('tokens.json', 'r') as file:
        tokens = json.load(file)
        issue_date = tokens.get('refresh_token_issued')
        issue_date = datetime.datetime.fromisoformat(issue_date).replace(tzinfo=datetime.timezone.utc)

    now = datetime.datetime.now(datetime.timezone.utc)
    expiration_period = datetime.timedelta(days=7)

    time_left = (issue_date + expiration_period - now).total_seconds()

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("willse06@gmail.com", "htmm ygpm ecfn imdj")

    message = f"Subject: Schwab Token Update\n\nLast Schwab refresh token was issued on {issue_date.strftime('%Y-%m-%d %H:%M:%S %Z')}. It will expire in {time_left/3600:.2f} hours. Reminder: use mainCli.py to refresh the token."

    s.sendmail("willse06@gmail.com", to_email, message)
    s.quit()
