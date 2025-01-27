import fs from "fs";
import yaml from "js-yaml";

try {
  // Load YAML files
  const configBase = yaml.load(
    fs.readFileSync("static/admin/config_base.yml", "utf8"),
  );
  const commonFields = yaml.load(
    fs.readFileSync("static/admin/common_fields.yml", "utf8"),
  );

  // Function to merge fields
  function mergeFields(commonFields, collectionFields = []) {
    // Start with a deep copy of common fields
    const mergedFields = JSON.parse(JSON.stringify(commonFields.book_fields));

    // If no collection-specific fields, return common fields
    if (!collectionFields || collectionFields.length === 0) {
      return mergedFields;
    }

    // Find or create params field in merged fields
    let paramsField = mergedFields.find((f) => f.name === "params");
    if (!paramsField) {
      paramsField = {
        label: "Params",
        name: "params",
        widget: "object",
        required: true,
        fields: [],
      };
      mergedFields.push(paramsField);
    }

    // Process collection-specific fields
    collectionFields.forEach((field) => {
      if (field.name === "params") {
        // Merge params fields
        field.fields.forEach((paramField) => {
          const existingField = paramsField.fields.find(
            (f) => f.name === paramField.name,
          );
          if (!existingField) {
            paramsField.fields.push(paramField);
          }
        });
      } else {
        // If it's not already in params, add it to params
        const existingField = paramsField.fields.find(
          (f) => f.name === field.name,
        );
        if (!existingField) {
          paramsField.fields.push(field);
        }
      }
    });

    return mergedFields;
  }

  // Process each collection
  const collections = ["books_en", "books_ru", "books_fa", "books_ku"];
  const mergedCollections = collections
    .map((collectionName) => {
      try {
        const collectionPath = `static/admin/collections/${collectionName}.yml`;
        const collection = yaml.load(fs.readFileSync(collectionPath, "utf8"));

        // Ensure collection has a fields array
        collection.fields = collection.fields || [];

        // Merge fields
        collection.fields = mergeFields(commonFields, collection.fields);
        return collection;
      } catch (err) {
        console.error(`Error processing ${collectionName}:`, err.message);
        return null;
      }
    })
    .filter(Boolean); // Remove any null collections

  // Combine everything into a single config
  const finalConfig = {
    ...configBase,
    collections: mergedCollections,
  };

  // Write the final config to a file
  fs.writeFileSync(
    "static/admin/config.yml",
    yaml.dump(finalConfig, { noRefs: true }),
  );

  console.log(
    "Successfully merged configuration written to static/admin/config.yml",
  );
} catch (err) {
  console.error("Error during config build:", err.message);
  process.exit(1);
}
