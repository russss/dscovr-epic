# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
import dateutil.parser
from dateutil.relativedelta import relativedelta
import requests
import datetime


class EPIC(object):
    """ A programmatic interface to the processed DSCOVR EPIC imagery. """
    ENDPOINT = 'http://epic.gsfc.nasa.gov'
    EPOCH = datetime.datetime(2015, 6, 14)  # Date of first EPIC image

    def __init__(self):
        self.session = requests.Session()

    def get_images_for_date(self, date):
        response = self.session.get(self.ENDPOINT + '/api/natural/date/' + date.isoformat(), timeout=10)
        response.raise_for_status()
        for row in response.json():
            row['date'] = dateutil.parser.parse(row['date'])
            yield row

    def get_recent_images(self, since, count=None, reverse=True):
        date = datetime.date.today()
        images = []
        finished = False
        while (count is None or len(images) < count) and not finished:
            for row in sorted(self.get_images_for_date(date), key=lambda image: image['date'], reverse=True):
                if row['date'] <= since or row['date'] <= self.EPOCH:
                    finished = True
                    break
                images.append(row)
            date -= relativedelta(days=1)
        images = sorted(images, key=lambda image: image['date'], reverse=reverse)
        if count is not None:
            images = images[:count]
        return images

    def get_image_range(self, since, until):
        date = since
        images = []
        while date <= until:
            images.extend(self.get_images_for_date(date))
            date += relativedelta(days=1)
        return sorted(images, key=lambda image: image['date'])

    def download_image(self, image, fp):
        url = "%s/archive/natural/%d/%02d/%02d/png/%s.png" % (self.ENDPOINT,
                                                              image['date'].year,
                                                              image['date'].month,
                                                              image['date'].day,
                                                              image['image'])
        response = self.session.get(url, stream=True, timeout=10)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                fp.write(chunk)
        fp.flush()
