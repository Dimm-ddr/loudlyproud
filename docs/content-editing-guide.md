# Content Editing Guide for LoudlyProud

This guide will help you understand how to add and edit content using Decap CMS for the LoudlyProud website. The website is organized into collections of books in different languages, with each book having specific fields that need to be filled out.

## Accessing the CMS

1. Navigate to `/admin` on the website
2. Log in using your credentials
3. You'll see the main dashboard with different collections for each language

## Common Fields for All Books

Every book entry, regardless of language, has the following fields:

### Basic Information

- **Draft** (Required): Toggle whether the book is in draft mode
- **Title** (Required): The title for the book page URL (usually in English)
- **Slug** (Required): After entering the title, click the "Generate" button next to the Slug field to create a URL-friendly version of the title. You can still customize it after generation if needed.
- **Book Title** (Required): The actual title of the book as it should appear on the site
- **Authors** (Required): Add one or more authors. Click "+" to add multiple authors
- **Book Description**: Full description of the book, supports markdown formatting
- **Short Book Description**: Brief summary for book cards on the main page

### Book Details

- **Cover**: URL to the book's cover image
- **Cover Alt Text**: Accessibility description for the cover image
- **ISBN**: Main ISBN (ISBN-10 or ISBN-13)
- **Additional ISBNs**: List of ISBNs for other editions
- **Languages**: List of languages the book is available in
- **Page Count**: Number of pages (can use approximate format like "~300")
- **Publication Year**: Year of publication (can be approximate)
- **Goodreads Link**: URL to the book's Goodreads page

### Purchase Information

- **Where to Get**: List of stores where the book can be purchased
  - Store Name
  - Link
  - Date (optional)

## Language-Specific Collections

### English Books (`books_en`)

Additional fields:

- **Target Translation Languages**: List of languages the book should be translated into

### Russian Books (`books_ru`)

No additional specific fields

### Farsi Books (`books_fa`)

No additional specific fields

### Kurdish Books (`books_ku`)

No additional specific fields

## Best Practices

1. **Images**:

   - Always provide cover images as direct URLs
   - Ensure cover images are of good quality but not excessively large
   - Always provide alt text for accessibility

2. **Descriptions**:

   - Use markdown for formatting the full description
   - Keep short descriptions concise (1-2 sentences)
   - Include relevant quotes or reviews in the full description

3. **Links**:

   - Always verify that external links (Goodreads, purchase links) are working
   - Use complete URLs including 'https://'

4. **Translations**:
   - When adding books in English, specify target languages for translation
   - For translated books, ensure proper credit to translators

## Field Formatting Guidelines

1. **Authors and Translators**:

   - Add each author/translator separately
   - Include translations of names if available
   - Format: "Last Name, First Name" or cultural equivalent

2. **ISBN**:

   - Can include hyphens
   - Both ISBN-10 and ISBN-13 formats are accepted
   - For multiple editions, use the Additional ISBNs field

3. **Dates**:

   - Publication Year: Can be approximate (e.g., "~1950")
   - Store Dates: Use consistent format (e.g., "2024-01")

4. **URLs**:
   - Must start with 'http://' or 'https://'
   - Test links before saving

## Tips for Optimal Content

1. **Book Descriptions**:

   - Start with a compelling opening sentence
   - Include genre, themes, and target audience
   - Mention awards or recognition
   - Use markdown for formatting:

     ```markdown
     **Bold text**
     *Italic text*
     - Bullet points
     > Quotes
     ```

2. **Tags and Categorization**:

   - Use existing tags when possible
   - Create new tags sparingly
   - Consider searchability

3. **Translation Status**:
   - Keep translation status up to date
   - Include progress updates in descriptions

## Need Help?

If you encounter any issues or have questions:

1. Check this documentation first
2. Contact the technical team if you need further assistance
3. For urgent matters, use the emergency contact provided in your onboarding email

Remember: Changes are saved automatically, but you can always revert to previous versions if needed.
