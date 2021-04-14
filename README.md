# net2blend

Export igraph networks from R and convert them to blender objects.

## How to use:
NOTE: Built under Blender 2.8

- Read the R function into R using source. 

- place the import_net.py file in your blender addon folder. Install using the addons menu - it'll be under the name "Import network". This will add an "import network"  category in the sidebar.

- Run the R function using an igraph object and other parameters as detailed below - this will export and edge csv and a vertex csv. 

-Then just select these files in the Blender panel and click "import network". Your network objects should appear (depending on the coordinates it might not be in view). 

-Alternatively you can point blender to a folder of networks with a set interval between them, or interval defined by the network suffix (netname2 in R).

## Changelog:

14/04/21 - Added the following features:
- When importing by folder, you can now sort networks by their suffix (netname2 in R). By default Blender will sort networks by their date created.
- When importing by folder, you can now import networks at frames based on their suffix (netname2 in R), rather than at set intervals.

19/11/20 - Fixed bug that would prevent import. Thanks to andyrevell for spotting this!

17/07/20 - Added the following features:
- Changed the position of interface in Blender. Import network now has its own tab instead of being hidden in "tools".
- Added the ability to import entire folders of networks at set frame intervals.
- Added ability to animate line dashes. Still only visible in cycles renderer unfortunatley.
- Added ability to animate whether an edge is curved or not
- Completely changed how dashed edges work. Previously the material would completely break when an edge was at a certain angle.
- Exposed arguments for how much to offset 2d edges.
- Quite a few bugfixes.

26/06/20 - Added the following features:

- Networks can now be animated! Simply set the frame option to wherever you want the keyframe to be added. If the objects exist already they will be modified with the new values. Size, position and colour of edges can have keyframes associated with them in blender. This has neccesitated the changing of a few things:
- Size of nodes is now in relation to the initial size of blender primities (2m) rather than absolute units. This is to ensure consistency when modifying a nodes size.
- Unfortunatley the previous code where a material was created per colour has had to be retired. Each object now has its own material so that this material can be animated.
- There is now an additional suffix option in the R script (netname2). Blender will ignore this additional name. This means that R will export files as follows "netname_ename_netname2.csv". This allows a user to export different versions of the same network for animation.
- There is now a "directed" argument due to the new way in which the script will attempt to create consistent edge names. In the future I'll modify this to check the igraph object instead. I have not tested animations thorougly with arrows and directed networks yet.
- Added a few utility functions to aid in the setting up of networks for animations, namely to fill a network with the empty edges that might not exist in a particular version of that network, but still need a keyframe.

26/08/19 - Added the following features:

- Edges can now be dashed lines. Giving the edge.dash argument a value will make that edge dashed. Note that at the moment edges will only be dashed in the Cycles renderer.
- Edge and node collections now named based on the filename for easier organisation.
- Flat square node size multiplied by 2 for better parity with circular nodes.
- 2d edges offset slightly below nodes to avoid clipping.
- 2d edges offset slightly in the order of edge plotting, so that as with igraph the last edges in the graph will be on top.
- Added a maxlength argument - can be used to control the amount of curve which is usually based on the longest edge on the network. This could lead to networks with fewer or more edges having slightly different curves to each other. The findmaxlength function can be used to obtain this value from one particular network/layout combination. This value can then be used to force other networks to use the same cuves.

## Detailed instructions:

### R

# net2blend
Arguments are similar to igraph.plot:

