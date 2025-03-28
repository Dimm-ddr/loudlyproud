import fs from 'fs-extra';
import path from 'path';
import { glob } from 'glob';

async function fixOfflinePaths() {
    try {
        console.log('Fixing paths in offline build...');

        const offlineDir = path.join('archives', 'offline');

        // Find all HTML files
        const htmlFiles = await glob('**/*.html', { cwd: offlineDir });

        for (const htmlFile of htmlFiles) {
            const filePath = path.join(offlineDir, htmlFile);
            let content = await fs.readFile(filePath, 'utf8');

            // Fix font paths (change /fonts/ to ./fonts/)
            content = content.replace(/url\(\/fonts\//g, 'url(./fonts/');

            // Fix other absolute paths if needed
            content = content.replace(/src="\/js\//g, 'src="./js/');
            content = content.replace(/src="\/css\//g, 'src="./css/');
            content = content.replace(/href="\/css\//g, 'href="./css/');
            content = content.replace(/src="\/images\//g, 'src="./images/');
            content = content.replace(/href="\/images\//g, 'href="./images/');

            await fs.writeFile(filePath, content);
        }

        console.log('Path fixing complete!');
    } catch (error) {
        console.error('Error fixing offline paths:', error);
        process.exit(1);
    }
}

fixOfflinePaths();