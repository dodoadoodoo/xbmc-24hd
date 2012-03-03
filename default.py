# coding: latin-1                                                                                                      
import urllib2
import urllib

import xbmcgui
import xbmcplugin
import xbmcaddon

from xml.dom.minidom import parse, parseString

PLAYLIST_URL = "http://hd.se/services/play/playlist.xml?id=<id>"
ARCHIVE_URL = "http://hd.se/services/play/settings.xml?type=archive"
BASE_URL = "rtmp://fl1.c01040.cdn.qbrick.com/01040/_definst_/"
FOLDER_NAME = "24hd/"

__settings__ = xbmcaddon.Addon(id='plugin.video.24hd')

def list_programs():
    doc, state = load_xml(ARCHIVE_URL)
    if doc and not state:
        url = sys.argv[0]
        settings = doc.getElementsByTagName("settings")[0]
        setting = settings.getElementsByTagName("setting")[0]
        allcategories = setting.getElementsByTagName("categories")
        for categories in allcategories:
            if categories.parentNode.tagName=="setting":
                for program in categories.getElementsByTagName("category"):
                    categoryid = program.getAttribute("id").encode('utf_8')
                    date = program.getAttribute("latest").encode('utf_8')
                    title = program.childNodes[0].data.encode('utf_8')
                    add_posts(title, url + "category/" + categoryid, isFolder=True)
    else:
        if state == "site":
            xbmc.executebuiltin('Notification("24HD","Site down")')
        else:
            xbmc.executebuiltin('Notification("24HD","Malformed result")')
    xbmcplugin.endOfDirectory(HANDLE)

def list_program(categoryid):
    rand = "864.2308372071875"
    url = PLAYLIST_URL.replace("<id>", categoryid)
    url = url.replace("<rand>", rand)
    if categoryid == "0":
        url = url + "&date=playlist"
    doc, state = load_xml(url)
    if doc and not state:
        playlist = doc.getElementsByTagName("playlist")[0]
        category = playlist.getAttribute("title")
        for item in playlist.getElementsByTagName("item"):
            itemid = item.getAttribute("id")
            title = get_node_value(item, "title").encode('utf_8')
            thumb = get_node_value(item, "image")
            date = get_node_value(item, "pubdate")
            description = get_node_value(item, "introduction")
            if description != None:
                description = description.encode('utf_8')
            description = ""
            subitems = item.getElementsByTagName("subitems")[0]
            for subitem in subitems.getElementsByTagName("subitem"):
                clip = subitem.getElementsByTagName("clip")[0]
                prefix = clip.getAttribute("prefix")
                clipname = clip.childNodes[0].data.encode('utf_8')
                #TODO: create captions file?
                url = BASE_URL + prefix + FOLDER_NAME + clipname
                url = url.encode('utf_8')
                add_posts(title, url, description, thumb)
    else:
        if state == "site":
            xbmc.executebuiltin('Notification("24HD","Site down")')
        else:
            xbmc.executebuiltin('Notification("24HD","Malformed result")')
    xbmcplugin.endOfDirectory(HANDLE)

def add_posts(title, url, description='', thumb='', isPlayable='true', isFolder=False):
    if title == None:
        title = ""
    else:
        title = title.replace("\n", " ")
    if thumb == None:
        listitem=xbmcgui.ListItem(title)
    else:
        listitem=xbmcgui.ListItem(title, iconImage=thumb)        
    if  description == None:
        listitem.setInfo(type='video', infoLabels={'title': title})
    else:
        listitem.setInfo(type='video', infoLabels={'title': title, 'plotoutline': description})
    listitem.setProperty('IsPlayable', isPlayable)
    listitem.setPath(url)
    return xbmcplugin.addDirectoryItem(HANDLE, url=url, listitem=listitem, isFolder=isFolder)


def get_node_value(parent, name, ns=""):
	if ns:
		if parent.getElementsByTagNameNS(ns, name) and \
			    parent.getElementsByTagNameNS(ns, name)[0].childNodes:
			return parent.getElementsByTagNameNS(ns, name)[0].childNodes[0].data
	else:
		if parent.getElementsByTagName(name) and \
			    parent.getElementsByTagName(name)[0].childNodes:
			return parent.getElementsByTagName(name)[0].childNodes[0].data
	return None

def load_xml(url):
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        xbmc.log("plugin.video.24hd: unable to load url: " + url)
        xbmc.log(str(e))
        return None, "site"
    xml = response.read()
    response.close()
    try:
        out = parseString(xml)
    except:
        xbmc.log("plugin.video.24hd: malformed xml from url: " + url)
        return None, "xml"
    return out, None


if (__name__ == "__main__" ):
    MODE=sys.argv[0]
    HANDLE=int(sys.argv[1])
    modes = MODE.split('/')
    print "MODE: " + MODE
    print "modes done: " + str(len(modes))
    
    print "0:" + modes[0]
    print "1:" + modes[1]
    print "2:" + modes[2]
    print "3:" + modes[3]

    activemode = modes[len(modes) - 2]
    category = modes[len(modes) - 1]
    print "ac: " + activemode
    print "cat: " + category
    
    if activemode == "category" :
        list_program(category)
    else :
        list_programs()


