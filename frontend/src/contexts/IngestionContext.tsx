import React, { createContext, useContext, useState } from 'react';

type IngestionContextType = {
  isIngestingGlobal: boolean;
  setIsIngestingGlobal: (val: boolean) => void;
};

const IngestionContext = createContext<IngestionContextType | undefined>(undefined);

export function IngestionProvider({ children }: { children: React.ReactNode }) {
  const [isIngestingGlobal, setIsIngestingGlobal] = useState(false);

  return (
    <IngestionContext.Provider value={{ isIngestingGlobal, setIsIngestingGlobal }}>
      {children}
    </IngestionContext.Provider>
  );
}

export function useIngestion() {
  const context = useContext(IngestionContext);
  if (context === undefined) {
    throw new Error('useIngestion must be used within an IngestionProvider');
  }
  return context;
}
