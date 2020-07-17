#This is an example animating nodes moving, appearing/disappearing and changing colour

#load requirements
library(igraph)
source("net2blend.R")

#generate a random network of 13 nodes
g1=erdos.renyi.game(13,0.25)
#as this method does not give nodes names, assign them randomly from the alphabet
V(g1)$name=sample(LETTERS,length(V(g1)))
#give all these nodes an attribute that they were present
V(g1)$present=T
#give edges a weight attribute
E(g1)$weight=1

#generate a second network of 26 nodes
g2=erdos.renyi.game(26,0.1)
#as this method does not give nodes names, assign them randomly from the alphabet
V(g2)$name=sample(LETTERS,length(V(g2)))
#give all these nodes an attribute that they were present
V(g2)$present=T
#give edges a weight attribute
E(g2)$weight=1

#find all nodes
allnodes=find_all_nodes(list(g1,g2))

#find all edges
alledges=find_all_edges(list(g1,g2))

#add nodes to g1 with present attribute set to false
g1=add_missing_nodes(g1,allnodes=allnodes,attrlist=list(present=F))

#If we had nodes disappearing in g2, can run the same line
g2=add_missing_nodes(g2,allnodes=allnodes,attrlist=list(present=F))

#add missing edges to g1 and g2 with a weight of 0
g1=add_missing_edges(g1,alledges=alledges,attrlist=list(weight=0))
g2=add_missing_edges(g2,alledges=alledges,attrlist=list(weight=0))

#For convenience (not required though) can also match the order of nodes
g1=permute(g1,match(V(g1)$name,sort(V(g1)$name)))
g2=permute(g1,match(V(g2)$name,sort(V(g2)$name)))

#generate edge names for convenience - makes it easier to find the same edges in different graphs
E(g1)$name=get_edge_names(g1)
E(g2)$name=get_edge_names(g2)

#generate a layout for both networks to use. 
#This will be identical, but we'll add a change in z coordinate in the second frame
l1=as.data.frame(layout_in_circle(g1))
row.names(l1)=V(g2)$name
#add a z coordinate
l1$z=0
#make a copy
l2=l1
#add z components 
l2$z[row.names(l2)%in%V(g1)[present]$name]=-0.5
l2$z[!row.names(l2)%in%V(g1)[present]$name]=0.5

#export g1
net2blend(g1,layout=l1[match(V(g1)$name,row.names(l1)),],
vertex.color="red",
edge.color="black",
edge.size=0.01*E(g1)$weight,#edges of weight 0 will be invisible
edge.dash=0,#no dashes
edge.isdashed=T,#but force the edge to prepare to be dashed
edge.curve=T,
edge.forcecurve=T,
vertex.size=0.05*V(g1)$present,#non present nodes will be invisible
netname="example1",
netname2=1)

#for this example, edges that are present in g1 will become blue in g2 while edges that are disappearing will become red
edgecol=rep("black",length(E(g2)))
edgecol[E(g2)$weight==0]="red"
edgecol[E(g2)$name%in%E(g1)[weight>0]$name&E(g2)$weight>0]="blue"

#similarly new nodes will be green while old nodes will become blue.
nodecol=rep("green",length(V(g2)))
nodecol[V(g2)$name%in%V(g1)[present]$name]="blue"

#export g2
net2blend(g2,layout=l2[match(V(g2)$name,row.names(l2)),],
vertex.color=nodecol,
edge.color=edgecol,
edge.size=0.01*E(g2)$weight,#edges of weight 0 will be invisible
edge.dash=5,#dash size
edge.isdashed=T,
edge.curve=F,
edge.forcecurve=T,
vertex.size=0.05*V(g2)$present,#non present nodes will be invisible
netname="example1",
netname2=2)#note that netname 2 is different

#Go to blender and import the 2 networks on different frames.








