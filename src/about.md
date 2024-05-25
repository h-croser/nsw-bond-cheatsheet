---
title: About
theme: [coffee, parchment]
---

# About this site

**_Info about the NSW Rental Bond Cheatsheet_**

<br>

## Purpose

This site was written for the purpose of:
1. helping renters in NSW keep their bond
2. providing greater transparency of Rental Bonds Online data

<br>

## Author

This site was written by Hamish Croser. Please reach out if you have suggestions or corrections.

Contact email - [nswbondcheatsheet@gmail.com](mailto:nswbondcheatsheet@gmail.com)
<br>
Github - <https://github.com/h-croser>

<br>

## Source code

<https://github.com/h-croser/nsw-bond-cheatsheet>

<br>

## Access the data

The data for this page was originally sourced from the Fair Trading [rental bond data website](https://www.nsw.gov.au/housing-and-construction/rental-forms-surveys-and-data/rental-bond-data).

The original data has been transformed in order to reduce the download sizes and provide the visualisations. Download the transformed data below:

- <a id="holdingsLink" download>Download holdings</a>
- <a id="refundsTotalsLink" download>Download refunds totals</a>
- <a id="refundsPortionsLink" download>Download refunds portions</a>
- <a id="allMedianRentsLink" download>Download all median rents</a>
- <a id="bedroomMedianRentsLink" download>Download median rents by bedroom</a>

```js
const holdingsURL = await FileAttachment('./data/holdings.csv').url();
const refundsTotalURL = await FileAttachment('./data/refunds-totals.csv').url();
const refundsPortionsURL = await FileAttachment('./data/refunds-portions.csv').url();
const allMedianRentsURL = await FileAttachment('./data/median-rents.csv').url();
const bedroomMedianRentsURL = await FileAttachment('./data/median-rents-bedrooms.csv').url();

document.getElementById("holdingsLink").href = holdingsURL;
document.getElementById("holdingsLink").download = "holdings.csv";
document.getElementById("refundsTotalsLink").href = refundsTotalURL;
document.getElementById("refundsTotalsLink").download = "refunds-totals.csv";
document.getElementById("refundsPortionsLink").href = refundsPortionsURL;
document.getElementById("refundsPortionsLink").download = "refunds-portions.csv";
document.getElementById("allMedianRentsLink").href = allMedianRentsURL;
document.getElementById("allMedianRentsLink").download = "median-rents.csv";
document.getElementById("bedroomMedianRentsLink").href = bedroomMedianRentsURL;
document.getElementById("bedroomMedianRentsLink").download = "median-rents-bedrooms.csv";
```

<br>

## Information sources

---

Tenants’ Union of NSW. (2024). Website. <https://www.tenants.org.au>

This website was used as a primary information source for the [Cheatsheet](/) page

---

East Area Tenants Service. (2024). Website. <https://eats.org.au>

This website was used as a primary information source for the [Cheatsheet](/) page

---

Rental bond data. (2024). Website. <https://www.nsw.gov.au/housing-and-construction/rental-forms-surveys-and-data/rental-bond-data>

This website was used as the source of all data for the [Bond Data](./bond-data) and [Rent Data](./rent-data) pages.

---

M Proctor. (2024). Australian Postcodes. GitHub repository. <https://github.com/matthewproctor/australianpostcodes>

This dataset of Australian postcodes was used to create a map of postcode locations for a data visualisation on the [Bond Data](./bond-data) and [Rent Data](./rent-data) pages.

---

Australian Government - Department of Industry, Science and Resources. (2022). NSW State Boundary - Geoscape Administrative Boundaries. Dataset. <https://data.gov.au/data/dataset/nsw-state-boundary>

This dataset of NSW state boundaries was used to create a map of NSW for data visualisation on the [Bond Data](./bond-data) and [Rent Data](./rent-data) pages.

---

## Acknowledgements

---

Observable Framework. (2024). Software library. <https://observablehq.com/framework>

This site was built with Observable

---

M Bloch. (2024). Mapshaper. Software. <https://mapshaper.org/>, <https://github.com/mbloch/mapshaper>

This tool was used to simplify and convert the NSW state boundary shape file.

---

Zac Agius. Site reviewer. <https://zacagius.cargo.site>

Zac provided valuable feedback on the usability and presentation of this site
