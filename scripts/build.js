import * as esbuild from "esbuild";
import { copy } from "fs-extra";
import path from "path";
import { glob } from "glob";

// Copy Alpine.js to static directory
async function copyAlpineJs() {
  const isProd = process.env.NODE_ENV === "production";
  const sourceFile = isProd ? "cdn.min.js" : "cdn.js";
  const source = path.resolve(`node_modules/alpinejs/dist/${sourceFile}`);
  const destination = path.resolve("static/js/alpine.js");
  await copy(source, destination);
  console.log(`Copied Alpine.js (${sourceFile}) to static/js/alpine.js`);
}

// Get all TypeScript files from src/js
async function getEntryPoints() {
  const files = await glob("src/js/**/*.ts");
  return files;
}

async function build() {
  const entryPoints = await getEntryPoints();
  const isProd = process.env.NODE_ENV === "production";

  const buildOptions = {
    entryPoints,
    bundle: true,
    outdir: "static/js",
    format: "esm",
    sourcemap: !isProd,
    target: ["es2020"],
    minify: isProd,
    minifyIdentifiers: isProd,
    minifySyntax: isProd,
    minifyWhitespace: isProd,
    treeShaking: true,
    drop: isProd ? ["console", "debugger"] : [],
    splitting: true,
    chunkNames: "chunks/[name]-[hash]",
    metafile: isProd,
    legalComments: "none",
    define: {
      "process.env.NODE_ENV": JSON.stringify(
        process.env.NODE_ENV || "development",
      ),
    },
  };

  try {
    if (process.argv.includes("--watch")) {
      await copyAlpineJs();
      const ctx = await esbuild.context(buildOptions);
      await ctx.watch();
      console.log("Watching for changes...");
    } else {
      await copyAlpineJs();
      const result = await esbuild.build(buildOptions);

      if (isProd && result.metafile) {
        // Log bundle size analysis
        const analysis = await esbuild.analyzeMetafile(result.metafile);
        console.log("Bundle size analysis:");
        console.log(analysis);
      }

      console.log("Build complete");
    }
  } catch (err) {
    console.error("Build failed:", err);
    process.exit(1);
  }
}

build();
