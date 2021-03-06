#!BPY

"""
Name: 'Second Life LSL (to dir)'
Blender: 245
Group: 'Export'
Tooltip: 'Export lsl and tga files for Second Life (to dir)'
"""

__author__ = ["Domino Marama"]
__url__ = ("Online Help, http://dominodesigns.info/manuals/primstar/export-sculptie")
__version__ = "1.0.0"
__bpydoc__ = """\

LSL Exporter

This script exports Second Life sculpties in lsl + tga files
"""

# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C) 2008-2009 Domino Designs Limited
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
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

#***********************************************
# Import modules
#***********************************************

try:
    import psyco
    psyco.full()
except:
    pass

import os
import Blender
from primstar.primitive import get_prims
from primstar.sculpty import map_type
from primstar.version import LABEL

#***********************************************
# Globals
#***********************************************

PRIM_NAME = "Primstar"
BAKE_REGISTRY = 'PrimstarBake'
bake_settings = Blender.Registry.GetKey(BAKE_REGISTRY, True)
if bake_settings is None or bake_settings['alpha'] is None:
    use_alpha_sculptmaps = True
else:
    use_alpha_sculptmaps = (bake_settings['alpha'] != 0)

#***********************************************
# Classes
#***********************************************


class UniqueList(list):

    def __init__(self, items=None):
        list.__init__(self, [])
        if items:
            self.extend(items)

    def append(self, item):
        if item not in self:
            list.append(self, item)

    def extend(self, items):
        for item in items:
            self.append(item)

#***********************************************
# Templates
#***********************************************

# Note: The generated LSL script is licensed under
# The Creative Commons Attribution 2.0 UK: England & Wales license

MAIN_LSL = """// Created with %(version)s from http://dominodesigns.info
// http://creativecommons.org/licenses/by/2.0/uk/
// Do not delete the attribution and license information unless you have
// purchased a commercial license for Primstar from Domino Designs.

integer multi = %(multi)s;
list textures = %(textures)s;
vector myPos;
integer tI;
string tS;
key tK;
key crate = "bcf02ab6-1cf8-fc38-0a50-94f9cf1c6c8b";

integer isKey(key in)
{
    if(in) return 2;
    return (in == NULL_KEY);
}
%(functions)s
default
{
    state_entry()
    {
        llSetObjectName( "%(name)s" );
        llSetPrimitiveParams( [ PRIM_TEXTURE, ALL_SIDES, crate, <1.0, 1.0, 0.0>, <0.0, 0.0, 0.0>, 0.0 ] );%(setup)s
        tI = llGetListLength( textures );
        while ( tI ){
            tI = tI - 1;
            tS = llList2String( textures, tI );
            if ( isKey( tS ) == 0 )
            {
                if ( llGetInventoryType( tS ) != INVENTORY_TEXTURE )
                {
                    llOwnerSay( "Please add texture \\"" + tS + "\\" to my contents" );
                    state needs_something;
                }
            }
        }
        if ( multi )
        {
            llRequestPermissions( llGetOwner(), PERMISSION_CHANGE_LINKS );
        }
        else
        {
            state ready;
        }
    }

    run_time_permissions( integer perm )
    {
        if ( perm & PERMISSION_CHANGE_LINKS )
        {
            state ready;
        }
        else
        {
            llOwnerSay( "You must give link permissions for the build to work. Click to try again." );
            state needs_something;
        }
    }
}
%(states)s
state needs_something
{
    on_rez( integer num)
    {
        state default;
    }

    changed( integer change )
    {
        if ( change & CHANGED_INVENTORY )
        {
            state default;
        }
    }

    touch_start( integer num )
    {
        if ( llDetectedKey ( 0 ) == llGetOwner() )
        {
            state default;
        }
    }
}
"""

STATE_SHORT = """
state ready
{
    state_entry()
    {
        list params = [
            PRIM_TYPE, PRIM_TYPE_SCULPT, "%(sculpt_map)s",
            PRIM_SCULPT_TYPE_%(sculpt_type)s ,
            PRIM_SIZE, %(size)s, PRIM_ROTATION, %(rotation)s
        ];
        if (llGetLinkNumber() > 1)
            params += [PRIM_POSITION, %(position)s ];
        llSetObjectName( "%(name)s" );
        llSetPrimitiveParams(params);
        if (!isKey("%(sculpt_map)s"))
        {
            llRemoveInventory( "%(sculpt_map)s" );
        }
        llRemoveInventory( tS = llGetScriptName() );
        llSetScriptState( tS, FALSE );
    }
}
"""

