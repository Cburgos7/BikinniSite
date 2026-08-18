// Compares local theme files against a live-theme file list fetched from the Admin API.
// Usage: node scripts/diff-theme-files.js <liveFilesJson>
const fs = require('fs');
const path = require('path');

const liveJsonPath = process.argv[2];
if (!liveJsonPath) {
  console.error('Usage: node scripts/diff-theme-files.js <liveFilesJson>');
  process.exit(1);
}

const live = new Set(
  JSON.parse(fs.readFileSync(liveJsonPath, 'utf8')).data.theme.files.nodes.map((n) => n.filename)
);

// Directories Shopify recognises as theme content.
const THEME_DIRS = ['assets', 'config', 'layout', 'locales', 'sections', 'snippets', 'templates', 'blocks'];

const localFiles = [];
for (const dir of THEME_DIRS) {
  if (!fs.existsSync(dir)) continue;
  const walk = (d) => {
    for (const entry of fs.readdirSync(d, { withFileTypes: true })) {
      const full = path.join(d, entry.name);
      if (entry.isDirectory()) walk(full);
      else localFiles.push(full.split(path.sep).join('/'));
    }
  };
  walk(dir);
}

const missing = localFiles.filter((f) => !live.has(f));

console.log(`local files: ${localFiles.length}`);
console.log(`live files:  ${live.size}`);
console.log(`\nMISSING FROM LIVE THEME (${missing.length}):`);
for (const f of missing) console.log('  ' + f);
