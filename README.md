# Reddit-Fomo

Reddit can be addictive and time-consuming. This self-hosted script cuts on the noise and delivers the best of the user-subscribed subreddits.
Each day over 7 days the scripts emails 1/7th of the weekly best submissions per subreddits the user subscribes to.
 

# Installation

1. Create a reddit app, as a script for personal use: https://www.reddit.com/prefs/apps
2. Deploy on Heroku or similar and schedule daily to receive each day the best weekly subscriptions for 1/7th of the user subreddits.


# Configuration

* REDDIT_FOMO_CLIENT_ID: client id from the reddit app
* REDDIT_FOMO_CLIENT_SECRET: client secret from the reddit app
* REDDIT_FOMO_USER_AGENT: reddit app name
* REDDIT_FOMO_PASSWORD: password of the user owning the reddit app
* REDDIT_FOMO_USERNAME: username of the user owning the reddit app


* REDDIT_FOMO_SENDGRID_RECIPIENT: who to sends the daily digests to
* REDDIT_FOMO_SENDGRID_API_KEY: sendgrid api key



