# -*- coding: utf-8 -*-

import os, requests
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
from urllib import unquote_plus

from resources.lib.menus import get_main_menu
from resources.lib.listing import add_entries, parameters_string_to_dict


pluginhandle = int(sys.argv[1])
title = 'Doku5'
addon = xbmcaddon.Addon(id='plugin.video.doku5.com') #
home = addon.getAddonInfo('path').decode('utf-8')
icon = xbmc.translatePath(os.path.join(home, 'icon.png'))
fanart = xbmc.translatePath(os.path.join(home, 'fanart.jpg'))
imageDir = os.path.join(home, 'thumbnails') + '/' #
view_mode_id = int('503')
TRANSLATE = addon.getLocalizedString #

show_doku_src = addon.getSetting('show_doku_source')

xbmcplugin.setContent(pluginhandle, 'Episodes')
baseurl = 'http://doku5.com//api.php?' #
change_view = False
sett_show_logo_fanart = False
sett_show_doku_fanart = False
sett_show_doku_fanart_fallback = False

if addon.getSetting('show_logo_fanart') == 'true': sett_show_logo_fanart = True
if not sett_show_logo_fanart: fanart = 'fanart' + 'dis'
if addon.getSetting('show_doku_fanart') == 'true': sett_show_doku_fanart = True
if addon.getSetting('show_doku_fanart_fallback') == 'true': sett_show_doku_fanart_fallback = True

if addon.getSetting('show_main_menu_folder') == 'true': show_mm = True
if addon.getSetting('change_view') == 'true':
    change_view = True
    view_mode_id = int(addon.getSetting('change_view_episodes'))


sett_desc_show_date = False
sett_desc_show_vote = False
sett_desc_show_src = False
if addon.getSetting('desc_show_date') == 'true': sett_desc_show_date = True
if addon.getSetting('desc_show_vote') == 'true': sett_desc_show_vote = True
if addon.getSetting('desc_show_src') == 'true': sett_desc_show_src = True


def main():
    main_menu = get_main_menu()
    add_entries(main_menu)
    set_view()
    xbmcplugin.endOfDirectory(pluginhandle)


def search():
    search_entered = search_dialog()
    url = '%ssearch=%s&page=1' % (baseurl, search_entered)
    index(url, True)


def search_dialog():
    search_entered = ''
    keyboard = xbmc.Keyboard(search_entered, TRANSLATE(30040))
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_entered = keyboard.getText()
        if search_entered == None:
            return False
    return search_entered


def get_cat():
    items = []
    url = '%sgetCats' % baseurl
    data = get_json(url)
    for item in data:
        name = item['name']
        url = item['url']
        items.append({
            "name": name, "url": url, "mode": "index_a", "type": "dir",
            "infolabels": {"title": name},
            "images": {"thumb": icon, "fanart": fanart}})
        #addDir(name, url, 'index', icon)
    add_entries(items)
    set_view()
    xbmcplugin.endOfDirectory(pluginhandle)


def list_alphabet():
    items = []
    for i in range(ord('A'), ord('Z') + 1):
        name = chr(i)
        url = '%sletter=%s&page=1' % (baseurl, name)
        items.append({
            "name": name, "url": url, "mode": "index", "type": "dir",
            "infolabels": {"title": name},
            "images": {"thumb": icon, "fanart": fanart}})
    add_entries(items)
    set_view()
    xbmcplugin.endOfDirectory(pluginhandle)


