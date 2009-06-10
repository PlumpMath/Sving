#!BPY
"""
Name: 'GUI Test'
Blender: 246
Group: 'AddMesh'
Tooltip: 'Add a Second Life sculptie compatible mesh - Test GUI'
"""

__author__ = ["Domino Marama"]
__url__ = ("http://dominodesigns.info")
__version__ = "0.00"
__bpydoc__ = """\

Sculpt Mesh

This script creates an object with a gridded UV map suitable for Second Life sculpties.
"""

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
import sculpty
from Tkinter import *
from binascii import hexlify

class GuiApp:
	def __init__(self, master, theme):
		w,h = 32, 256
		self.master = master
		self.master.grab_set()
		frame = LabelFrame(master,
				border=3,
				bg=hex_colour(theme.neutral),
				text="Primstar - Add sculpt mesh",
				labelanchor=N)
		frame.pack()
		f = LabelFrame(frame,
				text="Geometry",
				bg=hex_colour(theme.neutral),
				fg=hex_colour(theme.text))
		f.pack(padx=5, pady=5, side=LEFT)
		fx = Frame(f, bg=hex_colour(theme.neutral))
		fx.pack(side=LEFT)
		t = Label(fx,
			text="X Faces",
			justify=RIGHT,
			bg=hex_colour(theme.neutral),
			fg=hex_colour(theme.text))
		t.pack(padx=5, pady=5, side=LEFT)
		self.x_faces = IntVar(self.master, 8)
		s = Spinbox(fx,
				textvariable=self.x_faces,
				from_=1,
				to=256,
				width=3,
				bg=hex_colour(theme.num),
				fg=hex_colour(theme.text),
				activebackground=hex_colour(theme.setting))
		s.pack(padx=5, pady=5, side=RIGHT)
		fy = Frame(f, bg=hex_colour(theme.neutral))
		fy.pack(side=RIGHT)
		t = Label(fy,
			text="Y Faces",
			justify=RIGHT,
			bg=hex_colour(theme.neutral),
			fg=hex_colour(theme.text))
		t.pack(padx=5, pady=5, side=LEFT)
		self.y_faces = IntVar(self.master, 8)
		s = Spinbox(fy,
				textvariable=self.y_faces,
				from_=1,
				to=256,
				width=3,
				bg=hex_colour(theme.num),
				fg=hex_colour(theme.text),
				activebackground=hex_colour(theme.setting))
		s.pack(padx=5, pady=5, side=RIGHT)
		f = LabelFrame(frame,
				text="Map Image",
				bg=hex_colour(theme.neutral),
				fg=hex_colour(theme.text),
				labelanchor=N)
		f.pack(padx=5, pady=5, side=LEFT)
		self.lod_display = Label(f,
				text=sculpty.lod_info(w, h)[:-1],
				justify=LEFT,
				bg=hex_colour(theme.neutral),
				fg=hex_colour(theme.text))
		self.lod_display.pack(padx=5, pady=5, ipadx=3, ipady=3, side=LEFT)
		self.map_type = Button(frame,
				text="Type",
				command=self.set_map_type,
				border=1,
				bg=hex_colour(theme.textfield),
				fg=hex_colour(theme.text),
				activebackground=hex_colour(theme.setting))
		self.map_type.pack(padx=5, pady=5, fill=X)
		self.sculpt_menu = Menu(frame,
				tearoff=0,
				bg=hex_colour(theme.menu_item),
				fg=hex_colour(theme.menu_text),
				activebackground=hex_colour(theme.menu_hilite),
				activeforeground=hex_colour(theme.menu_text_hi))
		for sculpt_type in [ "Sphere", "Torus", "Plane", "Cylinder", "Hemi"]:
			def type_command( sculpt_type ):
				def new_command():
					self.set_sculpt_type(sculpt_type)
				return new_command
			self.sculpt_menu.add_command(label=sculpt_type,
					command=type_command(sculpt_type))
		self.set_sculpt_type("Sphere")
		b = Button(frame, text="Add",
				command=self.add,
				border=1,
				bg=hex_colour(theme.action),
				activebackground=hex_colour(theme.action),
				fg=hex_colour(theme.menu_text),
				activeforeground=hex_colour(theme.menu_text_hi))
		b.pack( padx=5, pady=5, fill=X )
		b = Button(frame, text="Close",
				command=self.master.destroy,
				border=1,
				bg=hex_colour(theme.action),
				activebackground=hex_colour(theme.action),
				fg=hex_colour(theme.menu_text),
				activeforeground=hex_colour(theme.menu_text_hi))
		b.pack( padx=5, pady=5, fill=X )

	def set_map_type(self):
		t = self.map_type.cget('text')
		i = self.sculpt_menu.index( t )
		y = self.map_type.winfo_rooty() - self.sculpt_menu.yposition( i )
		x  = self.master.winfo_pointerx() - self.sculpt_menu.winfo_reqwidth() // 2
		self.sculpt_menu.post(x, y)

	def set_sculpt_type(self, sculpt_type):
		self.map_type.configure(text=sculpt_type)
		self.redraw()

	def redraw(self):
		self.master.update_idletasks()
		Blender.Redraw()

	def add(self):
		print "Create a " + self.map_type.cget('text') + " sculptie"
		# self.master.destroy()

def hex_colour(theme_colour):
	return "#" + hexlify("".join([chr(i) for i in theme_colour[:-1]]))

def main():
	root = Tk()
	root.title("Add sculpt mesh")
	root.overrideredirect(1)
	root.geometry('+100+100')
	theme = Blender.Window.Theme.Get()[0].get('ui')
	root.bg = hex_colour(theme.neutral)
	gui = GuiApp(root, theme)
	root.mainloop()

if __name__ == '__main__':
	main()