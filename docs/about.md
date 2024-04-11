---
title: About
---

# About this site
## Info about the NSW Rental Bond Cheatsheet

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

The data for this page was originally sourced from the Fair Trading [rental bond data website](https://www.fairtrading.nsw.gov.au/about-fair-trading/rental-bond-data).

The original data has been transformed in order to reduce the download sizes and provide the visualisations. Download the transformed data below:

- <a id="holdingsLink" download>Download holdings</a>
- <a id="refundsTotalsLink" download>Download refunds totals</a>
- <a id="refundsPortionsLink" download>Download refunds portions</a>

```js
const holdingsURL = await FileAttachment('./data/holdings.csv').url();
const refundsTotalURL = await FileAttachment('./data/refunds-totals.csv').url();
const refundsPortionsURL = await FileAttachment('./data/refunds-portions.csv').url();

document.getElementById("holdingsLink").href = holdingsURL;
document.getElementById("refundsTotalsLink").href = refundsTotalURL;
document.getElementById("refundsPortionsLink").href = refundsPortionsURL;
```

<br>

## Information sources/acknowledgements

---

Observable Framework. (2024). Software library. https://observablehq.com/

This site was built with Observable

---

Tenants’ Union of NSW. (2024). Website. https://www.tenants.org.au/

This website was used as a primary information source for the [Cheatsheet](/) page

---

East Area Tenants Service. (2024). Website. https://eats.org.au

This website was used as a primary information source for the [Cheatsheet](/) page

---

Fair Trading NSW. (2024). Website. https://www.fairtrading.nsw.gov.au/about-fair-trading/rental-bond-data

This website was used as the source of all rental bonds data for the [Data](./data) page.

---

M Proctor. (2024). Australian Postcodes. GitHub repository. <https://github.com/matthewproctor/australianpostcodes>

This dataset of Australian postcodes was used to create a map of postcode locations for a data visualisation on the [Data](./data) page.

---

Australian Government - Department of Industry, Science and Resources. (2022). NSW State Boundary - Geoscape Administrative Boundaries. Dataset. <https://data.gov.au/data/dataset/nsw-state-boundary>

This dataset of NSW state boundaries was used to create a map of NSW for data visualisation on the [Data](./data) page.

---

M Bloch. (2024). Mapshaper. Software. https://mapshaper.org/, https://github.com/mbloch/mapshaper

This tool was used to simplify and convert the NSW state boundary shape file.
