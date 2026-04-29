import * as d3 from "d3";
import { JSDOM } from "jsdom";
import { readFileSync } from "fs";

const stdin = readFileSync(0, "utf8");

function toJSONSafe(x) {
  if (x !== x) return { __nan__: true };
  if (x === undefined) return { __undefined__: true };
  if (typeof x === "bigint") return Number(x);
  if (x === null || typeof x !== "object") return x;
  if (Array.isArray(x)) return x.map(toJSONSafe);
  if (x instanceof Date) return { __date__: x.toISOString() };
  if (x instanceof Map) return { __error__: "Map not serializable" };
  const o = {};
  for (const k of Object.keys(x).sort()) {
    o[k] = toJSONSafe(x[k]);
  }
  return o;
}

const req = JSON.parse(stdin || "{}");

if (req.op === "eval") {
  const fn = new Function("d3", "JSDOM", `"use strict"; return (${req.expr});`);
  const out = fn(d3, JSDOM);
  console.log(JSON.stringify(toJSONSafe(out)));
} else if (req.op === "run") {
  const fn = new Function("d3", "JSDOM", `"use strict"; ${req.code};`);
  const out = fn(d3, JSDOM);
  console.log(JSON.stringify(toJSONSafe(out)));
} else {
  console.log(JSON.stringify({ __error__: "unknown op", op: req.op }));
  process.exitCode = 1;
}
