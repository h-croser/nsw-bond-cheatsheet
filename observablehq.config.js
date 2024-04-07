// See https://observablehq.com/framework/config for documentation.
export default {
    // The project’s title; used in the sidebar and webpage titles.
    title: "NSW Bond Cheatsheet",

    // The pages and sections in the sidebar. If you don’t specify this option,
    // all pages will be listed in alphabetical order. Listing pages explicitly
    // lets you organize them into sections and have unlisted pages.
    pages: [
        {name: "Cheatsheet", path: "/index"},
        {name: "Data", path: "/data"},
        {name: "About", path: "/about"}
    ],

    // Some additional configuration options and their defaults:
    // theme: "coffee", // try "light", "dark", "slate", etc.
    style: "style.css",
    // header: "", // what to show in the header (HTML)
    // footer: "Built with Observable.", // what to show in the footer (HTML)
    // toc: true, // whether to show the table of contents
    // pager: true, // whether to show previous & next links in the footer
    // root: "docs", // path to the source root for preview
    // output: "dist", // path to the output root for build
    // search: true, // activate search
};
