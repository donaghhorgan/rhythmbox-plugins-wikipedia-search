# -*- Mode: python; coding: utf-8; tab-width: 4; indent-tabs-mode: nil; -*-
#
#    WikipediaSearch.py
#
#    Search for selected artist, album, track or genre at the click of a 
#    button.
#    Copyright (C) 2012-2013 Donagh Horgan <donagh.horgan@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject
from gi.repository import Peas
from gi.repository import RB
from gi.repository import Gtk

import webbrowser
import urllib2

# Rhythmbox compatibility module
import WikipediaSearch_rb3compat as rb3compat
from WikipediaSearch_rb3compat import ActionGroup
from WikipediaSearch_rb3compat import Action
from WikipediaSearch_rb3compat import ApplicationShell

class WikipediaSearchPlugin (GObject.Object, Peas.Activatable):
    object = GObject.property (type = GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)
        
    def log(self, function_name, message, error=False):
        if error:
            message_type = 'ERROR'
        else:
            message_type = 'DEBUG'
        print(function_name + ': ' + message_type + ': ' + message)

    def do_activate(self):
        self.log(self.do_activate.__name__, 'Activating plugin...')
        
        ui_str = '''
        <ui>
          <popup name="BrowserSourceViewPopup">
            <placeholder name="PluginPlaceholder">
              <menu name="BrowserSourcePopupPlaylistAdd" action="SearchWikipedia">
                <menuitem name="SearchWikipediaArtistPopup" action="SearchWikipediaArtist"/>
                <menuitem name="SearchWikipediaAlbumPopup" action="SearchWikipediaAlbum"/>
                <menuitem name="SearchWikipediaTrackPopup" action="SearchWikipediaTrack"/>
                <menuitem name="SearchWikipediaGenrePopup" action="SearchWikipediaGenre"/>
                <separator/>
                <placeholder name="BrowserSourcePopupPlaylistAddPlaceholder"/>
              </menu>
            </placeholder>
          </popup>
          <popup name="PlaylistViewPopup">
            <placeholder name="PluginPlaceholder">
              <menu name="BrowserSourcePopupPlaylistAdd" action="SearchWikipedia">
                <menuitem name="SearchWikipediaArtistPopup" action="SearchWikipediaArtist"/>
                <menuitem name="SearchWikipediaAlbumPopup" action="SearchWikipediaAlbum"/>
                <menuitem name="SearchWikipediaTrackPopup" action="SearchWikipediaTrack"/>
                <menuitem name="SearchWikipediaGenrePopup" action="SearchWikipediaGenre"/>
                <separator/>
                <placeholder name="BrowserSourcePopupPlaylistAddPlaceholder"/>
              </menu>
            </placeholder>
          </popup>
          <popup name="QueuePlaylistViewPopup">
            <placeholder name="PluginPlaceholder">
              <menu name="BrowserSourcePopupPlaylistAdd" action="SearchWikipedia">
                <menuitem name="SearchWikipediaArtistPopup" action="SearchWikipediaArtist"/>
                <menuitem name="SearchWikipediaAlbumPopup" action="SearchWikipediaAlbum"/>
                <menuitem name="SearchWikipediaTrackPopup" action="SearchWikipediaTrack"/>
                <menuitem name="SearchWikipediaGenrePopup" action="SearchWikipediaGenre"/>
                <separator/>
                <placeholder name="BrowserSourcePopupPlaylistAddPlaceholder"/>
              </menu>
            </placeholder>
          </popup>
          <popup name="PodcastViewPopup">
            <placeholder name="PluginPlaceholder">
              <menu name="BrowserSourcePopupPlaylistAdd" action="SearchWikipedia">
                <menuitem name="SearchWikipediaArtistPopup" action="SearchWikipediaArtist"/>
                <menuitem name="SearchWikipediaAlbumPopup" action="SearchWikipediaAlbum"/>
                <menuitem name="SearchWikipediaTrackPopup" action="SearchWikipediaTrack"/>
                <menuitem name="SearchWikipediaGenrePopup" action="SearchWikipediaGenre"/>
                <separator/>
                <placeholder name="BrowserSourcePopupPlaylistAddPlaceholder"/>
              </menu>
            </placeholder>
          </popup>
        </ui>
        '''
        
        self.shell = self.object
        
        self.action_group = ActionGroup(
            self.shell, 
            'WikipediaSearchActionGroup'
            )        
        self.action_group.add_action(
            func=self.null_function, 
            action_name='SearchWikipedia', 
            label='Search Wikipedia', 
            tooltip=_('Search Wikipedia')
            )
        self.action_group.add_action(
            func=self.search_artist, 
            action_name='SearchWikipediaArtist', 
            label='Artist', 
            tooltip=_('Search the selected artist on Wikipedia')
            )
        self.action_group.add_action(
            func=self.search_album, 
            action_name='SearchWikipediaAlbum', 
            label='Album', 
            tooltip=_('Search the selected album on Wikipedia')
            )
        self.action_group.add_action(
            func=self.search_track, 
            action_name='SearchWikipediaTrack', 
            label='Track', 
            tooltip=_('Search the selected track on Wikipedia')
            )
        self.action_group.add_action(
            func=self.search_genre, 
            action_name='SearchWikipediaGenre', 
            label='Genre', 
            tooltip=_('Search the selected genre on Wikipedia')
            )

        self._appshell = ApplicationShell(self.shell)
        self._appshell.insert_action_group(self.action_group)
        self._appshell.add_browser_menuitems(
            ui_str, 
            'WikipediaSearchActionGroup'
            )
    
    def do_deactivate(self):
        self.log(self.do_deactivate.__name__, 'Deactivating plugin...')
        
        self._appshell.cleanup()

    def get_metadata(self):
        page = self.shell.props.selected_page
        if not hasattr(page, 'get_entry_view'):
            return
        selected = page.get_entry_view().get_selected_entries()
        metadata = {}
        if selected != []:
            metadata['artist'] = selected[0].get_string(RB.RhythmDBPropType.ARTIST)
            metadata['album'] = selected[0].get_string(RB.RhythmDBPropType.ALBUM)
            metadata['track'] = selected[0].get_string(RB.RhythmDBPropType.TITLE)
            metadata['genre'] = selected[0].get_string(RB.RhythmDBPropType.GENRE)
        return metadata

    def search_wikipedia(self, query):
        metadata = self.get_metadata()
        base_url = 'https://en.wikipedia.org/w/index.php?search='
        query_url = urllib2.quote(metadata[query])
        if query is 'genre':
            url = base_url + query_url + '+(music)'
        else:
            url = base_url + query_url
        
        self.log(self.search_wikipedia.__name__, 'Opening URL: ' + url)
        
        webbrowser.open(url)

    def search_artist (self, action, shell, *args):
        self.search_wikipedia('artist')

    def search_album (self, action, shell, *args):
        self.search_wikipedia('album')

    def search_track (self, action, shell, *args):
        self.search_wikipedia('track')

    def search_genre (self, action, shell, *args):
        self.search_wikipedia('genre')
    
    def null_function(self):
        pass

