net2blend=function(net,layout,vertex.color="red",edge.color="black",vertex.shape="sphere",
	vertex.size=0.2,edge.size=0.1,edge.3d=T,edge.curve=0,vertex.intersect=T,vertex.edgeshorten=0,
	edge.arrows=F,edge.arrowsize=0,edge.arrowlength=0,edge.dash=0,outputdir=NA,netname="",netname2="",maxlength=NA){
	#######
	#Exports files to plot an igraph object in blender. Arguments are similar to igraph.plot
	#net = Igraph network object
	#layout = Layout matrix where first column is x coordinates and second column is y coordinates. Z coordinates can also be provided
	#vertex.color = Vertex colour as hex or colour name
	#edge.color = Edge colour as hex or colour name
	#vertex.shape = Name of vertex shape. Can be "sphere","cube","circle","square" or "none". Can also be the name of an object in the blender scene.
	#vertex.size = Size of vertex
	#edge.size = Edge size
	#edge.3d = Edges is a 3d object. If FALSE will flatten this edge.
	#edge.curve = Amount to curve edges. If a single value, this will be scaled by the length of the edges in the plot
	#vertex.intersect = Boolean. If TRUE edges will meet in the center of the vertex. If FALSE edges will be shortened by size of vertex.
	#vertex.edgeshorten = If provided, edges will be shortened by this value instead of the size of the vertex. 
	#edge.arrows= Boolean. If TRUE, plot arrowheads at the end of edges
	#edge.arrowsize = Thickness of arrows. If edge.arrows is TRUE and no value is provided, is based on edge.size
	#edge.arrowlength = Length of arrows. If edge.arrows is TRUE and no value is provided, this defaults to 0.2
	#edge.dash = Size of dashed edges. Larger values result in a greater number of short dashes.
	#outputdir = File path for export
	#netname = name to append to files
	#netname2 = second name to append to files - not used by blender
	#######
	if(is.na(outputdir)){
		outputdir=getwd()
	}
	if(all(edge.arrows)&all(edge.arrowsize==0)){
		edge.arrowsize=edge.size+0.05
	}
	if(all(edge.arrows)&all(edge.arrowlength==0)){
		edge.arrowlength=0.2
	}

	if((!vertex.intersect&vertex.edgeshorten==0)|edge.arrows){
		vertex.edgeshorten=vertex.size-0.05
	}
	
	
	colnames(layout)=c("x","y","z")[1:ncol(layout)]
	layout=as.data.frame(layout)
	if(!"z" %in% names(layout)){
		layout$z=0
	}
	V(net)$x=layout$x
	V(net)$y=layout$y
	V(net)$z=layout$z

	if(edge.curve==F){
		edge.curve=0
	}else if (edge.curve==T){
		edge.curve=0.2
	}

	if(length(edge.curve)==1){
		#if only one curve value is supplied, scale by edge length
		edata=as_long_data_frame(net)
		lengths=sqrt((edata$to_x-edata$from_x)^2+(edata$to_y-edata$from_y)^2+(edata$to_z-edata$from_z)^2)
		if(is.na(maxlength)){
			maxlength=max(lengths)
		}
		edge.curve=edge.curve*(lengths/maxlength)
	}

	V(net)$colour=vertex.color
	E(net)$colour=edge.color

	V(net)$shape=vertex.shape
	V(net)$size=vertex.size
	V(net)$size[V(net)$shape=="square"]=V(net)$size[V(net)$shape=="square"]*2
	V(net)$shorten=vertex.edgeshorten


	E(net)$size=edge.size
	E(net)$curve=edge.curve
	E(net)$is3d=edge.3d
	E(net)$arrowsize=edge.arrowsize
	E(net)$arrowlength=edge.arrowlength
	E(net)$dash=edge.dash
	

	edata=as_long_data_frame(net)
	if(any(!edata$is3d)){
		highz=max(c(edata$to_z[!edata$is3d],edata$from_z[!edata$is3d]))-0.01
		lowz=max(c(edata$to_z[!edata$is3d],edata$from_z[!edata$is3d]))-0.1
	
		edata$to_z[!edata$is3d]=seq(lowz,highz,length.out=sum(!edata$is3d))
		edata$from_z[!edata$is3d]=seq(lowz,highz,length.out=sum(!edata$is3d))
	}
	vdata=as_data_frame(net,what = 'vertices')
	edata=data.frame(edata,t(col2rgb(edata$colour)/255))

	edata$name=sapply(1:nrow(edata),function(x){
		cnodes=c(edata$from[x],edata$to[x])
		paste(cnodes[order(cnodes)],collapse="_")
	})

	vdata=data.frame(vdata,t(col2rgb(vdata$colour)/255))

	write.csv(edata,file.path(outputdir,paste(netname,"edata",netname2,".csv",sep="_")),row.names=F)
	write.csv(vdata,file.path(outputdir,paste(netname,"vdata",netname2,".csv",sep="_")),row.names=F)

}

findmaxlength=function(net,layout){

	colnames(layout)=c("x","y","z")[1:ncol(layout)]
	layout=as.data.frame(layout)
	if(!"z" %in% names(layout)){
		layout$z=0
	}
	V(net)$x=layout$x
	V(net)$y=layout$y
	V(net)$z=layout$z
	edata=as_long_data_frame(net)
	lengths=sqrt((edata$to_x-edata$from_x)^2+(edata$to_y-edata$from_y)^2+(edata$to_z-edata$from_z)^2)
	return(max(lengths))
}

add_missing_edges=function(net,directed=F,selfloop=F,attrlist=list()){

	alledges=t(combn(1:length(V(net)),2))
	if(directed){
		alledges=rbind(alledges,alledges[,c(2,1)])
	}
	alledges2=sapply(1:nrow(alledges),function(x){paste(alledges[x,],collapse="_")})

	if(!selfloop){
		samebool=alledges[,1]!=alledges[,2]
		alledges=alledges[samebool,]
		alledges2=alledges2[samebool]
	}

	curredges=as_edgelist(g)
	curredges2=sapply(1:nrow(curredges),function(x){paste(curredges[x,],collapse="_")})
	curredges3=sapply(1:nrow(curredges),function(x){paste(curredges[x,c(2,1)],collapse="_")})	
	if(directed){
		missingedges=alledges[!alledges2%in%curredges2,]
	}else{
		missingedges=alledges[(!alledges2%in%curredges2)&(!alledges2%in%curredges3),]
	}

	net2=add_edges(net,t(missingedges),attr=attrlist)
	
	return(net2)
}

add_missing_nodes=function(net,allnodes,attrlist=list()){
	if(!"name"%in%attrlist){
		attrlist$name=allnodes[!allnodes%in%V(net)$name]
	}

	net2=add_vertices(net,length(allnodes[!allnodes%in%V(net)$name]),attr=attrlist)

	return(net)
}

