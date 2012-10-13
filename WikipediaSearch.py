# -*- coding: utf-8 -*-
#
#    WikipediaSearch.py
#
#    Search for selected artist, album, track or genre at the click of a 
#    button.
#    Copyright (C) 2012 Donagh Horgan <donaghhorgan@gmail.com>
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

from gi.repository import GObject, RB, Peas, Gtk
import webbrowser
import urllib2

ui_str = """
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
"""

class Wikipedia (GObject.Object, Peas.Activatable):
	object = GObject.property (type = GObject.Object)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		data = dict()
		shell = self.object
		manager = shell.props.ui_manager
		
		data['action_group'] = Gtk.ActionGroup(name='WikipediaActions')

		action = Gtk.Action(name='SearchWikipedia', label=_("_Search Wikipedia"),
		                    tooltip=_("Search Wikipedia"),
		                    stock_id='gnome-mime-text-x-python')
		data['action_group'].add_action(action)

		action = Gtk.Action(name='SearchWikipediaArtist', label=_("_Artist"),
		                    tooltip=_("Search selected artist on Wikipedia"),
		                    stock_id='gnome-mime-text-x-python')
		action.connect('activate', self.search_artist, shell)
		data['action_group'].add_action(action)

		action = Gtk.Action(name='SearchWikipediaAlbum', label=_("_Album"),
		                    tooltip=_("Search selected album on Wikipedia"),
		                    stock_id='gnome-mime-text-x-python')
		action.connect('activate', self.search_album, shell)
		data['action_group'].add_action(action)

		action = Gtk.Action(name='SearchWikipediaTrack', label=_("_Track"),
		                    tooltip=_("Search selected track on Wikipedia"),
		                    stock_id='gnome-mime-text-x-python')
		action.connect('activate', self.search_track, shell)
		data['action_group'].add_action(action)

		action = Gtk.Action(name='SearchWikipediaGenre', label=_("_Genre"),
		                    tooltip=_("Search selected genre on Wikipedia"),
		                    stock_id='gnome-mime-text-x-python')
		action.connect('activate', self.search_genre, shell)
		data['action_group'].add_action(action)
				
		manager.insert_action_group(data['action_group'], 0)
		data['ui_id'] = manager.add_ui_from_string(ui_str)
		manager.ensure_update()
		
		shell.set_data('WikipediaInfo', data)
	
	def do_deactivate(self):
		shell = self.object
		data = shell.get_data('WikipediaInfo')

		manager = shell.props.ui_manager
		manager.remove_ui(data['ui_id'])
		manager.remove_action_group(data['action_group'])
		manager.ensure_update()

		shell.set_data('WikipediaInfo', None)

	def get_metadata(self, shell):
		page = shell.props.selected_page
		if not hasattr(page, "get_entry_view"):
			return
		selected = page.get_entry_view().get_selected_entries()
		metadata = {}
		if selected != []:
			metadata['artist'] = selected[0].get_string(RB.RhythmDBPropType.ARTIST)
			metadata['album'] = selected[0].get_string(RB.RhythmDBPropType.ALBUM)
			metadata['track'] = selected[0].get_string(RB.RhythmDBPropType.TITLE)
			metadata['genre'] = selected[0].get_string(RB.RhythmDBPropType.GENRE)
		return metadata

	def search_wikipedia(self, shell, query):
		metadata = self.get_metadata(shell)
		base_url = "https://en.wikipedia.org/w/index.php?search=" + urllib2.quote(metadata[query])
		if query is "genre":
			url = base_url + "+(music)"
		else:
			url = base_url
		webbrowser.open(url)

	def search_artist (self, action, shell):
		self.search_wikipedia(shell, "artist")

	def search_album (self, action, shell):
		self.search_wikipedia(shell, "album")

	def search_track (self, action, shell):
		self.search_wikipedia(shell, "track")

	def search_genre (self, action, shell):
		self.search_wikipedia(shell, "genre")

