net2blend introduction
================
Julian Evans
30/11/21

-   [Initial set up](#initial-set-up)
-   [Basic network export](#basic-network-export)
-   [Animating networks](#animating-networks)
    -   [Simple example](#simple-example)

# Initial set up

### R

We can then load the library. We’ll also load igraph to build our
networks.

``` r
library(igraph)
library(net2blendR)
```

# Basic network export

### R

Here we’ll walk through the most basic export possible.

For this example, we’ll load an artificial network provided with the
package.

``` r
data(examplenet1)
summary(examplenet1)
#> IGRAPH 9632bf4 UN-- 13 21 -- 
#> + attr: name (v/c)
```

This is a simple randomly generated graph. Currently the only attribute
is a name attribute for each vertex. We can now generate a simple circle
layout for this graph.

``` r
l1=as.data.frame(layout_in_circle(examplenet1))
row.names(l1)=V(examplenet1)$name
head(l1)
#>           V1        V2
#> E  1.0000000 0.0000000
#> L  0.8854560 0.4647232
#> M  0.5680647 0.8229839
#> F  0.1205367 0.9927089
#> X -0.3546049 0.9350162
#> N -0.7485107 0.6631227
```

Note that these coordinates are all between -1 and 1. When imported into
Blender these coordinates will be in the scene units, meters by default.
We’ll multiply by 10 to avoid our network being too squashed.

``` r
l1=l1*10
```

We can then export this network using the graph, layout and the default
settings of net2blend. We set the name of the network to be examplenet.

``` r
net2blend(examplenet1,l1,netname="examplenet")
```

This will generate two files. One contains vertex data
“examplenet\_vdata\_0\_.csv” the other edge data
“examplenet\_edata\_0\_.csv”.

### Blender

Open Blender and create a new general scene. Delete the default cube. If
you have installed the net2blend add-on correctly you should find the
“Import network” tab in the side bar (if this is hidden, click the
circled arrow).

<img src="net2blend/net2blendR/vignettes/blender1.jpg" title="Empty scene" alt="Empty scene" width="100%" />

We’ll use the “import single network” tool to import the network. Set
the edge and vertex files and click the import network button. The
network will be imported.

![Import network](blender2.jpg)

You’ll see that 2 collections have been added to the scene.
“examplenetnodes” (yes I’m sorry, I have been inconsistent in my use of
vertices/nodes) and “examplenetedges”. The vertices and edges are found
within these collections.

![Network objects](blender3.jpg)

You now have a network as a 3d object in Blender, ready to render!

# Animating networks

We’ll now look at how we can animate these networks in Blender. When you
import a network a [keyframe](https://en.wikipedia.org/wiki/Key_frame)
is automatically added for every vertex and edge. Blender will
interpolate between two keyframes, creating a smooth transition. When we
imported our network in the previous example, the “Frame” argument was
set to 0, meaning keyframes were added at frame 0. If we import another
network with the same edges/vertices

We’ll first add simple animation to the existing network and then look
at how to set up networks to animate edges/vertices appearing and
disappearing.

## Simple example

In this example we’ll add some simple changes to the network in our next
keyframe. We’ll keep the network the same, but change the export
settings.

### R

First we’ll generate a new layout. Once again we multiply everything by
10 to put it on a better scale in blender. Since we are working in 3d
space, lets also move the network up by 10 meters.

``` r
l2=as.data.frame(layout_in_circle(examplenet1))
row.names(l2)=V(examplenet1)$name
l2=l2*10
l2$Z = 10 #adding a Z column
```

we’ll export the network with the new layout and different colour vertex
and edges. Importantly, we keep the same network name “examplenet”. This
means that when we import these files, they will edit the existing
networks, either overwriting existing keyframes (if imported at frame 0)
or adding new keyframes (if added at any other frame). We give it a
different netname2, meaning the filenames will have a different suffix
to distinguish it. The filenames will be “examplenet\_vdata\_2\_.csv”
and “examplenet\_edata\_2\_.csv”.

``` r
net2blend(examplenet1,l2,netname="examplenet",netname2=2,edge.color = "red",vertex.color = "blue")
```

### Blender

In blender, change the edge and vertex data paths to the new files. Set
the frame to 30 and click import.

![New keyframe](blender4.jpg)

If the network seems to disappear, it is because your current viewpoint
isn’t pulled back enough to see the network’s new Z position. The
current frame on the timeline will be set to 30, where a new keyframe
has been added for every node and edge. You can slide the timeline back
and forth and see the network move and change colour.

![Animated network](blendergif1.gif) \#\# Animating networks of changing
size

### R
