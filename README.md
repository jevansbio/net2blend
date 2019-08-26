# net2blend

Export igraph networks from R and convert them to blender objects.

## How to use:
NOTE: Built under Blender 2.8

- Read the R function into R using source. 

- place the import_net.py file in your blender addon folder. Install using the addons menu - it'll be under the name "Import network". This will add an "import network" panel under the "tools" category in the sidebar.

- Run the R function - this will export and edge csv and a vertex csv. Then just select these files in the Blender panel and click "import network". Your network objects should appear (depending on the coordinates it might not be in view).

## Changelog:
26/08/19 - Added the following features:

- Edges can now be dashed lines. Giving the edge.dash argument a value will make that edge dashed. Note that at the moment edges will only be dashed in the Cycles renderer.
- Edge and node collections now named based on the filename for easier organisation.
- Flat square node size multiplied by 2 for better parity with circular nodes.
- 2d edges offset slightly below nodes to avoid clipping.
- 2d edges offset slightly in the order of edge plotting, as that as with igraph the last edges in the graph will be on top.
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
- edge.size = Edge size. Default is 1.
- edge.3d = Edges is a 3d object. If FALSE will flatten this edge. Default is 3d.
- edge.curve = Amount to curve edges. If a single value, this will be scaled by the length of the edges in the plot. Default is 0
- vertex.intersect = Boolean. If TRUE edges will meet in the center of the vertex. If FALSE edges will be shortened by size of vertex. Default is TRUE
- vertex.edgeshorten = If provided, edges will be shortened by this value instead of the size of the vertex. Default is 0.
- edge.arrows= Boolean. If TRUE, plot arrowheads at the end of edges. Default is FALSE
- edge.arrowsize = Thickness of arrows. If edge.arrows is TRUE and no value is provided, is based on edge.size
- edge.arrowlength = Length of arrows. If edge.arrows is TRUE and no value is provided, this defaults to 0.2
- edge.dash = Size of dashed edges. Larger values result in a greater number of short dashes. Defaults to 0, no dash.
- outputdir = File path for export. Default is working directory
- netname = name to append as prefix to files. Format is netname_edata.csv or netname_vdata.csv

# findmaxlength
Returns the maximum length of edge in a particular network/layout combo.
- net = Igraph network object
- layout = Layout matrix where first column is x coordinates and second column is y coordinates. Z coordinates can also be provided

### Blender

- The script creates two collections for convenience - nodes and edges, named based on the filenames If these collections already exist they will not be created again.
- The script then checks for all the colours used in the network and creates materials for them. If these materials already exist they will not be created again. This process is repeated for any dashed edges.
- Nodes and edges will be created, each with a unique name. Once again, if these objects already exist in that collection they will not be created again.
- As mentioned above, nodes can either be primitive spheres, cubes, circles or planes. Using a custom object is easy, just set the vertex.shape in R as the name of that object in Blender. If the object doesn't have materials, it'll be given the colour assigned in R, otherwise the existing materials are kept.
- If you run the script multiple times, make sure you purge orphaned data regularly as the curves used to generate edges will still be in the blender file otherwise, even if new edges have been generated.
