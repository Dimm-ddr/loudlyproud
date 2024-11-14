const fs = require('fs');
const path = require('path');
const archiver = require('archiver');

async function createOfflineBundle() {
    const output = fs.createWriteStream('offline-bundle.zip');
    const archive = archiver('zip');

    output.on('close', () => {
        console.log('Offline bundle created successfully');
    });

    archive.pipe(output);

    // Add required directories
    archive.directory('public/', 'public');
    archive.directory('node_modules/', 'node_modules');
    archive.directory('static/', 'static');

    // Add required files
    archive.file('package.json', { name: 'package.json' });
    archive.file('hugo.toml', { name: 'hugo.toml' });

    // Add README with offline usage instructions
    const readmeContent = `
    # Offline Usage Instructions

    1. Extract this archive
    2. Run 'hugo server --offline'
    3. Access the site at http://localhost:1313

    Note: External book covers will not be available in offline mode.
    `;

    archive.append(readmeContent, { name: 'README.md' });

    await archive.finalize();
}

createOfflineBundle().catch(console.error); 