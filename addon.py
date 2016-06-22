#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, xbmcplugin, xbmcgui, requests
import xbmc
import xbmcaddon
import os
import urlparse
from urllib import quote, unquote_plus, unquote, urlencode, quote_plus, urlretrieve


pluginhandle = int(sys.argv[1])
title = 'Doku5'
addon = xbmcaddon.Addon(id='plugin.video.doku5.com')
home = addon.getAddonInfo('path').decode('utf-8')
icon = xbmc.translatePath(os.path.join(home, 'icon.png'))
fanart = xbmc.translatePath(os.path.join(home, 'fanart.jpg'))
imageDir = os.path.join(home, 'thumbnails') + '/'
view_mode_id = int('503')
show_doku_src = addon.getSetting('show_doku_source')
show_menu_search = addon.getSetting('show_menu_search')
show_menu_cats = addon.getSetting('show_menu_cats')
show_menu_abc = addon.getSetting('show_menu_abc')

xbmcplugin.setContent(pluginhandle, 'Episodes')
baseurl = 'http://doku5.com//api.php?'
change_view = False

if addon.getSetting('show_doku_fanart') == 'false': fanart = 'fanart' + 'dis'
if addon.getSetting('show_main_menu_folder') == 'true': show_mm = True
if addon.getSetting('change_view') == 'true':
    change_view = True
    view_mode_id = int(addon.getSetting('change_view_episodes'))

dis_genre = []
if addon.getSetting('show_menu_new') == 'false': dis_genre.append('Die neusten Dokus')
if addon.getSetting('show_menu_reup') == 'false': dis_genre.append('Die neusten reUploads')
if addon.getSetting('show_menu_week') == 'false': dis_genre.append('Aufsteiger der Woche')
if addon.getSetting('show_menu_month') == 'false': dis_genre.append('Top Dokus des Monats')
if addon.getSetting('show_menu_year') == 'false': dis_genre.append('Top Dokus des Jahres')


def categories():
    genres = get_genres()
    for genre in genres:
        url = genre['url']
        name = genre['genre']
        icon = genre['thumb']
        if name in dis_genre:
            continue
        addDir(name, url, 'index', icon)
    if show_menu_search == 'true': addDir('Suche', '', 'Search', imageDir + '6.png')
    if show_menu_cats == 'true': addDir('Kategorien', '', 'getcat', imageDir + '7.png')
    if show_menu_abc == 'true': addDir('A-Z', '', 'Alphabet', imageDir + '8.png')
    if script_chk('plugin.video.bookmark') == 1:
        addDir('Merkliste', '', 'merk', imageDir + '9.png')
    xbmcplugin.endOfDirectory(pluginhandle)
    if change_view:
        xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)


def get_genres():
    genres = ({'url': '%sget=new-dokus&page=1' % baseurl, 'genre': 'Die neusten Dokus', 'thumb': imageDir + '1.png'},
              {'url': '%sget=reuploads&page=1' % baseurl, 'genre': 'Die neusten reUploads',
               'thumb': imageDir + '2.png'},
              {'url': '%stop-dokus=trend&page=1' % baseurl, 'genre': 'Aufsteiger der Woche',
               'thumb': imageDir + '3.png'},
              {'url': '%stop-dokus=last-month&page=1' % baseurl, 'genre': 'Top Dokus des Monats',
               'thumb': imageDir + '4.png'},
              {'url': '%stop-dokus=last-year&page=1' % baseurl, 'genre': 'Top Dokus des Jahres',
               'thumb': imageDir + '5.png'})
    return genres


def getcat():
    url = '%sgetCats' % baseurl
    data = getjson(url)
    for item in data:
        name = item['name']
        url = item['url']
        addDir(name, url, 'index', icon)
    xbmcplugin.endOfDirectory(pluginhandle)
    if change_view:
        xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)


