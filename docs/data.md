---
title: Data
---
# Bond Data

```js
const lodgements = FileAttachment("./data/lodgements.csv").csv({typed: true});
const refunds = FileAttachment("./data/refunds.csv").csv({typed: true});
```

```js
display(lodgements);
display(refunds);
```
