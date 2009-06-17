# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C) Domino Designs Limited
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, maximum  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

import Blender
from os import name as OSNAME
import Tkinter
from binascii import hexlify

def hex_color(theme_color):
	return "#" + hexlify("".join([chr(i) for i in theme_color[:-1]]))

def float_alpha(theme_color):
	return float(theme_color[3]) / 255.0

class Theme:
	def __init__(self):
		ui = Blender.Window.Theme.Get()[0].get('ui')
		self.action = {'color':hex_color(ui.action),
				'alpha':float_alpha(ui.action)}
		self.draw_type = ui.drawType
		self.icon_theme = ui.iconTheme
		self.menu_back = {'color':hex_color(ui.menu_back),
				'alpha':float_alpha(ui.menu_back)}
		self.menu_hilite = {'color':hex_color(ui.menu_hilite),
				'alpha':float_alpha(ui.menu_hilite)}
		self.menu_item = {'color':hex_color(ui.menu_item),
				'alpha':float_alpha(ui.menu_item)}
		self.menu_text = {'color':hex_color(ui.menu_text),
				'alpha':float_alpha(ui.menu_text)}
		self.menu_text_hi = {'color':hex_color(ui.menu_text_hi),
				'alpha':float_alpha(ui.menu_text_hi)}
		self.neutral = {'color':hex_color(ui.neutral),
				'alpha':float_alpha(ui.neutral)}
		self.num = {'color':hex_color(ui.num),
				'alpha':float_alpha(ui.num)}
		self.outline = {'color':hex_color(ui.outline),
				'alpha':float_alpha(ui.outline)}
		self.popup = {'color':hex_color(ui.popup),
				'alpha':float_alpha(ui.popup)}
		self.setting = {'color':hex_color(ui.setting),
				'alpha':float_alpha(ui.setting)}
		self.setting1 = {'color':hex_color(ui.setting1),
				'alpha':float_alpha(ui.setting1)}
		self.setting2 = {'color':hex_color(ui.setting2),
				'alpha':float_alpha(ui.setting2)}
		self.text = {'color':hex_color(ui.text),
				'alpha':float_alpha(ui.text)}
		self.text_hi = {'color':hex_color(ui.text_hi),
				'alpha':float_alpha(ui.text_hi)}
		self.textfield = {'color':hex_color(ui.textfield),
				'alpha':float_alpha(ui.textfield)}
		self.textfield_hi = {'color':hex_color(ui.textfield_hi),
				'alpha':float_alpha(ui.textfield_hi)}

class Root(Tkinter.Tk):
	def __init__(self, **kw):
		Tkinter.Tk.__init__(self, **kw)
		self.config(bg=theme.menu_back['color'])
		# OS specific features
		if OSNAME in ['nt','mac']:
			self.attributes("-alpha". theme.menu_back['alpha'])
		# event handling
		self.focusmodel("passive")
		self.bind('<FocusOut>', self.focus_out_handler)
		self.bind('<FocusIn>', self.focus_in_handler)
		self.bind('<Configure>', self.configure_handler)
		self.bind('<Escape>', self.destroy_handler)
		self.protocol("WM_DELETE_WINDOW", self.destroy)
		px, py = self.winfo_pointerxy()
		self.geometry("+%d+%d"%(px - 100, py - 100))

	def focus_out_handler(self, event):
		self.grab_release()

	def focus_in_handler(self, event):
		self.grab_set()

	def configure_handler(self, event):
		Blender.Window.RedrawAll()
		self.grab_set()

	def destroy_handler(self, event):
		self.destroy()

class ModalRoot(Tkinter.Tk):
	def __init__(self):
		Tkinter.Tk.__init__(self)
		self.overrideredirect(True)
		self.config(takefocus=True,
				bg=theme.menu_back['color'])
		# OS specific features
		if OSNAME == "nt":
			self.attributes("-topmost", 1)
		if OSNAME in ['nt','mac']:
			self.attributes("-alpha", theme.menu_back['alpha'])
		# event handling
		px, py = self.winfo_pointerxy()
		self.geometry("+%d+%d"%(px - 100, py - 100))
		self.update_idletasks()
		self.bind('<Escape>', self.destroy_handler)
		#todo:figure out why this keeps triggering
		#self.bind('<Leave>', self.destroy_handler)
		self.bind('<Enter>',self.enter_handler)
		self.protocol("WM_DELETE_WINDOW", self.destroy)
		self.focus_force()

	def destroy_handler(self, event):
		if event.widget == self:
			self.destroy()

	def enter_handler(self, event):
		self.grab_set_global()
		self.update_idletasks()