def index(url):
    data = getjson(url)
    for item in data['dokus']:
        url = item['youtubeId']
        desc = item['description']
        name = item['title']
        thumb = item['cover']
        duration = item['length']
        date = cleandate(item['date'])
        source = get_item_src(item['dokuSrc'])
        perc = get_item_perc(item['voting']['voteCountInPerc'])
        vote = get_item_vote(item['voting']['voteCountAll'])
        desc = '%s    %s  bei  %s\n%s%s' % (
        date, perc, vote, source, desc)
        addLink(name, url, 'play', thumb, desc, duration)
    try:
        url = (data['query']['nextpage'])
        addDir('Next', url, 'index', imageDir + '10.png')
    except:
        pass
    try:
        url = (data['query']['prevpage'])
        addDir('Prev', url, 'index', imageDir + '11.png')
        if show_mm: addDir('Hauptmenü', '', '', '')
    except:
        pass
    xbmcplugin.endOfDirectory(pluginhandle)
    if change_view:
        xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)


def play(url):
    try:
        video_url = "plugin://plugin.video.youtube/play/?video_id="+url
        listitem = xbmcgui.ListItem(path=video_url)
        xbmcplugin.setResolvedUrl(pluginhandle, succeeded=True, listitem=listitem)
    except ValueError:
        pass
        # xbmc.executebuiltin("XBMC.Notification(%s, Video not available!, 2000, %s)" % (title, icon))


def Search():
    search_entered = search()
    url = '%ssearch=%s&page=1' % (baseurl, search_entered)
    index(url)


def search():
    search_entered = ''
    keyboard = xbmc.Keyboard(search_entered, 'Suche auf %s' % title)
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_entered = keyboard.getText()
        if search_entered == None:
            return False
    return search_entered


def Alphabet():
    for i in range(ord('A'), ord('Z') + 1):
        name = chr(i)
        url = '%sletter=%s&page=1' % (baseurl, name)
        addDir(name, url, 'index', icon)
    xbmcplugin.endOfDirectory(pluginhandle)
    if change_view:
        xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)


def cleandate(date):
    date = date.split(' ', 1)[0]
    date = '%s.%s.%s' % (date.split('-')[2], date.split('-')[1], date.split('-')[0])
    return date


def get_item_src(source):
    if show_doku_src == 'true':
        if source.upper() != 'PROGRAMM' and len(source) > 2:
            if len(source) > 15:
                source = source[0:14]
            source = 'von: ' + source + '\n'
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
        vote = str(vote) + '    Vote  '
    elif vote < 10:
        vote = str(vote) + '    Votes'
    elif vote != 100:
        vote = str(vote) + '  Votes'
    else:
        vote = str(vote) + 'Votes'
    return vote


def getjson(url):
    r = requests.get(url)
    data = r.json()
    r.connection.close()
    return data


def script_chk(script_name):
    return xbmc.getCondVisibility('System.HasAddon(%s)' % script_name) == 1


def addLink(name, url, mode, iconimage, desc, duration):
    u = sys.argv[0] + "?url=" + quote_plus(url) + "&mode=" + str(mode)
    ok = True
    item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    item.setInfo(type="Video", infoLabels={'Genre': 'Doku', "Title": name, "Plot": desc, "Duration": duration})
    item.setProperty('IsPlayable', 'true')
    menu = []
    item.addContextMenuItems(items=menu, replaceItems=False)
    item.setProperty('fanart_image', fanart)
    xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)
    xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=item)


def addDir(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + quote_plus(url) + "&mode=" + str(mode) + "&name=" + quote_plus(name)
    ok = True
    item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    item.setInfo(type="Video", infoLabels={"Title": name})
    item.setProperty('fanart_image', fanart)
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
    Search()
elif mode == 'Alphabet':
    Alphabet()
elif mode == 'getcat':
    getcat()
elif mode == 'merk':
    xbmc.log('MERK')
    xbmc.executebuiltin(
        "XBMC.RunPlugin(\"plugin://plugin.video.bookmark/?mode=episodes&url=plugin.video.doku5.com\")")
    xbmc.executebuiltin("ActivateWindow(10024,plugin://plugin.video.bookmark/?mode=episodes&url=plugin.video.doku5.com)")
else:
    categories()

