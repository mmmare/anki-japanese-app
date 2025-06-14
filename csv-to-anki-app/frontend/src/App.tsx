import React, { useState, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { Box, Container, Flex, Heading, Image, useColorModeValue, useToast, Tabs, TabList, TabPanels, Tab, TabPanel } from '@chakra-ui/react';
import CsvUpload from './components/CsvUpload';
import AnkiControls from './components/AnkiControls';
import JapaneseWordLookup from './components/JapaneseWordLookup';
import FieldMappingPage from './components/FieldMappingPage';
import { SessionContext, SessionProvider } from './context/SessionContext';

function AppContent() {
  const { 
    sessionId, setSessionId, 
    deckId, setDeckId, 
    cardCount, setCardCount, 
    deckName, setDeckName, 
    isEnriched, setIsEnriched 
  } = useContext(SessionContext);
  const navigate = useNavigate();
  const toast = useToast();

  // Define handler functions required by AnkiControls
  const handleCreateDeck = async (
    options = { enrichCards: false, includeAudio: false, includeExamples: false, includeExampleAudio: false, useCore2000: false },
    onProgress?: (progress: { processed: number, total: number, status: string }) => void
  ) => {
    if (!sessionId) {
      toast({
        title: "Session error",
        description: "No CSV file has been uploaded yet",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
      navigate('/');
      return;
    }
    
    try {
      // Use the API service to create the deck with progress tracking
      const { createDeck } = await import('./services/api');
      
      // Get field mapping from session storage if available
      let fieldMapping = null;
      const savedMapping = sessionStorage.getItem('csvFieldMapping');
      if (savedMapping) {
        try {
          fieldMapping = JSON.parse(savedMapping);
          console.log("Using custom field mapping:", fieldMapping);
        } catch (e) {
          console.error("Error parsing field mapping from session storage:", e);
        }
      }
      
      const data = await createDeck(
        sessionId,
        deckName || "Japanese Vocabulary Deck",
        options,
        fieldMapping, // Use the field mapping from session storage
        onProgress
      );
      
      console.log('Deck created:', data);
      
      setDeckId(data.deck_id);
      
      // Update card count in context if available
      if (data.card_count) {
        setCardCount(data.card_count);
      }
      
      // Update enriched status
      if (data.enriched !== undefined) {
        setIsEnriched(data.enriched);
      }
      
      return data;
    } catch (error) {
      console.error('Error creating deck:', error);
      toast({
        title: "Failed to create deck",
        description: "There was an error creating your Anki deck",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
      throw error;
    }
  };

  const handleDownloadDeck = async () => {
    if (!deckId) {
      toast({
        title: "Deck error",
        description: "No deck has been created yet",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
      return;
    }
    
    try {
      console.log(`Attempting to download deck with ID: ${deckId}`);
      
      toast({
        title: "Preparing download",
        description: "Getting your Anki deck ready for download...",
        status: "info",
        duration: 3000,
        isClosable: true,
      });
      
      // Add a small delay to allow the UI to update with the progress bar
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Check if the deck exists and server is ready before downloading
      try {
        console.log(`Checking if deck exists: ${deckId}`);
        const checkResponse = await fetch(`http://localhost:8000/api/deck/${deckId}`, {
          method: 'HEAD',
        });
        
        if (checkResponse.ok) {
          console.log(`Deck exists, proceeding with download`);
        } else {
          console.error(`Deck check failed with status: ${checkResponse.status}`);
          throw new Error(`Failed to verify deck exists: ${checkResponse.statusText}`);
        }
      } catch (error) {
        console.error("Error checking if deck exists:", error);
        toast({
          title: "Download error",
          description: "Could not verify deck exists on server. Try creating the deck again.",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
        return;
      }
      
      // Use the API service for downloading to handle errors better
      try {
        const { downloadDeck } = await import('./services/api');
        await downloadDeck(deckId);
        
        // Give time for the browser to register the download before showing success
        setTimeout(() => {
          toast({
            title: "Download started",
            description: "Your Anki deck is downloading. Import it into Anki using File > Import.",
            status: "success",
            duration: 5000,
            isClosable: true,
          });
        }, 1000);
      } catch (downloadError) {
        console.error("Download error:", downloadError);
        toast({
          title: "Download failed",
          description: "There was an error downloading your Anki deck. Please try again.",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      }
      
    } catch (error) {
      console.error('Error downloading deck:', error);
      toast({
        title: "Download failed",
        description: "There was an error downloading your Anki deck",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
      throw error;
    }
  };

  // Colors for light/dark mode support
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box minH="100vh" bg={useColorModeValue('gray.50', 'gray.900')}>
        <Box 
          as="header" 
          py={4} 
          bg="brand.600" 
          color="white" 
          boxShadow="md"
        >
          <Container maxW="container.xl">
            <Flex align="center" justify="space-between">
              <Heading size="lg" fontWeight="bold">
                日本語 Anki Deck Generator
              </Heading>
              <Box>
                {/* Optional: Add a Japanese flag or icon here */}
                {/* <Image h="30px" src="/japan-flag.svg" alt="Japanese Flag" /> */}
              </Box>
            </Flex>
          </Container>
        </Box>

        <Container 
          maxW="container.xl" 
          py={8}
        >
          <Box 
            bg={bgColor}
            borderRadius="lg" 
            boxShadow="lg" 
            border="1px"
            borderColor={borderColor}
            overflow="hidden"
            p={4}
          >
            <Tabs 
              isFitted 
              variant="enclosed-colored" 
              colorScheme="brand" 
              mb={4}
            >
              <TabList>
                <Tab>CSV to Anki Deck</Tab>
                <Tab>Japanese Word Lookup</Tab>
              </TabList>
              <TabPanels>
                <TabPanel p={0}>
                  <Routes>
                    <Route path="/" element={<CsvUpload />} />
                    <Route path="/mapping" element={<FieldMappingPage />} />
                    <Route path="/controls" element={
                      <AnkiControls 
                        onCreateDeck={handleCreateDeck} 
                        onDownloadDeck={handleDownloadDeck} 
                      />
                    } />
                    <Route path="*" element={<CsvUpload />} />
                  </Routes>
                </TabPanel>
                <TabPanel>
                  <JapaneseWordLookup />
                </TabPanel>
              </TabPanels>
            </Tabs>
          </Box>
        </Container>
      </Box>
  );
}

function App() {
  return (
    <Router>
      <SessionProvider>
        <AppContent />
      </SessionProvider>
    </Router>
  );
}

export default App;