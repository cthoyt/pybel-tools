function render_frame() {

    d = document;
    e = d.documentElement;
    g = d.getElementsByTagName('body')[0];

    var border = 1, bordercolor = 'black';

    var graph_div = $('#graph-chart');
    var w = graph_div.width(), h = graph_div.height();

    var div_graph = d3.select("#graph-chart");

    var svg = d3.select("#graph-chart").append("svg")
        .attr("width", w)
        .attr("height", h);

    // Background
    svg.append("rect")
        .attr("class", "background")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("fill", "#fcfbfb")
        .style("pointer-events", "all");

    svg.append("text")
        .attr("class", "title")
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "central")
        .text("Why Are We Leaving Facebook?");
}

// Initialize d3.js force to plot the networks from neo4j json
function init_d3_force(graph) {

    //////////////////////////////
    // Main graph visualization //
    //////////////////////////////

    d = document;
    e = d.documentElement;
    g = d.getElementsByTagName('body')[0];


    // Graph uses 0.85 x 0.85 of the window size
    var w = $('.col-lg-12').width(), h = 0.72 * w.innerHeight ||
        0.72 * e.clientHeight || 0.72 * g.clientHeight;

    var focus_node = null, highlight_node = null;

    // Highlight color of the nodes
    var highlight_color = "#4EB2D4";

    // Size when zooming scale
    var size = d3.scalePow().exponent(1)
        .domain([1, 100])
        .range([8, 24]);

    // Simulation parameters
    var linkDistance = 100, fCharge = -1000, linkStrength = 0.7, collideStrength = 1;

    // Simulation defined with variables
    var simulation = d3.forceSimulation()
        .force("link", d3.forceLink()
            .distance(linkDistance)
            .strength(linkStrength)
        )
        .force("collide", d3.forceCollide()
            .radius(function (d) {
                return d.r + 10
            })
            .strength(collideStrength)
        )
        .force("charge", d3.forceManyBody()
            .strength(fCharge)
        )
        .force("center", d3.forceCenter(w / 2, h / 2))
        .force("y", d3.forceY(0))
        .force("x", d3.forceX(0));

    // Pin down functionality
    var node_drag = d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);

    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
    }

    function releasenode(d) {
        d.fx = null;
        d.fy = null;
    }

    //END Pin down functionality

    var color_circunferencia = "black";
    var default_link_color = "#888";
    var nominal_base_node_size = 8;
    // Normal and highlighted stroke of the links (double the width of the link when highlighted)
    var nominal_stroke = 1.5, highlighted_stroke = 3;
    // Zoom variables
    var min_zoom = 0.1, max_zoom = 10;
    var border = 1, bordercolor = 'black';

    var svg = d3.select("#graph-chart").append("svg")
        .attr("width", w)
        .attr("height", h);

    // // Create definition for arrowhead.
    svg.append("defs").append("marker")
        .attr("id", "arrowhead")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 20)
        .attr("refY", 0)
        .attr("markerUnits", "strokeWidth")
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5");

    // // Create definition for stub.
    svg.append("defs").append("marker")
        .attr("id", "stub")
        .attr("viewBox", "-1 -5 2 10")
        .attr("refX", 15)
        .attr("refY", 0)
        .attr("markerUnits", "strokeWidth")
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M 0,0 m -1,-5 L 1,-5 L 1,5 L -1,5 Z");

    // Background
    svg.append("rect")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("fill", "#fcfbfb")
        .style("pointer-events", "all")
        // Zoom + panning functionality
        .call(d3.zoom()
            .scaleExtent([min_zoom, max_zoom])
            .on("zoom", zoomed))
        .on("dblclick.zoom", null);


    function zoomed() {
        g.attr("transform", d3.event.transform);
    }

    // Border
    svg.append("rect")
        .attr("height", h)
        .attr("width", w)
        .style("stroke", bordercolor)
        .style("fill", "none")
        .style("stroke-width", border);

    // g = svg object where the graph will be appended
    var g = svg.append("g");

    var linkedByIndex = {};
    graph.links.forEach(function (d) {
        linkedByIndex[d.source + "," + d.target] = true;
    });

    function isConnected(a, b) {
        return linkedByIndex[a.index + "," + b.index] || linkedByIndex[b.index + "," + a.index] || a.index == b.index;
    }

    function ticked() {
        link
            .attr("x1", function (d) {
                return d.source.x;
            })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

        node
            .attr("transform", function (d) {
                return "translate(" + d.x + ", " + d.y + ")";
            });
    }


    simulation
        .nodes(graph.nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(graph.links);

    // Definition of links nodes text...

    var link = g.selectAll(".link")
        .data(graph.links)
        .enter().append("line")
        .style("stroke-width", nominal_stroke)
        .style("stroke", default_link_color)
        .attr("class", function (d) {
            if (['decreases', 'directlyDecreases', 'increases', 'directlyIncreases', 'negativeCorrelation',
                    'positiveCorrelation'].indexOf(d.relation) >= 0) {
                return "link link_continuous"
            }
            else {
                return "link link_dashed"
            }
        })
        .attr("marker-start", function (d) {
            if ('positiveCorrelation' == d.relation) {
                return "url(#arrowhead)"
            }
            else if ('negativeCorrelation' == d.relation) {
                return "url(#stub)"
            }
            else {
                return ""
            }
        })
        .attr("marker-end", function (d) {
            if (['increases', 'directlyIncreases', 'positiveCorrelation'].indexOf(d.relation) >= 0) {
                return "url(#arrowhead)"
            }
            else if (['decreases', 'directlyDecreases', 'negativeCorrelation'].indexOf(d.relation) >= 0) {
                return "url(#stub)"
            }
            else {
                return ""
            }
        });

    var node = g.selectAll(".nodes")
        .data(graph.nodes)
        .enter().append("g")
        .attr("class", "node")
        // Next two lines -> Pin down functionality
        .on('dblclick', releasenode)
        .call(node_drag);

    var circle = node.append("path")
        .attr("d", d3.symbol()
            .size(function (d) {
                return Math.PI * Math.pow(size(d.size) || nominal_base_node_size, 2);
            })
        )
        .attr("class", function (d) {
            return d.function
        })
        .style("stroke-width", nominal_stroke)
        .style("stroke", color_circunferencia);

    var text = node.append("text")
        .attr("class", "node-name")
        // .attr("id", nodehashes[d])
        .attr("fill", "black")
        .attr("dx", 12)
        .attr("dy", ".35em")
        .text(function (d) {
            return d.name
        });

    // Highlight on mouseenter and back to normal on mouseout
    node.on("mouseenter", function (d) {
        set_highlight(d);
    })
        .on("mousedown", function () {
            d3.event.stopPropagation();
        }).on("mouseout", function () {
        exit_highlight();
    });

    function exit_highlight() {
        highlight_node = null;
        if (focus_node === null) {
            if (highlight_color != color_circunferencia) {
                circle.style("stroke", color_circunferencia);
                text.style("font-weight", "normal");
                link.style("stroke-width", nominal_stroke);
            }
        }
    }

    function set_highlight(d) {
        if (focus_node !== null) d = focus_node;
        highlight_node = d;

        if (highlight_color != color_circunferencia) {
            circle.style("stroke", function (o) {
                return isConnected(d, o) ? highlight_color : color_circunferencia;
            });
            text.style("font-weight", function (o) {
                return isConnected(d, o) ? "bold" : "normal";
            });
            link.style("stroke-width", function (o) {
                return o.source.index == d.index || o.target.index == d.index ? highlighted_stroke : nominal_stroke;
            });
        }
    }

    // Freeze the graph when space is pressed
    function freezeGraph() {
        // Space button Triggers STOP
        if (d3.event.keyCode == 32) {
            simulation.stop();
        }
    }

    // Search functionality to check if array exists in an array of arrays
    function searchForArray(haystack, needle) {
        var i, j, current;
        for (i = 0; i < haystack.length; ++i) {
            if (needle.length === haystack[i].length) {
                current = haystack[i];
                for (j = 0; j < needle.length && needle[j] === current[j]; ++j);
                if (j === needle.length)
                    return i;
            }
        }
        return -1;
    }

    function reset_attributes_on_double_click() {

        // On double click reset attributes (Important disabling the zoom behavior of dbl click because it interferes with this)
        svg.on("dblclick", function () {
            // SET default color
            svg.selectAll(".link").style("stroke", default_link_color);
            // SET default attributes //
            svg.selectAll(".link, .node").style("visibility", "visible")
                .style("opacity", "1");
            // Show node names
            svg.selectAll(".node-name").style("visibility", "visible").style("opacity", "1");
        });

    }

    function reset_attributes() {
        // Reset visibility and opacity
        svg.selectAll(".link, .node").style("visibility", "visible").style("opacity", "1");
        // Show node names
        svg.selectAll(".node-name").style("visibility", "visible").style("opacity", "1");
    }

    function hide_select_nodes_text(node_list, visualization) {
        // Filter the text to those not belonging to the list of node names

        var not_selected_names = g.selectAll(".node-name").filter(function (d) {
            return node_list.indexOf(d.name) < 0;
        });

        if (visualization != true) {
            //noinspection JSDuplicatedDeclaration
            var visualization_option = "opacity", on = "1", off = "0.1";
        } else {
            //noinspection JSDuplicatedDeclaration
            var visualization_option = "visibility", on = "visible", off = "hidden";
        }

        // Change display property to 'none'
        $.each(not_selected_names._groups[0], function (index, value) {
            value.style.setProperty(visualization_option, off);
        });
    }

    function hide_select_nodes_text_paths(data, visualization) {

        // Array with all nodes in all paths
        var nodes_in_paths = [];

        $.each(data, function (index, value) {
            $.each(value, function (index, value) {
                nodes_in_paths.push(value);
            });
        });

        // Filter the text whose innerHTML is not belonging to the list of nodeIDs
        var not_selected_names = g.selectAll(".node-name").filter(function (d) {
            return nodes_in_paths.indexOf(d.id) < 0;
        });

        if (visualization != true) {
            //noinspection JSDuplicatedDeclaration
            var visualization_option = "opacity", on = "1", off = "0.1";
        } else {
            //noinspection JSDuplicatedDeclaration
            var visualization_option = "visibility", on = "visible", off = "hidden";
        }

        // Change display property to 'none'
        $.each(not_selected_names._groups[0], function (index, value) {
            value.style.setProperty(visualization_option, off);
        });
    }

    function selected_edge_highlight(edge) {

        // Array with names of the nodes in the selected edge
        var mapped_nodes_names = [];

        // Filtered not selected links
        var links_not_mapped = g.selectAll(".link").filter(function (el) {

            if (el.label == edge) {
                mapped_nodes_names.push(el.source.id);
                mapped_nodes_names.push(el.target.id);
            }

            // Source and target should be present in the edge
            return el.label != edge;
        });

        hide_select_nodes_text(mapped_nodes_names, false);

        var not_mapped_nodes_objects = node.filter(function (el) {
            return mapped_nodes_names.indexOf(el.id) < 0;
        });

        not_mapped_nodes_objects.style("opacity", "0.1");
        links_not_mapped.style("opacity", "0.1");

    }

    // Highlight nodes from array of ids and change the opacity of the rest of nodes
    function selected_nodes_highlight(node_list) {

        hide_select_nodes_text(node_list, false);
        console.log('Node list');
        console.log(node_list);

        // Filter not mapped nodes to change opacity
        var not_mapped_nodes_objects = svg.selectAll(".node").filter(function (el) {
            return searchForArray(node_list, el.id) < 0;
        });

        // Not mapped links
        var links_not_mapped = g.selectAll(".link").filter(function (el) {
            // Source and target should be present in the edge

            return !((searchForArray(node_list, el.source.id) >= 0 || searchForArray(node_list, el.target.id) >= 0));
        });

        not_mapped_nodes_objects.style("opacity", "0.1");
        links_not_mapped.style("opacity", "0.1");
    }

    function color_all_paths(data, visualization) {

        /**
         * Returns a random integer between min (inclusive) and max (inclusive)
         * Using Math.round() will give you a non-uniform distribution!
         */
        function getRandomInt(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }

        // data: nested array with all nodes in each path
        // visualization: parameter with visualization info ('hide' || 'opaque)

        var link = g.selectAll(".link");

        ///////// Filter the nodes ////////

        // Array with all nodes in all paths
        var nodes_in_paths = [];

        $.each(data, function (index, value) {
            $.each(value, function (index, value) {
                nodes_in_paths.push(value);
            });
        });

        // Filtering the nodes that are not in any of the paths
        var not_mapped_nodes_objects = svg.selectAll(".node").filter(function (el) {
            return nodes_in_paths.indexOf(el.id) < 0;
        });

        if (visualization != true) {
            //noinspection JSDuplicatedDeclaration
            var visualization_option = "opacity", on = "1", off = "0.1";
        } else {
            //noinspection JSDuplicatedDeclaration
            var visualization_option = "visibility", on = "visible", off = "hidden";
        }
        not_mapped_nodes_objects.style(visualization_option, off);

        ///////// Colour links in each path differently and hide others ////////

        // Colour the links ( Max 21 paths )
        var color_list = ['#ff2200', ' #282040', ' #a68d7c', ' #332b1a', ' #435916', ' #00add9', ' #bfd0ff', ' #f200c2',
            ' #990014', ' #d97b6c', ' #ff8800', ' #f2ffbf', ' #e5c339', ' #5ba629', ' #005947', ' #005580', ' #090040',
            ' #8d36d9', ' #e5005c', ' #733941', ' #993d00', ' #80ffb2', ' #66421a', ' #e2f200', ' #20f200', ' #80fff6',
            ' #002b40', ' #6e698c', ' #802079', ' #330014', ' #331400', ' #ffc480', ' #7ca682', ' #264a4d', ' #0074d9',
            ' #220080', ' #d9a3d5', ' #f279aa'];

        // iter = number of paths ( Max 21 paths )
        if (data.length > color_list.length) {
            //noinspection JSDuplicatedDeclaration
            var iter = color_list.length;
        } else {
            //noinspection JSDuplicatedDeclaration
            var iter = data.length;
        }

        // First hide or set to opacity 0.1 all links
        link.style(visualization_option, off);

        // Make visible again all the edges that are in any of the paths
        var links_in_paths = [];

        for (var x = 0; x < iter; x++) {

            // Push the array (each path) to a new one where all paths are stored
            var path = link.filter(function (el) {
                // Source and target should be present in the edge and the distance in the array should be one
                return ((data[x].indexOf(el.source.id) >= 0 && data[x].indexOf(el.target.id) >= 0)
                && (Math.abs(data[x].indexOf(el.source.id) - data[x].indexOf(el.target.id)) == 1));
            });

            links_in_paths.push(path);
        }

        // Only the links that are in any of the paths are visible
        for (var j = 0, len = links_in_paths.length; j < len; j++) {
            links_in_paths[j].style(visualization_option, on);
        }

        // For each path give a different color
        for (var i = 0; i < iter; i++) {
            var links_in_this_path = link.filter(function (el) {
                // Source and target should be present in the edge and the distance in the array should be one
                return ((data[i].indexOf(el.source.id) >= 0 && data[i].indexOf(el.target.id) >= 0)
                && (Math.abs(data[i].indexOf(el.source.id) - data[i].indexOf(el.target.id)) == 1));
            });

            // Select randomly a color and apply to this path
            links_in_this_path.style("stroke", color_list[getRandomInt(0, 21)]);
        }

    }

    // Call freezeGraph when a key is pressed, freezeGraph checks whether this key is "Space" that triggers the freeze
    d3.select(window).on("keydown", freezeGraph);

    /////////////////////////
    // Additional features //
    /////////////////////////

    function download_link(response, name) {
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(response));
        element.setAttribute('download', name);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    // Build the node multi-level dropdown
    $('#node-list').append("<ul id='node-list-ul' class='dropdown-menu node-dropdown' role='menu' " +
        "aria-labelledby='dropdownMenu' " + "class='no-bullets min-padding-left'></ul>");

    // Variable with all node names for shortest path autocompletion input
    var node_names = [];

    $.each(graph.nodes, function (key, value_array) {

        node_names.push(value_array.id);

        $("#node-list-ul").append("<li class='dropdown-submenu node_selector node-dropdown'><a id='" +
            value_array.id + "'>" + value_array.name + "<ul class='dropdown-menu no-bullets min-padding-left'>" +
            "<li>Name: " + value_array.name + "" + "</li><li>Namespace: " + value_array.namespace + "</li>" +
            "<li>BEL function: " + value_array.function + "</li></ul></li>");
    });

    ///////////////////////////////////////
    // Build the edge multi-level dropdown
    ///////////////////////////////////////

    $('#edge-list').append("<ul id='edge-list-ul' class='dropdown-menu edge-dropdown' role='menu' " +
        "aria-labelledby='dropdownMenu' " + "class='no-bullets min-padding-left'></ul>");

    $.each(graph.links, function (key, value_array) {

        var pubmed_hyperlink = 'https://www.ncbi.nlm.nih.gov/pubmed/' + value_array.citation.reference;

        $("#edge-list-ul").append("<li class='dropdown-submenu edge_selector '><a id='value'>" +
            value_array.source.name + ' ' + value_array.relation + ' ' + value_array.target.name +
            "</a><ul class='dropdown-menu no-bullets min-padding-left edge-info'><li><span class='color_red'>" +
            "From: </span>" + value_array.source.name + "</li><li><span class='color_red'>To: </span>" +
            value_array.target.name + "</li><li><span class='color_red'>Relationship </span>" + value_array.relation +
            "</li><li><span class='color_red'>PubMed: </span><a href='" + pubmed_hyperlink + "' target='_blank' " +
            "style='color: blue; text-decoration: underline'>" + value_array.citation.reference + "</a></li><li>" +
            "<span class='color_red'>Journal: </span>" + value_array.citation.name + "</li><li>" +
            "<span class='color_red'>Evidence: </span>" + value_array.SupportingText + "+</li><li>" +
            "<span class='color_red'>Context: </span>" + value_array.context + "" + "</li></ul></li>");

    });

    // Shortest path autocompletion input
    node_names = node_names.sort();

    $("#source-node").autocomplete({
        source: node_names,
        appendTo: "#info-graph"
    });

    $("#target-node").autocomplete({
        source: node_names,
        appendTo: "#info-graph"
    });

    // Select node in the graph from selector
    $(".node_selector").click(function () {

        reset_attributes();

        // $this=li, first element is the a with the id of the node
        var node_array = [$(this)[0].childNodes[0].id.split(',')];
        selected_nodes_highlight(node_array);
        reset_attributes_on_double_click();

    });

    // Update Node Dropdown
    $("#node-search").on("keyup", function () {
        // Get value from search form (fixing spaces and case insensitive
        var searchText = $(this).val();
        searchText = searchText.toLowerCase();
        searchText = searchText.replace(/\s+/g, '');

        $.each($('#node-list-ul')[0].childNodes, dropdown_update);
        function dropdown_update() {
            var currentLiText = $(this).find("a")[0].innerHTML,
                showCurrentLi = ((currentLiText.toLowerCase()).replace(/\s+/g, '')).indexOf(searchText) !== -1;
            $(this).toggle(showCurrentLi);
        }
    });

    // Update Edge Dropdown
    $("#edge-search").on("keyup", function () {
        // Get value from search form (fixing spaces and case insensitive
        var searchText = $(this).val();
        searchText = searchText.toLowerCase();
        searchText = searchText.replace(/\s+/g, '');

        $.each($('#edge-list-ul')[0].childNodes, dropdown_update);
        function dropdown_update() {

            var currentLiText = $(this).find("a")[0].innerHTML,
                showCurrentLi = ((currentLiText.toLowerCase()).replace(/\s+/g, '')).indexOf(searchText) !== -1;
            $(this).toggle(showCurrentLi);
        }
    });

    // Select node in the graph from selector
    $(".edge_selector").on("click", "#value", function () {
        console.log($(this)[0])

        reset_attributes();

        // textContent or innerHTML
        var edge_name = $(this)[0].innerHTML;
        selected_edge_highlight(edge_name);

        reset_attributes_on_double_click()
    });

    // Hide text in graph
    $("#hide_node_names").on("click", function () {
        svg.selectAll(".node-name").style("display", "none");
    });

    // Hide text in graph
    $("#restore_node_names").on("click", function () {
        svg.selectAll(".node-name").style("display", "block");
    });

    // Hide text in graph
    $("#restore").on("click", function () {
        reset_attributes();
    });
}
;

// Saves visualized network as image
$("#save-svg-graph").click(function () {
    var graphName = "graph_image";
    var svgContainer = $("svg").svg(),
        svgGet = svgContainer.svg("get");
    svgGet = svgGet.toSVG();
    var blob = new Blob([svgGet], {type: "data:image/svg+xml;charset="});
    saveAs(blob, graphName + ".svg");
});