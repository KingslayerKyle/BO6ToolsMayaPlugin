#   Copyright (C) 2025  Kyle Wood
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import maya.cmds as cmds
import maya.mel as mel
import webbrowser

def error( message ):
    cmds.confirmDialog( title = "An error has occurred", message = message )

def confirm_dialog( message ):
    cmds.confirmDialog( title = "Confirmation", message = message )

def view_faces():
    mel.eval( "changeSelectMode -component" )

def view_object():
    mel.eval( "changeSelectMode -object" )

def delete_faces( faces_to_select ):
    # Select the faces
    cmds.select( faces_to_select, add = True )

    # Delete them
    mel.eval( "doDelete" )

def create_new_meshes_per_vertex_color( mesh, vertex_colors ):
    # Create a new mesh for each vertex color
    for index, element in enumerate( vertex_colors ):
        # Duplicate it
        duplicate = cmds.duplicate( mesh )[0]

        # Rename it
        cmds.rename( duplicate, mesh + "_" + element )

def get_faces_for_vertex_color( mesh, index, inverse ):
    # Get all vertices of the mesh
    vertices = cmds.ls( mesh + ".vtx[*]", flatten = True )

    # Initialize a set to collect unique faces
    faces_to_select = set()

    # Loop over each vertex and check for color
    for vertex in vertices:
        # Retrieve color information
        rgb = cmds.polyColorPerVertex( vertex, query = True, rgb = True )
        
        if rgb:
            color = rgb[index]  # Extract the color component

            # If the color component is above the threshold, select all connected faces
            if( color > 0 if not inverse else color == 0 ):
                faces = cmds.polyListComponentConversion( vertex, toFace = True )
                faces = cmds.ls( faces, flatten = True )  # Ensure we get a clean list
                
                # Add all connected faces to the set
                faces_to_select.update( faces )
        
    # Convert the set to a list for selection
    return list( faces_to_select )

def set_new_material_with_suffix( mesh, suffix ):
    # Get the shape for the mesh
    shape = cmds.listRelatives( mesh, shapes = True )[0]

    # Get the shading group assigned to the shape
    shading_group = cmds.listConnections( shape, type = "shadingEngine" )[0]

    # Get the material connected to the shading group
    original_material = cmds.ls( cmds.listConnections( shading_group ), materials = True )[0]

    # Duplicate the material
    new_material = cmds.duplicate( original_material, name = original_material + "_" + suffix )[0]

    # Create a new shading group for the duplicated material
    new_shading_group = cmds.sets( renderable = True, noSurfaceShader = True, empty = True, name = new_material + "SG" )

    # Connect the new material to the new shading group
    cmds.connectAttr( new_material + ".outColor", new_shading_group + ".surfaceShader", force = True )

    # Assign the new shading group to the shape
    cmds.sets( shape, edit = True, forceElement = new_shading_group )

def split_mesh_by_vertex_colors():
    if len( cmds.ls( selection = True ) ) < 1:
        error( "Nothing is selected!" )
        return
    
    # Get the selected mesh
    selected_mesh = cmds.ls( selection = True )[0]

    # Vertex colors
    vertex_colors = ["red", "green", "blue"]

    # Create new meshes per vertex color
    create_new_meshes_per_vertex_color( selected_mesh, vertex_colors )

    # Set a unique name for each shape
    for index, mesh in enumerate( cmds.ls( type = "mesh", long = True ) ):
        cmds.rename( mesh, "MeshShape" + str( index ) )

    # Extract the faces for each vertex color
    for index, element in enumerate( vertex_colors ):
        # Select mesh
        cmds.select( selected_mesh )

        # Go into faces view
        view_faces()

        # Get faces for vertex color
        faces_to_select = get_faces_for_vertex_color( selected_mesh, index, False )

        # Delete faces
        delete_faces( faces_to_select )

        # Clear selection
        cmds.select( clear = True )

        # Go back to object view
        view_object()

        # Duplicated mesh
        duplicated_mesh = selected_mesh + "_" + element

        # Set new material for duplicated mesh
        set_new_material_with_suffix( duplicated_mesh, element )

        # Select duplicated mesh
        cmds.select( duplicated_mesh )

        # Go into faces view
        view_faces()

        # Get faces for vertex color
        faces_to_select = get_faces_for_vertex_color( duplicated_mesh, index, True )

        # Inverse delete
        delete_faces( faces_to_select )

        # Clear selection
        cmds.select( clear = True )

        # Go back to object view
        view_object()

    # Clear selection
    cmds.select( clear = True )

    # Done
    confirm_dialog( "Mesh separated." )

def menu_items():
    cmds.setParent( mel.eval( "$temp1=$gMainWindow" ) )

    # Get rid of it, if it already exists
    if cmds.control( "BO6Tools", exists = True ):
        cmds.deleteUI( "BO6Tools", menu = True )

    # Create the menu
    main_menu = cmds.menu( "BO6Tools", label = "BO6Tools", tearOff = True )

    # Misc
    cmds.menuItem( parent = main_menu, divider = True, dividerLabel = "Utilities" )
    cmds.menuItem( parent = main_menu, label = "Separate selected mesh", command = lambda x: split_mesh_by_vertex_colors() )

    # Help
    cmds.menuItem( parent = main_menu, divider = True, dividerLabel = "Information" )
    cmds.menuItem( parent = main_menu, label = "About", command = lambda x: confirm_dialog( "=======\n BO6Tools\n=======\n\nRequirements:\n\nEnsure \"Export Vertex Colors\" is enabled in Greyhound.\n\nModels must be exported in the Cast model format:\nhttps://github.com/dtzxporter/cast/releases\n\nWhat does this plugin do?\n\nThis plugin separates a mesh into individual parts based on its vertex colors.\n\nIn newer CoD titles, vertex colors are used to designate image placements within a material.\n\nUnfortunately, this feature isn't supported in BO3, which is where this plugin comes in.\n\nThe process is fully automated, with new materials being created for each mesh per vertex color.\n\nOnce your mesh is separated, you can proceed with exporting your model as usual.\n\nby Kingslayer Kyle." ) )

    # Donate
    cmds.menuItem( parent = main_menu, divider = True, dividerLabel = "Kingslayer Kyle" )
    cmds.menuItem( parent = main_menu, label = "Say thanks (donate)", command = lambda x: webbrowser.open( "https://paypal.me/kingslayerkyle" ) )

menu_items()
