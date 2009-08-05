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
SCRIPT="add_mesh_gui_test"

class MenuMap(sculpty.LibFile):
	def get_command(self, app):
		def new_command():
			app.set_shape(self.local_path, self.path)
		return new_command

class MenuDir(sculpty.LibDir):
	def add_to_menu(self, app, menu):
		for f in self.files:
			menu.add_command(label=f.name, command=f.get_command(app))
		if self.dirs and self.files:
			menu.add_separator()
		for d in self.dirs:
			submenu = gui.Menu(menu, tearoff=0)
			d.add_to_menu(app, submenu)
			menu.add_cascade(label=d.name, menu=submenu)

class GuiApp:
	def __init__(self, master):
		self.master = master
		self.cube = gui.BitmapImage(data="""#define cube_width 16
#define cube_height 16
static unsigned char cube_bits[] = {
   0x00, 0x00, 0x80, 0x03, 0x70, 0x1c, 0x8c, 0x62, 0x94, 0x53, 0x64, 0x4c,
   0xa4, 0x4b, 0x2c, 0x69, 0x34, 0x59, 0x64, 0x4d, 0xa4, 0x4b, 0x2c, 0x69,
   0x30, 0x19, 0x40, 0x05, 0x80, 0x03, 0x00, 0x00 };
""")

		# ==========================================
		# Main window frame
		# ==========================================

		top_frame = gui.Frame(master, border=4)
		top_frame.pack()
		frame = gui.LabelFrame(top_frame,
				text=ADD_SCULPT_MESH_LABEL,
				labelanchor=NW)
		frame.pack()

		# ==========================================
		# Settings frame
		# ==========================================

		shape_frame = gui.Frame(frame)
		shape_frame.pack(fill=X)
		t = gui.Label(shape_frame,
			text="Shape",
			justify=RIGHT)
		t.pack(side=LEFT)
		self.shape_name = StringVar()
		self.shape_file = None
		self.map_type = gui.Button(shape_frame,
				textvariable= self.shape_name,
				command=self.set_map_type,
				cursor='based_arrow_down',
				background=gui.hex_color(gui.theme.ui.textfield),
				relief=SUNKEN,
				pady=1,
				)
		self.map_type.pack(fill=X)

		# ==========================================
		# Geometry section (top left)
		# ==========================================

		f = gui.LabelFrame(frame,
				text="Geometry")
		f.pack(side=LEFT, fill=Y)
		ff = gui.Frame(f)
		ff.pack()
		fx = gui.Frame(ff)
		fx.pack()
		t = gui.Label(fx,
			text="X Faces",
			justify=RIGHT)
		t.pack(side=LEFT)
		self.x_faces = IntVar(self.master, 8)
		self.x_faces_input = gui.Spinbox(fx,
				textvariable=self.x_faces,
				from_=1,
				to=256,
				width=3,
				command=self.update_info)
		self.x_faces_input.pack(side=RIGHT)
		fy = gui.Frame(ff)
		fy.pack()
		t = gui.Label(fy,
				text="Y Faces",
				justify=RIGHT)
		t.pack(side=LEFT)
		self.y_faces = IntVar(self.master, 8)
		self.y_faces_input = gui.Spinbox(fy,
				textvariable=self.y_faces,
				from_=1,
				to=256,
				width=3,
				command=self.update_info)
		self.y_faces_input.pack(side=RIGHT)
		fr = gui.Frame(ff)
		fr.pack()
		t = gui.Label(fr,
				text="Radius",
				justify=RIGHT)
		t.pack(side=LEFT)
		self.radius = DoubleVar(self.master, 0.25)
		self.radius_input = gui.Spinbox(fr,
				textvariable=self.radius,
				from_=0.05,
				to=0.5,
				width=6)
		self.radius_input.pack(side=RIGHT)

		self.clean_lods = BooleanVar( self.master, True )
		c = gui.Checkbutton(f,
				text="Clean LODs",
				variable=self.clean_lods)
		c.pack(side=LEFT)


		# ==========================================
		# Subdivision section (top right)
		# ==========================================

		fs = gui.LabelFrame(frame,
				text="Subdivision")
		fs.pack(side=LEFT, padx=4, fill=Y)
		
		self.levels = IntVar(self.master, 2)
		fl = gui.Frame(fs)
		fl.pack()

		t = gui.Label(fl,
				text="Levels",
				justify=RIGHT)
		t.pack(side=LEFT)
		self.levels_input = gui.Spinbox(fl,
				textvariable=self.levels,
				from_=0,
				to=6,
				width=3,
				command=self.update_info)
		self.levels_input.pack(side=RIGHT)

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
		build_frame = gui.Frame(frame)
		build_frame.pack(fill=Y, side=LEFT)

		self.info_text = StringVar(self.master)
		self.info_frame = gui.LabelFrame(build_frame)
		self.info_frame.pack()

		self.lod_display = gui.Label(self.info_frame,
				textvariable=self.info_text,
				justify=LEFT)
		self.lod_display.pack()
		self.update_info()

		# ==========================================
		# Sculpty type selection (bottom right)
		# ==========================================

		createButton = gui.Button(build_frame,
				text="Build",
				image=self.cube,
				compound=LEFT,
				command=self.add,
				default=ACTIVE)
		createButton.pack()

		self.sculpt_menu = gui.Menu(self.master, tearoff=0)
		for sculpt_type in [ "Sphere", "Torus", "Plane", "Cylinder", "Hemi"]:
			def type_command( sculpt_type ):
				def new_command():
					self.set_shape(sculpt_type)
				return new_command
			self.sculpt_menu.add_command(label=sculpt_type,
					command=type_command(sculpt_type))
		self.sculpt_menu.add_separator()
		library = sculpty.build_lib(LibDir=MenuDir, LibFile=MenuMap)
		library.add_to_menu(self, self.sculpt_menu)

		self.set_shape("Sphere") # TODO: retrieve settings from registry

	def set_map_type(self):
		t = self.shape_name.get().split(os.sep)
		if t[0]:
			t = t[0]
		else:
			t = t[1]
		i = self.sculpt_menu.index( t )
		y = self.map_type.winfo_rooty() - self.sculpt_menu.yposition( i ) + 8
		x  = self.master.winfo_pointerx() - self.sculpt_menu.winfo_reqwidth() // 2
		self.sculpt_menu.post(x, y)

	def set_shape(self, name, filename=None):
		self.shape_name.set(name)
		self.shape_file = filename
		if filename:
			# reading the image file leaves it in the blend
			# can uncomment this when able to remove the temporary image
			#i = Blender.Image.Load(filename)
			#sculpt_type = sculpty.map_type(i)
			#if sculpt_type == "TORUS":
			self.radius_input.config(state=NORMAL)
			#else:
			#	self.radius_input.config(state=DISABLED)
			#self.x_faces_input.config(to=i.size[0] / 2)
			#self.y_faces_input.config(to=i.size[1] / 2)
		else:
			if name == "Torus":
				self.radius_input.config(state=NORMAL)
			else:
				self.radius_input.config(state=DISABLED)
			#self.x_faces_input.config(to=256)
			#self.y_faces_input.config(to=256)

	def redraw(self):
		self.master.update_idletasks()
		Blender.Redraw()

	def update_info(self, event=None):
		s, t, w, h, clean_s, clean_t = sculpty.map_size(self.x_faces.get(), self.y_faces.get(), self.levels.get())
		self.info_frame.config(text="Map Size - %d x %d"%(w, h))
		self.info_text.set(sculpty.lod_info(w, h)[:-1])
		if not (clean_s and clean_t):
			self.levels_input.configure(
					background=gui.hex_color(gui.theme.ui.textfield_hi))
		else:
			self.levels_input.configure(
					background=gui.hex_color(gui.theme.ui.textfield))
			if clean_s:
				self.x_faces_input.configure(
						background=gui.hex_color(gui.theme.ui.textfield))
			else:
				self.x_faces_input.configure(
						background=gui.hex_color(gui.theme.ui.textfield_hi))
			if clean_t:
				self.y_faces_input.configure(
						background=gui.hex_color(gui.theme.ui.textfield))
			else:
				self.y_faces_input.configure(
						background=gui.hex_color(gui.theme.ui.textfield_hi))

	def add(self):
		Blender.Window.WaitCursor(1)
		name = self.shape_name.get()
		basename = name.split(os.sep)[-1]
		if self.shape_file:
			baseimage = Blender.Image.Load(self.shape_file)
			sculpt_type = sculpty.map_type(baseimage)
		else:
			sculpt_type = name.upper()
			baseimage = None
		gui.debug(11,
				"Add sculptie (%s) of type %s"%(name, sculpt_type),
				"add_mesh_sculpt_mesh")
		scene = Blender.Scene.GetCurrent()
		for ob in scene.objects:
			ob.sel = False
		try:
			mesh = sculpty.new_mesh( basename,sculpt_type,
					self.x_faces.get(), self.y_faces.get(),
					self.levels.get(), self.clean_lods.get(), self.radius.get())
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
				z = self.radius.get() * z
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
			#Blender.Draw.PupBlock("Unable to create sculptie", ["Please decrease face counts","or subdivision levels"])
			pass
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

def main():
	root = None
	start_time = Blender.sys.time()
	gui.debug(1, "started", SCRIPT)
	try:
		root = gui.ModalRoot()
		app = GuiApp(root)
		root.mainloop()
		root.destroy()
	except:
		if root:
			root.destroy()
		raise
	gui.debug(1, "ended in %.4f sec."%(Blender.sys.time() - start_time), SCRIPT)

if __name__ == '__main__':
	main()