STATE_SINGLE = """
state ready
{
    state_entry()
    {
        if (isKey("%(texture_image)s"))
        {
            tK = "%(texture_image)s";
        }
        else
        {
            tK = llGetInventoryKey( "%(texture_image)s" );
            llRemoveInventory( "%(texture_image)s" );
        }
        list params = [
            PRIM_TYPE, PRIM_TYPE_SCULPT, "%(sculpt_map)s",
            PRIM_SCULPT_TYPE_%(sculpt_type)s ,PRIM_SIZE, %(size)s,
            PRIM_ROTATION, %(rotation)s%(textures)s
        ];
        if (llGetLinkNumber() > 1)
            params += [PRIM_POSITION, %(position)s ];
        llSetObjectName( "%(name)s" );
        llSetPrimitiveParams(params);
        if (!isKey("%(sculpt_map)s"))
        {
            llRemoveInventory( "%(sculpt_map)s" );
        }
        llRemoveInventory( tS = llGetScriptName() );
        llSetScriptState( tS, FALSE );
    }
}
"""

STATE_MULTI = """
state ready
{
    state_entry()
    {
        llOwnerSay( "Ready to build. Click to start." );
    }

    touch_start( integer num )
    {
        if ( llDetectedKey ( 0 ) == llGetOwner() )
        {
            state build;
        }
    }
}

state build
{
    state_entry()
    {
        myPos = llGetPos();
        llSetRot( ZERO_ROTATION );
        llOwnerSay( "Building" );
        addPrim( "%(prim)s" );
    }

    object_rez( key id )
    {
        llCreateLink(id, TRUE );
    }

    changed( integer change )
    {
        if ( change & CHANGED_LINK )
        {
            tI = llGetNumberOfPrims() - 1;
            llOwnerSay( "Configuring Prim " + (string)tI);
            %(builder)sif (tI > 0 )
            {
                llSetLinkPrimitiveParams( 2, [ %(root_params)s ] );
                llBreakLink( 1 );
            }
            else
            {
                llOwnerSay( "Finished!" );
                state ready;
            }
        }
    }
}
"""

LINK_LSL = """if ( tI == %(link_num)s )
            {
                llSetLinkPrimitiveParams( 2, [ PRIM_TYPE, PRIM_TYPE_SCULPT, "%(sculpt_map)s", PRIM_SCULPT_TYPE_%(sculpt_type)s, PRIM_SIZE, %(size)s, PRIM_ROTATION, %(rotation)s, PRIM_POSITION, %(position)s%(textures)s ] );
                addPrim( "%(prim)s" );
            }
            else """

PRIM_REZ = """
addPrim( string prim )
{
    llRezObject(prim, myPos, ZERO_VECTOR, ZERO_ROTATION, 0 );
}
"""

PRIM_TEST = """
        if ( llGetInventoryType( "%(prim)s" ) != INVENTORY_OBJECT )
        {
            llOwnerSay( "Please add a prim called \\"%(prim)s\\" to my contents" );
            state needs_something;
        }"""


PRIM_PARAMS = """PRIM_TYPE, PRIM_TYPE_SCULPT, "%(sculpt_map)s", PRIM_SCULPT_TYPE_%(sculpt_type)s, PRIM_SIZE, %(size)s, PRIM_ROTATION, %(rotation)s"""


PRIM_LOCATION = """PRIM_POSITION, %(position)s"""


TEXTURE = """, PRIM_TEXTURE, %(face)s, "%(name)s", %(repeat)s, %(offset)s, %(rotation)s"""


def clean_name(name):
    while name[-4:].lower() in ['.tga', '.png', '.jpg', '.bmp']:
        name = name[:-4]
    return name


def collect_textures(prim):
    textures = UniqueList([clean_name(prim.sculpt_map.name)])
    for t in prim.textures:
        textures.append(clean_name(t.image.name))
    for c in prim.children:
        textures.extend(collect_textures(c))
    return textures


