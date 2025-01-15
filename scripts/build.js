import * as esbuild from "esbuild";
import { copy } from "fs-extra";
import path from "path";
import { glob } from "glob";

// Copy Alpine.js to static directory
async function copyAlpineJs() {
  const source = path.resolve("node_modules/alpinejs/dist/cdn.js");
  const destination = path.resolve("static/js/alpine.js");
  await copy(source, destination);
  console.log("Alpine.js copied to static/js/");
}

// Get all TypeScript files from src/js
async function getEntryPoints() {
  const files = await glob("src/js/**/*.ts");
  return files;
}

async function build() {
  const entryPoints = await getEntryPoints();

  const buildOptions = {
    entryPoints,
    bundle: true,
    outdir: "static/js",
    format: "esm",
    sourcemap: process.env.NODE_ENV !== "production",
    target: ["es2020"],
    minify: process.env.NODE_ENV === "production",
    minifyIdentifiers: process.env.NODE_ENV === "production",
    minifySyntax: process.env.NODE_ENV === "production",
    minifyWhitespace: process.env.NODE_ENV === "production",
    treeShaking: true,
    drop: process.env.NODE_ENV === "production" ? ["console", "debugger"] : [],
  };

  try {
    if (process.argv.includes("--watch")) {
      await copyAlpineJs();
      const ctx = await esbuild.context(buildOptions);
      await ctx.watch();
      console.log("Watching for changes...");
    } else {
      await copyAlpineJs();
      await esbuild.build(buildOptions);
      console.log("Build complete");
    }
  } catch (err) {
    console.error("Build failed:", err);
    process.exit(1);
  }
}

build();
