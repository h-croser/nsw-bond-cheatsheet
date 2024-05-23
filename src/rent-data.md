---
title: Rent data
theme: [coffee, parchment]
---

# Rent Data

**_Rental price data for NSW_**

The following visualisation has been created using data scraped from the Rental Bonds Online site.<br>
The data is published monthly and covers postcodes within NSW.

```js
const nswStateOutline = FileAttachment("./data/nsw_outline.json").json();
const nswPostcodes = FileAttachment("./data/nsw_postcodes.csv").csv({typed: true});
const medianRentsBedsRaw = FileAttachment("./data/median-rents-bedrooms.parquet").parquet();
const medianRentsRaw = FileAttachment("./data/median-rents.parquet").parquet();
```

```js
const medianRentsBeds = medianRentsBedsRaw.toArray();
const medianRents = medianRentsRaw.toArray();
```

```js
var postcodeInput = Inputs.text({
    placeholder: "All NSW",
    type: "number",
    label: "Enter postcode",
    submit: true
});

var postcode = view(postcodeInput, {marginBottom: 0, marginTop: 0});
```

```js
const currPostcode = nswPostcodes.filter(row => ((postcode == "") || (row.postcode.toString() === postcode)));
const postcodeStr = postcode !== "" ? "postcode " + postcode : "all NSW";

const postcodeRentsAllBeds = medianRentsBeds.filter(row => (((postcode == "") && (row.postcode.toString() === "0")) || (row.postcode.toString() === postcode)));
const postcodeRents = medianRents.filter(row => (((postcode == "") && (row.postcode.toString() === "0")) || (row.postcode.toString() === postcode)));
```

```js
const postcodeMap = Plot.plot({
    width: `${width}`,

    projection: {
        type: "reflect-y",
        domain: nswStateOutline
    },
    marks: [
        Plot.geo(nswStateOutline),
        Plot.dot(currPostcode, {x: 'long', y: 'lat', r: 1, fill: 'var(--theme-foreground-focus)', tip: true, title: (d) => `Postcode: ${d.postcode} \nLocality: ${d.locality}`}),
        Plot.dot(currPostcode, Plot.pointer({x: "long", y: "lat", fill: "#b3e2cd", r: 3}))
    ]
});

postcodeMap.addEventListener("click", (event) => {
    if ((postcodeMap.value !== null) && (postcodeMap.value !== undefined)) {
        postcodeInput.value = postcodeMap.value.postcode;
        postcodeInput.dispatchEvent(new Event("input"));
    } else {
        postcodeInput.value = "";
        postcodeInput.dispatchEvent(new Event("input"));
    }
});
```

```js
const bedFilterInput = Inputs.toggle({label: "Filter by bedroom count"});
const bedFilterToggle = view(bedFilterInput, {marginBottom: 0, marginTop: 0});

let minBeds = postcodeRentsAllBeds.at(0).num_bedrooms;
let maxBeds = postcodeRentsAllBeds.at(0).num_bedrooms;
for (let row of postcodeRentsAllBeds) {
    if (row.num_bedrooms < minBeds) minBeds = row.num_bedrooms;
    if (row.num_bedrooms > maxBeds) maxBeds = row.num_bedrooms;
}
```

```js
let numBedsInput = "\n";
let numBeds = null;
if (bedFilterToggle) {
    numBedsInput = Inputs.range([minBeds, maxBeds], { value: minBeds, label: "Num Bedrooms", step: 1 });
    numBeds = view(numBedsInput, {marginBottom: 0, marginTop: 0});
}
```

```js
const postcodeRentsBeds = postcodeRentsAllBeds.filter(row => (row.num_bedrooms === numBeds));
```

```js
const rentsData = bedFilterToggle ? postcodeRentsBeds : postcodeRents;
const v1 = (d) => d.median_rent;
const v2 = (d) => Number(d.data_points);
const y2 = d3.scaleLinear(d3.extent(rentsData, v2), [0, d3.max(rentsData, v1)]);
const rentByBedroom = Plot.plot({
    title: `Median weekly rents ${bedFilterToggle ? "by number of bedrooms" : ""} for ${postcodeStr}`,
    subtitle: "Left y axis: Median weekly rents | Right y axis: Number of bonds lodged per month",
    width: `${width}`,
    marginBottom: 60,
  
    grid: true,
    x: {
        label: "Month of lodgement",
        labelAnchor: "center",
        type: "time"
    },
    y: {
        label: "Median weekly rent ($)",
        tickFormat: (d) => `$${d}`,
        axis: "left"
    },
    marks: [
        Plot.ruleY([0]),
        Plot.axisY(y2.ticks(), { color: "var(--syntax-entity)", anchor: "right", label: "Bonds lodged", y: y2, tickFormat: y2.tickFormat() }),
        Plot.dotY(rentsData, Plot.mapY((D) => D.map(y2), { x: "date", y: v2, r: 2, fill: "#93748A", fillOpacity: 0.6 })),
        Plot.lineY(rentsData, Plot.mapY((D) => D.map(y2), { x: "date", y: v2, curve: "bump-x", stroke: "var(--syntax-entity)", strokeOpacity: 0.5 })),
        Plot.lineY(rentsData, { x: "date", y: v1, curve: "monotone-x", stroke: "var(--theme-foreground-focus)", tip: 'x', channels: {"Bonds lodged": "data_points"} }),
        Plot.areaY(rentsData, { x: "date", y: v1, curve: "monotone-x", fill: "var(--theme-foreground-focus)", fillOpacity: 0.1 }),
        Plot.dotY(rentsData, { x: "date", y: v1, fill: "var(--theme-foreground)", stroke: "var(--theme-background-alt)" })
    ]
});
```


<div class="card" >
    <p>
    Enter a postcode below or click on a location on the map to display data about that postcode.<br>
    Leave the field empty to display data for all of NSW.
    </p>
    ${postcodeInput}
    ${resize((width) => postcodeMap)}
</div>

<div class="card" >
    ${bedFilterInput}
    ${numBedsInput}
    <br><br>
    ${rentByBedroom}
</div>

### Access the data

See the [Access the data](/about#access-the-data) section on the about page.
