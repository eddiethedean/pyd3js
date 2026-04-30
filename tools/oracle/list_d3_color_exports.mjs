import * as d3Color from "d3-color";

function stableRepr(v) {
  if (typeof v === "function") return "function";
  if (v === null) return "null";
  return typeof v;
}

const entries = Object.keys(d3Color)
  .sort()
  .map((k) => ({ name: k, type: stableRepr(d3Color[k]) }));

// Print a stable JSON payload so other tooling can reuse it.
console.log(JSON.stringify({ exports: entries }, null, 2));
