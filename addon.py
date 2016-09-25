#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re, urlparse, requests
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
from urllib import quote, unquote_plus, unquote, urlencode, quote_plus, urlretrieve


pluginhandle = int(sys.argv[1])
title = 'Doku5'
addon = xbmcaddon.Addon(id='plugin.video.doku5.com')
home = addon.getAddonInfo('path').decode('utf-8')
icon = xbmc.translatePath(os.path.join(home, 'icon.png'))
fanart = xbmc.translatePath(os.path.join(home, 'fanart.jpg'))
imageDir = os.path.join(home, 'thumbnails') + '/'
view_mode_id = int('503')
TRANSLATE = addon.getLocalizedString

show_doku_src = addon.getSetting('show_doku_source')
show_menu_search = addon.getSetting('show_menu_search')
show_menu_cats = addon.getSetting('show_menu_cats')
show_menu_abc = addon.getSetting('show_menu_abc')

xbmcplugin.setContent(pluginhandle, 'Episodes')
baseurl = 'http://doku5.com//api.php?'
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

dis_genre = []
if addon.getSetting('show_menu_new') == 'false': dis_genre.append(TRANSLATE(30010))
if addon.getSetting('show_menu_reup') == 'false': dis_genre.append(TRANSLATE(30011))
if addon.getSetting('show_menu_week') == 'false': dis_genre.append(TRANSLATE(30012))
if addon.getSetting('show_menu_month') == 'false': dis_genre.append(TRANSLATE(30013))
if addon.getSetting('show_menu_year') == 'false': dis_genre.append(TRANSLATE(30014))

sett_desc_show_date = False
sett_desc_show_vote = False
sett_desc_show_src = False
if addon.getSetting('desc_show_date') == 'true': sett_desc_show_date = True
if addon.getSetting('desc_show_vote') == 'true': sett_desc_show_vote = True
if addon.getSetting('desc_show_src') == 'true': sett_desc_show_src = True


def categories():
    genres = get_genres()
    for genre in genres:
        url = genre['url']
        name = genre['genre']
        icon = genre['thumb']
        if name in dis_genre:
            continue
        addDir(name, url, 'index', icon)
    if show_menu_search == 'true': addDir(TRANSLATE(30015), '', 'Search', imageDir + '6.png')
    if show_menu_cats == 'true': addDir(TRANSLATE(30016), '', 'getcat', imageDir + '7.png')
    if show_menu_abc == 'true': addDir(TRANSLATE(30017), '', 'Alphabet', imageDir + '8.png')
    if script_chk('plugin.video.bookmark') == 1: addDir(TRANSLATE(30018), '', 'merk', imageDir + '9.png')
    xbmcplugin.endOfDirectory(pluginhandle)
    if change_view:
        xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)


def get_genres():
    genres = ({'url': '%sget=new-dokus&page=1' % baseurl, 'genre': TRANSLATE(30010), 'thumb': imageDir + '1.png'},
              {'url': '%sget=reuploads&page=1' % baseurl, 'genre': TRANSLATE(30011),
               'thumb': imageDir + '2.png'},
              {'url': '%stop-dokus=trend&page=1' % baseurl, 'genre': TRANSLATE(30012),
               'thumb': imageDir + '3.png'},
              {'url': '%stop-dokus=last-month&page=1' % baseurl, 'genre': TRANSLATE(30013),
               'thumb': imageDir + '4.png'},
              {'url': '%stop-dokus=last-year&page=1' % baseurl, 'genre': TRANSLATE(30014),
               'thumb': imageDir + '5.png'})
    return genres


def get_cat():
    url = '%sgetCats' % baseurl
    data = get_json(url)
    for item in data:
        name = item['name']
        url = item['url']
        addDir(name, url, 'index', icon)
    xbmcplugin.endOfDirectory(pluginhandle)
    if change_view:
        xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)


def index(url):
    data = get_json(url)
    for item in data['dokus']:
        url = item['youtubeId']
        desc = item['description']
        name = item['title']
        thumb = item['cover']
        #thumb = 'http://img.youtube.com/vi/' + url + '/0.jpg'
        fanart = get_fanart(url)
        duration = item['length']
        date = clean_date(item['date'])
        source = get_item_src(item['dokuSrc'])
        perc = get_item_perc(item['voting']['voteCountInPerc'])
        vote = get_item_vote(item['voting']['voteCountAll'])
        desc = get_desc(date, perc, vote, source, desc)
        addLink(name, url, 'play', thumb, desc, duration, date, fanart)
    try:
        url = (data['query']['nextpage'])
        addDir(TRANSLATE(30030), url, 'index', imageDir + '10.png')
    except:
        pass
    try:
        url = (data['query']['prevpage'])
        addDir(TRANSLATE(30031), url, 'index', imageDir + '11.png')
        if show_mm: addDir(TRANSLATE(30032), '', '', imageDir + '12.png')
    except:
        pass
    if change_view:
        xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)
    xbmcplugin.endOfDirectory(pluginhandle)


def search():
    search_entered = search_dialog()
    url = '%ssearch=%s&page=1' % (baseurl, search_entered)
    index(url)


def search_dialog():
    search_entered = ''
    keyboard = xbmc.Keyboard(search_entered, TRANSLATE(30040))
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_entered = keyboard.getText()
        if search_entered == None:
            return False
    return search_entered


def list_alphabet():
    for i in range(ord('A'), ord('Z') + 1):
        name = chr(i)
        url = '%sletter=%s&page=1' % (baseurl, name)
        addDir(name, url, 'index', icon)
    xbmcplugin.endOfDirectory(pluginhandle)
    if change_view:
        xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)


def clean_date(date):
    date = date.split(' ', 1)[0]
    date = '%s.%s.%s' % (date.split('-')[2], date.split('-')[1], date.split('-')[0])
    return date


def get_item_src(source):
    if sett_desc_show_src:
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


def script_chk(script_name):
    return xbmc.getCondVisibility('System.HasAddon(%s)' % script_name) == 1


def play(url):
    video_url = "plugin://plugin.video.youtube/play/?video_id="+url
    listitem = xbmcgui.ListItem(path=video_url)
    xbmcplugin.setResolvedUrl(pluginhandle, succeeded=True, listitem=listitem)


def addLink(name, url, mode, iconimage, desc, duration, date, fanart):
    u = sys.argv[0] + "?url=" + quote_plus(url) + "&mode=" + str(mode)
    ok = True
    item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    item.setInfo(type="Video", infoLabels={'genre': 'Doku', "title": name, "plot": desc, "duration": duration, "aired": date})
    item.setProperty('IsPlayable', 'true')
    menu = []
    item.addContextMenuItems(items=menu, replaceItems=False)
    item.setProperty('fanart_image', fanart)
    #xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)
    xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=item)


def addDir(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + quote_plus(url) + "&mode=" + str(mode) + "&name=" + quote_plus(name)
    ok = True
    item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    item.setInfo(type="Video", infoLabels={"Title": name})
    item.setProperty('fanart_image', fanart)
    #xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)
    xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=item, isFolder=True)


def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


params = parameters_string_to_dict(sys.argv[2])
mode = params.get('mode')
url = params.get('url')
if type(url) == type(str()):
    url = unquote_plus(url)

if mode == 'index':
    index(url)
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
    categories()

