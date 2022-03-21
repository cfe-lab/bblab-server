var canvasOffsetX = 0;
var canvasOffsetY = 0;


/* ****************************************************************************************** */


// edge pruning limit slider.
var distanceLimitSlider = document.getElementById("distanceLimit");
var distanceLimitLabel = document.getElementById("distanceLimitLabel");
distanceLimitLabel.innerHTML = "Edge distance limit <= " + distanceLimitSlider.value;

distanceLimitSlider.oninput = function() {
  distanceLimitLabel.innerHTML = "Edge distance limit <= " + distanceLimitSlider.value;
}

// viewport scale slider.
var modelScaleSlider = document.getElementById("scaleSlider");
var modelScaleLabel = document.getElementById("modelScale");
modelScaleLabel.innerHTML = "Model scale is " + modelScaleSlider.value + " units";

modelScaleSlider.oninput = updateModelScale;
function updateModelScale() {
  modelScaleLabel.innerHTML = "Model scale is " + modelScaleSlider.value + " units";
  let scale = Number(modelScaleSlider.value)
  if (scale > 3500) {
    //modelScaleSlider.max = scale;
  } else {
    modelScaleSlider.max = 3500;
  }
 
  d3.select("#svgCanvas").attr("viewBox", [-scale / 2 + canvasOffsetX, -scale / 2 + canvasOffsetY, scale, scale]);
}

// file load listener
var fileList = null;
const fileInput = document.getElementById('filein');
fileInput.addEventListener('change', (event) => {
  fileList = event.target.files;
  console.log(fileList);
});


/* ****************************************************************************************** */


// get scrolling event
const canvas = document.getElementById("content");
canvas.onwheel = zoom;
function zoom(event) {
  event.preventDefault();
  let speed = 1;

  // inc max if needed
  if (Number(modelScaleSlider.value) > Number(modelScaleSlider.max) - 100) {
    modelScaleSlider.max = Number(modelScaleSlider.max) + 100
  }

  modelScaleSlider.value = Number(modelScaleSlider.value) + speed * event.deltaY;
  console.log(modelScaleSlider.value);
  updateModelScale();  // updates svg scale
}

var isCanvasDrag = false;
var mouseX = 0;
var mouseY = 0;
var lastMouseX = 0;
var lastMouseY = 0;

// mouse down event for canvas dragging
canvas.addEventListener("mousedown", event => {
  if (!g_isDragging) {
    console.log("start dragging canvas position");
    isCanvasDrag = true;
  }
});

canvas.addEventListener("mouseup", event => {
  isCanvasDrag = false;
});


canvas.addEventListener("mousemove", event => {
  if(isCanvasDrag) {
    let scale = Number(modelScaleSlider.value);
    let size = canvas.clientWidth > canvas.clientHeight ? canvas.clientHeight : canvas.clientWidth;
    canvasOffsetX += -(mouseX - lastMouseX) * scale / size;
    canvasOffsetY += -(mouseY - lastMouseY) * scale / size;
    updateModelScale();
  }

  // save lastpos and update to next pos
  lastMouseX = mouseX;
  lastMouseY = mouseY;
  mouseX = event.offsetX;
  mouseY = event.offsetY;
});


/* ****************************************************************************************** */


var g_isDragging = false;

// interactive portion of simulation
var height = Number(modelScaleSlider.value),
    width = Number(modelScaleSlider.value);
const svg = d3.select("#svgCanvas").attr("viewBox", [-width / 2, -height / 2, width, height]);

drag = simulation => {
  function dragstarted(d) {
    console.log("dragging");
    g_isDragging = true;
    if (!d3.event.active && simulation_paused == false) {
      simulation.alphaTarget(0.3).restart();
    }
    d.fx = d.x;
    d.fy = d.y;
  }
  
  function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }
  
  function dragended(d) {
    console.log("drag off");
    g_isDragging = false;
    if (!d3.event.active && simulation_paused == false) {
      simulation.alphaTarget(0);
    }
    d.fx = null;
    d.fy = null;
  }
  
  return d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
}

color = function() {
  const scale = d3.scaleOrdinal(d3.schemeCategory10);
  return d => scale(d.group);
}


/* ****************************************************************************************** */


// manages hiding nodes with no connections.
var hideNoConnects = true;
$("#hideNoConnects").on("click", function (){
  hideNoConnects = !hideNoConnects;
});

