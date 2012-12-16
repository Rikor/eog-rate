#!/usr/bin/env python
__all__ = ['EogRankPlugin']
import subprocess
from gi.repository import GObject, Eog, Gtk
import logging
import dumbattr
logging.getLogger('dumbattr').setLevel(logging.INFO)

RATING = 'rating'
TAGS = 'tags'

ui_str = """
	<ui>
	  <menubar name="MainMenu">
	    <menu name="ToolsMenu" action="Tools">
	      <separator/>
	      <menuitem name="EyeRank_label" action="EyeRank_label"/>
	      <menuitem name="EyeRank_0" action="EyeRank_0"/>
	      <menuitem name="EyeRank_1" action="EyeRank_1"/>
	      <menuitem name="EyeRank_2" action="EyeRank_2"/>
	      <menuitem name="EyeRank_3" action="EyeRank_3"/>
	      <menuitem name="EyeRank_4" action="EyeRank_4"/>
	      <menuitem name="EyeRank_5" action="EyeRank_5"/>
	      <menuitem name="EyeRank_tag" action="EyeRank_tag"/>
	      <separator/>
	    </menu>
	  </menubar>
	</ui>
	"""

class EogRatePlugin(GObject.Object, Eog.WindowActivatable):

	# Override EogWindowActivatable's window property
	window = GObject.property(type=Eog.Window)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		ui_manager = self.window.get_ui_manager()
		self.action_group = Gtk.ActionGroup('EyeRank')

		action = Gtk.Action('EyeRank_label', _(u'EyeRank'), None, None)
		action.set_sensitive(False)
		self.action_group.add_action(action)

		star = u'\u2605'
		for i in range(0,6):
			action = Gtk.Action('EyeRank_%s' % i, _(u'%s: %s' % (i, star * i)), None, None)
			action.connect('activate', self.make_rate_cb(i), self.window)
			self.action_group.add_action_with_accel(action, "<Alt>%s" % (i,))

		action = Gtk.Action('EyeRank_tag', _(u'Edit tags'), None, None)
		action.connect('activate', self.edit_tag_cb, self.window)
		self.action_group.add_action_with_accel(action, "<Ctrl>t")

		ui_manager.insert_action_group(self.action_group, 0)
		self.ui_id = ui_manager.add_ui_from_string(ui_str)

	def do_deactivate(self):
		ui_manager = self.window.get_ui_manager()
		ui_manager.remove_ui(self.ui_id)
		self.ui_id = 0
		ui_manager.remove_action_group(self.action_group)
		self.action_group = None
		ui_manager.ensure_update()
	
	def make_rate_cb(self, val):
		def cb(action, window):
			img = window.get_image()
			f = img.get_file()
			dumbattr.set(f.get_path(), RATING, str(val))
		return cb

	#TODO: operate on multiple files using window.get_thumb_view()

	def edit_tag_cb(self, action, window):
		img = window.get_image()
		f = img.get_file()
		attrs = dumbattr.load(f.get_path())
		tags = list(map(lambda x: x.strip(), attrs.get(TAGS, '').split(",")))
		dialog = Gtk.Dialog("Tag editor", parent=window, flags=(Gtk.DialogFlags.DESTROY_WITH_PARENT | Gtk.DialogFlags.MODAL))

		entry = Gtk.Entry()
		#TODO: GtkEntryCompletion
		entry.set_text(", ".join(tags))
		label = Gtk.Label("Edit tags:")
		box = dialog.get_content_area()
		box.add(label)
		box.add(entry)

		dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
		dialog.add_button("OK", Gtk.ResponseType.OK)
		dialog.set_default_response(Gtk.ResponseType.OK)
		entry.set_property("activates-default", True)

		dialog.show_all()

		def cb(dialog, response):
			if response == Gtk.ResponseType.OK:
				attrs[TAGS] = entry.get_text()
			else:
				pass # cancelled
			dialog.destroy()
		dialog.connect("response", cb)
		dialog.show()