class BitmapImage(Tkinter.BitmapImage):
	def __init__(self, parent, **kw):
		Tkinter.BitmapImage(self, parent)
		self.config(**kw)

class Button(Tkinter.Button):
	def __init__(self, parent, **kw):
		Tkinter.Button.__init__(self, parent)
		self.config(bg=theme.action['color'],
				activebackground=theme.action['color'],
				fg=theme.menu_text['color'],
				activeforeground=theme.text_hi['color'],
				highlightbackground=theme.menu_back['color'],
				highlightcolor=theme.outline['color'],
				disabledforeground=theme.menu_back['color'])
		self.config( **kw )

class Canvas(Tkinter.Canvas):
	def __init__(self, parent, **kw):
		Tkinter.Canvas(self, parent)
		self.config(**kw)

class Checkbutton(Tkinter.Checkbutton):
	def __init__(self, parent, **kw):
		Tkinter.Checkbutton(self, parent)
		self.config(**kw)

class Entry(Tkinter.Entry):
	def __init__(self, parent, **kw):
		Tkinter.Entry(self, parent)
		self.config(**kw)

class Frame(Tkinter.Frame):
	def __init__(self, parent, **kw):
		Tkinter.Frame.__init__(self, parent)
		self.config(bg=theme.menu_back['color'],
				highlightcolor=theme.outline['color'],
				highlightbackground=theme.menu_back['color'])
		self.config( **kw )
		# OS specific features
		if OSNAME in ['nt','mac']:
			self.attributes("-alpha", theme.menu_back['alpha'])

class Label(Tkinter.Label):
	def __init__(self, parent, **kw):
		Tkinter.Label(self, parent)
		self.config(**kw)

class LabelFrame(Tkinter.LabelFrame):
	def __init__(self, parent, **kw):
		Tkinter.LabelFrame.__init__(self, parent)
		self.config(bg=theme.menu_back['color'],
				fg=theme.menu_text['color'],
				highlightcolor=theme.outline['color'],
				highlightbackground=theme.menu_back['color'])
		self.config( **kw )
		# OS specific features
		if OSNAME in ['nt','mac']:
			self.attributes("-alpha", theme.menu_back['alpha'])

class Listbox(Tkinter.Listbox):
	def __init__(self, parent, **kw):
		Tkinter.Listbox(self, parent)
		self.config(**kw)

class Menu(Tkinter.Menu):
	def __init__(self, parent, **kw):
		Tkinter.Menu(self, parent)
		self.config(**kw)

class Menubutton(Tkinter.Menubutton):
	def __init__(self, parent, **kw):
		Tkinter.Menubutton(self, parent)
		self.config(**kw)

class Message(Tkinter.Message):
	def __init__(self, parent, **kw):
		Tkinter.Message(self, parent)
		self.config(**kw)

class OptionMenu(Tkinter.OptionMenu):
	def __init__(self, parent, **kw):
		Tkinter.OptionMenu(self, parent)
		self.config(**kw)

class PanedWindow(Tkinter.PanedWindow):
	def __init__(self, parent, **kw):
		Tkinter.PanedWindow(self, parent)
		self.config(**kw)

class PhotoImage(Tkinter.PhotoImage):
	def __init__(self, parent, **kw):
		Tkinter.PhotoImage(self, parent)
		self.config(**kw)

class RadioButton(Tkinter.RadioButton):
	def __init__(self, parent, **kw):
		Tkinter.RadioButton(self, parent)
		self.config(**kw)

class Scale(Tkinter.Scale):
	def __init__(self, parent, **kw):
		Tkinter.Scale(self, parent)
		self.config(**kw)

class Scrollbar(Tkinter.Scrollbar):
	def __init__(self, parent, **kw):
		Tkinter.Scrollbar(self, parent)
		self.config(**kw)

class Spinbox(Tkinter.Spinbox):
	def __init__(self, parent, **kw):
		Tkinter.Spinbox(self, parent)
		self.config(**kw)

class Text(Tkinter.Text):
	def __init__(self, parent, **kw):
		Tkinter.Text(self, parent)
		self.config(**kw)

class TopLevel(Tkinter.TopLevel):
	def __init__(self, parent, **kw):
		Tkinter.TopLevel(self, parent)
		self.config(**kw)

def main():
	try:
		root = ModalRoot()
		f = Frame(root)
		f.pack()
		Lf = LabelFrame(f, text="Label Frame")
		Lf.pack()
		Button(Lf, text="Panic", command=root.destroy).pack()
		root.mainloop()
	except:
		root.destroy()
		raise

theme = Theme()

if __name__ == '__main__':
	main()