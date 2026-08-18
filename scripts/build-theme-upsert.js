// Builds a GraphQL themeFilesUpsert payload for one or more theme files.
// Usage: node scripts/build-theme-upsert.js <themeGid> <outFile> <file...>
const fs = require('fs');

const [themeId, outFile, ...files] = process.argv.slice(2);

if (!themeId || !outFile || files.length === 0) {
  console.error('Usage: node scripts/build-theme-upsert.js <themeGid> <outFile> <file...>');
  process.exit(1);
}

const payload = {
  query: `mutation upsert($themeId: ID!, $files: [OnlineStoreThemeFilesUpsertFileInput!]!) {
    themeFilesUpsert(themeId: $themeId, files: $files) {
      upsertedThemeFiles { filename }
      userErrors { filename code message }
    }
  }`,
  variables: {
    themeId,
    files: files.map((filename) => ({
      filename,
      body: { type: 'TEXT', value: fs.readFileSync(filename, 'utf8') },
    })),
  },
};

fs.writeFileSync(outFile, JSON.stringify(payload));
console.log(`payload written: ${outFile} (${files.length} file(s))`);
