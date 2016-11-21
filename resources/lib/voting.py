# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import requests
import xbmcvfs

from _json import read_json, write_json, addon_vote_file

vote_file = addon_vote_file
xbmc.log(vote_file)

def vote_up(doku_id, nonce):
    votes = already_voted(doku_id)
    if votes == -1:
        return -1
    url = "http://doku5.com/api.php?vote4=true&postId=%s&type=1&nonce=%s&callback=kody" % (doku_id, nonce)
    requests.get(url)
    votes.append(doku_id)
    write_json(vote_file, votes)


def vote_down(doku_id, nonce):
    votes = already_voted(doku_id)
    if votes == -1:
        return -1
    url = "http://doku5.com/api.php?vote4=true&postId=%s&type=2&nonce=%s&callback=kody" % (doku_id, nonce)
    requests.get(url)
    votes.append(doku_id)
    write_json(vote_file, votes)


def vote_neut(doku_id, nonce):
    return -1


def already_voted(doku_id):
    votes = read_json(vote_file)
    if doku_id in votes:
        return -1
    else:
        return votes
