## Changelog:

20/04/21 - Altered code so that added nodes/edges are no longer linked to the scene master collection as well as the network collection.

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
