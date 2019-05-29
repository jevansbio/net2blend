bl_info = {
    "name": "Network to blender",
    "description": "Script to plot networks in Blender",
    "author": "Julian Evans",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}


import bpy
from mathutils import Vector
import csv

from bpy.props import (StringProperty,
                       PointerProperty,
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

   

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class NetImport(bpy.types.Operator):
    """Import network to blender"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.network"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Import network"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.


    
    def execute(self, context):        # execute() is called when running the operator.
        scene = context.scene
        netimp = scene.netimport
        edatapath=netimp.edatapath
        vdatapath=netimp.vdatapath
        def add_arrowhead(v0, v1, ecol,edgename='edge',toshorten=0,fromshorten=0,arrowlength=0,arrowsize=0,ecurve=0,edge3d=True):
            curved=ecurve>0
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
            
            bpy.ops.mesh.primitive_cone_add(depth=arrowlength,radius1=arrowsize,radius2=0,end_fill_type='TRIFAN')    
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            bpy.context.object.location=v1
            if edge3d == 'FALSE':
                bpy.context.object.scale.x=0.00001
            bpy.context.object.rotation_mode = 'QUATERNION'
            bpy.context.object.rotation_quaternion = avec.to_track_quat('Z', 'X')
            bpy.context.object.data.materials.append(bpy.data.materials[ecol])
            bpy.context.object.name=edgename+'ah'
            bpy.context.object.data.name=edgename+'ah'
            edges.objects.link(bpy.context.object)  
    
        def add_bezier(v0 , v1,edgename='edge',ecurve=0,toshorten=0,fromshorten=0,arrowlength=0):
            curved=ecurve>0
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
                vsize=[abs(i) for i in list(v1-v0)]
                res = len(vsize) - 1 - vsize[::-1].index(min(vsize))        
                curvev=[0,0,0]
                curvev[res]=1
                curvev=Vector(curvev)        
                
                dir = v1-v0
                dir2 = dir.cross(curvev)
                dir2.normalize()
                v2=o+(dir2*ecurve )
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
            
            ob = bpy.data.objects.new(edgename, curve)
            ob.matrix_world.translation = o
            return ob



        #get materials and column indexes

        cola=[]
        reda=[]
        bluea=[]
        greena=[]

        #get all vertex colours
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
                else:
                    vname,vx, vy, vz, vcol, vshape, vsz, vred, vgreen, vblue = [row[i] for i in vcolind]
                    cola.append(vcol)
                    reda.append(vred)
                    bluea.append(vblue)
                    greena.append(vgreen)

        #get all edge colours            
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
                    ecolind.append(row.index('from_shorten'))
                    ecolind.append(row.index('to_shorten'))
                    ecolind.append(row.index('arrowlength'))
                    ecolind.append(row.index('arrowsize'))     
                    ecolind.append(row.index('is3d'))              
                else:
                    efromname,etoname,esz, ecol,from_x, from_y, from_z, to_x, to_y, to_z, ered,egreen,eblue,curve,fromshort,toshort,arrowlength,arrowsize,edge3d = [row[i] for i in ecolind]               
                    cola.append(ecol)
                    reda.append(ered)
                    bluea.append(eblue)
                    greena.append(egreen)
        #get unique colour names
        cola2=set(cola)
        #create a mat for each
        for i in cola2:
            #get first occurence index
            colind=cola.index(i)
            #get RGB
            cr=reda[colind]
            cg=greena[colind]
            cb=bluea[colind]

            #make material
            if i not in bpy.data.materials:
                mat = bpy.data.materials.new(name=i)
                mat.diffuse_color = (float(cr), float(cg), float(cb), 1)


        #add nodes
        if 'nodes' not in bpy.data.collections:
            nodes = bpy.data.collections.new('nodes')
            bpy.context.scene.collection.children.link(nodes)
        else:
            nodes=bpy.data.collections['nodes']
            
        with open(vdatapath) as csvfile:
            rdr = csv.reader( csvfile )
            for i, row in enumerate( rdr ):
                if i == 0:continue 

                vname,vx, vy, vz, vcol, vshape, vsz, vred, vgreen, vblue = [row[i] for i in vcolind]
                if vname not in nodes.objects:
                    if vshape in ["sphere","cube","circle","square"]:
                        
                        if vshape == "sphere":
                            bpy.ops.mesh.primitive_uv_sphere_add(location = ( float(vx), float(vy), float(vz) ), radius = float(vsz))
                        elif vshape == "cube":
                            bpy.ops.mesh.primitive_cube_add(location = ( float(vx), float(vy), float(vz) ), size = float(vsz))
                        elif vshape == "circle":
                            bpy.ops.mesh.primitive_circle_add(location = ( float(vx), float(vy), float(vz) ), radius = float(vsz), fill_type="TRIFAN")
                        elif vshape == "square":
                            bpy.ops.mesh.primitive_plane_add(location = ( float(vx), float(vy), float(vz) ), size = float(vsz))
                        bpy.context.object.data.materials.append(bpy.data.materials[vcol])
                        bpy.context.object.name=vname
                        bpy.context.object.data.name=vname
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
                            new_obj.data.materials.append(bpy.data.materials[vcol])
                        nodes.objects.link(new_obj)  
        
        #add edges


        if 'edges' not in bpy.data.collections:
            edges = bpy.data.collections.new('edges')
            bpy.context.scene.collection.children.link(edges)
        else:
            edges=bpy.data.collections['edges']
            
        with open(edatapath) as csvfile:
            rdr = csv.reader( csvfile )
            for i, row in enumerate( rdr ):
                #if i == 0: continue # Skip column titles
                if i == 0: continue
            
                efromname,etoname,esz, ecol,from_x, from_y, from_z, to_x, to_y, to_z, ered,egreen,eblue,ecurve,fromshort,toshort,arrowlength,arrowsize,edge3d = [row[i] for i in ecolind] 
                ename=efromname+"_"+etoname     
                if ename not in edges.objects:   
                    o = add_bezier([float(from_x),float(from_y),float(from_z)],[float(to_x),float(to_y),float(to_z)],
                    ename,float(ecurve),toshorten=float(toshort),fromshorten=float(fromshort),arrowlength=float(arrowlength))
                                
                    o.name=ename
                    curve = o.data
                    curve.name=ename   
                    curve.materials.append(bpy.data.materials[ecol])
                    curve.dimensions = '3D'
                    curve.bevel_depth = float(esz)
                    curve.bevel_resolution = 3
                    if edge3d == 'FALSE':
                        o.scale.z=0.00001
                    edges.objects.link(o)
                    if float(arrowlength)>0:
                        o=add_arrowhead([float(from_x),float(from_y),float(from_z)],[float(to_x),float(to_y),float(to_z)],ecol,ename+'ah',float(toshort),float(fromshort),arrowsize=float(arrowsize),arrowlength=float(arrowlength),ecurve=float(ecurve),edge3d=edge3d)
        return {'FINISHED'}            # Lets Blender know the operator finished successfully.



# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class NetImportPanel(Panel):
    bl_idname = "object.netimport_panel"
    bl_label = "Network Import"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_context = "objectmode"   




    def draw(self, context):
        layout = self.layout
        scene = context.scene
        netimp = scene.netimport

        layout.prop(netimp, "edatapath")
        layout.prop(netimp, "vdatapath")
        layout.separator()
        layout.operator( "object.network")
        

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    NetProps,
    NetImport,
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