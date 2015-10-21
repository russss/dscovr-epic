# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
import json
import dateutil.parser
from dateutil.relativedelta import relativedelta
import requests
import datetime


class EPIC(object):
    ENDPOINT = 'http://epic.gsfc.nasa.gov'

    def __init__(self):
        self.session = requests.Session()

    def get_images_for_date(self, date):
        response = self.session.get(self.ENDPOINT + '/api/images.php?date=' + date.isoformat())
        response.raise_for_status()
        for row in response.json():
            row['coords'] = json.loads(row['coords'])
            row['date'] = dateutil.parser.parse(row['date'])
            yield row

    def get_recent_images(self, since, count):
        date = datetime.date.today()
        images = []
        finished = False
        while len(images) < count and not finished:
            for row in self.get_images_for_date(date):
                if row['date'] <= since:
                    finished = True
                    break
                images.append(row)
            date -= relativedelta(days=1)
        return sorted(images, key=lambda image: image['date'], reverse=True)[:count]

    def get_image_range(self, since, until):
        date = since
        images = []
        while date <= until:
            images.extend(self.get_images_for_date(date))
            date += relativedelta(days=1)
        return sorted(images, key=lambda image: image['date'])

    def download_image(self, filename, fp):
        url = "%s/epic-archive/png/%s.png" % (self.ENDPOINT, filename)
        response = self.session.get(url, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                fp.write(chunk)
        fp.flush()
