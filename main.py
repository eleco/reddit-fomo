import praw
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging
import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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


reddit = praw.Reddit(client_id=os.environ.get('REDDIT_FOMO_CLIENT_ID'),
                     client_secret=os.environ.get('REDDIT_FOMO_CLIENT_SECRET'),
                     user_agent=os.environ.get('REDDIT_FOMO_USER_AGENT'),
                     password=os.environ.get('REDDIT_FOMO_PASSWORD'),
                     username=os.environ.get('REDDIT_FOMO_USERNAME'))


def send_email(content, subreddit):
    message = Mail(
        from_email='me@redditfomo.xyz',
        to_emails=os.environ.get('REDDIT_FOMO_SENDGRID_RECIPIENT'),
        subject='Reddit Fomo: best weekly posts for: ' + subreddit + " on: " + str(datetime.datetime.now()),
        html_content=content)
    try:
        
        sg = SendGridAPIClient(os.environ.get('REDDIT_FOMO_SENDGRID_API_KEY'))
        response = sg.send(message)
        logging.debug(response.status_code)
        logging.debug(response.body)
        logging.debug(response.headers)
    except Exception as e:
        logger.exception(e)


def get_subscriptions():
    try:
        logging.info("fetching subscriptions")
        return list(reddit.user.subreddits(limit=None))
    except Exception as e:
        logger.exception(e)


def get_bestof(subreddit):
    try:
        logging.info("fetching reddit best of for subreddit:" + subreddit)
        ret= reddit.subreddit(subreddit).top(time_filter='week',limit=20)
        print("ret :" + str(ret))
        return ret
    except Exception as e:
        logger.exception(e)

subscribeds = get_subscriptions()
counter = 0
for subreddit_sub in get_subscriptions():
    #email 1/7 of the top 20  best weekly submissions from the user subreddits
    #so the whole of the subreddits are covered over one week
    if counter % 7 == datetime.datetime.today().weekday():
        logging.info('emailing bestof for subreddit:'+ subreddit_sub.display_name)
        send_email(template.render(results=get_bestof(subreddit_sub.display_name)), subreddit_sub.display_name)
      
    counter = counter + 1