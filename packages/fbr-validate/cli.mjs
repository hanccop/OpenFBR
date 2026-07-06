#!/usr/bin/env node
// fbr-validate — CLI. Uso: fbr-validate <archivo.fbr.json> [más archivos...]
import { validateFile, schema } from "./lib.mjs";
import { argv, exit } from "node:process";

const files = argv.slice(2).filter((a) => !a.startsWith("-"));
const flags = new Set(argv.slice(2).filter((a) => a.startsWith("-")));

if (flags.has("-h") || flags.has("--help") || files.length === 0) {
  console.log(`fbr-validate — validador del formato FBR (Football Replay Format)

Uso:
  fbr-validate <archivo.fbr.json> [más archivos...]
  fbr-validate --version

Valida en dos capas: (1) estructura contra el JSON Schema y (2) invariantes
semánticos (referencias, cobertura de occupants, coherencia del marcador, etc.).
Sale con código 0 si todos los archivos son válidos, 1 si alguno falla.`);
  exit(files.length === 0 && !flags.has("--help") && !flags.has("-h") ? 1 : 0);
}
if (flags.has("--version") || flags.has("-v")) {
  console.log(`fbr-validate — schema ${schema.$id ? schema.$id : "FBR"} · perfil FBR 1.0`);
  exit(0);
}

const json = flags.has("--json");
const results = files.map((f) => ({ file: f, ...safeValidate(f) }));
function safeValidate(f) {
  try { return validateFile(f); }
  catch (e) { return { valid: false, schema: [], semantic: [`no se pudo leer: ${e.message}`] }; }
}

if (json) {
  console.log(JSON.stringify(results, null, 2));
} else {
  for (const r of results) {
    if (r.valid) {
      console.log(`\x1b[32m✓\x1b[0m ${r.file} — válido`);
    } else {
      console.log(`\x1b[31m✗\x1b[0m ${r.file} — inválido`);
      for (const m of r.schema) console.log(`    schema:    ${m}`);
      for (const m of r.semantic) console.log(`    semántica: ${m}`);
    }
  }
  const ok = results.filter((r) => r.valid).length;
  console.log(`\n${ok}/${results.length} válidos`);
}
exit(results.every((r) => r.valid) ? 0 : 1);
