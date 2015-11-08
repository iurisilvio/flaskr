# coding: UTF-8
from __future__ import absolute_import
import random

from funkload.FunkLoadTestCase import FunkLoadTestCase
from funkload.Lipsum import Lipsum
from funkload.utils import extract_token

P_LOGIN = 0.8
P_POST = 0.5
P_DELETE = 0.1

lipsum = Lipsum()


def _P(v):
    return random.random() < v


class Flaskr(FunkLoadTestCase):
    def setUp(self):
        self.server_url = self.conf_get('main', 'url')

    def test_index(self):
        self.get(self.server_url + '/', description='GET app.index')

    def test_login(self):
        login_url = self.server_url + '/login'
        login_data = {'username': 'admin', 'password': 'admin'}
        self.get(login_url, description='GET app.login')
        self.post(login_url, login_data, description='POST app.login')

    def test_add_entry(self, logged_in=False):
        if not logged_in:
            self.test_login()
        add_entry_url = self.server_url + '/add'
        data = {'title': lipsum.getSubject(), 'text': lipsum.getSentence()}
        self.post(add_entry_url, data, description='POST app.add_entry')
        post_id = extract_token(self.getBody(), '<h2 id=', '>')
        return post_id

    def test_delete_entry(self, post_id=None):
        if post_id is None:
            post_id = self.test_add_entry(logged_in=False)
        delete_entry_url = self.server_url + '/delete/%s' % post_id
        self.get(delete_entry_url, description='GET app.delete_entry')
        post_id = extract_token(self.getBody(), '<h2 id=', '>')
        return post_id

    def test_full(self):
        self.test_index()
        if _P(P_LOGIN):
            self.test_login()
            if _P(P_POST):
                post_id = self.test_add_entry(logged_in=True)
                if _P(P_DELETE):
                    self.test_delete_entry(post_id)
