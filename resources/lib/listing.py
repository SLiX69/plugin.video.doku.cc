import xbmc
import xbmcgui
import xbmcplugin
import sys

from urllib import quote_plus

pluginhandle = int(sys.argv[1])


def add_entries(entries_list):
    entries = []
    is_folder = False
    for entry in entries_list:
        #xbmc.log(str(entry))
        entry_name = entry['name']
        item = xbmcgui.ListItem(entry_name)
        item.setArt(entry.get('images'))
        item.addContextMenuItems(entry.get('cm', []))
        entry_url = get_entry_url(entry)
        info_labels = entry.get('infolabels')
        if entry['type'] == 'video':
            item.setInfo(type="video", infoLabels=info_labels)
            item.setProperty('IsPlayable', 'true')
            is_folder = False
        if entry['type'] == 'dir':
            item.setInfo(type="video", infoLabels=info_labels)
            is_folder = True
        entries.append([entry_url, item, is_folder])
    xbmcplugin.addDirectoryItems(pluginhandle, entries)


def get_entry_url(entry_dict):
    entry_url = sys.argv[0] + '?'
    for param in entry_dict:
        if not isinstance(entry_dict[param], dict) and not isinstance(entry_dict[param], list) and str(param != 'desc'):
            if isinstance(entry_dict[param], unicode):
                entry_dict[param] = entry_dict[param].encode("UTF-8")
            entry_url += "%s=%s&" % (param, quote_plus(entry_dict[param]))
    if entry_url.endswith("&"):
        entry_url = entry_url[:-1]
    return entry_url


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict
