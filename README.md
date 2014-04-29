BASIC INSTRUCTIONS
==================

  brew install python (http://pypi.python.org/packages/source/l/lxml/lxml-3.3.5.tar.gz)

Requires [wget](http://www.gnu.org/software/wget/) or [cURL ](http://curl.haxx.se/).

cURL typically comes pre-installed.

For Mac use [homebrew](http://brew.sh/) and one of:

    brew install wget
    brew install curl

Requires Python with [lxml](http://lxml.de/), [requests](http://docs.python-requests.org/),
[pystache](http://defunkt.io/pystache/), [PIL](http://effbot.org/imagingbook/),
and [ModestMaps](https://github.com/stamen/modestmaps-py).

Optionally [set up virtualenv](http://www.virtualenv.org/en/latest/#usage):

    virtualenv --no-site-packages venv
    source venv/bin/activate

Install libraries needed for fast XML processing and Python extensions.
For Ubuntu/Linux:

    apt-get install python-dev libxml2-dev libxslt1-dev

Install Python packages:

    pip install -r requirements.txt

## Running

    python changewithin.py

## Automating

Assuming the above installation, edit your [cron table](https://en.wikipedia.org/wiki/Cron) (`crontab -e`) to run the script once a day at 7:00am.

    0 7 * * * ~/path/to/changewithin/bin/python ~/path/to/changewithin/changewithin.py



Might have to do these individually:

```pip install requests```
```pip install pystache```
```pip install lxml```
```pip install modestmaps --allow-unverified modestmaps```