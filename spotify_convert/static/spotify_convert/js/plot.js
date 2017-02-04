function drawPlot(plot_json) {

    var margin = {top: 20, right: 20, bottom: 30, left: 100},
                      width = 1000 - margin.left - margin.right,
                      height = 500 - margin.top - margin.bottom;
      // for dates in ISO
    var average_bool = document.getElementById("compare-check").checked;
    console.log(average_bool);

    d3.json(plot_json, function (error, data) {
        var parseDate = d3.time.format.iso.parse;
        data.forEach(function (d) {
            d.date = parseDate(d.date);
            d.output = +d.output;
        });

        var x = d3.time.scale()
            .range([0, width])
            .domain(d3.extent(data, function (d) {
                return d.date;
            }));

        var lineMargin = 3;
        if (average_bool) {
            var y = d3.scale.linear()
            .range([height, 0])
            .domain([
                d3.min(data, function (d) {
                  return Math.min(d.output, d.average) - lineMargin;
                }),
                d3.max(data, function (d) {
                  return Math.max(d.output, d.average) + lineMargin;
                })
            ]);
        }

        else {
            var y = d3.scale.linear()
            .range([height, 0])
            .domain([
                d3.min(data, function (d) {
                  return d.output - lineMargin;
                }),
                d3.max(data, function (d) {
                  return d.output + lineMargin;
                })
            ]);
        }


        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");

        var line = d3.svg.line()
            .x(function(d) { return x(d.date); })
            .y(function(d) { return y(d.output); });
        var average = d3.svg.line()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.average); });

        d3.select("svg").remove();
        var svg = d3.select("#plot").append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
          .append("g")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        svg.append("path")
            .datum(data)
            .attr("class", "line")
            .attr("d", line);
        if (average_bool) {
            svg.append("path")
            .datum(data)
            .attr("class", "average")
            .attr("d", average);
        }

        var type_page = document.getElementById("type-select").value;
        var metric_select = document.getElementById("metric-select-" + type_page)
        var metric_name = metric_select.options[metric_select.selectedIndex].text;
        var tip = d3.tip()
            .attr('class', 'd3-tip')
            .offset([120, 40])
            .html(function(d) {
                if(d.message){
                    return "<strong>" +d.output + " " + metric_name + "<br>"
                        + d.message + "<br>"
                        +"on </strong>" + d.date;
                }
                else{
                    return "<strong>" + d.output +
                        " " + metric_name + " on </strong><br>" +
                        d.date;
                }
            });

        svg.call(tip);
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text(metric_name + " Total");

        svg.selectAll(".dot")
            .data(data)
            .enter().append("a")
            .attr('href', function (d) {
                return d.link;
            })
            .append("circle")
            .attr('class', 'datapoint')
            .attr('cx', function(d) { return x(d.date); })
            .attr('cy', function(d) { return y(d.output); })
            .attr('r', 6)
            .attr('fill', 'white')
            .attr('stroke', 'steelblue')
            .attr('stroke-width', '3')

            .on('mouseover', tip.show)
	        .on('mouseout', tip.hide)
    });
}

function updatePlot() {
  var type_page = document.getElementById("type-select").value;
  var constructed_url;
  if (type_page == "fb-select"){
      constructed_url =  base_plot_url + 'facebook/';
  }
  else if (type_page == "tw-select"){
      constructed_url = base_plot_url + 'twitter/'
  }
  if (type_page == "fb-posts"){
      constructed_url = base_plot_url + "fb-posts/"
  }
  if (type_page == "tw-posts"){
      constructed_url = base_plot_url + "tw-posts/"
  }
  var metric = document.getElementById("metric-select-" + type_page).value;
  var tag = document.getElementById("tag-select").value;
  var start_date = document.getElementById("startdate").value;
  var end_date = document.getElementById("enddate").value;


  constructed_url += document.getElementById(type_page).value + "/" + metric + "/?";

  constructed_url += "compare_years=" + document.getElementById("compare-select").value;
  constructed_url += "&";

  if (tag != 'all') {
        constructed_url += "tag=" + tag;
        constructed_url += "&";
  }

  if (start_date != "") {
      constructed_url += "start_date=" + start_date;
      constructed_url += "&";
  }

  if (end_date != "") {
      constructed_url += "end_date=" + end_date;
      constructed_url += "&";
  }

  var csv_path = constructed_url + 'csv=True';
  document.getElementById("csv-button").href = csv_path;

  if (constructed_url.slice(-1) == "?" || constructed_url.slice(-1) == "&"){
      constructed_url = constructed_url.slice(0,-1);
  }
  console.log(constructed_url);

  drawPlot(constructed_url);
  //drawComparison(constructed_url);
}

function updateMenu() {
    var type_menu = document.getElementById("type-select").value;

    Array.from(document.getElementsByClassName("type-menu")).forEach( function (item) {
        item.style.display = "none";

    });
    Array.from(document.getElementsByClassName("metric-menu")).forEach( function (item) {
        item.style.display = "none";

    });
    document.getElementById(type_menu + "-group").style.display = "block";
    document.getElementById("metric-select-" + type_menu + "-group").style.display = "block";
    updatePlot()
}

drawPlot(start_plot_url)