// manages the centering force toggle
$("#centerForce").on("click", updateCenterForce);
function updateCenterForce() {
  if (simulation == null) { return; }
  
  var checked = document.getElementById("centerForce").checked;
  if( checked == false ) {
    simulation
      .force("x", null)
      .force("y", null); // remove centering force
  } else {
    simulation
      .force("x", d3.forceX())
      .force("y", d3.forceY());
    
    if (simulation_paused == false) {
      simulation.alphaTarget(0.3).restart(); // add centering force & reheat simulation
    }
  }
}

var isSample = false;
$("#sampleBtn").on("click", function(event){
  event.preventDefault();
  isSample = true;
  processData();
});


/* ****************************************************************************************** */
// Simulation heating & cooling

var simulation_paused = false;
var simulation_heat = 0.3;

$("#heatBtn").on("click", function(event){
  if (simulation_paused == false) {
    simulation_heat = 0.9;
    simulation.alphaTarget(simulation_heat);
    simulation.alpha(simulation_heat).restart();
  }
});

$("#coolBtn").on("click", function(event){
  if (simulation_paused == false) {
    simulation_heat = 0.1;
    simulation.alphaTarget(simulation_heat);
    simulation.alpha(simulation_heat);
  }
});

$("#pauseSim").on("click", function(event){
  simulation_paused = !simulation_paused;
  if (simulation_paused) {
    simulation.stop();
  } else {
    simulation.restart();
  }
});

$("#nodeForce").on("click", function(event){
  if (simulation == null) { return; }
  
  var checked = document.getElementById("nodeForce").checked;
  if( checked == true ) {
    simulation
      .force("charge", null); // remove charge force
  } else {
    simulation
      .force("charge", d3.forceManyBody());
    
    if (simulation_paused == false) {
      simulation.alphaTarget(0.3).restart(); // add centering force & reheat simulation
    }
  }
});


/* ****************************************************************************************** */
// Code for svg generation


$("#svgDownload").on("click", function(event){
  event.preventDefault();
  
  var svgEl = document.getElementById("svgCanvas");  
  
  //get svg source.
  var serializer = new XMLSerializer();
  var source = serializer.serializeToString(svgEl);

  //add name spaces.
  if(!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)){
    source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
  }
  if(!source.match(/^<svg[^>]+"http\:\/\/www\.w3\.org\/1999\/xlink"/)){
    source = source.replace(/^<svg/, '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
  }  

  //add xml declaration
  source = '<?xml version="1.0" standalone="no"?>\r\n' + source;
  
  //you can download svg file by right click menu.
  downloadSvg("graph", source);
  console.log("downloaded");
});

