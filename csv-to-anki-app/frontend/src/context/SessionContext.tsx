import React, { createContext, useState } from 'react';

interface SessionContextType {
  sessionId: string | null;
  setSessionId: React.Dispatch<React.SetStateAction<string | null>>;
  deckId: string | null;
  setDeckId: React.Dispatch<React.SetStateAction<string | null>>;
  cardCount: number;
  setCardCount: React.Dispatch<React.SetStateAction<number>>;
  deckName: string;
  setDeckName: React.Dispatch<React.SetStateAction<string>>;
  isEnriched: boolean;
  setIsEnriched: React.Dispatch<React.SetStateAction<boolean>>;
}

// Default empty context values
const defaultContextValue: SessionContextType = {
  sessionId: null,
  setSessionId: () => {},
  deckId: null,
  setDeckId: () => {},
  cardCount: 0,
  setCardCount: () => {},
  deckName: "Japanese Vocabulary Deck",
  setDeckName: () => {},
  isEnriched: false,
  setIsEnriched: () => {}
};

// Create the context
export const SessionContext = createContext<SessionContextType>(defaultContextValue);

// Create a provider component for this context
export const SessionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [deckId, setDeckId] = useState<string | null>(null);
  const [cardCount, setCardCount] = useState<number>(0);
  const [deckName, setDeckName] = useState<string>("Japanese Vocabulary Deck");
  const [isEnriched, setIsEnriched] = useState<boolean>(false);

  return (
    <SessionContext.Provider value={{ 
      sessionId, 
      setSessionId, 
      deckId, 
      setDeckId, 
      cardCount, 
      setCardCount, 
      deckName, 
      setDeckName,
      isEnriched,
      setIsEnriched
    }}>
      {children}
    </SessionContext.Provider>
  );
};
