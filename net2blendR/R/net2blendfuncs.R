#' Export network files
#'
#' \code{net2blend} Exports networks in a format for importing into blender
#'
#' @param net igraph network object
#' @param layout Matrix or dataframe of the same number of rows as vertices
#'     in the networks, where first column is vertex x coordinates
#'     and second column is vertex y coordinates. Z coordinates can also be
#'     provided.
#' @param vertex.color Vertex colour as hex or colour name.
#'     Can be single value or vector the same length as the number of vertices
#'     in the network. of Default is "red"
#' @param edge.color Edge colour as hex or colour name. Can be a single value or
#'     a vector of the same length as the number of edges in the network.
#'     Default is "black"
#' @param vertex.shape Name of vertex shape.  Can be single value or vector of
#'     the same length as the number of vertices in the network.
#'     Can be "sphere","cube","circle", "square" or "none".
#'     Alternative, this can be the name of an object in the blender scene.
#'     This object will be duplicated and rescaled as necessary. If the
#'     object has no materials assigned, the object will also be recoloured.
#'     Default is "sphere".
#' @param vertex.size Size of vertex object. Can be single value or vector of
#'     the same length as the number of vertices in the network. Defaults to 0.2.
#' @param edge.size Size of edge. Can be a single value or a vector the same
#'     length as the number of edges in the network. Default is 0.1
#' @param edge.3d Boolean determining if edges will be 3d in blender.
#'     If FALSE will flatten this edge. Can be a single value or a vector the
#'     same length as the number of edges in the network. Default is TRUE.
#' @param edge.curve Amount to curve edges. Can be a single value or a vector of
#'      the same length as the number of edges in the network.
#'      If a single value >0, the amount each edge curves will be scaled by the
#'      length of the longest edge in the layout OR by \code{maxlength} if provided.
#' @param maxlength If provided, a single value to scale \code{edge.curve} by.
#'      Default is NA, meaning the length of the longest edge of the layout is used.
#' @param edge.forcecurve Boolean determining if edges will be forced to be
#'      created as curves in blender, even if the edge is straight
#'      (\code{edge.curve == 0}). Can be a single value or a vector of
#'      the same length as the number of edges in the network. Defaults to FALSE.
#' @param vertex.intersect Boolean. If TRUE edges will meet in the center of
#'     the vertex. If FALSE edges will be shortened by size of vertex or by
#'     \code{vertex.edgeshorten}. Can be a single value or a vector of
#'      the same length as the number of vertices in the network.
#'      Default is TRUE.
#' @param vertex.edgeshorten If provided, edges will be shortened by this value
#'     instead of the size of the vertex. Can be a single value or a vector of
#'      the same length as the number of edges in the network. Default is 0.
#' @param edge.arrows Boolean. If TRUE, arrowheads are added at the end of
#'     edges. Can be a single value or a vector of the same length as the number
#'     of edges in the network. Default is FALSE.
#' @param edge.arrowsize Thickness of arrowheads. Can be a single value or a vector of
#'      the same length as the number of edges in the network.
#'      If \code{edge.arrows} is TRUE and no value is provided, defaults to
#'       \code{edge.size + 0.05}.
#' @param edge.arrowlength Length of arrowheads. Can be a single value or a vector of
#'      the same length as the number of edges in the network.
#'      If \code{edge.arrows} is TRUE and no value is provided, this defaults
#'      to 0.2.
#' @param edge.dash Size of dashed edges. Can be a single value or a vector of
#'      the same length as the number of edges in the network.
#'      Larger values result in a greater number of short dashes. Defaults to 0.
#' @param edge.isdashed Boolean determining if edges will be forced to be set up
#'     in Blender to allow dashed edges, even if \code{edge.dash == 0}
#' @param zoffset1 Minimum amount to offset 2d edges (\code{edge.3d == FALSE})
#'     below the Z axis by. Default is 0.01.
#' @param zoffset2 Maximum amount to offset 2d edges (\code{edge.3d == FALSE})
#'     below the Z axis by. Default is 0.05.
#' @param outputdir Directory in which to export the networks. Defaults to NA,
#'     the working directory.
#' @param netname Network prefix name. Will be used as the network name in
#'     Blender. Default is "net"
#' @param netname2 Network suffix name. Can be used as frame number by blender.
#'     Default is 0.
#' @return Exports two files, one for edges (edata) and one for vertices (vdata).
#'     Files are named in the format netname_filetype_netname2.csv. See vignette
#'     for full R to Blender workflow and examples.
#'
#' @examples
#' data(examplenet1)
#' l1=layout_nicely(examplenet1)
#' l1=l1*10
#' net2blend(examplenet1,l1,netname="examplenet")
#' @export
net2blend=function(net,layout,vertex.color="red",edge.color="black",
                   vertex.shape="sphere",	vertex.size=0.2,edge.size=0.1,
                   edge.3d=T,edge.curve=0,edge.forcecurve=F,maxlength=NA,
                   vertex.intersect=T,vertex.edgeshorten=0,edge.arrows=F,
                   edge.arrowsize=0, edge.arrowlength=0,edge.dash=0,
                   edge.isdashed=F,zoffset1=0.01,zoffset2=0.05,	outputdir=NA,
                   netname="net",netname2=0){
	directed=igraph::is.directed(net)

	if(is.na(outputdir)){
		outputdir=getwd()
	}
	if(all(edge.arrows)&all(edge.arrowsize==0)){
		edge.arrowsize=edge.size+0.05
	}
	if(all(edge.arrows)&all(edge.arrowlength==0)){
		edge.arrowlength=0.2
	}

	if((!vertex.intersect&vertex.edgeshorten==0)){
		vertex.edgeshorten=vertex.size-0.05
	}

	if(edge.arrows){
	  vertex.edgeshorten=vertex.edgeshorten+edge.arrowlength
	}

	colnames(layout)=c("x","y","z")[1:ncol(layout)]
	layout=as.data.frame(layout)
	if(!"z" %in% names(layout)){
		layout$z=0
	}
	igraph::V(net)$x=layout$x
	igraph::V(net)$y=layout$y
	igraph::V(net)$z=layout$z

	if(any(edge.curve%in%c(T,F))){
		edge.curve2=edge.curve
		edge.curve=rep(0,length(edge.curve))
		edge.curve[edge.curve2]=0.2
	}

	edge.dash2=edge.dash
	if(any(edge.dash>0)|edge.isdashed){
		edata=igraph::as_long_data_frame(net)

		if(length(edge.dash2)<nrow(edata)){
			edge.dash2=rep(edge.dash2,nrow(edata))
		}
		lengths=sqrt((edata$to_x-edata$from_x)^2+(edata$to_y-edata$from_y)^2+(edata$to_z-edata$from_z)^2)
		edge.dash2[edge.dash>0]=edge.dash2[edge.dash>0]*lengths[edge.dash>0]
	}

	if(length(edge.curve)==1){
		#if only one curve value is supplied, scale by edge length
		edata=igraph::as_long_data_frame(net)
		lengths=sqrt((edata$to_x-edata$from_x)^2+(edata$to_y-edata$from_y)^2+(edata$to_z-edata$from_z)^2)
		if(is.na(maxlength)){
			maxlength=max(lengths)
		}
		edge.curve=edge.curve*(lengths/maxlength)
	}

	igraph::V(net)$colour=vertex.color
	igraph::E(net)$colour=edge.color

	igraph::V(net)$shape=vertex.shape
	igraph::V(net)$size=vertex.size
	igraph::V(net)$size[igraph::V(net)$shape=="square"]=igraph::V(net)$size[igraph::V(net)$shape=="square"]*2
	igraph::V(net)$shorten=vertex.edgeshorten


	igraph::E(net)$size=edge.size
	igraph::E(net)$curve=edge.curve
	igraph::E(net)$forcecurve=edge.forcecurve
	igraph::E(net)$is3d=edge.3d
	igraph::E(net)$arrowsize=edge.arrowsize
	igraph::E(net)$arrowlength=edge.arrowlength
	igraph::E(net)$dash=edge.dash2
	igraph::E(net)$isdashed=edge.isdashed

	#It is important to permute the nodes to the same order, otherwise the from and to of edges can change, leading to your edges flipping
	net=permute(net,match(igraph::V(net)$name,sort(igraph::V(net)$name)))

	edata=igraph::as_long_data_frame(net)
	if(nrow(edata>0)){
  	if(any(!edata$is3d)){
  		highz=max(c(edata$to_z[!edata$is3d],edata$from_z[!edata$is3d]))-zoffset1
  		lowz=max(c(edata$to_z[!edata$is3d],edata$from_z[!edata$is3d]))-zoffset2

  		edata$to_z[!edata$is3d]=seq(lowz,highz,length.out=sum(!edata$is3d))
  		edata$from_z[!edata$is3d]=seq(lowz,highz,length.out=sum(!edata$is3d))
  	}

  	edata=data.frame(edata,t(grDevices::col2rgb(edata$colour)/255))

  	edata$name=sapply(1:nrow(edata),function(x){
  		cnodes=c(edata$from_name[x],edata$to_name[x])
  		if(!directed){
  			cnodes=cnodes[order(cnodes)]
  		}
  		paste(cnodes,collapse="_")
  	})
  	write.csv(edata,file.path(outputdir,paste(netname,"edata",netname2,".csv",sep="_")),row.names=F)
  }

	vdata=igraph::as_data_frame(net,what = 'vertices')
	vdata=data.frame(vdata,t(grDevices::col2rgb(vdata$colour)/255))
	write.csv(vdata,file.path(outputdir,paste(netname,"vdata",netname2,".csv",sep="_")),row.names=F)

}


