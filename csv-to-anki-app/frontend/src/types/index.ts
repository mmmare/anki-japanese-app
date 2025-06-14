export interface JapaneseWord {
    id: number;
    word: string;
    meaning: string;
}

export interface AnkiDeck {
    title: string;
    words: JapaneseWord[];
}

export interface CsvUploadResponse {
    success: boolean;
    message: string;
    deck?: AnkiDeck;
}