import xbmcaddon
import xbmc
import os

addon = xbmcaddon.Addon(id='plugin.video.doku5.com')
TRANSLATE = addon.getLocalizedString

baseurl = 'http://doku5.com//api.php?'
home = addon.getAddonInfo('path').decode('utf-8')

fanart = xbmc.translatePath(os.path.join(home, 'fanart.jpg'))
imageDir = os.path.join(home, 'thumbnails') + '/'


dis_genre = []
if addon.getSetting('show_menu_new') == 'false': dis_genre.append(TRANSLATE(30010))
if addon.getSetting('show_menu_reup') == 'false': dis_genre.append(TRANSLATE(30011))
if addon.getSetting('show_menu_week') == 'false': dis_genre.append(TRANSLATE(30012))
if addon.getSetting('show_menu_month') == 'false': dis_genre.append(TRANSLATE(30013))
if addon.getSetting('show_menu_year') == 'false': dis_genre.append(TRANSLATE(30014))
###
if addon.getSetting('show_menu_search') == 'false': dis_genre.append(TRANSLATE(30015))
if addon.getSetting('show_menu_cats') == 'false': dis_genre.append(TRANSLATE(30016))
if addon.getSetting('show_menu_abc') == 'false': dis_genre.append(TRANSLATE(30017))


def script_chk(script_name):
    return xbmc.getCondVisibility('System.HasAddon(%s)' % script_name) == 1


def get_main_menu():
    new = {
            "name": TRANSLATE(30010),
            "url": '%sget=new-dokus&page=1' % baseurl,
            "mode": "index",
            "type": "dir",
            "images": {
                "thumb": imageDir + '1.png',
                "fanart": fanart
            }
    }
    reup = {
            "name": TRANSLATE(30011),
            "url": '%sget=reuploads&page=1' % baseurl,
            "mode": "index",
            "type": "dir",
            "images": {
                "thumb": imageDir + '2.png',
                "fanart": fanart
            }
    }
    top_week = {
            "name": TRANSLATE(30012),
            "url": '%stop-dokus=trend&page=1' % baseurl,
            "mode": "index",
            "type": "dir",
            "images": {
                "thumb": imageDir + '3.png',
                "fanart": fanart
            }
    }
    top_month = {
            "name": TRANSLATE(30013),
            "url": '%stop-dokus=last-month&page=1' % baseurl,
            "mode": "index",
            "type": "dir",
            "images": {
                "thumb": imageDir + '4.png',
                "fanart": fanart
            }

    }
    top_year = {
            "name": TRANSLATE(30014),
            "url": '%stop-dokus=last-year&page=1' % baseurl,
            "mode": "index",
            "type": "dir",
            "images": {
                "thumb": imageDir + '5.png',
                "fanart": fanart
            }
    }
    search = {
            "name": TRANSLATE(30015),
            "url": "",
            "mode": "Search",
            "type": "dir",
            "images": {
                "thumb": imageDir + '6.png',
                "fanart": fanart
            }
    }
    cats = {
            "name": TRANSLATE(30016),
            "url": "",
            "mode": "getcat",
            "type": "dir",
            "images": {
                "thumb": imageDir + '7.png',
                "fanart": fanart
            }
    }
    abc = {
            "name": TRANSLATE(30017),
            "url": "",
            "mode": "Alphabet",
            "type": "dir",
            "images": {
                "thumb": imageDir + '8.png',
                "fanart": fanart
            }
    }
    bookmark = {
            "name": TRANSLATE(30018),
            "url": "",
            "mode": "merk",
            "type": "dir",
            "images": {
                "thumb": imageDir + '9.png',
                "fanart": fanart
            }
    }
    items = [new, reup, top_week, top_month, top_year, search, cats, abc]
    if script_chk('plugin.video.bookmark'):
        items.append(bookmark)
    for i in items:
        if i['name'] in dis_genre:
            items.remove(i)
    main_menu = items
    return main_menu







