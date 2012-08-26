#!/usr/bin/python 
# -*- coding: utf-8 -*-
# ========================================================================================= 
# Author: Andre Boechat <boechat107@gmail.com>
# File: googleDocs.py
# Date: April 25, 2011
# Description: Search and open documents from a Google account.
# 
# Reference: 
# http://code.google.com/apis/documents/docs/3.0/developers_guide_python.html 
# Gmail and Picasa plugins's code, both made by Karol Będkowski <karol.bedkowski@gmail.com>
#
# TODO: Opcao para mostrar apenas documentos do qual eh dono ou um deretorio especifico
# TODO: Definir funcao de monitoramento de mudancas
# ========================================================================================= 

__kupfer_name__ = _("Google Docs")
__kupfer_sources__ = ("GoogleDocsSource", )
#__kupfer_actions__ = ("Open", )
__description__ = _("Search and open documents from a Google account.")
__version__ = "0.3"
__author__ = "Andre Ambrosio Boechat\n www.das.ufsc.br/~boechat"

import gdata.docs.data 
import gdata.docs.client 
from kupfer.objects import Source, UrlLeaf
from kupfer import plugin_support, pretty 
from kupfer.obj.special import PleaseConfigureLeaf
from kupfer import kupferstring

# ========================================================================================= 
# Plugin settings: username and password
plugin_support.check_keyring_support()
__kupfer_settings__ = plugin_support.PluginSettings(
	{
		'key': 'userpass',
		'label': '',
		'type': plugin_support.UserNamePassword,
		'value': "",
	})

def is_plugin_configured():
	upass = __kupfer_settings__['userpass']
	return bool(upass and upass.username and upass.password)

# ========================================================================================= 
# Functions related with Google services 
def get_googleClient():
    if not is_plugin_configured():
        return None
    try:
        upass = __kupfer_settings__['userpass']
        client = gdata.docs.client.DocsClient(source='kupfer-googleDocs')
        client.ssl = True  # Force all API requests through HTTPS
        client.http_client.debug = False  # Set to True for debugging HTTP requests 
        client.ClientLogin(upass.username, upass.password, client.source)
    #except (gdata.service.BadAuthentication, gdata.service.CaptchaRequired), err:
    except:
        pretty.print_error(__name__, 'google_login', 'authentication error')
        client = None
    return client

def get_googleDocsList():
    gclient = get_googleClient()
    if (gclient == None):
        return [PleaseConfigureLeaf(__name__, __kupfer_name__)]
    docList = []
    feed = gclient.GetDocList()
    for entry in feed.entry:
        doc = GoogleDocument(entry.GetAlternateLink().href , entry.title.text.encode('UTF-8'),
                entry.GetDocumentType(), entry.resource_id.text,
                kupferstring.tounicode(__kupfer_settings__['userpass'].username))
        docList.append(doc)
    return docList

# ========================================================================================= 
# Plugin classes

class GoogleDocsSource (Source):

    source_user_reloadable = True

    def __init__(self, name=None):
        name = name or _("Google Documents")
        super(GoogleDocsSource, self).__init__(name)

    #def initialize(self):
	#	__kupfer_settings__.connect("plugin-setting-changed", self._changed)

    #def _changed(self, settings, key, value):
    #    if key == "userpass":

    #    pass
    #__kupfer_settings__.connect("plugin-setting-changed", self._changed)
    #viminfofile = os.path.expanduser(self.vim_viminfo_file)
    #gfile = gio.File(viminfofile)
    #self.monitor = gfile.monitor_file(gio.FILE_MONITOR_NONE, None)
    #if self.monitor:
    #	self.monitor.connect("changed", self._changed)
    
    #def finalize(self):
    #    if self.monitor:
    #        self.monitor.cancel()
    #        self.monitor = None
    
    #def _changed(self, monitor, file1, file2, evt_type):
    #	"""Change callback; something changed"""
    
    
    def get_items(self):
        self.docs = get_googleDocsList()		
        return self.docs
    
    def get_icon_name(self):
        return "x-office-spreadsheet"
    
    def provides(self):
        yield GoogleDocument
        # Possible result of get_googleDocsList()
        yield PleaseConfigureLeaf


class GoogleDocument(UrlLeaf):
    def __init__(self, url, name, type, doc_id, user):
        super(GoogleDocument, self).__init__(url,name)
        self.doctype = type
        self.id = doc_id
        self.description = _("Google Docs -- account: %s") % (user)

    def get_description(self):
        return self.description 

    def get_icon_name(self):
        if self.doctype == "document":
            return "x-office-document"
        elif self.doctype == "spreadsheet":
            return "x-office-spreadsheet"
        elif self.doctype == "presentation":
            return "x-office-presentation"
        else:
            return "text-x-generic"

