bl_info = {
    "name": "Network to blender",
    "description": "Script to plot networks in Blender",
    "author": "Julian Evans",
    "version": (0, 0, 6),
    "blender": (2, 80, 0),
    "location": "3D View",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}


import bpy
from mathutils import Vector
import csv
import os

from bpy.props import (StringProperty,
                       PointerProperty,
                       IntProperty
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class NetProps(PropertyGroup):

  

    edatapath: StringProperty(
        name="Edge data path",
        description=":Edge CSV",
        default="",
        maxlen=1024,
        subtype="FILE_PATH"
        )
        
    vdatapath: StringProperty(
        name="Vertex data path",
        description=":Vertex CSV",
        default="",
        maxlen=1024,
        subtype="FILE_PATH",
        )
        
    cframe: IntProperty(
        name="Frame",
        description=":Frame number",
        default=0,
        )
        
    frameint: IntProperty(
        name="Frame interval",
        description=":Gap between network timesteps",
        default=24,
        )
        
    folderpath: StringProperty(
        name="Folder path",
        description=":Folder of networks",
        default="",
        maxlen=1024,
        subtype="FILE_PATH",
        )
# ------------------------------------------------------------------------
#    Functions
# ------------------------------------------------------------------------



class importnet():
    
    def __init__(self,context,edatapath,vdatapath,cframe):
        self.context=context
        self.edatapath=edatapath
        self.vdatapath=vdatapath
        self.cframe=cframe
        

        
    def do_import(self):
        context=self.context
        scene=context.scene
        edatapath=self.edatapath
        vdatapath=self.vdatapath
        cframe=self.cframe
        
        def add_arrowhead(v0, v1, ered,egreen,eblue,edgename='edge',toshorten=0,fromshorten=0,arrowlength=0,arrowsize=0,ecurve=0,forcecurve=False,edge3d=True):
            curved=(ecurve>0)|forcecurve
            v0, v1 = Vector(v0), Vector(v1)  
            #backup original coords
            v02=v0
            v01=v1
            
            toshorten=toshorten+arrowlength
            vec1=(v1-v0)
            vec1.normalize()
            v0=v0+(vec1*fromshorten)
            v1=v0+(vec1*((v1-v0).length-toshorten))

            o = (v1 + v0) / 2  
            if curved:
                vsize=[abs(i) for i in list(v1-v0)]
                res = len(vsize) - 1 - vsize[::-1].index(min(vsize))        
                curvev=[0,0,0]
                curvev[res]=1
                curvev=Vector(curvev)        
                
                dir = v1-v0
                dir2 = dir.cross(curvev)
                dir2.normalize()
                v2=o+(dir2*ecurve )
            else:
                v2=v1
            avec=v01-v2
            #avec.normalized()
            
            bpy.ops.mesh.primitive_cone_add(radius2=0,end_fill_type='TRIFAN')
            bpy.ops.object.scale.x=arrowsize
            bpy.ops.object.scale.y=arrowsize
            bpy.ops.object.scale.z=arrowlength
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            bpy.context.object.location=v1
            if edge3d == 'FALSE':
                bpy.context.object.scale.x=0.00001
            bpy.context.object.rotation_mode = 'QUATERNION'
            bpy.context.object.rotation_quaternion = avec.to_track_quat('Z', 'X')
            newmat=make_material(edgename,ered,egreen,eblue)
            bpy.context.object.data.materials.append(newmat)
            bpy.context.object.name=edgename+'ah'
            bpy.context.object.data.name=edgename+'ah'
            bpy.context.object.keyframe_insert(data_path="location", frame=cframe)
            bpy.context.object.keyframe_insert(data_path="scale", frame=cframe)
            bpy.context.object.keyframe_insert(data_path="rotation", frame=cframe)
            edges.objects.link(bpy.context.object)
            
        def move_arrowhead(v0, v1, ered,egreen,eblue,edgename='edge',toshorten=0,fromshorten=0,arrowlength=0,arrowsize=0,ecurve=0,forcecurve=False,edge3d=True):
            curved=(ecurve>0)|forcecurve
            v0, v1 = Vector(v0), Vector(v1)  
            #backup original coords
            v02=v0
            v01=v1
            
            toshorten=toshorten+arrowlength
            vec1=(v1-v0)
            vec1.normalize()
            v0=v0+(vec1*fromshorten)
            v1=v0+(vec1*((v1-v0).length-toshorten))

            o = (v1 + v0) / 2  
            if curved:
                vsize=[abs(i) for i in list(v1-v0)]
                res = len(vsize) - 1 - vsize[::-1].index(min(vsize))        
                curvev=[0,0,0]
                curvev[res]=1
                curvev=Vector(curvev)        
                
                dir = v1-v0
                dir2 = dir.cross(curvev)
                dir2.normalize()
                v2=o+(dir2*ecurve )
            else:
                v2=v1
            avec=v01-v2
            
            old_obj=edges.objects[edgename+'ah']
            old_obj.location=v1
            old_obj.scale.x=arrowsize
            old_obj.scale.y=arrowsize
            old_obj.scale.z=arrowlength
            if edge3d == 'FALSE':
               old_obj.scale.x=0.00001
            old_obj.rotation_quaternion = avec.to_track_quat('Z', 'X')
            modify_material(edgename,ered,egreen,eblue)
            old_obj.keyframe_insert(data_path="location", frame=cframe)
            old_obj.keyframe_insert(data_path="scale", frame=cframe)
            old_obj.keyframe_insert(data_path="rotation", frame=cframe)
            
        def add_bezier(v0 , v1,edgename='edge',ecurve=0,forcecurve=False,toshorten=0,fromshorten=0,arrowlength=0):
            curved=(ecurve>0)|forcecurve
            v0, v1 = Vector(v0), Vector(v1)  
            #backup original coords
            v02=v0
            v01=v0
            toshorten=toshorten+arrowlength
            
            
            vec1=(v1-v0)
            vec1.normalize()
            v0=v0+(vec1*fromshorten)
            v1=v0+(vec1*((v1-v0).length-toshorten))
            
            o = (v1 + v0) / 2  
            if curved:
                if ecurve>0:
                    vsize=[abs(i) for i in list(v1-v0)]
                    res = len(vsize) - 1 - vsize[::-1].index(min(vsize))        
                    curvev=[0,0,0]
                    curvev[res]=1
                    curvev=Vector(curvev)        
                    
                    dir = v1-v0
                    dir2 = dir.cross(curvev)
                    dir2.normalize()
                    v2=o+(dir2*ecurve )
                else:
                    v2=o
            curve = bpy.data.curves.new(edgename, 'CURVE')
            spline = curve.splines.new('BEZIER')
            bp0 = spline.bezier_points[0]
            bp0.co = v0 - o
            bp0.handle_left_type = bp0.handle_right_type = 'AUTO'

            
            if curved:
                spline.bezier_points.add(count=1)
                bp2 = spline.bezier_points[1]

                bp2.co = v2 - o

                bp2.handle_left_type = bp2.handle_right_type = 'AUTO'

                
            spline.bezier_points.add(count=1)
            bp1 = spline.bezier_points[len(spline.bezier_points)-1]
            bp1.co = v1 - o
            bp1.handle_left_type = bp1.handle_right_type = 'AUTO'

            bp0 = spline.bezier_points[0]
            bp0.keyframe_insert(data_path="co", frame=cframe)
            bp0.keyframe_insert(data_path="handle_right", frame=cframe)
            bp0.keyframe_insert(data_path="handle_left", frame=cframe)
            bp0.keyframe_insert(data_path="handle_right_type", frame=cframe)
            bp0.keyframe_insert(data_path="handle_left_type", frame=cframe)
            
            if curved:
                bp2 = spline.bezier_points[1]
                bp2.keyframe_insert(data_path="co", frame=cframe)
                bp2.keyframe_insert(data_path="handle_right", frame=cframe)
                bp2.keyframe_insert(data_path="handle_left", frame=cframe)
                bp2.keyframe_insert(data_path="handle_right_type", frame=cframe)
                bp2.keyframe_insert(data_path="handle_left_type", frame=cframe)
            
            bp1 = spline.bezier_points[len(spline.bezier_points)-1]
            bp1.keyframe_insert(data_path="co", frame=cframe)
            bp1.keyframe_insert(data_path="handle_right", frame=cframe)
            bp1.keyframe_insert(data_path="handle_left", frame=cframe)
            bp1.keyframe_insert(data_path="handle_right_type", frame=cframe)
            bp1.keyframe_insert(data_path="handle_left_type", frame=cframe)
            
            ob = bpy.data.objects.new(edgename, curve)
            ob.data.use_uv_as_generated = True

            ob.matrix_world.translation = o
            ob.keyframe_insert(data_path="scale", frame=cframe)
            ob.keyframe_insert(data_path="location", frame=cframe)
            ob.keyframe_insert(data_path="rotation_euler", frame=cframe)
            return ob

        def modify_bezier(v0,v1,edgename='edge',ecurve=0,forcecurve=False,toshorten=0,fromshorten=0,arrowlength=0):
            curved=(ecurve>0)|forcecurve
            v0, v1 = Vector(v0), Vector(v1)  
            #backup original coords
            v02=v0
            v01=v0
            toshorten=toshorten+arrowlength
            
            vec1=(v1-v0)
            vec1.normalize()
            v0=v0+(vec1*fromshorten)
            v1=v0+(vec1*((v1-v0).length-toshorten))

            o = (v1 + v0) / 2  
            if curved:
                if ecurve>0:
                    vsize=[abs(i) for i in list(v1-v0)]
                    res = len(vsize) - 1 - vsize[::-1].index(min(vsize))        
                    curvev=[0,0,0]
                    curvev[res]=1
                    curvev=Vector(curvev)        
                    
                    dir = v1-v0
                    dir2 = dir.cross(curvev)
                    dir2.normalize()
                    v2=o+(dir2*ecurve )
                else:
                    v2=o
            old_obj=edges.objects[ename]
            bp0 = old_obj.data.splines.active.bezier_points.values()[0]
            bp0.co = v0 - o
            bp0.handle_left_type = bp0.handle_right_type = 'AUTO'


            if curved:
                bp2 = old_obj.data.splines.active.bezier_points.values()[1]

                bp2.co = v2 - o

                bp2.handle_left_type = bp2.handle_right_type = 'AUTO'
                

            
            bp1 = old_obj.data.splines.active.bezier_points.values()[len(old_obj.data.splines.active.bezier_points.values())-1]
            bp1.co = v1 - o
            
            bp1.handle_left_type = bp1.handle_right_type = 'AUTO'
            
            bp0 = old_obj.data.splines.active.bezier_points.values()[0]
            bp0.keyframe_insert(data_path="co", frame=cframe)
            bp0.keyframe_insert(data_path="handle_right", frame=cframe)
            bp0.keyframe_insert(data_path="handle_left", frame=cframe)
            bp0.keyframe_insert(data_path="handle_right_type", frame=cframe)
            bp0.keyframe_insert(data_path="handle_left_type", frame=cframe)
            
            if curved:
                print("Add curve keyframe")
                bp2 = old_obj.data.splines.active.bezier_points.values()[1]
                bp2.keyframe_insert(data_path="co", frame=cframe)
                bp2.keyframe_insert(data_path="handle_right", frame=cframe)
                bp2.keyframe_insert(data_path="handle_left", frame=cframe)
                bp2.keyframe_insert(data_path="handle_right_type", frame=cframe)
                bp2.keyframe_insert(data_path="handle_left_type", frame=cframe)
            
            bp1 = old_obj.data.splines.active.bezier_points.values()[len(old_obj.data.splines.active.bezier_points.values())-1]
            bp1.keyframe_insert(data_path="co", frame=cframe)
            bp1.keyframe_insert(data_path="handle_right", frame=cframe)
            bp1.keyframe_insert(data_path="handle_left", frame=cframe)
            bp1.keyframe_insert(data_path="handle_right_type", frame=cframe)
            bp1.keyframe_insert(data_path="handle_left_type", frame=cframe)
            
            old_obj.matrix_world.translation = o
            old_obj.keyframe_insert(data_path="scale", frame=cframe)
            old_obj.keyframe_insert(data_path="location", frame=cframe)
            old_obj.keyframe_insert(data_path="rotation_euler", frame=cframe)
            return old_obj

        def make_material(name,cr,cg,cb,cd=0,forcedash=False):
            i=(name+"_mat")
            dash=(cd>0)|forcedash
            print('material '+i)
            if i not in bpy.data.materials:
                print('created')
                if not dash:
                    mat = bpy.data.materials.new(name=i)
                    mat.diffuse_color = (float(cr), float(cg), float(cb), 1)
                    mat.keyframe_insert(data_path="diffuse_color",frame=cframe)
                    return mat
                else:
                    #make material
                    mat = bpy.data.materials.new(name=i)
                    bpy.data.materials[i].use_nodes=True
                    
                    bpy.data.materials[i].node_tree.nodes.new(type="ShaderNodeTexChecker")
                    
                    bpy.data.materials[i].node_tree.nodes["Checker Texture"].inputs[3].default_value = (1)                    
                    
                    bpy.data.materials[i].node_tree.nodes.new(type="ShaderNodeMixShader")
                    bpy.data.materials[i].node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")

                    #link to Mix texture
                    outp=bpy.data.materials[i].node_tree.nodes["Checker Texture"].outputs["Fac"]
                    inp=bpy.data.materials[i].node_tree.nodes["Mix Shader"].inputs["Fac"]
                    bpy.data.materials[i].node_tree.links.new(inp,outp)

                    outp=bpy.data.materials[i].node_tree.nodes["Principled BSDF"].outputs["BSDF"]
                    inp=bpy.data.materials[i].node_tree.nodes["Mix Shader"].inputs[1]
                    bpy.data.materials[i].node_tree.links.new(inp,outp)
                    
                    outp=bpy.data.materials[i].node_tree.nodes["Principled BSDF.001"].outputs["BSDF"]
                    inp=bpy.data.materials[i].node_tree.nodes["Mix Shader"].inputs[2]
                    bpy.data.materials[i].node_tree.links.new(inp,outp)
                    
                    bpy.data.materials[i].node_tree.nodes["Principled BSDF"].inputs[0].default_value=(float(cr), float(cg), float(cb), 1)
                    bpy.data.materials[i].node_tree.nodes["Principled BSDF.001"].inputs[0].default_value=(float(cr), float(cg), float(cb), 1)
                    bpy.data.materials[i].node_tree.nodes["Principled BSDF"].inputs[0].keyframe_insert(data_path="default_value",frame=cframe)                    
                    bpy.data.materials[i].node_tree.nodes["Principled BSDF.001"].inputs[0].keyframe_insert(data_path="default_value",frame=cframe)
                    
                    if cd>0:
                        bpy.data.materials[i].node_tree.nodes["Principled BSDF.001"].inputs[18].default_value=0
                    else:
                        bpy.data.materials[i].node_tree.nodes["Principled BSDF.001"].inputs[18].default_value=1
                    bpy.data.materials[i].node_tree.nodes["Principled BSDF.001"].inputs[18].keyframe_insert(data_path="default_value",frame=cframe)

                    bpy.data.materials[i].node_tree.nodes.new(type="ShaderNodeCombineXYZ")
                    
                    outp=bpy.data.materials[i].node_tree.nodes["Combine XYZ"].outputs["Vector"]
                    inp=bpy.data.materials[i].node_tree.nodes["Checker Texture"].inputs["Vector"]
                    bpy.data.materials[i].node_tree.links.new(inp,outp)
                    
                    bpy.data.materials[i].node_tree.nodes.new(type="ShaderNodeMath")
                    bpy.data.materials[i].node_tree.nodes.new(type="ShaderNodeMath")
                    
                    outp=bpy.data.materials[i].node_tree.nodes["Math"].outputs["Value"]
                    inp=bpy.data.materials[i].node_tree.nodes["Combine XYZ"].inputs["X"]
                    bpy.data.materials[i].node_tree.links.new(inp,outp)
                    
                    bpy.data.materials[i].node_tree.nodes["Math"].operation='MULTIPLY'
                    
                    bpy.data.materials[i].node_tree.nodes["Math"].inputs[1].default_value=cd
                    bpy.data.materials[i].node_tree.nodes["Math"].inputs[1].keyframe_insert(data_path="default_value",frame=cframe)   
                    
                    outp=bpy.data.materials[i].node_tree.nodes["Math.001"].outputs["Value"]
                    inp=bpy.data.materials[i].node_tree.nodes["Combine XYZ"].inputs["Y"]
                    bpy.data.materials[i].node_tree.links.new(inp,outp)
                    bpy.data.materials[i].node_tree.nodes["Math.001"].operation='MULTIPLY'
                    bpy.data.materials[i].node_tree.nodes["Math.001"].inputs[1].default_value=0
                    
                    bpy.data.materials[i].node_tree.nodes.new(type="ShaderNodeSeparateXYZ")
                    outp=bpy.data.materials[i].node_tree.nodes["Separate XYZ"].outputs["Z"]
                    inp=bpy.data.materials[i].node_tree.nodes["Combine XYZ"].inputs["Z"]
                    bpy.data.materials[i].node_tree.links.new(inp,outp)
                    
                    outp=bpy.data.materials[i].node_tree.nodes["Separate XYZ"].outputs["X"]
                    inp=bpy.data.materials[i].node_tree.nodes["Math"].inputs[0]
                    bpy.data.materials[i].node_tree.links.new(inp,outp)

                    outp=bpy.data.materials[i].node_tree.nodes["Separate XYZ"].outputs["Y"]
                    inp=bpy.data.materials[i].node_tree.nodes["Math.001"].inputs[0]
                    bpy.data.materials[i].node_tree.links.new(inp,outp)
                    
                    bpy.data.materials[i].node_tree.nodes.new(type="ShaderNodeTexCoord")                    

                    outp=bpy.data.materials[i].node_tree.nodes["Texture Coordinate"].outputs["UV"]
                    inp=bpy.data.materials[i].node_tree.nodes["Separate XYZ"].inputs["Vector"]
                    bpy.data.materials[i].node_tree.links.new(inp,outp)
                    
                    outp=bpy.data.materials[i].node_tree.nodes["Mix Shader"].outputs["Shader"]
                    inp=bpy.data.materials[i].node_tree.nodes["Material Output"].inputs["Surface"]
                    bpy.data.materials[i].node_tree.links.new(inp,outp)                                  
                    return mat
            else:
                modify_material(name,cr,cg,cb,cd=cd,forcedash=forcedash)
                mat = bpy.data.materials[i]
                return mat

        def modify_material(name,cr,cg,cb,cd=0,forcedash=False):
            i=(name+"_mat")
            dash=(cd>0)|forcedash
            if not dash:
                bpy.data.materials[i].diffuse_color = (float(cr), float(cg), float(cb), 1)
                bpy.data.materials[i].keyframe_insert(data_path="diffuse_color",frame=cframe)
            else:
                bpy.data.materials[i].node_tree.nodes["Principled BSDF"].inputs[0].default_value=(float(cr), float(cg), float(cb), 1)
                bpy.data.materials[i].node_tree.nodes["Principled BSDF.001"].inputs[0].default_value=(float(cr), float(cg), float(cb), 1)
                bpy.data.materials[i].node_tree.nodes["Principled BSDF"].inputs[0].keyframe_insert(data_path="default_value",frame=cframe)                    
                bpy.data.materials[i].node_tree.nodes["Principled BSDF.001"].inputs[0].keyframe_insert(data_path="default_value",frame=cframe)
                if cd>0:
                    bpy.data.materials[i].node_tree.nodes["Principled BSDF.001"].inputs[18].default_value=0
                else:
                    bpy.data.materials[i].node_tree.nodes["Principled BSDF.001"].inputs[18].default_value=1
                bpy.data.materials[i].node_tree.nodes["Math"].inputs[1].default_value=cd  
                bpy.data.materials[i].node_tree.nodes["Principled BSDF.001"].inputs[18].keyframe_insert(data_path="default_value",frame=cframe)                    
                bpy.data.materials[i].node_tree.nodes["Math"].inputs[1].keyframe_insert(data_path="default_value",frame=cframe)        
        
        
        ##functions defined
        
        #names
        vnames=vdatapath.split("_")[0].split("\\")[-1]
        enames=edatapath.split("_")[0].split("\\")[-1]        

        with open(vdatapath) as csvfile:
            rdr = csv.reader( csvfile )
            for i, row in enumerate( rdr ):
                if i == 0: 
                    #get column names
                    vcolind=[]
                    vcolind.append(row.index('name'))
                    vcolind.append(row.index('x'))
                    vcolind.append(row.index('y'))
                    vcolind.append(row.index('z'))
                    vcolind.append(row.index('colour'))
                    vcolind.append(row.index('shape'))
                    vcolind.append(row.index('size'))
                    vcolind.append(row.index('red'))
                    vcolind.append(row.index('green'))
                    vcolind.append(row.index('blue'))
                # else:
                    # vname,vx, vy, vz, vcol, vshape, vsz, vred, vgreen, vblue = [row[i] for i in vcolind]
                    # cola.append(vcol)
                    # reda.append(vred)
                    # bluea.append(vblue)
                    # greena.append(vgreen)

        # #get all edge colours            
        with open(edatapath) as csvfile:
            rdr = csv.reader( csvfile )
            for i, row in enumerate( rdr ):
                #if i == 0: continue # Skip column titles
                if i == 0: 
                    #get column names
                    ecolind=[]
                    ecolind.append(row.index('from_name'))
                    ecolind.append(row.index('to_name'))
                    ecolind.append(row.index('size'))
                    ecolind.append(row.index('colour'))
                    ecolind.append(row.index('from_x'))
                    ecolind.append(row.index('from_y'))
                    ecolind.append(row.index('from_z'))
                    ecolind.append(row.index('to_x'))
                    ecolind.append(row.index('to_y'))
                    ecolind.append(row.index('to_z')) 
                    ecolind.append(row.index('red'))
                    ecolind.append(row.index('green'))
                    ecolind.append(row.index('blue'))  
                    ecolind.append(row.index('curve'))
                    ecolind.append(row.index('forcecurve'))
                    ecolind.append(row.index('from_shorten'))
                    ecolind.append(row.index('to_shorten'))
                    ecolind.append(row.index('arrowlength'))
                    ecolind.append(row.index('arrowsize'))     
                    ecolind.append(row.index('is3d'))   
                    ecolind.append(row.index('dash'))
                    ecolind.append(row.index('isdashed'))
                    ecolind.append(row.index('name'))


        #add nodes
        if (vnames+'nodes') not in bpy.data.collections:
            nodes = bpy.data.collections.new((vnames+'nodes'))
            bpy.context.scene.collection.children.link(nodes)
        else:
            nodes=bpy.data.collections[(vnames+'nodes')]
            
        with open(vdatapath) as csvfile:
            rdr = csv.reader( csvfile )
            for i, row in enumerate( rdr ):
                if i == 0:continue 

                vname,vx, vy, vz, vcol, vshape, vsz, vred, vgreen, vblue = [row[i] for i in vcolind]
                if vname not in nodes.objects:
                    print("adding "+vname+" "+str(i))
                    if vshape in ["sphere","cube","circle","square"]:
                        
                        if vshape == "sphere":
                            bpy.ops.mesh.primitive_uv_sphere_add(location = ( float(vx), float(vy), float(vz) ))
                        elif vshape == "cube":
                            bpy.ops.mesh.primitive_cube_add(location = ( float(vx), float(vy), float(vz) ))
                        elif vshape == "circle":
                            bpy.ops.mesh.primitive_circle_add(location = ( float(vx), float(vy), float(vz) ), fill_type="TRIFAN")
                        elif vshape == "square":
                            bpy.ops.mesh.primitive_plane_add(location = ( float(vx), float(vy), float(vz) ))
                        bpy.context.object.scale=(float(vsz),float(vsz),float(vsz))
                        newmat=make_material(vname,vred,vgreen,vblue)
                        bpy.context.object.data.materials.append(newmat)
                        bpy.context.object.name=vname
                        bpy.context.object.data.name=vname
                        bpy.context.object.keyframe_insert(data_path="location", frame=cframe)
                        bpy.context.object.keyframe_insert(data_path="scale", frame=cframe)
                        nodes.objects.link(bpy.context.object)            
                    else:
                        if vshape not in bpy.data.objects: 
                            if vshape is not "none":
                                print("object not found")
                            continue

                        new_obj = bpy.data.objects[vshape].copy()
                        new_obj.data = bpy.data.objects[vshape].data.copy()
                        new_obj.name=vname
                        new_obj.data.name=vname
                        new_obj.location=( float(vx), float(vy), float(vz) )
                        new_obj.scale=(float(vsz),float(vsz),float(vsz))
                        if not new_obj.data.materials:
                            newmat=make_material(vname,vred,vgreen,vblue)
                            new_obj.data.materials.append(newmat)
                        new_obj.keyframe_insert(data_path="location", frame=cframe)
                        new_obj.keyframe_insert(data_path="scale", frame=cframe)
                        nodes.objects.link(new_obj)
                else:
                    print("add keyframe "+vname+" "+str(cframe))
                    old_obj=nodes.objects[vname]
                    old_obj.location=( float(vx), float(vy), float(vz) )
                    old_obj.scale=(float(vsz),float(vsz),float(vsz))
                    old_obj.keyframe_insert(data_path="location", frame=cframe)
                    old_obj.keyframe_insert(data_path="scale", frame=cframe)
                    modify_material(vname,vred,vgreen,vblue)
                
        
        print("add edges")


        if (enames+'edges') not in bpy.data.collections:
            edges = bpy.data.collections.new((enames+'edges'))
            bpy.context.scene.collection.children.link(edges)
        else:
            edges=bpy.data.collections[(enames+'edges')]
            
        with open(edatapath) as csvfile:
            rdr = csv.reader( csvfile )
            for i, row in enumerate( rdr ):
                #if i == 0: continue # Skip column titles
                if i == 0: continue
            
                efromname,etoname,esz, ecol,from_x, from_y, from_z, to_x, to_y, to_z, ered,egreen,eblue,ecurve,forcecurve,fromshort,toshort,arrowlength,arrowsize,edge3d,edash,forcedash,ename = [row[i] for i in ecolind] 
                forcecurve=forcecurve=='TRUE'
                forcedash=forcedash=='TRUE'
                if ename not in edges.objects:  
                    print("adding "+ename+" "+str(i)) 
                    o = add_bezier([float(from_x),float(from_y),float(from_z)],[float(to_x),float(to_y),float(to_z)],
                    ename,float(ecurve),forcecurve,toshorten=float(toshort),fromshorten=float(fromshort),arrowlength=float(arrowlength))
                                
                    o.name=ename
                    curve = o.data
                    curve.name=ename
                    
                    

                    newmat=make_material(ename,ered,egreen,eblue,float(edash),forcedash=forcedash)
                    curve.materials.append(newmat)

                    curve.dimensions = '3D'
                    curve.bevel_depth = float(esz)
                    curve.keyframe_insert(data_path="bevel_depth", frame=cframe)
                    curve.bevel_resolution = 3
                    if edge3d == 'FALSE':
                        o.scale.z=0.00001
                        curve.extrude=1
                    o.keyframe_insert(data_path="scale", frame=cframe)
                    edges.objects.link(o)
                    if float(arrowlength)>0:
                        o=add_arrowhead([float(from_x),float(from_y),float(from_z)],[float(to_x),float(to_y),float(to_z)],ecol,ename+'ah',float(toshort),float(fromshort),arrowsize=float(arrowsize),arrowlength=float(arrowlength),ecurve=float(ecurve),forcecurve=forcecurve,edge3d=edge3d)
                else:
                    print("add keyframe "+ename+" "+str(cframe))
                    #get edge
                    o = modify_bezier([float(from_x),float(from_y),float(from_z)],[float(to_x),float(to_y),float(to_z)],
                    ename,float(ecurve),forcecurve=forcecurve,toshorten=float(toshort),fromshorten=float(fromshort),arrowlength=float(arrowlength))
                    curve = o.data
                    curve.name=ename
                    curve.dimensions = '3D'
                    curve.bevel_depth = float(esz)
                    curve.keyframe_insert(data_path="bevel_depth", frame=cframe)
                    curve.bevel_resolution = 3
                    if edge3d == 'FALSE':
                        o.scale.z=0.00001
                    o.keyframe_insert(data_path="scale", frame=cframe)
                    modify_material(ename,ered,egreen,eblue,float(edash),forcedash)
                    if float(arrowlength)>0:
                        modify_material(ename+ah,ered,egreen,eblue)
                    
                    
                    


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class FolderImport(bpy.types.Operator):
    """Import network to blender"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.networkfolder"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Import folder of networks"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.  

    def execute(self, context):        # execute() is called when running the operator.
        print("import multiple networks")
        scene = context.scene
        netimp = scene.netimport
        folderpath=netimp.folderpath
        frameint=netimp.frameint
        files=os.listdir(folderpath)
        fullfiles=[folderpath+"\\"+f for f in files]
        fullfiles.sort(key=os.path.getmtime)
        edatafiles = [f for f in fullfiles if "edata" in f]
        vdatafiles = [f for f in fullfiles if "vdata" in f]
        for file in range(0,len(edatafiles)):
            print("importing network "+str(file))
            edatapath=edatafiles[file]
            vdatapath=vdatafiles[file]
            cframe=file*frameint
            bpy.context.scene.frame_set(cframe)       
            netimporter1=importnet(context,edatapath,vdatapath,cframe)
            netimporter1.do_import()
            
        print("DONE")
        return {'FINISHED'}            # Lets Blender know the operator finished successfully.    
    
class NetImport(bpy.types.Operator):
    """Import network to blender"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.network"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Import network"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.       


            
    def execute(self, context):        # execute() is called when running the operator.
        print("import single network")
        scene = context.scene
        netimp = scene.netimport
        edatapath=netimp.edatapath
        vdatapath=netimp.vdatapath
        cframe=netimp.cframe
        bpy.context.scene.frame_set(cframe)
        netimporter1=importnet(context,edatapath,vdatapath,cframe)
        netimporter1.do_import()
              
        print("DONE")
        return {'FINISHED'}            # Lets Blender know the operator finished successfully.



# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class NetImportPanel(Panel):
    bl_idname = "object.netimport_panel"
    bl_label = "Network Import"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Import Network"
    bl_context = "objectmode"   




    def draw(self, context):
        layout = self.layout
        scene = context.scene
        netimp = scene.netimport

        layout.prop(netimp, "edatapath")
        layout.prop(netimp, "vdatapath")
        layout.prop(netimp, "cframe")
        layout.separator()
        layout.operator( "object.network")
        layout.separator()
        layout.prop(netimp, "folderpath")
        layout.prop(netimp, "frameint")
        layout.operator( "object.networkfolder")

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    NetProps,
    NetImport,
    FolderImport,
    NetImportPanel
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.netimport = PointerProperty(type=NetProps)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.netimport


if __name__ == "__main__":
    register()