def save_textures(prim, path=None):
    # [GC] Nasty trick to preserve alpha for sculptmaps:
    is_packed = True
    if use_alpha_sculptmaps and not prim.sculpt_map.packed:
        #print "Enable nasty trick for alpha preserving"
        is_packed = False
        prim.sculpt_map.pack()
        
    textures = UniqueList([prim.sculpt_map])
    for t in prim.textures:
        textures.append(t.image)
    for c in prim.children:
        textures.extend(save_textures(c))
    if not path:
        return textures
    for t in textures:
        old = t.filename
        fn, ext = Blender.sys.splitext(old)

        if not ext or  (ext != 'png' and ext != 'tga' ):
            if t.packed:
                ext = ".png"
            else:
                ext = ".tga"
        t.setName(clean_name(t.name) + ext)        
        t.setFilename(Blender.sys.join(path, t.getName()))
        t.save()
        t.updateDisplay()
        print "Saved ", t.getName(), "of depth", t.getDepth(), "to file", t.filename
        if not is_packed:
            t.unpack(Blender.UnpackModes.WRITE_ORIGINAL)
        t.filename = old


def export_lsl(filename):
    Blender.Window.WaitCursor(1)
    prims = get_prims()
    if prims is None:
        #Blender.Window.WaitCursor(0)
        return
    if prims == []:
        #Blender.Window.WaitCursor(0)
        Blender.Draw.PupBlock("Nothing to do",
                ["No root prims are selected", " for export"])
        return
    basepath = Blender.sys.dirname(filename)
    for p in prims:
        print "save LSL linkset:", p['name']
        save_linkset(p, basepath)
    #Blender.Window.WaitCursor(0)


def prim2dict(prim, link=0):
    return {'prim': PRIM_NAME,
        'name': clean_name(prim.name),
        'position': "< %(x).5f, %(y).5f, %(z).5f >" % prim.location,
        'rotation': "< %.5f, %.5f, %.5f, %.5f >" % prim.rotation,
        'size': "< %(x).5f, %(y).5f, %(z).5f >" % prim.size,
        'sculpt_map': clean_name(prim.sculpt_map.name),
        'link_num': link,
        'sculpt_type': map_type(prim.sculpt_map)}


def texture2dict(texture):
    d = {'name': clean_name(texture.image.name),
        'offset': "< %(x).5f, %(y).5f, %(z).5f >" % texture.offset,
        'repeat': "< %(x).5f, %(y).5f, %(z).5f >" % texture.repeat,
        'rotation': "%.5f" % texture.rotation}
    if texture.face == -1:
        d['face'] = "ALL_SIDES"
    else:
        d['face'] = str(texture.face)
    return d


def link_lsl(prim, link=0):
    if link > 0:
        p = prim2dict(prim, link)
        p['textures'] = ''
        print "LSL adding child prim: ", p['name']
        for t in prim.textures:
            p['textures'] += TEXTURE % texture2dict(t)
        lsl = LINK_LSL % p
    else:
        print "LSL adding  root prim: ", prim['name']
        lsl = ''
    link += 1
    for c in prim.children:
        tc, link = link_lsl(c, link)
        lsl += tc
    return lsl, link


def save_linkset(prim, basepath):
    root = prim2dict(prim)
    d = {'prim': PRIM_NAME,
        'version': LABEL,
        'name': "Primstar - %s" % root['name']}
    if prim.children:
        d['multi'] = 'TRUE'
        d['functions'] = PRIM_REZ
        d['setup'] = PRIM_TEST % d
        builder, link = link_lsl(prim)
        print "Summary: exported Linkset containing ",link, " prims";
        root_tex = ''
        for t in prim.textures:
            root_tex += TEXTURE % texture2dict(t)
        d['states'] = STATE_MULTI % {
                'prim': PRIM_NAME,
                'builder': builder,
                'root_params': PRIM_PARAMS % root + ", " + PRIM_LOCATION\
                 % root + root_tex}
    else:
        d['multi'] = 'FALSE'
        d['functions'] = ''
        d['setup'] = ''
        root['textures'] = ''
        if prim.textures:
            for t in prim.textures:
                root['textures'] += TEXTURE % texture2dict(t)
            root['texture_image'] = clean_name(prim.textures[0].image.name)
            d['states'] = STATE_SINGLE % root
        else:
            d['states'] = STATE_SHORT % root
    d['textures'] = str(collect_textures(prim)).replace("'", "\"")
    f = open(Blender.sys.join(basepath, clean_name(prim.name) + ".lsl"), 'w')
    f.write(MAIN_LSL % d)
    f.close()
    save_textures(prim, basepath)

#***********************************************
# register callback
#***********************************************


def my_callback(filename):
    export_lsl(filename)

if __name__ == '__main__':
    Blender.Window.FileSelector(my_callback, "Export LSL", '.')
