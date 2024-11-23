export interface Book {
  title: string;
  authors: string[];
  translators?: string[];
  bookTitle: string;
  book_description: string;
  short_book_description?: string;
  cover?: string;
  isbn: string;
  additional_isbns?: string[];
  languages: string[];
  page_count: number | string;
  publication_year: string;
  russian_translation_status: 'exists' | 'might_exist' | 'unknown' | 'unlikely_to_exist' | 'does_not_exist';
  russian_audioversion: 'yes' | 'no';
  tags: string[];
  goodreads_link?: string;
  buy_link?: string;
  series?: string;
  publishers?: string[];
  where_to_get?: {
    store: string;
    link: string;
    date: string;
  }[];
}

export interface TagStyle {
  bg: string;
  text: string;
  dark: {
    bg: string;
    text: string;
  };
}

export interface TagColors {
  [key: string]: TagStyle;
}
