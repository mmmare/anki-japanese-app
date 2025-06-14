import React, { useState, useContext } from 'react';
import { 
  Box,
  Button,
  VStack,
  Heading,
  Text,
  HStack,
  Divider,
  useColorModeValue,
  Badge,
  Icon,
  Flex,
  useToast,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Checkbox,
  FormControl,
  FormLabel,
  Switch,
  Stack
} from '@chakra-ui/react';
import { ViewIcon } from '@chakra-ui/icons';
import { motion } from 'framer-motion';
import { SessionContext } from '../context/SessionContext';
import CardPreviewModal from './CardPreviewModal';
import { previewCards as fetchPreviewCards } from '../services/api';

const MotionBox = motion(Box);

interface EnrichmentOptions {
  enrichCards: boolean;
  includeAudio: boolean;
  includeExamples: boolean;
  includeExampleAudio: boolean;
  useCore2000: boolean;
}

interface AnkiControlsProps {
  onCreateDeck: (
    options?: EnrichmentOptions, 
    progressCallback?: (progressData: { processed: number, total: number, status: string }) => void
  ) => void;
  onDownloadDeck: () => void;
}

const AnkiControls: React.FC<AnkiControlsProps> = ({ onCreateDeck, onDownloadDeck }) => {
  const [isCreating, setIsCreating] = useState<boolean>(false);
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const [deckCreated, setDeckCreated] = useState<boolean>(false);
  const [enrichCards, setEnrichCards] = useState<boolean>(true);
  const [includeAudio, setIncludeAudio] = useState<boolean>(true);
  const [includeExamples, setIncludeExamples] = useState<boolean>(true);
  const [includeExampleAudio, setIncludeExampleAudio] = useState<boolean>(true);
  const [useCore2000, setUseCore2000] = useState<boolean>(false);
  const [progressStatus, setProgressStatus] = useState<string>("");
  const [progress, setProgress] = useState<{ processed: number, total: number }>({ processed: 0, total: 100 });
  const { cardCount, deckName, sessionId } = useContext(SessionContext);
  const toast = useToast();
  const [hasCustomMapping, setHasCustomMapping] = useState<boolean>(false);
  
  // Preview state
  const [isPreviewOpen, setIsPreviewOpen] = useState<boolean>(false);
  const [cardSamples, setCardSamples] = useState<any[]>([]);
  const [isLoadingPreview, setIsLoadingPreview] = useState<boolean>(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  
  // Check if we have a custom field mapping
  React.useEffect(() => {
    const savedMapping = sessionStorage.getItem('csvFieldMapping');
    if (savedMapping) {
      try {
        const mapping = JSON.parse(savedMapping);
        const hasMapping = Object.keys(mapping).length > 0;
        setHasCustomMapping(hasMapping);
        
        // If custom mapping exists, log it
        if (hasMapping) {
          console.log("Using custom field mapping:", mapping);
        }
      } catch (e) {
        console.error("Error parsing field mapping:", e);
      }
    }
  }, []);
  
  // Colors for light/dark mode
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const accentColor = useColorModeValue('accent.500', 'accent.400');
  
  const handleCreateDeck = async () => {
    setIsCreating(true);
    setProgressStatus("Initializing deck creation...");
    setProgress({ processed: 0, total: 100 });
    setDeckCreated(false);
    
    try {
      // Create a tracking function for progress updates with phases
      const trackProgress = (progressData: { processed: number, total: number, status: string }) => {
        // Use requestAnimationFrame for smoother UI updates
        requestAnimationFrame(() => {
          setProgressStatus(progressData.status);
          setProgress({ 
            processed: progressData.processed, 
            total: progressData.total 
          });
          
          // When we reach the "Deck created successfully!" status, mark the deck as created
          if (progressData.status === 'Deck created successfully!') {
            setDeckCreated(true);
          }
        });
      };
      
      // Pass the enrichment options to the onCreateDeck handler with the progress tracker
      await onCreateDeck({
        enrichCards,
        includeAudio,
        includeExamples,
        includeExampleAudio,
        useCore2000
      }, trackProgress);
      
      // Successful deck creation
      setDeckCreated(true);
      let messagePrefix = useCore2000 ? "Your Core 2000 style " : "Your ";
      const enrichmentMessage = enrichCards 
        ? messagePrefix + "enriched Anki deck with translations, " +
          (includeAudio ? "audio, " : "") + 
          (includeExamples 
            ? "example sentences" + 
              (useCore2000 && includeExampleAudio ? " with audio " : " ") 
            : "") +
          "is ready for download"
        : messagePrefix + "Anki deck is ready for download";
          
      toast({
        title: "Deck created successfully!",
        description: enrichmentMessage,
        status: "success",
        duration: 5000,
        isClosable: true,
      });
      
    } catch (error) {
      toast({
        title: "Failed to create deck",
        description: "There was an error creating your Anki deck",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsCreating(false);
    }
  };
  
  const handleDownloadDeck = async () => {
    setIsDownloading(true);
    
    try {
      // Show download starting toast immediately
      toast({
        title: "Download starting...",
        description: "Your Anki deck is being prepared for download",
        status: "info",
        duration: 2000,
        isClosable: true,
      });
      
      // Add a minimum duration for the progress animation to be visible
      const downloadStartTime = Date.now();
      
      // Start the download
      await onDownloadDeck();
      
      // Check if download was too fast, ensure progress animation shows for at least 1.5 seconds
      const downloadDuration = Date.now() - downloadStartTime;
      const minimumVisibleDuration = 1500;
      
      if (downloadDuration < minimumVisibleDuration) {
        // If download was fast, still show the progress animation for a sensible duration
        await new Promise(resolve => setTimeout(resolve, minimumVisibleDuration - downloadDuration));
      }
      
      // Show success toast after a brief delay
      setTimeout(() => {
        toast({
          title: "Download successful!",
          description: "If your download didn't start automatically, please try again",
          status: "success",
          duration: 5000,
          isClosable: true,
        });
      }, 500);
      
    } catch (error) {
      toast({
        title: "Download failed",
        description: "There was an error downloading your Anki deck",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      // Allow a delay before resetting the download state to show the progress indicator
      setTimeout(() => {
        setIsDownloading(false);
      }, 2000);
    }
  };
  
  // Handle Preview request
  const handlePreviewCards = async () => {
    if (!sessionId) {
      toast({
        title: "Session Error",
        description: "No active session found. Please upload a file first.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
      return;
    }
    
    setIsLoadingPreview(true);
    setPreviewError(null);
    
    try {
      const options = {
        enrichCards,
        includeAudio,
        includeExamples,
        includeExampleAudio,
        useCore2000
      };
      
      // Get field mapping from session storage if available
      let fieldMapping = null;
      const savedMapping = sessionStorage.getItem('csvFieldMapping');
      if (savedMapping) {
        try {
          fieldMapping = JSON.parse(savedMapping);
        } catch (e) {
          console.error("Error parsing field mapping for preview:", e);
        }
      }
      
      // Fetch preview cards
      const result = await fetchPreviewCards(
        sessionId,
        deckName,
        5, // Sample count
        options,
        fieldMapping
      );
      
      if (result && result.sample_cards && result.sample_cards.length > 0) {
        setCardSamples(result.sample_cards);
        setIsPreviewOpen(true);
        
        toast({
          title: "Preview loaded",
          description: `Showing ${result.sample_cards.length} sample cards from your deck`,
          status: "info",
          duration: 3000,
          isClosable: true,
        });
      } else {
        setPreviewError("No cards available for preview");
      }
      
    } catch (error: any) {
      console.error("Error fetching preview cards:", error);
      setPreviewError(error.response?.data?.detail || "Failed to load preview cards");
      
      toast({
        title: "Preview failed",
        description: "There was an error generating card previews",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoadingPreview(false);
    }
  };
  
  return (
    <MotionBox
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      p={8}
    >
      <VStack spacing={6} align="stretch">
        <Heading 
          as="h2" 
          size="xl" 
          textAlign="center" 
          color="brand.600"
          fontWeight="bold"
        >
          アンキデッキ生成
        </Heading>
        
        <Text textAlign="center" fontSize="lg" mb={4}>
          Generate and download your Japanese vocabulary Anki deck
        </Text>
        
        <Alert status="info" borderRadius="md" mb={4}>
          <AlertIcon />
          <Box>
            <AlertTitle>CSV Format Tips</AlertTitle>
            <AlertDescription>
              <Text fontSize="sm">• Standard CSV format: Japanese,English,Tags (optional)</Text>
              <Text fontSize="sm">• Anki format also supported with #separator:tab directive</Text>
              <Text fontSize="sm">• For tags, use underscores instead of spaces (e.g., "noun_animal")</Text>
              <Text fontSize="sm">• Tags should be single words or use underscores</Text>
              {hasCustomMapping && (
                <HStack mt={2}>
                  <Badge colorScheme="purple" variant="solid" fontSize="0.8em">
                    Custom CSV Mapping
                  </Badge>
                  <Text fontSize="xs" fontWeight="bold">
                    Your field mapping settings will be applied to this deck
                  </Text>
                </HStack>
              )}
              <HStack mt={2}>
                <Badge colorScheme="green">New</Badge>
                <Text fontSize="xs" fontWeight="bold">Native .apkg format download now available!</Text>
              </HStack>
            </AlertDescription>
          </Box>
        </Alert>
        
        {deckCreated ? (
          <Alert
            status="success"
            variant="subtle"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            textAlign="center"
            borderRadius="lg"
            p={6}
            mb={4}
          >
            <AlertIcon boxSize="40px" mr={0} />
            <AlertTitle mt={4} mb={1} fontSize="lg">
              Deck Ready!
            </AlertTitle>
            <AlertDescription maxWidth="md">
              Your Japanese vocabulary Anki deck has been created successfully with {cardCount} cards and is ready for download.
            </AlertDescription>
            <Badge colorScheme="green" mt={3} p={1} px={2} borderRadius="md">
              {cardCount} vocabulary cards
            </Badge>
          </Alert>
        ) : (
          <Box
            borderWidth="1px"
            borderColor={borderColor}
            borderRadius="lg"
            bg={cardBg}
            p={6}
            mb={4}
            shadow="md"
          >
            <VStack spacing={4} align="center">
              <Icon viewBox="0 0 24 24" boxSize="16" color="brand.500">
                <path
                  fill="currentColor"
                  d="M4,6H20V16H4M20,18V20H4V18H20M2,4V22H22V4H2M10,10H14V14H10V10Z"
                />
              </Icon>
              
              <HStack>
                <Heading size="md">Create Your Anki Deck</Heading>
                {hasCustomMapping && (
                  <Badge colorScheme="purple" variant="solid" fontSize="0.8em">
                    Custom CSV Mapping
                  </Badge>
                )}
              </HStack>
              
              <Text textAlign="center" color="gray.500">
                Convert your CSV file to an Anki deck format optimized for Japanese vocabulary learning.
              </Text>
              
              <Box w="full" mt={3} p={3} borderWidth="1px" borderRadius="md" borderColor="gray.200">
                <VStack align="start" spacing={3}>
                  <FormControl display="flex" alignItems="center">
                    <FormLabel htmlFor="enrich-toggle" mb="0" fontSize="sm">
                      Enhance vocabulary with translations
                    </FormLabel>
                    <Switch 
                      id="enrich-toggle"
                      colorScheme="green" 
                      size="md"
                      isChecked={enrichCards}
                      onChange={() => setEnrichCards(!enrichCards)}
                    />
                  </FormControl>
                  
                  <FormControl display="flex" alignItems="center">
                    <FormLabel htmlFor="core2000-toggle" mb="0" fontSize="sm">
                      Use Core 2000 format (Recognition + Production cards)
                    </FormLabel>
                    <Switch 
                      id="core2000-toggle"
                      colorScheme="accent" 
                      size="md"
                      isChecked={useCore2000}
                      onChange={() => setUseCore2000(!useCore2000)}
                    />
                  </FormControl>
                  
                  {useCore2000 && (
                    <Text fontSize="xs" color="accent.500">
                      Creates both Recognition (JP→EN) and Production (EN→JP) cards with Core 2000 styling
                    </Text>
                  )}
                  
                  {enrichCards && (
                    <Stack pl={4} spacing={2} w="full">
                      <FormControl display="flex" alignItems="center">
                        <FormLabel htmlFor="audio-toggle" mb="0" fontSize="sm">
                          Include audio pronunciation
                        </FormLabel>
                        <Switch
                          id="audio-toggle"
                          colorScheme="green"
                          size="sm"
                          isChecked={includeAudio}
                          onChange={() => setIncludeAudio(!includeAudio)}
                        />
                      </FormControl>
                      
                      <FormControl display="flex" alignItems="center">
                        <FormLabel htmlFor="examples-toggle" mb="0" fontSize="sm">
                          Include example sentences
                        </FormLabel>
                        <Switch
                          id="examples-toggle"
                          colorScheme="green"
                          size="sm"
                          isChecked={includeExamples}
                          onChange={() => setIncludeExamples(!includeExamples)}
                        />
                      </FormControl>
                      
                      {includeExamples && (
                        <>
                          <FormControl display="flex" alignItems="center" ml={4}>
                            <FormLabel htmlFor="example-audio-toggle" mb="0" fontSize="sm">
                              Include example audio
                            </FormLabel>
                            <Switch
                              id="example-audio-toggle"
                              colorScheme="green"
                              size="sm"
                              isChecked={includeExampleAudio}
                              onChange={() => setIncludeExampleAudio(!includeExampleAudio)}
                            />
                          </FormControl>
                          <Text fontSize="xs" color="blue.500" ml={4}>
                            Examples can come from your CSV or be auto-generated if not present
                          </Text>
                        </>
                      )}
                    </Stack>
                  )}
                  
                  {enrichCards && (
                    <Text fontSize="xs" color="gray.500">
                      Vocabulary will be automatically enhanced with dictionary lookups,
                      readings, and more.
                    </Text>
                  )}
                </VStack>
              </Box>
              
              {isCreating && (
                <Box width="100%" mb={4}>
                  <Text 
                    fontSize="sm" 
                    mb={1} 
                    textAlign="center" 
                    fontWeight="medium" 
                    color={progressStatus === 'Deck created successfully!' ? "green.500" : "gray.700"}
                    key={`status-${progressStatus}`} // Key helps React detect changes
                  >
                    {progressStatus}
                  </Text>
                  <Box
                    width="100%"
                    height="8px"
                    bg="gray.200"
                    borderRadius="full"
                    overflow="hidden"
                    mb={2}
                    position="relative"
                  >
                    <Box
                      as={motion.div}
                      initial={{ width: '0%' }}
                      animate={{ 
                        width: `${(progress.processed / progress.total) * 100}%`,
                        transition: { 
                          duration: 0.5,
                          ease: "easeOut" 
                        }
                      }}
                      height="100%"
                      bg={progressStatus === 'Deck created successfully!' ? "green.500" : "brand.500"}
                      borderRadius="full"
                      key={`progress-bar-${progress.processed}`} // Force re-render on progress change
                    />
                    {/* Pulsing effect for active progress */}
                    {progress.processed > 0 && progress.processed < progress.total && (
                      <Box
                        as={motion.div}
                        position="absolute"
                        right={`${100 - ((progress.processed / progress.total) * 100)}%`}
                        top="0"
                        height="100%"
                        width="4px"
                        bg="white"
                        opacity={0.6}
                        animate={{
                          opacity: [0.6, 0.2, 0.6],
                          transition: { 
                            duration: 1.5, 
                            repeat: Infinity,
                            ease: "linear"
                          }
                        }}
                      />
                    )}
                  </Box>
                  <Flex justify="space-between" width="100%">
                    <Text fontSize="xs" color="gray.500" fontWeight="medium">
                      {Math.round((progress.processed / progress.total) * 100)}% complete
                    </Text>
                    <Text fontSize="xs" color="gray.500" textAlign="right">
                      {progress.processed} of {progress.total} words processed
                    </Text>
                  </Flex>
                </Box>
              )}
              
              <Button
                colorScheme="brand"
                size="lg"
                width="full"
                isLoading={isCreating}
                loadingText="Creating deck..."
                onClick={handleCreateDeck}
                mt={4}
              >
                {isCreating ? "Creating..." : `Generate ${enrichCards ? "Enhanced " : ""}Anki Deck`}
              </Button>
            </VStack>
          </Box>
        )}
        
        <Divider my={2} />
        
        <Box
          borderWidth="1px"
          borderColor={borderColor}
          borderRadius="lg"
          bg={cardBg}
          p={6}
          shadow="md"
        >
          <VStack spacing={4} align="center">
            <Icon viewBox="0 0 24 24" boxSize="16" color="accent.500">
              <path
                fill="currentColor"
                d="M5,20H19V18H5M19,9H15V3H9V9H5L12,16L19,9Z"
              />
            </Icon>              <HStack>
              <Heading size="md">Download Deck</Heading>
              <Badge colorScheme="green" variant="solid" fontSize="0.8em">
                .apkg format
              </Badge>
              {hasCustomMapping && (
                <Badge colorScheme="purple" variant="solid" fontSize="0.8em">
                  Custom CSV Mapping
                </Badge>
              )}
            </HStack>
            
            <Text textAlign="center" color="gray.500">
              Download your Anki deck and import it directly into Anki.
            </Text>

            <Button
              colorScheme="blue"
              variant="outline"
              size="md"
              width="full"
              leftIcon={<ViewIcon />}
              onClick={handlePreviewCards}
              isLoading={isLoadingPreview}
              loadingText="Loading preview..."
              isDisabled={!sessionId || isCreating || isDownloading || isLoadingPreview}
              mb={3}
            >
              Preview Sample Cards
            </Button>
            
            {isDownloading && (
              <Box width="100%">
                <Text 
                  fontSize="sm" 
                  mb={1} 
                  textAlign="center" 
                  as={motion.p}
                  animate={{
                    opacity: [1, 0.8, 1],
                    transition: { duration: 1.5, repeat: Infinity }
                  }}
                >
                  Preparing download...
                </Text>
                <Box
                  width="100%"
                  height="6px"
                  bg="gray.200"
                  borderRadius="full"
                  overflow="hidden"
                  mb={2}
                  position="relative"
                >
                  <Box
                    as={motion.div}
                    width="10%"
                    height="100%"
                    bg="accent.500"
                    animate={{
                      width: ["10%", "30%", "60%", "80%", "95%"],
                      transition: { 
                        duration: 3.0, 
                        times: [0, 0.1, 0.3, 0.6, 0.9],
                        ease: "easeInOut" 
                      }
                    }}
                  />
                  {/* Add glowing effect at the front edge */}
                  <Box
                    as={motion.div}
                    position="absolute"
                    left="0"
                    top="0"
                    height="100%"
                    bg="white"
                    width="6px" 
                    animate={{
                      left: ["10%", "30%", "60%", "80%", "95%"],
                      opacity: [0.7, 0.7, 0.5, 0.3, 0.2],
                      transition: { 
                        duration: 3.0, 
                        times: [0, 0.1, 0.3, 0.6, 0.9],
                        ease: "easeInOut" 
                      }
                    }}
                    style={{ filter: 'blur(3px)' }}
                  />
                </Box>
                <Text 
                  fontSize="xs" 
                  color="gray.500" 
                  textAlign="center"
                  as={motion.p}
                  animate={{
                    opacity: [1, 0.7, 1],
                    transition: { duration: 2, repeat: Infinity }
                  }}
                >
                  Packaging files for download...
                </Text>
              </Box>
            )}
            
            <Button
              colorScheme="accent"
              variant={deckCreated && !isCreating ? "solid" : "outline"}
              size="lg"
              width="full"
              isLoading={isDownloading}
              loadingText="Downloading..."
              onClick={handleDownloadDeck}
              isDisabled={!deckCreated || isCreating}
              mt={2}
              _hover={{
                bg: deckCreated && !isCreating ? "accent.600" : "transparent",
                color: deckCreated && !isCreating ? "white" : "accent.500",
                borderColor: "accent.500"
              }}
            >
              {isDownloading ? "Preparing file..." : "Download Deck"}
            </Button>
          </VStack>
        </Box>
        
        <Box mt={6}>
          <Flex justify="center" align="center" direction="column">
            <Text fontSize="sm" color="gray.500" textAlign="center">
              Import the downloaded .apkg file by opening Anki and selecting File &gt; Import
            </Text>
            <Text fontSize="xs" color="green.500" mt={1} fontWeight="bold">
              Native .apkg format ensures 100% compatibility with Anki
            </Text>
          </Flex>
        </Box>
        
        {/* Card Preview Modal */}
        <CardPreviewModal 
          isOpen={isPreviewOpen} 
          onClose={() => setIsPreviewOpen(false)}
          deckName={deckName}
          cards={cardSamples}
          isLoading={isLoadingPreview}
          error={previewError}
          onRefresh={handlePreviewCards}
        />
      </VStack>
    </MotionBox>
  );
};

export default AnkiControls;