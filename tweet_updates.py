# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from time import sleep
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError
import ConfigParser
import tempfile
import logging
import pickle
import tweepy
from tweepy.error import TweepError
from epic import EPIC


class TweetEPIC(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.config = ConfigParser.ConfigParser()
        self.config.read('epictweet.conf')
        #auth = tweepy.OAuthHandler(self.config.get('twitter', 'api_key'),
        #                           self.config.get('twitter', 'api_secret'))
        #auth.set_access_token(self.config.get('twitter', 'access_key'),
        #                      self.config.get('twitter', 'access_secret'))
        #self.twitter = tweepy.API(auth)
        self.state = {'image_queue': {},
                      'last_posted_image': datetime(2015, 9, 1),
                      'last_post_time': datetime(2015, 9, 1)}
        self.post_interval = timedelta(seconds=1)

    def poll(self):
        try:
            most_recent = sorted(self.state['image_queue'].keys())[-1]
        except IndexError:
            most_recent = self.state['last_posted_image']

        try:
            images = self.epic.get_recent_images(most_recent, 20)
        except ConnectionError:
            self.log.exception("Unable to fetch images")
            images = []

        added = 0
        for image in images:
            if (image['date'] not in self.state['image_queue'] and
               image['date'] > self.state['last_posted_image']):
                self.state['image_queue'][image['date']] = image
                added += 1
        if added > 0:
            self.log.info("Added %s images to queue", added)

        if self.state['last_post_time'] < (datetime.now() - self.post_interval):
            self.post_tweet()

    def post_tweet(self):
        image_date = sorted(self.state['image_queue'].keys())[0]
        image = self.state['image_queue'][image_date]
        self.log.info("Tweet image: %s", image)

        with tempfile.NamedTemporaryFile() as imagefile:
            self.fetch_image(image, imagefile)

        del self.state['image_queue'][image_date]
        self.state['last_posted_image'] = image_date
        self.state['last_post_time'] = datetime.now()
        self.log.info("One image tweeted, %s left in queue", len(self.state['image_queue']))

    def fetch_image(self, image, destfile):
        with tempfile.NamedTemporaryFile() as downloadfile:
            self.epic.download_image(image['image'], downloadfile)
            self.process_image(downloadfile, destfile)

    def process_image(self, sourcefile, destfile):
        self.log.info("Process %s -> %s", sourcefile, destfile)

    def run(self):
        logging.basicConfig(level=logging.INFO)
        self.epic = EPIC()

        try:
            with open("./state.pickle", "r") as f:
                self.state = pickle.load(f)
        except IOError:
            self.log.exception("Failure loading state file, resetting")

        self.log.info("Running")
        try:
            while True:
                self.poll()
                sleep(60)
        finally:
            self.log.info("Saving state...")
            with open("./state.pickle", "w") as f:
                pickle.dump(self.state, f, pickle.HIGHEST_PROTOCOL)
            self.log.info("Shut down.")

TweetEPIC().run()
