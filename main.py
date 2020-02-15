import praw
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import pprint
import datetime

from jinja2 import Template, Environment, PackageLoader, select_autoescape
template = Template('''
   {% for result in results %}
    <tr>
        <td> <p>
            <a href={{result.shortlink}}>{{result.title}}</a> </td>
            </p>
        </td><p>Posted by <b>{{result.author}}</b></p></td>
    </tr>
   {% endfor %}''')


def send_email(content, subreddit):
    message = Mail(
        from_email='me@redditfomo.xyz',
        to_emails=os.environ.get('REDDIT_FOMO_SENDGRID_RECIPIENT'),
        subject='Reddit Fomo: best weekly posts for: ' + subreddit,
        html_content=content)
    try:
        sg = SendGridAPIClient(os.environ.get('REDDIT_FOMO_SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

reddit = praw.Reddit(client_id=os.environ.get('REDDIT_FOMO_CLIENT_ID'),
                     client_secret=os.environ.get('REDDIT_FOMO_CLIENT_SECRET'),
                     user_agent=os.environ.get('REDDIT_FOMO_USER_AGENT'),
                     password=os.environ.get('REDDIT_FOMO_PASSWORD'),
                     username=os.environ.get('REDDIT_FOMO_USERNAME'))


subscribeds = list(reddit.user.subreddits(limit=None))
counter = 0
for subreddit_sub in subscribeds:
    #email 1/7 of the top 20  best weekly submissions from the user subreddits
    #so the whole of the subreddits are covered over one week
    if counter % 7 == datetime.datetime.today().weekday():
        print('emailing bestof for subreddit:'+ subreddit_sub.display_name)
        submissions = reddit.subreddit(subreddit_sub.display_name).top(time_filter='week',limit=20)
        send_email(template.render(results=submissions), subreddit_sub.display_name)
      
    counter = counter + 1


