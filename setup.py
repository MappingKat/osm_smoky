import time, re, json, requests, os, sys
import pystache

from distutils.core import setup
from flask import Flask, request, render_template
from ConfigParser import ConfigParser
from lxml import etree
from datetime import datetime
from lib import ( get_bbox, getstate, getosc, point_in_box, point_in_poly,
    getaddresstags, hasaddresschange, loadChangeset, addchangeset, html_summary_tmpl, html_headers_tmpl, html_changes_tmpl, text_summary_tmpl,text_headers_tmpl, text_changes_tmpl
    )

setup(name='OSM Smoky',
      version='1.0',
      description='Change edits in OSM',
      author='Katrina Engelsted',
      author_email='katrina@engelsted.co',
      url='http://www.great-smoky-mtns.herokuapp.com/'
     )

dir_path = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config.update(dict(
  EMAIL_RECIPIENTS='npmap@nps.gov thomas_colson@nps.gov katrina@engelsted.co',
  MAILGUN_DOMAIN='key-93qnq9-x-zo8bq3i2tyu4v9363dw41u6',
  MAILGUN_API_KEY='sandboxd37dc97a8696408f9f93ca3b5b0ee4f5.mailgun.org'
  ))
app.config.from_envvar('APP_SETTINGS', silent=True)


# loads configs and grabs configs from environment variable

# if __name__ == '__main__':
#   app.run()


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/report/osm_change_report<path:report_id>')
def show():
  return 'Report %d' % report_id

if __name__ == '__main__':
  app.run()