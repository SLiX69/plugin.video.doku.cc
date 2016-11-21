# -*- coding: utf-8 -*-
import json
import io, os
import xbmc, xbmcvfs, xbmcaddon

addonID = "plugin.video.doku5.com"
addon = xbmcaddon.Addon(id=addonID)
addon_data_dir = xbmc.translatePath(addon.getAddonInfo('profile'))
addon_db_dir = os.path.join(addon_data_dir, 'db')
addon_vote_file = os.path.join(addon_db_dir, 'votes.json')

log_msg = 'plugin.video.doku5.com - _json_lib -'


def read_json(db_file):
    xbmc.log(log_msg + '!READ JSON!', 1)
    xbmc.log(log_msg + 'File: '+db_file, 1)
    if xbmcvfs.exists(db_file):
        xbmc.log(log_msg+'File Exists', 1)
        with open(db_file) as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    data = upgrade_db(data)
                    write_json(db_file, data)
                    xbmc.log("DIIICT!!!")
                f.close()
            except ValueError:
                data = []
    else:
        xbmc.log(log_msg + 'File Not Exists', 1)
        data = []
    return data


def write_json(db_file, data):
    xbmc.log(log_msg + '!WRITE JSON!', 1)
    xbmc.log(log_msg + 'File: ' + db_file, 1)
    create_dir(addon_data_dir)
    create_dir(addon_db_dir)
    with io.open(db_file, 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(data, ensure_ascii=False)))
        f.close()


def create_dir(directory):
    if not xbmcvfs.exists(directory):
        xbmcvfs.mkdir(directory)