def index(url, check=False):    # temp fix pages
    items = []
    data = get_json(url)
    for item in data['dokus']:
        url = item['youtubeId']
        desc = item['description']
        name = item['title']
        thumb = item['cover']
        fanart = get_fanart(url)
        duration = item['length']
        date = clean_date(item['date'])
        source = get_item_src(item['dokuSrc'])
        perc = get_item_perc(item['voting']['voteCountInPerc'])
        vote = get_item_vote(item['voting']['voteCountAll'])
        desc = get_desc(date, perc, vote, source, desc)
        #addLink(name, url, 'play', thumb, desc, duration, date, fanart)
        items.append({
            "name": name, "url": url, "mode": "play", "type": "video", "infolabels": {"title": name, "plot": desc,
            "duration": duration, "aired": date}, "images": {"thumb": thumb, "fanart": fanart}})
    if 'nextpage' in data['query']:
        url = (data['query']['nextpage'])
        data_next_page = {}
        if check:
            data_next_page = get_json(url)
        if data_next_page.get('dokus') != data['dokus']:
            name = TRANSLATE(30030)
            #addDir(TRANSLATE(30030), url, 'index', imageDir + '10.png')
            items.append({
                "name": name, "url": url, "mode": "index", "type": "dir", "infolabels": {"title": name},
                "images": {"thumb": imageDir + '10.png'}})
    if 'prevpage' in data['query']:
        url = (data['query']['prevpage'])
        name = TRANSLATE(30031)
        items.append({
            "name": name, "url": url, "mode": "index", "type": "dir", "infolabels": {"title": name},
            "images": {"thumb": imageDir + '11.png'}})
        #addDir(TRANSLATE(30031), url, 'index', imageDir + '11.png')
        if show_mm:
            name = TRANSLATE(30032)
            items.append({
                "name": name, "url": "", "mode": "", "type": "", "infolabels": {"title": name},
                "images": {"thumb": imageDir + '12.png'}})
    add_entries(items)
    set_view()
    xbmcplugin.endOfDirectory(pluginhandle)


def clean_date(date):
    date = date.split(' ', 1)[0]
    date = '%s.%s.%s' % (date.split('-')[2], date.split('-')[1], date.split('-')[0])
    return date


def get_item_src(source):
    if sett_desc_show_src:
        if source.startswith('WWW1.'):
            source = source[5:]
            pass
        if source.upper() != 'PROGRAMM' and len(source) > 2:
            if len(source) > 15:
                source = source[0:14]
            source = TRANSLATE(30043) + source
        else:
            source = ''
    else:
        source = ''
    return source


def get_item_perc(perc):
    if perc < 10:
        perc = str(perc) + '    %'
    elif perc != 100:
        perc = str(perc) + '  %'
    else:
        perc = str(perc) + '%'
    return perc


def get_item_vote(vote):
    if vote == 1:
        vote = str(vote) + '   Vote  '
    elif vote < 10:
        vote = str(vote) + '   Votes'
    else:
        vote = str(vote) + '  Votes'
    return vote


def get_json(url):
    r = requests.get(url)
    data = r.json()
    r.connection.close()
    return data


def get_desc(date, perc, vote, source, description):
    desc = ''
    if sett_desc_show_date: desc = date + '   '
    if sett_desc_show_vote: desc += vote + '  ' + perc + '   '
    if sett_desc_show_src and source != '': desc += source

    if sett_desc_show_date or sett_desc_show_vote or sett_desc_show_src and source != '':
        desc += '\n'
    desc += description
    return desc


def get_fanart(yt_id):
    fanart = ''
    if sett_show_logo_fanart:
        fanart = xbmc.translatePath(os.path.join(home, 'fanart.jpg'))
    if sett_show_doku_fanart:
        fanart = 'http://img.youtube.com/vi/' + yt_id + '/maxresdefault.jpg'
        if sett_show_doku_fanart_fallback:
            if not exists(fanart):
                fanart = 'http://img.youtube.com/vi/' + yt_id + '/hqdefault.jpg'
    return fanart


def exists(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok


def play(url):
    video_url = "plugin://plugin.video.youtube/play/?video_id="+url
    listitem = xbmcgui.ListItem(path=video_url)
    xbmcplugin.setResolvedUrl(pluginhandle, succeeded=True, listitem=listitem)


def set_view():
    if change_view:
        xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)

params = parameters_string_to_dict(sys.argv[2])
mode = params.get('mode')
url = params.get('url')
if type(url) == type(str()):
    url = unquote_plus(url)

if mode == 'index':
    index(url)
elif mode == 'index_a':
    index(url, True)
elif mode == 'play':
    play(url)
elif mode == 'Search':
    search()
elif mode == 'Alphabet':
    list_alphabet()
elif mode == 'getcat':
    get_cat()
elif mode == 'merk':
    xbmc.executebuiltin("ActivateWindow(10024,plugin://plugin.video.bookmark/?mode=episodes&url=plugin.video.doku5.com)")
else:
    main()