#' Find longest edge in a layout
#'
#' \code{findmaxlength} Calculate longest edge in a given layout
#'
#' @param net igraph network object
#' @param layout Matrix or dataframe of the same number of rows as vertices
#'     in the networks, where first column is vertex x coordinates
#'     and second column is vertex y coordinates. Z coordinates can also be
#'     provided.
#' @return Returns the length of the longest edge in a given layout. This can
#'     then be used as the \code{maxlength} argument in \code{net2blend} to keep
#'     curved edges consistent over multiple networks.
#'
#' @examples
#' data(examplenet1)
#' l1=layout_nicely(examplenet1)
#' l1=l1*10
#' findmaxlength(examplenet1,l1)
#' @export
findmaxlength=function(net,layout){

	colnames(layout)=c("x","y","z")[1:ncol(layout)]
	layout=as.data.frame(layout)
	if(!"z" %in% names(layout)){
		layout$z=0
	}
	V(net)$x=layout$x
	V(net)$y=layout$y
	V(net)$z=layout$z
	edata=igraph::as_long_data_frame(net)
	lengths=sqrt((edata$to_x-edata$from_x)^2+(edata$to_y-edata$from_y)^2+(edata$to_z-edata$from_z)^2)
	return(max(lengths))
}

#' Find all possible edges in a list of networks
#'
#' \code{find_all_edges} Find all edges that exist in a list of networks.
#'
#' @param allnets list of igraph network objects
#' @return Returns a dataframe of all edges that exist within \code{allnets}.
#'     This can be used as an argument in \code{add_missing_edges} to ensure
#'     that all edges are correctly generated for animation in Blender.
#'
#' @examples
#' data(examplenet1)
#' data(examplenet2)
#' netlist=list(examplenet1,examplnet2)
#' find_all_edges(netlist)
#' @export
find_all_edges=function(allnets){
  directed=any(sapply(allnets,igraph::is.directed))
	alledges1=sapply(1:length(allnets),function(i){

		allnet=allnets[[i]]
		edges=igraph::as_edgelist(allnet)

		return(edges)
	})
	alledges1=do.call(rbind,alledges1)
	if(!directed){
		alledges1=t(sapply(1:nrow(alledges1),function(x){alledges1[x,order(alledges1[x,])]}))
	}
	alledges2=sapply(1:nrow(alledges1),function(x){paste(alledges1[x,],collapse="_")})
	alledges3=alledges1[!duplicated(alledges2),]
	return(alledges3)
}

