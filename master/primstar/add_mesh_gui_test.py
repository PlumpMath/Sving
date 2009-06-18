#!BPY
"""
Name: 'GUI Test'
Blender: 246
Group: 'AddMesh'
Tooltip: 'Add a Second Life sculptie compatible mesh - Test GUI'
"""

__author__ = ["Domino Marama", "Gaia Clary"]
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
from primstar import sculpty
import os
from Tkinter import *
from binascii import hexlify
from primstar import gui

ADD_SCULPT_MESH_LABEL = "Primstar - Add sculpt mesh"

class MenuMap(sculpty.LibFile):
	def get_command(self, app):
		def new_command():
			app.set_sculpt_type(self.local_path)
			self.selectorActive = False
		return new_command

class MenuDir(sculpty.LibDir):
	def add_to_menu(self, app, menu):
		for f in self.files:
			menu.add_command(label=f.name, command=f.get_command(app))
		for d in self.dirs:
			submenu = gui.Menu(menu, tearoff=0)
			d.add_to_menu(app, submenu)
			menu.add_cascade(label=d.name, menu=submenu)

class GuiApp:
	def __init__(self, master):
		w,h = 32, 256
		self.master = master
		self.master.overrideredirect(True)
		
		# ==========================================
		# Main window frame		
		# ==========================================
		topFrame = Frame(master, border=4)
		topFrame.pack()

		frame = gui.LabelFrame(topFrame,
				border=3, relief=FLAT,
				text=ADD_SCULPT_MESH_LABEL,
				labelanchor=NW)
		frame.pack(anchor=CENTER)
		self.map_type = gui.Button(frame,
				text="Type",
				command=self.set_map_type,
				border=1)
		self.map_type.pack(padx=4, fill=X, pady=5, side=TOP, anchor=CENTER)

		# ==========================================
		# Geometry section (top left)
		# ==========================================

		upperFrame = gui.Frame(frame)
		upperFrame.pack()
		
		f = gui.LabelFrame(upperFrame,
				text="Geometry")
		f.pack(padx=5, pady=5, fill=BOTH, side=LEFT, anchor=CENTER ) 
		
		ff = gui.Frame(f)
		ff.pack()
		fx = gui.Frame(ff)
		fx.pack()
		t = gui.Label(fx,
			text="X Faces",
			justify=RIGHT)
		t.pack(padx=5, pady=5, side=LEFT)
		self.x_faces = IntVar(self.master, 8)
		s = gui.Spinbox(fx,
				textvariable=self.x_faces,
				from_=1,
				to=256,
				width=3)
		s.pack(padx=5, pady=5, side=RIGHT)
		fy = gui.Frame(ff)
		fy.pack()
		t = gui.Label(fy,
				text="Y Faces",
				justify=RIGHT)
		t.pack(padx=5, pady=5, side=LEFT)
		self.y_faces = IntVar(self.master, 8)
		s = gui.Spinbox(fy,
				textvariable=self.y_faces,
				from_=1,
				to=256,
				width=3)
		s.pack(padx=5, pady=5, side=RIGHT)

		self.clean_lods = BooleanVar( self.master, True )
		c = gui.Checkbutton(f,
				text="Clean LODs",
				variable=self.clean_lods)
		c.pack(padx=0, pady=5, side=LEFT)


		# ==========================================
		# Subdivision section (top right)
		# ==========================================

		fs = gui.LabelFrame(upperFrame,
				text="Subdivision")
		fs.pack(padx=5, pady=5, fill=BOTH, side=RIGHT, anchor=CENTER )
		
		self.levels = IntVar(self.master, 2)
		fl = gui.Frame(fs)
		fl.pack()

		t = gui.Label(fl,
				text="Levels",
				justify=RIGHT)
		t.pack(padx=5, pady=5, side=LEFT)
		s = gui.Spinbox(fl,
				textvariable=self.levels,
				from_=0,
				to=6,
				width=3)
		s.pack(padx=5, pady=5, side=RIGHT)

		self.sub_type = IntVar(self.master, 1)
		r = gui.Frame(fs)
		r.pack(side=LEFT)
		gui.Radiobutton(r,
				text="Subsurf",
				variable=self.sub_type,
				value=1).pack()

		gui.Radiobutton(r,
				text="Multires",
				variable=self.sub_type,
				value=0).pack()
		self.subdivision = IntVar(self.master, 1)
		r = gui.Frame(fs)
		r.pack(side=RIGHT)
		gui.Radiobutton(r,
				text="Catmull",
				variable=self.subdivision,
				value=1).pack()
		gui.Radiobutton(r,
				text="Simple",
				variable=self.subdivision,
				value=0).pack()

		# ==========================================
		# LOD display (bottom left)
		# ==========================================				
				
		f = gui.LabelFrame(frame,
				text="Map Image")
		f.pack(padx=6, ipadx=3, pady=3, fill=BOTH, side=LEFT, anchor=CENTER)

		self.lod_display = gui.Label(f,
				text=sculpty.lod_info(w, h)[:-1],
				justify=LEFT)
		self.lod_display.pack(padx=5, pady=5, ipadx=3, ipady=3, side=LEFT)

		# ==========================================
		# Sculpty type selection (bottom right)
		# ==========================================

		controlFrame = gui.Frame(frame)
		controlFrame.pack(padx=5, pady=6, fill=Y, side=RIGHT, anchor=N)

		self.sculpt_menu = gui.Menu(controlFrame,
				tearoff=0)
		for sculpt_type in [ "Sphere", "Torus", "Plane", "Cylinder", "Hemi"]:
			def type_command( sculpt_type ):
				def new_command():
					self.set_sculpt_type(sculpt_type)
					self.selectorActive = False
				return new_command
			self.sculpt_menu.add_command(label=sculpt_type,
					command=type_command(sculpt_type))
		library = sculpty.build_lib(LibDir=MenuDir, LibFile=MenuMap)
		library.add_to_menu(self, self.sculpt_menu)

		self.selector = self.map_type
		self.set_sculpt_type("Sphere") # TODO: retrieve settings from registry
		
		# ==========================================
		# Control section (bottom right)
		# ==========================================

		buttonFrame = gui.Frame(controlFrame)
		buttonFrame.pack(side=BOTTOM, anchor=CENTER)


		# Cancel/Create buttons need layout tuning.
		createButton = gui.Button(buttonFrame, text="Ok",
				command=self.add,
				default=ACTIVE)
		createButton.pack( ipadx=7 , padx=4, pady=0, side=LEFT, anchor=SW)
		
		b = gui.Button(buttonFrame, text="Cancel",
				command=self.master.quit)
		b.pack( ipadx=7, padx=8, pady=0, side=RIGHT, anchor=SE)
		
		# ===============================================================
		# Make master window sticky.
		# Bind <Leave> and <Enter> events to the top window
		# And preset "mouse is in app" and  "no selection active"
		# ===============================================================
		if os.name == "nt":
			self.master.wm_attributes("-topmost", 1)   # Make sure window remains on top of all others
		self.master.bind( "<Leave>",   self.mouse_leave_handler) # track leave main window
		self.master.bind( "<Enter>",   self.mouse_enter_handler) # track enter main window

		self.set_mouse_in_app(True)
		self.selectorActive = False

		self.master.configure(takefocus=True)
		createButton.focus_force()		

	def set_map_type(self):
		t = self.map_type.cget('text').split(os.sep)
		if t[0]:
			t = t[0]
		else:
			t = t[1]
		i = self.sculpt_menu.index( t )
		y = self.map_type.winfo_rooty() - self.sculpt_menu.yposition( i )
		x  = self.master.winfo_pointerx() - self.sculpt_menu.winfo_reqwidth() // 2
		self.selectorActive = True
		self.sculpt_menu.post(x, y)

	def set_sculpt_type(self, sculpt_type):
		self.map_type.configure(text=sculpt_type)
		self.redraw()

	def redraw(self):
		self.master.update_idletasks()
		Blender.Redraw()

	def add(self):
		Blender.Window.WaitCursor(1)
		name = self.map_type.cget('text')
		if name[:1] == os.sep:
			basename = name.split(os.sep)[1]
			if basename == "Object":
				basename = name.split(os.sep)[-1]
			baseimage = Blender.Image.Load(os.path.join(sculpty.lib_dir, name[1:]) + '.png')
			sculpt_type = sculpty.map_type(baseimage)
		else:
			basename = name
			sculpt_type = name.upper()
			baseimage = None
		print "Create a [", name, "] of type ", sculpt_type
		scene = Blender.Scene.GetCurrent()
		for ob in scene.objects:
			ob.sel = False
		try:
			mesh = sculpty.new_mesh( basename,sculpt_type,
					self.x_faces.get(), self.y_faces.get(),
					self.levels.get(), self.clean_lods.get(), 0.25) #todo: 0.25 radius needs gui add..
			s, t, w, h, clean_s, clean_t = sculpty.map_size(self.x_faces.get(), self.y_faces.get(), self.levels.get())
			image = Blender.Image.New(basename, w, h, 32)
			sculpty.bake_lod(image)
			ob = scene.objects.new(mesh, basename)
			mesh.flipNormals()
			ob.sel = True
			ob.setLocation(Blender.Window.GetCursorPos())
			sculpty.set_map(mesh, image)
			if baseimage:
				sculpty.update_from_map(mesh, baseimage)
			if self.levels.get():
				if self.sub_type.get():
					mods = ob.modifiers
					mod = mods.append(Blender.Modifier.Types.SUBSURF)
					mod[Blender.Modifier.Settings.LEVELS] = self.levels.get()
					mod[Blender.Modifier.Settings.RENDLEVELS] = self.levels.get()
					mod[Blender.Modifier.Settings.UV] = False
					if not self.subdivision.get():
						mod[Blender.Modifier.Settings.TYPES] = 1
				else:
					mesh.multires = True
					mesh.addMultiresLevel(self.levels.get(), ('simple', 'catmull-clark')[self.subdivision.get()])
					mesh.sel = True
			# adjust scale for subdivision
			minimum, maximum = sculpty.get_bounding_box(ob)
			x = 1.0 / (maximum.x - minimum.x)
			y = 1.0 / (maximum.y - minimum.y)
			try:
				z = 1.0 / (maximum.z - minimum.z)
			except:
				z = 0.0
			if sculpt_type == "TORUS":
				z = 0.25 * z #todo: radius again
			elif sculpt_type == "HEMI":
				z = 0.5 * z
			tran = Blender.Mathutils.Matrix([ x, 0.0, 0.0 ], [0.0, y, 0.0], [0.0, 0.0, z]).resize4x4()
			mesh.transform(tran)
			# align to view
			try:
				quat = None
				if Blender.Get('add_view_align'):
					quat = Blender.Mathutils.Quaternion(Blender.Window.GetViewQuat())
					if quat:
						mat = quat.toMatrix()
						mat.invert()
						mat.resize4x4()
						ob.setMatrix(mat)
			except:
				pass
		except RuntimeError:
			#todo tkinter this
			Blender.Draw.PupBlock("Unable to create sculptie", ["Please decrease face counts","or subdivision levels"])
		Blender.Window.WaitCursor(0)
		self.master.quit() # self.master.destroy() makes blender crash occasionally (thread problems)

	# =================================================================================
	# Purpose: Quit the application when the user clicks anywhere outside of the
	# application window.
	# This handler is called whenever the mouse leaves a widget. If 2 consecutive
	# events happen, which both state that the self.master widget has been left, then
	# the application will be terminated.
	# 
	# EXPLANATION: This situation happens only when
	# 1.) The mouse has fully left the application 
	# 2.) The user has clicked somewhere on the screen (outside the application)
	#
	# Exception: When the user has opened a Menu, the menu itemns can lay outside of the
	# application window. But we have remembered, that the menu has been opened. This
	# is stored in (self.buttonClicked = True) When the user selects a menu option, it
	# is then possible that a Window Left event happens, although focus will return
	# instantly to the main menu. In that case the Leave event is ignored.
	#
	# self.mouseInApp
	# self.activeElement
	# =================================================================================
	def mouse_leave_handler(self, event):
		if event.widget == self.master:
			# Mouse clicked outside of the application window
			if self.selectorActive == False:
				if self.mouseInApp == False:
					self.log(event, "quit now..." )
					self.master.update_idletasks()
					self.master.quit()
				self.log(event, "Mouse outside app (L)" )
			else:
				self.log(event, "Mouse outside app (L) with Selection active." )
				self.selectorActive = False
			self.set_mouse_in_app(False)
			self.redraw()

	def mouse_enter_handler(self, event):
		if event.widget == self.master:
			self.log(event, "Mouse inside app (E)" )
			self.set_mouse_in_app(True) # We enter into the application window

	def set_mouse_in_app(self, inApp):
		self.master.grab_set_global()
		self.master.update_idletasks()
		self.mouseInApp = inApp

	def log(self, event, label):
		wname  = event.widget.winfo_name()
		wclass = event.widget.winfo_class()
		tlw    = event.widget.winfo_toplevel().winfo_name()
		print label + " ["+wclass+":"+wname+"] member of ["+tlw+"]"

def main():
	root = Tk()

	# ==========================================================================
	# Calculate the position where the menu_back appears. Assume the dimension of 
	# the window is 256*256 pixel and correct the window position so thet the
	# mouse is in the center of the window 
	# ==========================================================================
	xPos, yPos      = root.winfo_pointerxy()
	root.geometry('+'+str(xPos-128)+'+'+str(yPos-128))

	gui = GuiApp(root)

	print ADD_SCULPT_MESH_LABEL + " started." 		
	try:
		root.mainloop()
	except:
		print "Application terminated with errors"

	# finalize application
	root.grab_release()
	root.destroy()   # If omitted, blender crashes (Threading problems)
	print ADD_SCULPT_MESH_LABEL + " terminated."

if __name__ == '__main__':
	main()
