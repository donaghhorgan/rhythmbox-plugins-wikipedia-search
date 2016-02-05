# -*- Mode: python; coding: utf-8; tab-width: 4; indent-tabs-mode: nil; -*-
#
#    WikipediaSearch.py
#
#    Search for selected artist, album, track or genre at the click of a
#    button.
#    Copyright (C) 2012-2016 Donagh Horgan <donagh.horgan@gmail.com>
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

from gi.repository import Gio, GObject, Gtk, Peas, RB
import logging
import urllib
import webbrowser


class WikipediaSearch(GObject.Object, Peas.Activatable):

    """Search for selected artist, album, track or genre at the click of a
    button."""

    object = GObject.property(type=GObject.Object)

    _action = 'wikipedia-search'
    _locations = ['browser-popup',
                  'playlist-popup',
                  'podcast-episode-popup',
                  'queue-popup']
    _base_url = 'https://en.wikipedia.org/w/index.php?search='

    def __init__(self):
        super(WikipediaSearch, self).__init__()
        self._app = Gio.Application.get_default()

    def do_activate(self):
        """Activate the plugin."""
        logging.debug('Activating plugin...')

        actions = {'Artist': self.search_artist,
                   'Album': self.search_album,
                   'Track': self.search_track,
                   'Genre': self.search_genre}

        section = Gio.Menu()
        for label, function in actions.items():
            name = "%s-%s" % (WikipediaSearch._action, label)

            action = Gio.SimpleAction(name=name)
            action.connect('activate', function)
            self._app.add_action(action)

            section_item = Gio.MenuItem()
            section_item.set_label(label)
            section_item.set_detailed_action('app.%s' % name)
            section.append_item(section_item)

        menu = Gio.Menu()
        menu.append_section(None, section)

        menu_item = Gio.MenuItem()
        menu_item.set_label('Search Wikipedia')
        menu_item.set_submenu(menu)
        for location in WikipediaSearch._locations:
            self._app.add_plugin_menu_item(location,
                                           WikipediaSearch._action,
                                           menu_item)

    def do_deactivate(self):
        """Deactivate the plugin."""
        logging.debug('Deactivating plugin...')

        app = Gio.Application.get_default()
        for location in WikipediaSearch._locations:
            app.remove_plugin_menu_item(location, WikipediaSearch._action)

    def _get_top_selection(self):
        page = self.object.props.selected_page
        try:
            selected = page.get_entry_view().get_selected_entries()
            if selected:
                return selected[0]
        except:
            logging.exception("Could not get selected entries")

    @staticmethod
    def search(topic):
        """Searches Wikipedia for the given topic.

        Args:
            topic: The topic to search for.
        """
        url = WikipediaSearch._base_url + topic
        logging.debug('Opening URL: ' + url)
        webbrowser.open(url)

    def _search(self, prop_type, is_genre=False):
        selection = self._get_top_selection()
        prop_value = selection.get_string(prop_type)
        topic = urllib.parse.quote(prop_value)
        if is_genre:
            topic += '+(music)'  # Helps to narrow down genre searches
        WikipediaSearch.search(topic)

    def search_artist(self, *args):
        """Searches for the selected artist."""
        self._search(RB.RhythmDBPropType.ARTIST)

    def search_album(self, *args):
        """Searches for the selected album."""
        self._search(RB.RhythmDBPropType.ALBUM)

    def search_track(self, *args):
        """Searches for the selected track."""
        self._search(RB.RhythmDBPropType.TITLE)

    def search_genre(self, *args):
        """Searches for the selected genre."""
        self._search(RB.RhythmDBPropType.GENRE, is_genre=True)
