---
title: Bond Data
theme: [coffee, parchment]
---
<script defer data-domain="nswrentalbonds.info" src="https://plausible.io/js/script.js"></script>

# Bond Data

**_Improving access to NSW bond data for tenants across NSW_**

The following has been created using data scraped from the Rental Bonds Online site.<br>
The data is published monthly, quarterly, and yearly, and covers postcodes within NSW.

```js
const nswStateOutline = FileAttachment("./data/nsw_outline.json").json();
const nswPostcodes = FileAttachment("./data/nsw_postcodes.csv").csv({typed: true});
const holdingsFile = FileAttachment("./data/holdings.parquet").parquet();
const refundsTotalsFile = FileAttachment("./data/refunds-totals.parquet").parquet();
const refundsPortionsFile = FileAttachment("./data/refunds-portions.parquet").parquet();
const medianRentsFile = FileAttachment("./data/median-rents.parquet").parquet();
```

```js
function castBigIntsToNumbers(arr) {
  return arr.map(obj => {
    const newObj = {};
    for (const key in obj) {
      if (typeof obj[key] === 'bigint') {
        newObj[key] = Number(obj[key]);
      } else {
        newObj[key] = obj[key];
      }
    }
    return newObj;
  });
}

const holdings = castBigIntsToNumbers(holdingsFile.toArray());
const refundsTotal = castBigIntsToNumbers(refundsTotalsFile.toArray());
const refundsPortions = castBigIntsToNumbers(refundsPortionsFile.toArray());
const medianRents = castBigIntsToNumbers(medianRentsFile.toArray());
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
const postcodeStr = postcode !== "" ? `postcode ${postcode}` : "all NSW";

const postcodeHoldings = holdings.filter(row => ((postcode == "") || (row.postcode.toString() === postcode)));
const postcodeRefundsTotals = refundsTotal.filter(row => ((postcode == "") || (row.postcode.toString() === postcode)));
const postcodeRefundsPortions = refundsPortions.filter(row => ((postcode == "") || (row.postcode.toString() === postcode)));
const postcodeMedianRents = medianRents.filter(row => ((postcode == "") || (row.postcode.toString() === postcode)));
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
const sumBonds = Plot.plot({
    title: `In ${postcodeStr}, how much bond money has been paid to landlords vs tenants?`,
    subtitle: "The sum of all bond funds returned to tenants or given to landlords after the bond is settled since January, 2022",
    marginTop: 20,
    marginBottom: 40,
    marginLeft: 80,

    color: {
        type: "categorical",
        domain: ["Landlords", "Tenants"],
        range: ["#fdcdac", "#b3e2cd"],
        legend: true
    },

    x: {
        label: "Recipient"
    },
    y: {
        label: "Bond kept (AUD$)",
        grid: true
    },
    marks: [
        Plot.ruleY([0]),
        Plot.axisY({tickFormat: (y) => "$" + y.toLocaleString()}),
        Plot.barY(postcodeRefundsTotals, Plot.groupZ({ y: "sum"}, { x: ["Tenants"], y: "tenant_payment", fill: "#b3e2cd", tip: "x"  })),
        Plot.text(postcodeRefundsTotals, Plot.groupZ({ text: "sum", y: "sum" }, { x: ["Tenants"], y: "tenant_payment", dy: -10, text: "tenant_payment", textAnchor: "middle" })),
        Plot.barY(postcodeRefundsTotals, Plot.groupZ({ y: "sum" }, { x: ["Landlords"], y: "agent_payment", fill: "#fdcdac", tip: "x" })),
        Plot.text(postcodeRefundsTotals, Plot.groupZ({ text: "sum", y: "sum" }, { x: ["Landlords"], y: "agent_payment", dy: -10, text: "agent_payment", textAnchor: "middle" }))
    ]
});
```

```js
const bondRecipients = Plot.plot({
    title: `In ${postcodeStr}, who received the bond at the end of the lease?`,
    subtitle: "Number of recipients of total bond since January, 2022",
    marginTop: 20,
    marginBottom: 40,
    marginLeft: 80,
    
    color: {
        type: "categorical",
        range: ["#fdcdac", "#ffffff", "#b3e2cd"],
        legend: true
    },

    x: {
        label: "Recipient"
    },
    y: {
        grid: true,
        label: "Count"
    },
    marks: [
        Plot.ruleY([0]),
        Plot.barY(postcodeRefundsPortions, Plot.groupX({ y: "sum" }, { x: "recipient", y: "bin_count", fill: "recipient", tip: true })),
        Plot.text(postcodeRefundsPortions, Plot.groupX({ text: "sum", y: "sum" }, { y: "bin_count", x: "recipient", dy: -10, text: "bin_count", textAnchor: "middle" }))
    ]
});
```

```js
const totalBonds = Plot.plot({
    title: `Total number of bonds held by RBO over time in ${postcodeStr}`,
    width: `${width}`,
    marginBottom: 50,
    marginLeft: 50,
    
    grid: true,
    x: {
        type: "time",
        label: "Date of recording",
        labelAnchor: "center"
    },
    y: {
        label: "Bonds held"
    },
    marks: [
        Plot.ruleY([0]),
        Plot.lineY(postcodeHoldings, Plot.groupX({ y: "sum" }, { x: "date", y: "bonds_held", curve: "monotone-x", stroke: "var(--theme-foreground-focus)" })),
        Plot.areaY(postcodeHoldings, Plot.groupX({ y: "sum" }, { x: "date", y: "bonds_held", curve: "monotone-x", fill: "var(--theme-foreground-focus)", fillOpacity: 0.1 })),
        Plot.dotY(postcodeHoldings, Plot.groupX({ y: "sum" }, { x: "date", y: "bonds_held", fill: "var(--theme-foreground)", stroke: "var(--theme-background-alt)", tip: "x" }))
    ]
});
```

```js
const newBonds = Plot.plot({
    title: `Number of bonds lodged per month in ${postcodeStr}`,
    width: `${width}`,
    marginBottom: 50,
    marginLeft: 50,
    
    grid: true,
    x: {
        type: "time",
        label: "Month of lodgement",
        labelAnchor: "center"
    },
    y: {
        label: "Bonds lodged"
    },
    marks: [
        Plot.ruleY([0]),
        Plot.lineY(postcodeMedianRents, Plot.groupX({ y: "sum" }, { x: "date", y: "data_points", curve: "monotone-x", stroke: "var(--theme-foreground-focus)" })),
        Plot.areaY(postcodeMedianRents, Plot.groupX({ y: "sum" }, { x: "date", y: "data_points", curve: "monotone-x", fill: "var(--theme-foreground-focus)", fillOpacity: 0.1 })),
        Plot.dotY(postcodeMedianRents, Plot.groupX({ y: "sum" }, { x: "date", y: "data_points", fill: "var(--theme-foreground)", stroke: "var(--theme-background-alt)", tip: "x" }))
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
    ${sumBonds}
</div>
<div class="card" >
    ${bondRecipients}
</div>
<div class="card" >
    ${resize((width) => totalBonds)}
</div>
<div class="card" >
    ${resize((width) => newBonds)}
</div>
<br>

### Access the data

See the [Access the data](/about#access-the-data) section on the about page.