#' Add missing edges to a network.
#'
#' \code{add_missing_edges} Add edges to a network to ensure consistency.
#'
#' @param net igraph network object
#' @param alledges Dataframe of edges as generated by \code{find_all_edges}
#' @param attrlist list of attributes to be given to the new edges, where the name
#'     of each list item is the name of an edge attribute.
#' @return Returns a network with the edges of \code{alledges} that are not
#'     present in \code{net} added. The new edges will have the attributes
#'     provided by \code{attrlist}.
#'
#' @examples
#' data(examplenet1)
#' data(examplenet2)
#' netlist=list(examplenet1,examplnet2)#list of nets
#' alledges=find_all_edges(netlist)#get all edges
#' allvertices=find_all_vertex(netlist)#get all vertices
#' #add missing vertices and edges to a network
#' examplenet1=add_missing_vertex(examplenet1,allvertices)
#' examplenet1=add_missing_edgeS(examplenet1,alledges)
#' @export
add_missing_edges=function(net,alledges=NULL,attrlist=list()){
  directed=igraph::is.directed(net)
	if(is.null(alledges)){
		alledges=t(combn(1:length(V(net)),2))
		if(directed){
			alledges=rbind(alledges,alledges[,c(2,1)])
		}
	}
	alledges2=sapply(1:nrow(alledges),function(x){paste(alledges[x,],collapse="_")})

	selfloop=F# no function currently
	if(!selfloop){
		samebool=alledges[,1]!=alledges[,2]
		alledges=alledges[samebool,]
		alledges2=alledges2[samebool]
	}

	curredges=igraph::as_edgelist(net)
	curredges2=sapply(1:nrow(curredges),function(x){paste(curredges[x,],collapse="_")})
	curredges3=sapply(1:nrow(curredges),function(x){paste(curredges[x,c(2,1)],collapse="_")})
	if(directed){
		missingedges=alledges[!alledges2%in%curredges2,]
	}else{
		missingedges=alledges[(!alledges2%in%curredges2)&(!alledges2%in%curredges3),]
	}

	net2=igraph::add_edges(net,t(missingedges),attr=attrlist)

	return(net2)
}