- net = Igraph network object
- layout = Layout matrix where first column is x coordinates and second column is y coordinates. Z coordinates can also be provided
- vertex.color = Vertex colour as hex or colour name. Default is red.
- edge.color = Edge colour as hex or colour name. Default is black.
- vertex.shape = Name of vertex shape. Can be "sphere","cube","circle","square" or "none". Can also be the name of an object in the blender scene. Default is sphere.
- vertex.size = Size of vertex. Default is 0.2
- edge.size = Edge size. Default is 0.1.
- edge.3d = Edges is a 3d object. If FALSE will flatten this edge. Default is 3d.
- edge.curve = Boolean:Should an edge be curved (defaults to 0.2) or numeric: Amount to curve edges. If a single value, this will be scaled by the length of the edges in the plot. Default is 0.
- edge.forcecurve= Boolean. If TRUE an edge will be set up so as to be curved in blender, even if edge.curve=0.
- vertex.intersect = Boolean. If TRUE edges will meet in the center of the vertex. If FALSE edges will be shortened by size of vertex. Default is TRUE
- vertex.edgeshorten = If provided, edges will be shortened by this value instead of the size of the vertex. Default is 0.
- edge.arrows= Boolean. If TRUE, plot arrowheads at the end of edges. Default is FALSE
- edge.arrowsize = Thickness of arrows. If edge.arrows is TRUE and no value is provided, is based on edge.size
- edge.arrowlength = Length of arrows. If edge.arrows is TRUE and no value is provided, this defaults to 0.2
- edge.dash = Size of dashed edges. Larger values result in a greater number of short dashes. Defaults to 0, no dash.
- edge.isdashed = Boolean. Should an edge be set up to be dashed even if the value of edge.dash is 0.
- zoffset1 = minimum amount to offset 2d edges below z coordinate to avoid clipping. Defaults to 0.01.
- zoffset2 = maximum amount to offset 2d edges below z coordinate to avoid clipping. Defaults to 0.05.
- directed = Boolean. Should be true for a directed network. In future this should be obtained from the net argument.
- outputdir = File path for export. Default is working directory
- netname = name to append as prefix to files. Format is netname_edata_netname2.csv or netname_vdata_netname2.csv
- netname2 = name to append as suffix to files. Format is netname_edata_netname2.csv or netname_vdata_netname2.csv. This is primarily for creating multiple versions of the same network for animation. If this is a number, this can be used to set the frame number in Blender.

# findmaxlength
Returns the maximum length of edge in a particular network/layout combo. This is used to keep curves consistent, as curve amount is based on the maximum edge length.
- net = Igraph network object
- layout = Layout matrix where first column is x coordinates and second column is y coordinates. Z coordinates can also be provided

# find_all_edges
Returns all edges in a list of networks as a matrix. These can then be added to all networks for consistency while animating using add_missing_edges
- allnets = list of Igraph network objects
- directed = Are these networks directed? False by default

# add_missing_edges
Adds edges to a network, if they are not present already and fill with an attribute. For example, edges not existing in certain versions of the network nethertheless need to be present in every version while animating in blender, and are assigned a size of 0 when not technically present.
- net = Igraph network object to which edges will be added
- alledges=Matrix of edges to be added (as generated by find_all_edges). If NULL (default) this will be all possible combinations of dyads. This can cause performance issues in blender for large networks!
- directed=Are the edges added directional? False by default
- selfloop=Are self loops to be added (if generating all possible combinations of edges). False by default.
- attrlist=List of attributes to be added to the new edges. For example, list(weight=0) for edges not technically present in a version of a network. Empty list by default.

# find_all_nodes
Returns all nodes in a list of networks as a matrix. These can then be added to all networks for consistency while animating using add_missing_nodes
- allnets =list of Igraph network objects

# add_missing_nodes
Add nodes to the network, if they are not present already, and fill with an attribute. For example, nodes not existing in certain versions of the network nethertheless need to be present in every version while animating in blender, and are assigned a size of 0 when not technically present.
- net = Igraph network object to which nodes will be added
- allnodes = vector of nodes (names or indices) to be added to the network
- attrlist= List of attributes to be assigned to the added nodes. Empty list by default.


### Blender
- You can either import networks one at a time or by folder.
- If importing single networks you will need to point Blender at the nodes and the edges folder and define a frame if you want to create an animation.
- If importing by folder, you will need to point Blender to the folder. You can then either add the networks at set frame intervals or based on their suffix. 
- The script creates two collections for convenience - nodes and edges, named based on the filenames If these collections already exist they will not be created again. 
- Nodes and edges will be created, each with a unique name. If these objects already exist in that collection they will be changed or have a keyframe added.
- As mentioned above, nodes can either be primitive spheres, cubes, circles or planes. Using a custom object is easy, just set the vertex.shape in R as the name of that object in Blender. If the object doesn't have materials, it'll be given the colour assigned in R, otherwise the existing materials are kept.
- If you run the script multiple times, make sure you purge orphaned data regularly as the curves used to generate edges will still be in the blender file otherwise, even if new edges have been generated.
