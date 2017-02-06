// Get json from URL
d3.json("/pathways/graph/get_json_pks/" + pks, function (error, graph) {
    init_d3_force(graph);

    if (error) throw error;
});

function save_previous_positioning() {
    // Save current positions into prevLoc 'object;
    var prevPos = {};

    // __data__ can be accessed also as an attribute (d.__data__)
    d3.selectAll(".node").data().map(function (d) {
        if (d) {
            prevPos[d.id] = [d.x, d.y];
        }

        return d;
    });

    return prevPos
}

function update_position(json_data, prevPos) {

    var new_nodes = [];

    // Set old locations back into the original nodes
    $.each(json_data.nodes, function (index, value) {

        if (prevPos[value.id]) {

            oldX = prevPos[value.id][0];
            oldY = prevPos[value.id][1];
            // value.fx = oldX;
            // value.fy = oldY;
        } else {
            // If no previous coordinate... Start from off screen for a fun zoom-in effect
            oldX = -100;
            oldY = -100;
            new_nodes.push(value.id);
        }

        value.x = oldX;
        value.y = oldY;

    });

    return {json: json_data, new_nodes: new_nodes}
}


// Initialize d3.js force to plot the networks from neo4j json
function init_d3_force(graph) {

    // Definition of context menu
    var menu = [
        {
            title: 'Expand node',
            action: function (elm, d, i) {
                // Variables explanation:
                // elm: [object SVGGElement] d: [object Object] i: (#Number)

                var positions = save_previous_positioning();

                // Push selected node to expand node list
                window.expand_nodes.push(d.id);

                // Ajax to update the cypher query. Three list are sent to the server. pks of the subgraphs, list of nodes to delete and list of nodes to expand

                $.ajax({
                    url: '/pathways/graph/get_json_cypher/',
                    dataType: "json",
                    data: {pks: pks, delete_nodes: window.delete_nodes, expand_nodes: window.expand_nodes}
                }).done(function (response) {

                    // Load new data, first empty all created divs and clear the current network
                    var data = update_position(response, positions);

                    $('#graph-chart').empty();
                    $('#sankey').empty();
                    $('#node-list').empty();
                    $('#edge-list').empty();

                    init_d3_force(data['json']);

                    selected_nodes_highlight(data['new_nodes']);

                });
            },
            disabled: false // optional, defaults to false
        },
        {
            title: 'Delete node',
            action: function (elm, d, i) {

                var positions = save_previous_positioning();

                // Push selected node to expand node list
                window.delete_nodes.push(d.id);

                $.ajax({
                    url: '/pathways/graph/get_json_cypher/',
                    dataType: "json",
                    data: {pks: pks, delete_nodes: window.delete_nodes, expand_nodes: window.expand_nodes}
                }).done(function (response) {

                    // Load new data, first empty all created divs and clear the current network
                    var data = update_position(response, positions);

                    $('#graph-chart').empty();
                    $('#sankey').empty();
                    $('#node-list').empty();
                    $('#edge-list').empty();

                    init_d3_force(data['json']);
                });

            }
        }
    ];

    //////////////////////////////
    // Main graph visualization //
    //////////////////////////////

    d = document;
    e = d.documentElement;
    g = d.getElementsByTagName('body')[0];

    // Graph uses 0.85 x 0.85 of the window size
    var w = 0.85 * window.innerWidth || 0.85 * e.clientWidth || 0.85 * g.clientWidth, h = 0.72 * w.innerHeight || 0.72 * e.clientHeight || 0.72 * g.clientHeight;

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
        // Allows NODE FIXING
        // d.fx = null;
        // d.fy = null;
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
        .attr("class", "link")
        .style("stroke-width", nominal_stroke)
        .style("stroke", default_link_color)
        .attr("class", function (d) {
            if (['decreases', 'directlyDecreases', 'increases', 'directlyIncreases', 'negativeCorrelation', 'positiveCorrelation'].indexOf(d.relation) >= 0) {
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
        .style("fill", function (d) {
            return d.node_color;
        })
        .on('contextmenu', d3.contextMenu(menu)) // Attach context menu to node's circle
        // Next two lines -> Pin down functionality
        .on('dblclick', releasenode)
        .call(node_drag);

    var circle = node.append("path")
        .attr("d", d3.symbol()
            .size(function (d) {
                return Math.PI * Math.pow(size(d.size) || nominal_base_node_size, 2);
            })
        )
        .style("fill", function (d) {
            return d.node_color;
        })
        .style("stroke-width", nominal_stroke)
        .style("stroke", color_circunferencia);

    var text = node.append("text")
        .attr("class", "node-name")
        .attr("fill", "black")
        .attr("dx", 12)
        .attr("dy", ".35em")
        .text(function (d) {
            return d.id
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
            return node_list.indexOf(d.id) < 0;
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

        // Filter not mapped nodes to change opacity
        var not_mapped_nodes_objects = svg.selectAll(".node").filter(function (el) {
            return node_list.indexOf(el.id) < 0;
        });

        console.log(not_mapped_nodes_objects);

        // Not mapped links
        var links_not_mapped = g.selectAll(".link").filter(function (el) {

            // Source and target should be present in the edge
            return !((node_list.indexOf(el.source.id) >= 0 || node_list.indexOf(el.target.id) >= 0));
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
        var color_list = ['#ff2200', ' #282040', ' #a68d7c', ' #332b1a', ' #435916', ' #00add9', ' #bfd0ff', ' #f200c2', ' #990014', ' #d97b6c', ' #ff8800', ' #f2ffbf', ' #e5c339', ' #5ba629', ' #005947', ' #005580', ' #090040', ' #8d36d9', ' #e5005c', ' #733941', ' #993d00', ' #80ffb2', ' #66421a', ' #e2f200', ' #20f200', ' #80fff6', ' #002b40', ' #6e698c', ' #802079', ' #330014', ' #331400', ' #ffc480', ' #7ca682', ' #264a4d', ' #0074d9', ' #220080', ' #d9a3d5', ' #f279aa'];

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

    // Show all mapped nodes for x seconds
    $("#mapped-nodes-button").click(function () {
        reset_attributes();
        //noinspection JSUnresolvedVariable
        selected_nodes_highlight(mapped_nodes);
        reset_attributes_on_double_click();
    });

    // Build the node multi-level dropdown
    $('#node-list').append("<ul id='node-list-ul' class='dropdown-menu node-dropdown' role='menu' aria-labelledby='dropdownMenu' " +
        "class='no-bullets min-padding-left'></ul>");

    // Variable with all node names for shortest path autocompletion input
    var node_names = [];

    $.each(graph.nodes, function (key, value_array) {

        node_names.push(value_array.label);

        $("#node-list-ul").append("<li class='dropdown-submenu node_selector node-dropdown'><a id='value'>" + value_array.label +
            "</a><ul class='dropdown-menu no-bullets min-padding-left'><li>Name: " + value_array.value + "</li><li>Namespace: " + value_array.namespace + "</li><li>BEL function: " + value_array.bel_function_type
            + "</li></ul></li>");
    });

    ///////////////////////////////////////
    // Build the edge multi-level dropdown
    ///////////////////////////////////////

    $('#edge-list').append("<ul id='edge-list-ul' class='dropdown-menu edge-dropdown' role='menu' aria-labelledby='dropdownMenu' " +
        "class='no-bullets min-padding-left'></ul>");

    $.each(graph.links, function (key, value_array) {
        var pubmed_hyperlink = 'https://www.ncbi.nlm.nih.gov/pubmed/' + value_array.citation.pubmed_id;

        $("#edge-list-ul").append("<li class='dropdown-submenu edge_selector '><a id='value'>" + value_array.label +
            "</a><ul class='dropdown-menu no-bullets min-padding-left edge-info'><li><span class='color_red'>From: </span>"
            + value_array.source.id + "</li><li><span class='color_red'>To: </span>" + value_array.target.id +
            "</li><li><span class='color_red'>Relationship </span>" + value_array.relation +
            "</li><li><span class='color_red'>PubmedID: </span><a href='" + pubmed_hyperlink + "' target='_blank'>" +
            value_array.citation.pubmed_id + "</a></li><li><span class='color_red'>Journal: </span>" + value_array.citation.journal_ref +
            "</li><<li><span class='color_red'>Evidence: </span>" + value_array.evidence +
            "+</li><li><span class='color_red'>Context: </span>" + value_array.context + "</li></ul></li>");

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

    var shortest_path_form = $("#shortest-path-form");

    // Get the shortest path between two nodes via Ajax or get the BEL for the shortest path
    $('.button-shortest-path').each(function () {
        $(this).on('click', function () {
            if (shortest_path_form.valid()) {
                if ($(this).attr('id') == "show-network-input") {
                    $.ajax({
                        url: '/pathways/graph/shortest_path/',
                        type: shortest_path_form.attr('method'),
                        dataType: 'json',
                        data: {
                            'source': shortest_path_form.find('input[name="source"]').val(),
                            'target': shortest_path_form.find('input[name="target"]').val(),
                            'expand_nodes[]': window.expand_nodes,
                            'delete_nodes[]': window.delete_nodes,
                            'pks': pks,
                            'visualization-options': shortest_path_form.find('input[name="visualization-options"]').is(":checked")
                        },
                        success: function (data) {

                            var shortest_path_nodes = data['shortest_path_nodes'];
                            var checkbox = data['checkbox'];

                            // Change style in force
                            reset_attributes();

                            // Filter not mapped nodes to change opacity
                            var not_mapped_nodes_objects = svg.selectAll(".node").filter(function (el) {
                                return shortest_path_nodes.indexOf(el.id) < 0;
                            });


                            var links_not_path = g.selectAll(".link").filter(function (el) {
                                // Source and target should be present in the edge and the distance in the array should be one
                                return !((shortest_path_nodes.indexOf(el.source.id) >= 0 && shortest_path_nodes.indexOf(el.target.id) >= 0)
                                && (Math.abs(shortest_path_nodes.indexOf(el.source.id) - shortest_path_nodes.indexOf(el.target.id)) == 1));
                            });

                            // If checkbox is True -> Hide all, Else -> Opacity 0.1
                            if (checkbox == true) {
                                not_mapped_nodes_objects.style("visibility", "hidden");
                                links_not_path.style("visibility", "hidden");
                            } else {
                                not_mapped_nodes_objects.style("opacity", "0.1");
                                links_not_path.style("opacity", "0.05");
                            }
                            hide_select_nodes_text(shortest_path_nodes, checkbox);
                            reset_attributes_on_double_click();
                        }, error: function (request) {
                            alert(request.responseText);
                        }
                    })
                } else {
                    $.ajax({
                        url: '/pathways/graph/bel/shortest_path/',
                        type: shortest_path_form.attr('method'),
                        dataType: 'text',
                        data: {
                            'source': shortest_path_form.find('input[name="source"]').val(),
                            'target': shortest_path_form.find('input[name="target"]').val(),
                            'expand_nodes[]': window.expand_nodes,
                            'delete_nodes[]': window.delete_nodes,
                            'pks': pks
                        },
                        success: function (response) {
                            download_link(response, 'shortest_path_BEL.txt');
                        }, error: function (request) {
                            alert(request.responseText);
                        }
                    })
                }
            }
        });
    });

    // Shortest path validation form
    shortest_path_form.validate(
        {
            rules: {
                source: {
                    required: true,
                    minlength: 5
                },
                target: {
                    required: true,
                    minlength: 5
                }
            },
            messages: {
                source: "Please enter a valid source",
                target: "Please enter a valid target"
            }
        });

    // All paths form autocompletion
    $("#source-node2").autocomplete({
        source: node_names,
        appendTo: "#info-graph"
    });

    $("#target-node2").autocomplete({
        source: node_names,
        appendTo: "#info-graph"
    });

    // Get or show all path between two nodes via Ajax

    var all_path_form = $("#all-paths-form");

    $('.button-all-paths').each(function () {
        $(this).on('click', function () {
            if (all_path_form.valid()) {
                if ($(this).attr('id') == "all-paths-show-input") {
                    $.ajax({
                        url: '/pathways/graph/all_paths/',
                        type: all_path_form.attr('method'),
                        dataType: 'json',
                        data: {
                            'source': all_path_form.find('input[name="source"]').val(),
                            'target': all_path_form.find('input[name="target"]').val(),
                            'expand_nodes[]': window.expand_nodes,
                            'delete_nodes[]': window.delete_nodes,
                            'pks': pks,
                            'visualization-options': all_path_form.find('input[name="visualization-options"]').is(":checked")
                        },
                        success: function (data) {

                            reset_attributes();

                            var all_path_nodes = data['all_path_nodes'];
                            var checkbox = data['checkbox'];
                            var json_sankey = JSON.parse(data['json_sankey']);

                            // Empty sankey's div
                            $('#sankey').empty();

                            if (json_sankey.links.length === 0) {
                                d3.select("#sankey").append("p").text("No paths between the nodes")
                            }
                            else {
                                // Init sankey diagram with all paths from node a to b
                                init_sankey_diagram(json_sankey);
                            }

                            // Apply changes in style for select paths
                            hide_select_nodes_text_paths(all_path_nodes, false);
                            color_all_paths(all_path_nodes, checkbox);

                            reset_attributes_on_double_click()
                        },
                        error: function (request) {
                            alert(request.responseText);
                        }
                    })
                } else {
                    $.ajax({
                        url: '/pathways/graph/bel/all_paths/',
                        type: all_path_form.attr('method'),
                        dataType: 'text',
                        data: {
                            'source': all_path_form.find('input[name="source"]').val(),
                            'target': all_path_form.find('input[name="target"]').val(),
                            'expand_nodes[]': window.expand_nodes,
                            'delete_nodes[]': window.delete_nodes,
                            'pks': pks
                        },
                        success: function (response) {
                            download_link(response, 'all_paths_BEL.txt');
                        },
                        error: function (request) {
                            alert(request.responseText);
                        }
                    });
                }
            }
        });
    });

    all_path_form.validate(
        {
            rules: {
                source: {
                    required: true,
                    minlength: 5
                },
                target: {
                    required: true,
                    minlength: 5
                }
            },
            messages: {
                source: "Please enter a valid source",
                target: "Please enter a valid target"
            }
        });

    // Required for multiple autocompletion
    function split(val) {
        return val.split(/,\s*/);
    }

    function extractLast(term) {
        return split(term).pop();
    }

    var export_gml = $('#export-gml');

    // Assign value of hidden input for exporting form
    export_gml.on('submit', function (e) {
        e.preventDefault();
        export_gml.find('input[name="delete_nodes"]').val(window.expand_nodes);
        export_gml.find('input[name="expand_nodes"]').val(window.delete_nodes);
        export_gml.find('input[name="pks"]').val(pks);

        this.submit();
    });


    $("#export-node-list")
    // don't navigate away from the field on tab when selecting an item
        .on("keydown", function (event) {
            if (event.keyCode === $.ui.keyCode.TAB &&
                $(this).autocomplete("instance").menu.active) {
                event.preventDefault();
            }
        })
        .autocomplete({
            minLength: 0,
            source: function (request, response) {
                // delegate back to autocomplete, but extract the last term
                response($.ui.autocomplete.filter(
                    node_names, extractLast(request.term)));
            },
            appendTo: "#info-graph",
            focus: function () {
                // prevent value inserted on focus
                return false;
            },
            select: function (event, ui) {
                var terms = split(this.value);
                // remove the current input
                terms.pop();
                // add the selected item
                terms.push(ui.item.value);
                // add placeholder to get the comma-and-space at the end
                terms.push("");
                this.value = terms.join(", ");
                return false;
            }
        });

    // Select node in the graph from selector
    $(".node_selector").on("click", "#value", function () {

        reset_attributes();

        // textContent or innerHTML
        var node_array = [$(this)[0].innerHTML];

        selected_nodes_highlight(node_array);
        reset_attributes_on_double_click()

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

    // Update candidate mechanism dropdown
    $("#candidate-search").on("keyup", function () {
        // Get value from search form (fixing spaces and case insensitive
        var searchText = $(this).val();
        searchText = searchText.toLowerCase();
        searchText = searchText.replace(/\s+/g, '');

        $.each($('.candidate-nodes'), dropdown_update);
        function dropdown_update() {
            var currentLiText = $(this)[0].innerHTML,
                showCurrentLi = ((currentLiText.toLowerCase()).replace(/\s+/g, '')).indexOf(searchText) !== -1;
            $(this).toggle(showCurrentLi);
        }
    });

    // Select node in the graph from selector
    $(".edge_selector").on("click", "#value", function () {

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

    // Mechanism show on click
    $(".candidate-nodes").on("click", show_mechanism_path);
    function show_mechanism_path() {

        // Index of the candidate mechanism to access it in the array
        var node_name = $(this)[0].id.replace("mechanism-", "");

        $.ajax({
            url: '/pathways/graph/mechanisms/' + node_name,
            type: 'GET',
            dataType: 'json',
            data: {
                'expand_nodes[]': window.expand_nodes,
                'delete_nodes[]': window.delete_nodes,
                'pks': pks,
                'mapped_nodes': JSON.stringify(mapped_nodes)
            },
            success: function (data) {

                var mechanism_paths = data['mechanism_paths'];
                var mechanism_story = data['story_mechanism_dict'];
                var json_sankey = JSON.parse(data['json_sankey']);

                // Sankey //
                // Empty sankey's div
                $('#sankey').empty();

                if (json_sankey.links.length === 0) {
                    d3.select("#sankey").append("p").text("No paths between the selected node and the input")
                }
                else {
                    // Init sankey diagram with all paths from node a to b
                    init_sankey_diagram(json_sankey);
                }
                // Sankey //

                // Erase stuffs if already a mechanism has been clicked
                $("#mechanism-list").html("");

                $.each(mechanism_story, function (key, value_array) {
                    $("#mechanism-list").append("<li class='dropdown-submenu candidate_mechanism'><a>" + key +
                        "</a><ul class='dropdown-menu no-bullets min-padding-left candidate_mechanism'><li>" + value_array + "</li></ul></li>");
                });

                reset_attributes();

                hide_select_nodes_text_paths(mechanism_paths, false);

                // true to hide all other paths
                color_all_paths(mechanism_paths, false);

                reset_attributes_on_double_click();
            },
            error: function (request) {
                alert(request.responseText);
            }
        });
    }
}


function init_sankey_diagram(graph) {

    // Adjust the height depending on the number of links in the diagram
    if (graph.links.length < 10) {
        height_factor = 0.5;
    }
    else if (graph.links.length > 10 && graph.links.length <= 30) {
        height_factor = 0.7;
    }
    else if (graph.links.length > 30 && graph.links.length <= 50) {
        height_factor = 0.9;
    }
    else if (graph.links.length > 50 && graph.links.length <= 70) {
        height_factor = 1.1;
    }
    else if (graph.links.length > 70 && graph.links.length <= 90) {
        height_factor = 1.3;
    }
    else {
        height_factor = 2;
        alert('Sankey diagram maybe crash due to the huge amount of paths requested');
    }

    // Size
    d = document;
    e = d.documentElement;
    g = d.getElementsByTagName('body')[0];

    var margin = {top: 10, bottom: 10, left: 10, right: 10};

    // Graph uses 0.85 x 0.85 of the window size
    var w = 0.85 * window.innerWidth - margin.left - margin.right || 0.85 * e.clientWidth - margin.left - margin.right || 0.85 * g.clientWidth, h = height_factor * w.innerHeight - margin.top - margin.bottom || height_factor * e.clientHeight - margin.top - margin.bottom || height_factor * g.clientHeight - margin.top - margin.bottom;

    var units = "Widgets";

    // format variables
    var formatNumber = d3.format(",.0f"),    // zero decimal places
        format = function (d) {
            return formatNumber(d) + " " + units;
        },
        color = d3.scaleOrdinal(d3.schemeCategory20);

    // append the svg object to the body of the page
    var svg = d3.select("#sankey").append("svg")
        .attr("width", w + margin.left + margin.right)
        .attr("height", h + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    // Set the sankey diagram properties
    var sankey = d3.sankey()
        .nodeWidth(36)
        .nodePadding(40)
        .size([w, h]);

    var path = sankey.link();

    sankey
        .nodes(graph.nodes)
        .links(graph.links)
        .layout(32);

    // add in the links
    var link = svg.append("g").selectAll(".link")
        .data(graph.links)
        .enter().append("path")
        .attr("class", "link sankey_link")
        .attr("d", path)
        .attr("id", function (d, i) {
            d.id = i;
            return "link-" + i;
        })
        .style("stroke-width", function (d) {
            return Math.max(1, d.dy);
        })
        .sort(function (a, b) {
            return b.dy - a.dy;
        });

    // add the link titles
    link.append("title")
        .text(function (d) {
            return d.source.name + " → " +
                d.target.name + "\n" + format(d.value);
        });

    // add in the nodes
    var node = svg.append("g").selectAll(".node")
        .data(graph.nodes)
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        })
        .on("click", highlight_node_links)
        .call(d3.drag()
            .subject(function (d) {
                return d;
            })
            .on("start", function () {
                this.parentNode.appendChild(this);
            })
            .on("drag", dragmove));

    // add the rectangles for the nodes
    node.append("rect")
        .attr("height", function (d) {
            return d.dy;
        })
        .attr("width", sankey.nodeWidth())
        .style("fill", function (d) {
            return d.color = color(d.name.replace(/ .*/, ""));
        })
        .style("stroke", function (d) {
            return d3.rgb(d.color).darker(2);
        })
        .append("title")
        .text(function (d) {
            return d.name + "\n" + format(d.value);
        });

    // add in the title for the nodes
    node.append("text")
        .attr("x", -6)
        .attr("y", function (d) {
            return d.dy / 2;
        })
        .attr("dy", ".35em")
        .attr("text-anchor", "end")
        .attr("transform", null)
        .text(function (d) {
            return d.name;
        })
        .filter(function (d) {
            return d.x < w / 2;
        })
        .attr("x", 6 + sankey.nodeWidth())
        .attr("text-anchor", "start");

    // the function for moving the nodes
    function dragmove(d) {
        d3.select(this).attr("transform",
            "translate(" + (
                d.x = Math.max(0, Math.min(w - d.dx, d3.event.x))
            ) + "," + (
                d.y = Math.max(0, Math.min(h - d.dy, d3.event.y))
            ) + ")");
        sankey.relayout();
        link.attr("d", path);
    }

    // Highlight_node_links -> http://bl.ocks.org/git-ashish/8959771
    function highlight_node_links(node) {

        var remainingNodes = [],
            nextNodes = [];

        var stroke_opacity = 0;
        if (d3.select(this).attr("data-clicked") == "1") {
            d3.select(this).attr("data-clicked", "0");
            stroke_opacity = 0.2;
        } else {
            d3.select(this).attr("data-clicked", "1");
            stroke_opacity = 0.5;
        }

        var traverse = [{
            linkType: "sourceLinks",
            nodeType: "target"
        }, {
            linkType: "targetLinks",
            nodeType: "source"
        }];

        traverse.forEach(function (step) {
            node[step.linkType].forEach(function (link) {
                remainingNodes.push(link[step.nodeType]);
                highlight_link(link.id, stroke_opacity);
            });

            while (remainingNodes.length) {
                nextNodes = [];
                remainingNodes.forEach(function (node) {
                    node[step.linkType].forEach(function (link) {
                        nextNodes.push(link[step.nodeType]);
                        highlight_link(link.id, stroke_opacity);
                    });
                });
                remainingNodes = nextNodes;
            }
        });
    }

    function highlight_link(id, opacity) {
        d3.select("#link-" + id).style("stroke-opacity", opacity);
    }

    // Highlight_node_links END
}


// Saves visualized network as image
$("#save-svg-graph").click(function () {
    var graphName = "graph_image";
    var svgContainer = $("svg").svg(),
        svgGet = svgContainer.svg("get");
    svgGet = svgGet.toSVG();
    var blob = new Blob([svgGet], {type: "data:image/svg+xml;charset="});
    saveAs(blob, graphName + ".svg");
});

