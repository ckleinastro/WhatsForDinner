(function (data) {
    'use strict';

    /* Bubble Chart */
    var margin,
        width,
        height,
        x,
        y,
        color,
        xAxis,
        yAxis,
        svg,
        text,
        bubbles;

    // Establishing chart margins, width, and height.
    margin = { top: 20, right: 20, bottom: 50, left: 100 };
    width = 960 - margin.left - margin.right;
    height = 500 - margin.top - margin.bottom;

    // Creating the x scale.
    x = d3.scale.linear().range([0, width]);

    // Creating the y scale.
    y = d3.scale.linear().range([height, 0]);

    // Built in d3 color function.
    color = d3.scale.category20();

    // x axis.
    xAxis = d3.svg.axis().scale(x).orient("bottom");

    // y axis.
    yAxis = d3.svg.axis().scale(y).orient("left");

    // SVG canvas.
    svg = d3.select("#chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    data.forEach(function (d) {
        d.country = d.country;
        d.gdp = +d.gdp;
        d.edu_index = +d.edu_index;
        d.median_age = +d.median_age;
    });

    x.domain(d3.extent(data, function (d) { return d.median_age; }));
    y.domain(d3.extent(data, function (d) { return d.edu_index; }));

    // Creating the x axis.
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        // x axis label
        .append("text")
        .attr("class", "x label")
        .attr("x", function () { return width/2; })
        .attr("y", 30)
        .attr("dy", ".71em")
        .style("text-anchor", "middle")
        .text("Median Age");

    // Creating the y axis.
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        // y axis label
        .append("text")
        .attr("class", "y label")
        .attr("transform", "rotate(-90)")
        .attr("y", -60)
        .attr("x", -height/2)
        .attr("dy", ".71em")
        .style("text-anchor", "middle")
        .text("Education Index");

    /* Creating clipPath which prevents bubbles from being drawn
     * outside the SVG container window.
     */
    svg.append("clipPath")
        .attr("id", "chart-area")
        .append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", width)
        .attr("height", height);

    // Creating the bubble chart.
    bubbles = svg.append("g")
        .attr("id", "circles")
        .attr("clip-path", "url(#chart-area)")
        .selectAll(".country").append("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("class", function (d) { return d.country; })
        .style("fill", function (d) { return color(d.country); });

    // Calculating the position of the bubbles on the x and y axis.
    bubbles
        .attr("cx", function (d) { return x(d.median_age); })
        .attr("cy", function (d) { return y(d.edu_index); })
        .attr("r", function (d) { return Math.log(d.gdp); });

    // Creating the tooltips for the bubble chart.
    bubbles
        .on("mouseover", function (d) {
            var mousemove = { left: d3.event.pageX, top: d3.event.pageY},
                scrolltop = document.body.scrollTop,
                hh = d3.select('#tooltip')[0][0].scrollHeight;

            d3.select("#tooltip")
                .style('top', mousemove.top - scrolltop - hh/2 + 'px')
                .style('left', mousemove.left + 20 + 'px')
                .select("#value")
                .html(
                    "Country: " + d.country +
                        "<br>Education Index: " + d.edu_index +
                        "<br>Median Age: " + d.median_age +
                        "<br>GDP: $" + numberWithCommas(d.gdp) + "M"
                );
            d3.select("#tooltip").classed("hidden", false);
        })
        .on("mouseout", function () {
            d3.select("#tooltip").classed("hidden", true);
        });

    function numberWithCommas(x) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    return svg;
}( window.data ));