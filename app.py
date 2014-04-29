#
# Configure for use. See config.ini for details.
#
config = ConfigParser()
config.read(os.path.join(dir_path, 'config.ini'))

# -------------------------------------------
# Environment variables override config file.
# -------------------------------------------
if 'MAILGUN_DOMAIN' in os.environ:
    config.set('mailgun', 'domain', os.environ['MAILGUN_DOMAIN'])

if 'MAILGUN_API_KEY' in os.environ:
    config.set('mailgun', 'api_key', os.environ['MAILGUN_API_KEY'])

if 'EMAIL_RECIPIENTS' in os.environ:
    emailers = re.sub(r'.*',' ', os.environ['EMAIL_RECIPIENTS'])
    config.set('email', 'recipients', emailers)

# ------------------------------------------
# Get started with the area of interest (AOI).
# ------------------------------------------
aoi_href = config.get('area', 'geojson')
# Convert tags from configuration from string to array
aoi_tags = config.get('area', 'tags')
tags = re.sub(r'\s', '', aoi_tags).split(',')

aoi_file = os.path.join(dir_path, aoi_href)

if os.path.exists(aoi_file):
    # normal file, available locally
    aoi = json.load(open(aoi_file))
else:
    # possible remote file, try to request it
    aoi = requests.get(aoi_href).json()

aoi_poly = aoi['features'][0]['geometry']['coordinates'][0]
aoi_box = get_bbox(aoi_poly)
sys.stderr.write('getting state\n')
osc_file = getosc()
sys.stderr.write('reading file located at'+ aoi_file+'\n')

# For node IDs
nids = set()
changesets = {}
stats = {}
stats['addresses'] = 0
stats['ways'] = {}
stats['nodes'] = {}
# Prepare changesets and stats to hold changes by tag name
for tag in tags:
    stats['nodes'][tag]  = 0
    stats['ways'][tag] = 0
    changesets[tag]= {}

sys.stderr.write('finding points\n')

# ------------------------------------------
# Find nodes that fall within specified area
# ------------------------------------------
context = iter(etree.iterparse(osc_file, events=('start', 'end')))
event, root = context.next()
for event, n in context:
    if event == 'start':
        if n.tag == 'node':
            lon = float(n.get('lon', 0))
            lat = float(n.get('lat', 0))
            if point_in_box(lon, lat, aoi_box) and point_in_poly(lon, lat, aoi_poly):
                cid = n.get('changeset')
                nid = n.get('id', -1)
                nids.add(nid)
                ntags = n.findall(".//tag[@k]")
                addr_tags = getaddresstags(ntags)
                version = int(n.get('version'))

                # Capture address changes
                if version != 1:
                    if hasaddresschange(nid, addr_tags, version, 'node'):
                        addchangeset(n, cid, changesets, '')
                        changesets[cid]['nids'].add(nid)
                        changesets[cid]['addr_chg_nd'].add(nid)
                        stats['addresses'] += 1
                elif len(addr_tags):
                    addchangeset(n, cid, changesets, '')
                    changesets[cid]['nids'].add(nid)
                    changesets[cid]['addr_chg_nd'].add(nid)
                    stats['addresses'] += 1
    # Clear memory
    n.clear()
    root.clear()

# Exit function if nids is empty, this will not send email
#if len(nids) == 0:
#    sys.exit("No nodes from day's changesets fall within"+aoi_file)

# ----------------------------------------------------------------------------------------
# Find ways that contain nodes that were previously determined to fall within specified area
# ----------------------------------------------------------------------------------------

