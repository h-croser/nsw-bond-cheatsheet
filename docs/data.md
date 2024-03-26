---
title: Data
---
# Bond Data

```js
// const lodgements = FileAttachment("./data/lodgements.csv").csv({typed: true});
const refunds = FileAttachment("./data/refunds-optimised.csv").csv({typed: true});
```

```js
const postcode = view(
    Inputs.text({
        type: "number",
        label: "Postcode",
        placeholder: "All NSW",
        submit: true
    })
);
```

```js
const postcode_refunds = refunds.filter(row => ((postcode == "") || (row.postcode.toString() === postcode)));
```

```js
display(Plot.legend({
    color:{
        type:"categorical",
        domain: ["Tenants", "Landlords/agents"],
        range: ["white", "orange"]

    }
}));
display(Plot.plot({
    marginTop: 20,
    marginRight: 100,
    marginBottom: 30,
    marginLeft: 100,
    width: 1000,
    
    title: "Cumulative bond held over time by tenants and landlords",
    grid: true,
    x: { type: "time", label: "Date" },
    y: { label: "Bond kept (AUD)" },
    marks: [
        Plot.ruleY([0]),
        Plot.axisY({tickFormat: (x) => "$" + x.toLocaleString()}),
        Plot.lineY(postcode_refunds, Plot.mapY("cumsum", { label: "Tenants", stroke: "white", y: "tenant_payment", x: "date_paid", markerEnd: "dot" })),
        Plot.lineY(postcode_refunds, Plot.mapY("cumsum", { label: "Landlords/agents", stroke: "orange", y: "agent_payment", x: "date_paid", markerEnd: "dot" })),
        Plot.text(postcode_refunds, Plot.selectLast( Plot.mapY("cumsum", { y: "tenant_payment", x: "date_paid", text: "${tenantSum}", textAnchor: "start", dx: 3 })))
    ]
}));
```
