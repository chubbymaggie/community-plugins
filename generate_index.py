''' Python script to generate a stub README.md files from a plugin.json file '''
import json
import argparse
import os
import sys
import configparser
from collections import OrderedDict

parser = argparse.ArgumentParser(description = 'Generate README.md index of all plugins')
parser.add_argument("-f", "--force", help = 'will automatically overwrite existing README', action='store_true')

args = parser.parse_args()

os.path.realpath(__file__)


basedir = os.path.join(os.path.dirname(os.path.realpath(__file__)))
pluginsdir = os.path.join(basedir, 'plugins')
pluginreadme = os.path.join(pluginsdir, 'README.md')
pluginjson = os.path.join(basedir, "plugins.json")

if not args.force and os.path.isfile(pluginreadme):
    print("Cowardly refusing to overwrite an existing README. Remove or re-run with -f.")
    sys.exit(0)

if not args.force and os.path.isfile(pluginjson):
    print("Cowardly refusing to overwrite an existing plugins.json. Remove or re-run with -f.")
    sys.exit(0)

config = configparser.ConfigParser()
config.readfp(open(os.path.join(basedir, '.gitmodules')))
submodules = {}

for section in config.items()[1:]:
    sectionname = section[0].split('"')[1]
    submodules[sectionname] = config.get(section[0], 'url')


template = '# Binary Ninja Plugins\n\n'
template += '''| PluginName | Author | License | Type | Description |
|------------|--------|---------|----------|-------------|
'''

plugins = []
for plugin in os.walk(pluginsdir).next()[1]:
    try:
        url = submodules[os.path.join('plugins', plugin)]
        if url.endswith('.git'):
                url = url[:-4]
        authorlink = '/'.join(url.split('/')[:4])
    except:
        url = 'https://github.com/Vector35/community-plugins/tree/master/plugins/{plugin}'.format(plugin=plugin)
        authorlink = 'https://github.com/Vector35/'
    try:
        data = json.load(open(os.path.join(pluginsdir, plugin, "plugin.json")), object_pairs_hook=OrderedDict, encoding="utf-8")['plugin']
    except Exception as exc:
        print exc
        print "Failed to load {}, possible json error.".format(plugin)
        continue
    if (not url.startswith("http") or (plugin == "" )):
        print "Failed to load {}, possible json error.".format(plugin)
        continue
    data['url'] = url
    data['path'] = plugin
    if 'type' not in data:
        data['type'] = ['none']
    plugins.append(data)
    template += u'|[{name}]({url})|[{author}]({authorlink})|[{license}]({plugin}/LICENSE)|{plugintype}|{description}|\n'.format(name = data['name'],
                url=url,
                plugin=plugin,
                author=data['author'],
                authorlink=authorlink,
                license=data['license']['name'],
                plugintype=', '.join(sorted(data['type'])),
                description=data['description'])
template += "\n\n"
print("Writing " + pluginjson)
open(pluginjson, 'w').write(json.dumps(plugins, indent=4, sort_keys=True, ensure_ascii=False, encoding="utf-8").encode("utf-8"))

print("Writing " + pluginreadme)
open(pluginreadme, "w").write(template.encode("utf-8"))
