// Build-time only. Bundles vendored front-end deps (xterm.js + addon-fit)
// into app/interface/static/js/vendor/, which IS checked into git and is
// what the app actually serves. Run `npm install && npm run build` from
// this directory after bumping a dependency in package.json.
const esbuild = require('esbuild');
const path = require('path');

const outdir = path.join(__dirname, 'vendor');

async function build() {
  // JS bundle: xterm + addon-fit, minified, attached to window.
  await esbuild.build({
    entryPoints: [path.join(__dirname, 'src', 'xterm-entry.js')],
    bundle: true,
    minify: true,
    format: 'iife',
    outfile: path.join(outdir, 'xterm.bundle.js'),
  });

  // CSS bundle: xterm's stylesheet, minified.
  await esbuild.build({
    entryPoints: [
      path.join(__dirname, 'node_modules', '@xterm', 'xterm', 'css', 'xterm.css'),
    ],
    bundle: true,
    minify: true,
    outfile: path.join(outdir, 'xterm.bundle.css'),
  });

  console.log(`Built vendor bundle -> ${outdir}`);
}

build().catch((err) => {
  console.error(err);
  process.exit(1);
});
