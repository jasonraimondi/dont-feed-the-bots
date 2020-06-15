# [@dontfeedthebots](https://twitter.com/dontfeedthebots)

**This is a work in progress**

Uses the twitter stream api to monitor a list of users.json and run any users they mention in tweets through botometer.iuni.iu.edu to see make sure any users you're interacting with are not bots


#### Text I am copy pastaing from the twitter app application that might be useful in the readme when I work on it:

Based on a list of users, mostly myself and a few friends, we will stream tweets and run mentioned users through botometer. If a user is above the threshold set, @dontfeedthebots will reply and let the user know that the person they are interacting with is a bot. 

```yaml
version: "3.7"

services:
  app:
    image: jasonraimondi/dont-feed-the-bots
    build: .
    env_file: .env

  redis:
    image: redis
    ports:
      - 6379:6379

```