---
title: Data
theme: [coffee, parchment, alt]
toc: true
---

# Bond Data

**_Improving access to NSW bond data for tenants across NSW_**

<br>

```js
const nsw_state_outline = FileAttachment("./data/nsw_outline.json").json();
const nsw_postcodes = FileAttachment("./data/nsw_postcodes.csv").csv({typed: true});
const holdings = FileAttachment("./data/holdings.csv").csv({typed: true});
const refunds_totals = FileAttachment("./data/refunds-totals.csv").csv({typed: true});
const refunds_portions = FileAttachment("./data/refunds-portions.csv").csv({typed: true});
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
const curr_postcode = nsw_postcodes.filter(row => ((postcode == "") || (row.postcode.toString() === postcode)));
const postcodeStr = postcode !== "" ? "postcode " + postcode : "all NSW";

const postcode_holdings = holdings.filter(row => ((postcode == "") || (row.postcode.toString() === postcode)));
const postcode_refunds_totals = refunds_totals.filter(row => ((postcode == "") || (row.postcode.toString() === postcode)));
const postcode_refunds_portions = refunds_portions.filter(row => ((postcode == "") || (row.postcode.toString() === postcode)));
```

```js
const postcodeMap = Plot.plot({
    width: `${width}`,

    projection: {
        type: "reflect-y",
        domain: nsw_state_outline
    },
    marks: [
        Plot.geo(nsw_state_outline),
        Plot.dot(curr_postcode, {x: 'long', y: 'lat', r: 1, fill: 'var(--theme-foreground-focus)', tip: true, title: (d) => `Postcode: ${d.postcode} \nLocality: ${d.locality}`}),
        Plot.dot(curr_postcode, Plot.pointer({x: "long", y: "lat", fill: "#b3e2cd", r: 3}))
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
    title: `In ${postcodeInput.value !== "" ? postcodeInput.value : "all NSW"}, how much bond money has been paid to landlords vs tenants?`,
    subtitle: "The sum of all bond funds returned to tenants or given to landlords after the bond is settled, since January, 2021",
    marginTop: 20,
    marginRight: 40,
    marginBottom: 40,
    marginLeft: 100,

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
        Plot.barY(postcode_refunds_totals, Plot.groupZ({ y: "sum"}, { x: ["Tenants"], y: "tenant_payment", fill: "#b3e2cd", tip: "x"  })),
        Plot.barY(postcode_refunds_totals, Plot.groupZ({ y: "sum" }, { x: ["Landlords"], y: "agent_payment", fill: "#fdcdac", tip: "x" }))
    ]
});
```

```js
const bondRecipients = Plot.plot({
    title: `In ${postcodeStr}, who received the bond at the end of the lease?`,
    subtitle: "Recipients of total bond since January, 2021",
    marginTop: 20,
    marginRight: 20,
    marginBottom: 40,
    marginLeft: 100,
    
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
        Plot.barY(postcode_refunds_portions, Plot.groupX({ y: "sum" }, { x: "recipient", y: "bin_count", fill: "recipient", tip: true })),
        Plot.text(postcode_refunds_portions, Plot.groupX({ text: "sum", y: "sum" }, { y: "bin_count", x: "recipient", dy: -10, text: "bin_count", textAnchor: "middle" }))
    ]
});
```

```js
const totalFunds = Plot.plot({
    title: `Total number of bonds held by RBO over time for ${postcodeInput.value !== "" ? postcodeInput.value : "all NSW"}`,
    marginTop: 30,
    marginRight: 20,
    marginBottom: 40,
    marginLeft: 100,
    
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
        Plot.lineY(postcode_holdings, Plot.groupX({ y: "sum" }, { x: "date", y: "bonds_held", stroke: "var(--theme-foreground-focus)" })),
        Plot.areaY(postcode_holdings, Plot.groupX({ y: "sum" }, { x: "date", y: "bonds_held", fill: "var(--theme-foreground-focus)", fillOpacity: 0.1 })),
        Plot.dotY(postcode_holdings, Plot.groupX({ y: "sum" }, { x: "date", y: "bonds_held", fill: "var(--theme-foreground)", stroke: "var(--theme-background-alt)", tip: "x" }))
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
    ${totalFunds}
</div>
<br>

### Access the data

See the [Access the data](/about#access-the-data) section on the about page.