#' Find all possible vertices in a list of networks
#'
#' \code{find_all_vertex} Find all edges that exist in a list of networks.
#'
#' @param allnets list of igraph network objects
#' @return Returns a vector of all vertices that exist within \code{allnets}.
#'     This can be used as an argument in \code{add_missing_vertex} to ensure
#'     that all vertices are correctly generated for animation in Blender.
#'
#' @examples
#' data(examplenet1)
#' data(examplenet2)
#' netlist=list(examplenet1,examplnet2)#list of nets
#' allvertices=find_all_vertex(netlist)#get all vertices
#' @export
find_all_vertex=function(allnets){
	unique(unlist(sapply(allnets,function(x){
	  igraph::V(x)$name
	})))
}

#' Add missing vertices to a network.
#'
#' \code{add_missing_vertices} Add edges to a network to ensure consistency.
#'
#' @param net igraph network object
#' @param allvertex Vector of edges as generated by \code{find_all_vertex}
#' @param attrlist list of attributes to be given to the new vertices, where the name
#'     of each list item is the name of an vertex attribute.
#' @return Returns a network with the vertices of \code{allvertex} that are not
#'     present in \code{net} added. The new vertices will have the attributes
#'     provided by \code{attrlist}.
#'
#' @examples
#' data(examplenet1)
#' data(examplenet2)
#' netlist=list(examplenet1,examplnet2)#list of nets
#' alledges=find_all_edges(netlist)#get all edges
#' allvertices=find_all_vertex(netlist)#get all vertices
#' #add missing vertices to examplenet1
#' examplenet1=add_missing_vertex(examplenet1,allvertices)
#' @export
add_missing_vertex=function(net,allvertex,attrlist=list()){
	if(!"name"%in%attrlist){
		attrlist$name=allvertex[!allvertex%in%V(net)$name]
	}

	net2=igraph::add_vertices(net,length(allvertex[!allvertex%in%igraph::V(net)$name]),attr=attrlist)

	return(net2)
}


#' Get edge names
#'
#' \code{get_edge_names} Utility function to assign each edge a name.
#'
#' @param net igraph network object
#' @return Returns a vector of edge names in the format "vertex1_vertex2"
#' @examples
#' data(examplenet1)
#' get_edge_names(examplenet1)
#' @export
get_edge_names=function(net){
  directed=igraph::is.directed(net)
	edges=igraph::as_edgelist(net)

	if(!directed){
		edges=t(sapply(1:nrow(edges),function(x){edges[x,order(edges[x,])]}))
	}
	edges=sapply(1:nrow(edges),function(x){paste(edges[x,],collapse="_")})
	return(edges)
}

