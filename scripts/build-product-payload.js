// Builds a productSet GraphQL payload from a product definition JSON file.
// Usage: node scripts/build-product-payload.js <productDefJson> <outFile>
//
// The definition file is plain JSON:
// {
//   "id": "gid://shopify/Product/...",        // omit to create a new product
//   "title": "...", "handle": "...", "descriptionHtml": "...",
//   "vendor": "...", "productType": "...", "tags": ["new"],
//   "status": "ACTIVE",
//   "sizes": ["XS","S"], "colors": ["Noir","Coral"],
//   "price": "68.00", "compareAtPrice": "88.00"
// }
const fs = require('fs');

const [defPath, outFile] = process.argv.slice(2);
if (!defPath || !outFile) {
  console.error('Usage: node scripts/build-product-payload.js <productDefJson> <outFile>');
  process.exit(1);
}

const def = JSON.parse(fs.readFileSync(defPath, 'utf8'));

// Shopify requires one variant per option-value combination.
const variants = [];
for (const color of def.colors) {
  for (const size of def.sizes) {
    const variant = {
      optionValues: [
        { optionName: 'Size', name: size },
        { optionName: 'Color', name: color },
      ],
      price: def.price,
    };
    if (def.compareAtPrice) variant.compareAtPrice = def.compareAtPrice;
    variants.push(variant);
  }
}

const input = {
  title: def.title,
  handle: def.handle,
  descriptionHtml: def.descriptionHtml,
  vendor: def.vendor,
  productType: def.productType,
  tags: def.tags,
  status: def.status || 'ACTIVE',
  productOptions: [
    { name: 'Size', values: def.sizes.map((s) => ({ name: s })) },
    { name: 'Color', values: def.colors.map((c) => ({ name: c })) },
  ],
  variants,
};
if (def.id) input.id = def.id;

const payload = {
  query: `mutation setProduct($input: ProductSetInput!) {
    productSet(synchronous: true, input: $input) {
      product {
        id
        handle
        options { name optionValues { name } }
        variants(first: 50) { nodes { title price compareAtPrice } }
      }
      userErrors { field message }
    }
  }`,
  variables: { input },
};

fs.writeFileSync(outFile, JSON.stringify(payload));
console.log(`payload written: ${outFile} — ${variants.length} variants (${def.sizes.length} sizes x ${def.colors.length} colors)`);
