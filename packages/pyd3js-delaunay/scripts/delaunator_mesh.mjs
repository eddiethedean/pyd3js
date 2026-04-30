import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const delaunatorPath = path.resolve(
  __dirname,
  "../../../tools/oracle/node_modules/delaunator/index.js"
);
const { default: Delaunator } = await import(pathToFileURL(delaunatorPath).href);

const raw = readFileSync(0, "utf8");
const flat = JSON.parse(raw);
const d = new Delaunator(Float64Array.from(flat));
process.stdout.write(
  JSON.stringify({
    triangles: Array.from(d.triangles),
    halfedges: Array.from(d.halfedges),
    hull: Array.from(d.hull),
  })
);
