// Waiting until document has loaded
//window.onload = () => { 

  // YOUR CODE GOES HERE
  const margin = {top:40,right:40,bottom:60,left:60};
const width = 900 - margin.left - margin.right;
const height = 600 - margin.top - margin.bottom;

const svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

d3.csv("cars_cleaned.csv").then(data => {

  // console.log("CSV data：", data);
  // console.log("the first line：",data[0]);
  data.forEach(d => {
    d["Retail Price"] = +d["Retail Price"];
    d["Horsepower(HP)"] = +d["Horsepower(HP)"];
    // d.Type = +d.Type; This is wrong
    d["Engine Size (l)"] = +d["Engine Size (l)"];
    d["City Miles Per Gallon"] = +d["City Miles Per Gallon"];
  });
  
  const x = d3.scaleLinear()
    .domain(d3.extent(data, d => d["Retail Price"])).nice()
    .range([0,width]);
  const y = d3.scaleLinear()
    .domain(d3.extent(data, d => d["Horsepower(HP)"])).nice()
    .range([height,0]);
  


  // Color Mapping: Category -> Discrete Color

  // const color = d3.scaleSequential(d3.interpolatePlasma)
  //   .domain(d3.extent(data, d => d.Type));

  // Because d.Type is charter, so we use d3.scaleOrdinal()
  const color = d3.scaleOrdinal()
  .domain([...new Set(data.map(d => d.Type))])
  .range(d3.schemeTableau10);

  const size = d3.scaleSqrt()
    .domain(d3.extent(data, d => d["Engine Size (l)"]))
    .range([1,6]);

  svg.append("g")
    .attr("transform", `translate(0,${height})`)
    // .attr("fill", d => color(d.Type))
    .call(d3.axisBottom(x));
  svg.append("g").call(d3.axisLeft(y));

  svg.selectAll(".circle")
    .data(data)
    .enter()
    .append("circle")
    .attr("class","circle")
    .attr("cx", d => x(d["Retail Price"]))  //x-axis
    .attr("cy", d => y(d["Horsepower(HP)"]))  // y-axis
    .attr("r", d => size(d["Engine Size (l)"])) //the size of the point 
    .attr("fill", d => color(d.Type))    // the color of the point
    .on("click", showDetails);
  
  //choose six elements to show, strong show the name of the car
  function showDetails(d) {
    document.getElementById("details").innerHTML = `
      <strong>${d.Name}</strong><br/>
      Price: $${d["Retail Price"]}<br/>
      Len: ${d.Len}L<br/>
      Weight: ${d.Weight}<br/>
      City MPG: ${d["City Miles Per Gallon"]}<br/>
      Cylinders: ${d.Cyl}<br/>
      Type: ${d.Type}
    `;
  }
});