// allows for downloading file using <a> element
function downloadSvg(filename, text) {
  var element = document.createElement('a');
  element.setAttribute('href', 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}


/* ****************************************************************************************** */


// runs the simulation prep code
$("#visualizeBtn").on("click", function(event){
  event.preventDefault();
  isSample = false;
  processData();
});

var fileData = null;
function readFileData(file) {
  const reader = new FileReader(); // this may break with older browsers.
  reader.onload = function(event) {
    fileData = event.target.result;
  };
  reader.readAsText(file);
}

// This function determines if a file has even been passed yet
const testData = "A 0 50 100\nB 50 0 20\nC 100 20 0";
function processData() {
  if(fileList != null) {
    readFileData(fileList[0]);
    setTimeout(waitForData, 100);
  } else {
    console.log("No file has been passed, using test data.")
    fileData = testData;
    visualizeData();
  }
}

// This funciton waits for the file to be read (files will be big so waiting is important.)
function waitForData() {
  if(fileData == null) {
    setTimeout(waitForData, 100);
    return;
  } else {
    visualizeData();
  }
}

// Global Simulation Variables
var link = null;
var node = null;
var g_links = null;
var g_nodes = null;
var simulation = null; // todo: make const

// Actually run the simulation
function visualizeData() {
  // convert string into matrix
  matrix = fileData.split("\n").map(el => el.split(" "));

  // extract names and create list of nodes for simulation
  let names = [];
  for (row of matrix) {
    names.push(row.shift());
  }
  var nodes = names.map(str => Object({id : str}));
  
  // go through all connections (smartly) and create links
  let limit = Number(distanceLimitSlider.value);
  var links = [];
  for (y = 0; y < matrix.length; y++) {
    let target = names[y]; // hopefully helps w/ optimization
    for (x = y+1; x < matrix[0].length; x++) {
      let dist = Number(matrix[y][x])
      if (dist <= limit) {
        links.push( {"source":names[x], "target":target, "distance":dist} )
      }
    }
  }

  let setToDelete = new Set();
  if (hideNoConnects == true) {
    for (y = 0; y < matrix.length; y++) {
      // check all of a nodes' connection
      let hasConnections = false;
      for (x = 0; x < matrix[0].length; x++) {
        let dist = Number(matrix[y][x])
        if (dist <= limit && x != y) {
          hasConnections = true;
          break;
        }
      }
		
      // save node id to delete later
      if (hasConnections == false) {
        setToDelete.add(names[y]);
      }
    }
       
    console.log(setToDelete);

    //clear nodes from nodes
    let end = 0;
    for (let i = 0; i < nodes.length; i++) {
      const obj = nodes[i];
      if (!setToDelete.has(obj.id)) {
        nodes[end++] = obj;
      }
    }				
    
    nodes.length = end;
  }

  console.log(nodes);
  console.log(links);
  
  document.getElementById("sampleInfo").innerHTML = "nodes = " + nodes.length + "<br> edges = " + links.length + "<br>";
  if (hideNoConnects == true) {
    document.getElementById("sampleInfo").innerHTML += "nodes hidden = " + setToDelete.size + "<br>";
  }   

  // exit early for sampling report
  if (isSample == true) {
    return;
  }
 
  document.getElementById("pauseSim").checked = false;
 
  // setup the network graph simulation
  if(simulation != null) { // Case: updating
    update_simulation(nodes, links);
  } else { // Case: initializing
    init_simulation(nodes, links);
  }

  //additional options:
  updateCenterForce();

}

function update_simulation(nodes, links) {

  var linkForce = d3.forceLink(links).id(d => d.id).distance(d => d.distance).iterations(1);

  simulation.stop();
  //simulation = d3.forceSimulation(nodes)
      //.alphaDecay(0.01)
  //    .force("link", linkForce)
  //    .force("charge", d3.forceManyBody())
  //    .force("x", d3.forceX())
  //    .force("y", d3.forceY());
  //simulation.alpha(1);    
  simulation.nodes(nodes).force("link", linkForce);
  simulation.alphaTarget(0.3).restart();

  //var update_links = g_links.selectAll("line")
  //    .data(links);
  //update_links.exit().remove()

    //link = g_links.selectAll("line")
    //.data(links)
    //.join("line")
      //.attr("stroke-width", d => Math.sqrt(d.value));
   
  //link = update_links.enter()
  //    .append("line")
  //    .merge(update_links);

  //var update_nodes = g_nodes.selectAll("circle")
  //    .data(nodes);
  //update_nodes.exit().remove();
  //node = update_nodes.enter()
  //    .append("circle")
  //    .merge(update_nodes);
  //node.append("title")
  //    .text(d => d.id);

//// **************************************** ////

  g_links.selectAll("line").remove();
  link = g_links.selectAll("line")
    .data(links)
    .join("line")
      .attr("stroke-width", 2.25);

  g_nodes.selectAll("circle").remove();
  node = g_nodes.selectAll("circle")
    .data(nodes)
    .join("circle")
      .attr("r", 5)
      .attr("fill", "black")
      .call(drag(simulation));

  node.append("title")
      .text(d => d.id);

}

function init_simulation(nodes, links) {
  var linkForce = d3.forceLink(links).id(d => d.id).distance(d => d.distance).iterations(1);
  //var width = Number(modelScaleSlider.value),
  //    height = Number(modelScaleSlider.value);

  simulation = d3.forceSimulation(nodes)
      //.alphaDecay(0.01)
      //.force("link", linkForce)
      //.force("charge", d3.forceManyBody())
      //.force("x", d3.forceX())
      //.force("x", d3.forceX())
      //.force("y", d3.forceY());
      //.force("y", d3.forceY())
      .force("link", linkForce)
      .force("charge", d3.forceManyBody().strength(-10))
      .force("center", d3.forceCenter(0, 0));

  g_links = svg.append("g")
      .attr("stroke", "#888")
      .attr("stroke-opacity", 0.65);
  link = g_links.selectAll("line")
    .data(links)
    .join("line")
      .attr("stroke-width", 2.25);
   
  g_nodes = svg.append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
  node = g_nodes.selectAll("circle")
    .data(nodes)
    .join("circle")
      .attr("r", 5)
      .attr("fill", "black")
      .call(drag(simulation));

  node.append("title")
      .text(d => d.id);

  simulation.on("tick", () => {
    link
	.attr("x1", d => d.source.x)
	.attr("y1", d => d.source.y)
	.attr("x2", d => d.target.x)
	.attr("y2", d => d.target.y);
    node
	.attr("cx", d => d.x)
	.attr("cy", d => d.y);
  });
}

