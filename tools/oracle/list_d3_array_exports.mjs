import * as d3Array from "d3-array";

function stableRepr(v) {
  if (typeof v === "function") return "function";
  if (v === null) return "null";
  return typeof v;
}

const entries = Object.keys(d3Array)
  .sort()
  .map((k) => ({ name: k, type: stableRepr(d3Array[k]) }));

// Print a stable JSON payload so other tooling can reuse it.
console.log(JSON.stringify({ exports: entries }, null, 2));

