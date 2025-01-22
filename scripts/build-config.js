const fs = require("fs");
const yaml = require("js-yaml");

// Load YAML files
const configBase = yaml.load(
  fs.readFileSync("static/admin/config_base.yml", "utf8"),
);
const commonFields = yaml.load(
  fs.readFileSync("static/admin/common_fields.yml", "utf8"),
);

// Function to merge fields
function mergeFields(commonFields, collectionFields) {
  const mergedFields = [...commonFields.book_fields];

  collectionFields.forEach((field) => {
    if (field.name === "params") {
      const paramsField = mergedFields.find((f) => f.name === "params");
      if (paramsField) {
        paramsField.fields.push(...field.fields);
      } else {
        mergedFields.push(field);
      }
    } else {
      mergedFields.push(field);
    }
  });

  return mergedFields;
}

// Process each collection
const collections = ["books_en", "books_ru", "books_fa", "books_ku"];
const mergedCollections = collections.map((collectionName) => {
  const collection = yaml.load(
    fs.readFileSync(`static/admin/collections/${collectionName}.yml`, "utf8"),
  );
  collection.fields = mergeFields(commonFields, collection.fields);
  return collection;
});

// Combine everything into a single config
const finalConfig = {
  ...configBase,
  collections: mergedCollections,
};

// Write the final config to a file
fs.writeFileSync("static/admin/config.yml", yaml.dump(finalConfig));

console.log("Merged configuration written to static/admin/config.yml");
