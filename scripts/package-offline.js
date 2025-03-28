import fs from 'fs-extra';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function packageOfflineBuild() {
    try {
        console.log('Packaging offline build...');

        // Ensure the archives directory exists
        await fs.ensureDir('archives');

        // Get current date for the zip filename
        const date = new Date();
        const dateString = date.toISOString().split('T')[0];
        const zipFilename = `loudlyproud-offline-${dateString}.zip`;
        const zipPath = path.join('archives', zipFilename);

        // Create a README file for the offline version
        const readmePath = path.join('archives', 'offline', 'README.txt');
        const readmeContent = `Loudly Proud - Offline Version
Created: ${date.toLocaleString()}

This is an offline version of the Loudly Proud website.
To use it, simply open the index.html file in your web browser.

All content and functionality should work without an internet connection.
`;

        await fs.writeFile(readmePath, readmeContent);

        // Create the zip file
        console.log(`Creating zip file: ${zipPath}`);

        if (process.platform === 'win32') {
            // Windows - use PowerShell to create zip
            await execAsync(`powershell -Command "Compress-Archive -Path '.\\archives\\offline\\*' -DestinationPath '.\\${zipPath}' -Force"`);
        } else {
            // Unix-like systems - use zip command
            await execAsync(`cd archives/offline && zip -r ../../${zipPath} ./*`);
        }

        console.log(`Offline package created successfully: ${zipPath}`);
    } catch (error) {
        console.error('Error packaging offline build:', error);
        process.exit(1);
    }
}

packageOfflineBuild();