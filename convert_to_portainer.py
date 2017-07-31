#!/usr/bin/env python

import json
import re
import glob
import os
import markdown
from pprint import pprint
from dockerfile_parse import DockerfileParser


apps = []

dfp = DockerfileParser()

# Find all Dockerfiles

for dockerfile in glob.glob('../docker-images/*/Dockerfile', recursive=True):
    app_name = dockerfile.split("/")[-2]
    print("Found " + app_name)
    readme_file = os.path.dirname(dockerfile) + "/README.md"

    file = open(dockerfile, "r")

    dfp.content = file.read()

    readme = open(readme_file, "r")
    readme_text = readme.read()

    labels = dfp.labels

    app = {}
    app['title'] = app_name
    app['image'] = dfp.baseimage
    app['ports'] = labels.get('org.freenas.port-mappings', '').split(",")
    logo = re.search("(?P<url>https?://[^\s]+(png|gif))", readme_text)
    if logo:
        app['logo'] = logo[0] # first match of an image URL
    app['volumes'] = []
    app['env'] = []

    app['description'] = markdown.markdown(readme_text)

    print( "Image:     " + app['image'] )
    print( "Ports:     " + str(app['ports']))
    #print( "Autostart: " + labels['org.freenas.autostart'] )
    print( "Volumes   ")
    volumes = json.loads(labels.get('org.freenas.volumes', '{}'))
    for vol in volumes:
        print( "   " + vol['name'] + " # " + vol['descr'] )
        app['volumes'].append(vol['name'])

    print( "ENV   ")
    settings = json.loads(labels.get('org.freenas.settings', '{}'))
    for set in settings:
        print( "   " + set['env'] + " # " + set['descr'] )
        app['env'].append({ 'name': set['env'], 'label': set['descr'] })


    #print(json.dumps(app))
    apps.append(app)

output = open('templates.json', 'w')
output.write(json.dumps(apps, sort_keys=False, indent=2))
output.close()