sys.stderr.write('finding changesets\n')
# Keep unique changeset IDs
cids = []
# Keep tags that appear (versus tags that are searched for, set in configuration file)
occurringtags =[]
# Parse through ways
context = iter(etree.iterparse(osc_file, events=('start', 'end')))
event, root = context.next()
for event, w in context:
    if event == 'start':
        # Find ways
        if w.tag == 'way':
            relevant = False
            cid = w.get('changeset')
            wid = w.get('id', -1)
            for x in w.xpath(".//tag"):
                # Only if the way has tags from configuration file
                if x.get('k') in tags:
                    t = x.get('k')
                    for nd in w.iterfind('./nd'):
                        if nd.get('ref', -2) in nids:
                            relevant = True
                            if t not in occurringtags:
                                occurringtags.append(t)
                            if cid not in cids:
                                cids.append(cid)
                            addchangeset(w, cid, changesets[t], t)
                            nid = nd.get('ref', -2)
                            changesets[t][cid]['nids'].add(nid)
                            changesets[t][cid]['wids'].add(wid)
            if relevant:
                wtags = w.findall(".//tag[@k]")
                t = ''
                for tag in wtags:
                    if tag.get('k') in tags:
                        # Add totals in stats object for output
                        stats['ways'][tag.get('k')] += 1
                        t = tag.get('k')
                version = int(w.get('version'))
                addr_tags = getaddresstags(wtags)

                # Capture address changes
                if version != 1:
                    if hasaddresschange(wid, addr_tags, version, 'way'):
                        changesets[t][cid]['addr_chg_way'].add(wid)
                        stats['addresses'] += 1
                elif len(addr_tags):
                    changesets[t][cid]['addr_chg_way'].add(wid)
                    stats['addresses'] += 1
        # Find nodes
        if w.tag == 'node':
            relevant = False
            cid = w.get('changeset')
            nid = w.get('id', -1)
            for x in w.xpath(".//tag"):
                # Only if the way has tags from configuration file
                if x.get('k') in tags:
                    t = x.get('k')
                    # for nd in w.iterfind('./nd'):
                    if nid in nids:
                        relevant = True
                        if t not in occurringtags:
                            occurringtags.append(t)
                        if cid not in cids:
                            cids.append(cid)
                        addchangeset(w, cid, changesets[t], t)
                        changesets[t][cid]['nids'].add(nid)
            if relevant:
                wtags = w.findall(".//tag[@k]")
                t = ''
                for tag in wtags:
                    if tag.get('k') in tags:
                        # Add totals in stats object for output
                        stats['nodes'][tag.get('k')] += 1
                        t = tag.get('k')
                version = int(w.get('version'))
                addr_tags = getaddresstags(wtags)

    w.clear()
    root.clear()

# Create an array for each changeset ID
finalobject = {}
for c in cids:
    finalobject[c] = []

for tag in occurringtags:
    values = map(loadChangeset, changesets[tag].values())
    for each in values:
        for c in cids:
            if c == each['id']:
                finalobject[c].append(each)

writeout = json.dumps(finalobject, sort_keys=True, separators=(',',':'))
f_out = open('testing.json', 'wb')
f_out.writelines(writeout)
f_out.close()

# Length of changeset IDs is total number of changesets
stats['total'] = len(cids)
if len(cids) > 1000:
    changesets = changesets[:999]
    stats['limit_exceed'] = 'Note: For performance reasons only the first 1000 changesets are displayed.'

now = datetime.now()

# ------------------------------------------
# Functions for rendering html for email
# ------------------------------------------
def renderChanges(each, type):
    changestemplate = str(type) +'_changes_tmpl'
    if type == 'html':
        change = pystache.render(html_changes_tmpl, {
            'changesets': each,
        })
    elif type == 'text':
        change = pystache.render(text_changes_tmpl, {
            'changesets': each,
        })
    return change

def rendertemplate(type):
    body = ''
    if type == 'html':
        summary = pystache.render(html_summary_tmpl, {
            'total': stats['total'],
            'addr': stats['addresses'],
            'nodes': stats['nodes'],
            'ways': stats['ways'],
            'date': now.strftime("%B %d, %Y")
        })
    elif type == 'text':
        summary = pystache.render(text_summary_tmpl, {
            'total': stats['total'],
            'addr': stats['addresses'],
            'nodes': stats['nodes'],
            'ways': stats['ways'],
            'date': now.strftime("%B %d, %Y")
        })
    # Add summary
    body+=summary
    for c in cids:
        if type == 'html':
            header = pystache.render(html_headers_tmpl, {
                'changeset': c,
            })
        elif type == 'text':
            header = pystache.render(text_headers_tmpl, {
                'changeset': c,
            })
        # Add header for each changeset ID
        body+=header
        for each in finalobject[c]:
            # Add changes, grouped by tags
            body+=renderChanges(each, type)
    return body

html_version = rendertemplate('html')
text_version = rendertemplate('text')

# ---------------------------------------------------
# Outputs: html file and emails
# ---------------------------------------------------
# Output html version as file
f_out = open('osm_change_report_%s.html' % now.strftime("%m-%d-%y"), 'w')
f_out.write(html_version.encode('utf-8'))
f_out.close()

resp = requests.post(('https://api.mailgun.net/v2/%s/messages' % config.get('mailgun', 'domain')),
    auth = ('api', config.get('mailgun', 'api_key')),
    data = {
            'from': 'Change Within <changewithin@%s>' % config.get('mailgun', 'domain'),
            'to': config.get('email', 'recipients').split(),
            'subject': 'OSM changes %s' % now.strftime("%B %d, %Y"),
            "html": html_version,
    })

# Remove OpenStreetMap changesets file
os.unlink(osc_file)

# Print outputs to terminal
# print html_version
print text_version