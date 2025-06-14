import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  Text,
  Divider,
  Badge,
  HStack,
  Card,
  CardBody,
  CardHeader,
  ListItem,
  UnorderedList,
  Spinner,
  useColorModeValue,
  Alert,
  AlertIcon,
  useToast,
  Flex,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  Checkbox,
  CheckboxGroup,
  Stack,
  SimpleGrid,
  IconButton,
  Tooltip,
} from '@chakra-ui/react';
import { AddIcon, DownloadIcon, ViewIcon } from '@chakra-ui/icons';
import { lookupWord, addWordToCollection, getCollection, createDeckFromCollection, removeWordFromCollection } from '../services/api';

const JapaneseWordLookup: React.FC = () => {
  const [word, setWord] = useState<string>('');
  const [result, setResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [collectionId, setCollectionId] = useState<string | null>(
    localStorage.getItem('wordCollectionId')
  );
  const [wordCount, setWordCount] = useState<number>(0);
  const [isAddingToCollection, setIsAddingToCollection] = useState<boolean>(false);
  const [isCreatingDeck, setIsCreatingDeck] = useState<boolean>(false);
  
  // New states for meaning selection and collection preview
  const [selectedSenseIds, setSelectedSenseIds] = useState<number[]>([]);
  const [collectionWords, setCollectionWords] = useState<any[]>([]);
  const [isLoadingCollection, setIsLoadingCollection] = useState<boolean>(false);
  
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { 
    isOpen: isCollectionOpen, 
    onOpen: onCollectionOpen, 
    onClose: onCollectionClose 
  } = useDisclosure();

  // Colors for styling
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const titleColor = useColorModeValue('brand.600', 'brand.400');

  const handleLookup = async () => {
    if (!word.trim()) {
      setError('Please enter a Japanese word to look up');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSelectedSenseIds([]); // Reset selected senses for new lookup

    try {
      const data = await lookupWord(word.trim());
      setResult(data);
      
      // If there are senses, handle sense selection
      if (data.senses && data.senses.length > 0) {
        if (data.senses.length === 1) {
          // Only one sense - auto-select it
          setSelectedSenseIds([0]);
        } else {
          // Multiple senses - let user choose, but pre-select first one
          setSelectedSenseIds([0]);
        }
      } else {
        // No senses structure - clear selection
        setSelectedSenseIds([]);
      }
    } catch (err) {
      setError('Failed to look up the word. Please try again.');
      console.error('Lookup error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddToCollection = async () => {
    if (!result) return;
    
    // Check if user has selected any senses when multiple are available
    if (result.senses && result.senses.length > 1 && selectedSenseIds.length === 0) {
      toast({
        title: "Please select meanings",
        description: "Please select at least one meaning to add to your collection.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    setIsAddingToCollection(true);
    
    try {
      // Filter meanings and parts of speech based on selected senses
      let selectedMeanings = result.meanings;
      let selectedPartsOfSpeech = result.parts_of_speech;
      
      if (result.senses && selectedSenseIds.length > 0) {
        selectedMeanings = [];
        selectedPartsOfSpeech = [];
        
        selectedSenseIds.forEach(senseId => {
          const sense = result.senses[senseId];
          if (sense) {
            selectedMeanings.push(...sense.meanings);
            selectedPartsOfSpeech.push(...sense.parts_of_speech);
          }
        });
      }
      
      const response = await addWordToCollection(
        result.word,
        result.reading,
        selectedMeanings,
        selectedPartsOfSpeech,
        result.examples,
        collectionId || undefined,
        selectedSenseIds.length > 0 ? selectedSenseIds : undefined
      );
      
      // Save collection ID if this is a new collection
      if (!collectionId && response.collection_id) {
        setCollectionId(response.collection_id);
        localStorage.setItem('wordCollectionId', response.collection_id);
      }
      
      setWordCount(response.word_count);
      
      toast({
        title: "Word added!",
        description: response.message,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      
    } catch (error) {
      toast({
        title: "Error adding word",
        description: "Failed to add word to collection. Please try again.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsAddingToCollection(false);
    }
  };

  const handleCreateDeck = async () => {
    if (!collectionId) {
      toast({
        title: "No collection",
        description: "Please add some words to your collection first.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    setIsCreatingDeck(true);
    
    try {
      await createDeckFromCollection(
        collectionId,
        "Japanese Words Collection",
        false, // include_audio
        true,  // include_examples
        false  // include_example_audio
      );
      
      toast({
        title: "Deck created!",
        description: "Your Anki deck has been downloaded successfully.",
        status: "success",
        duration: 5000,
        isClosable: true,
      });
      
    } catch (error) {
      toast({
        title: "Error creating deck",
        description: "Failed to create Anki deck. Please try again.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsCreatingDeck(false);
    }
  };

  const handlePreviewCollection = async () => {
    if (!collectionId) return;
    
    setIsLoadingCollection(true);
    
    try {
      const data = await getCollection(collectionId);
      setCollectionWords(data.words || []);
      onCollectionOpen();
    } catch (error) {
      toast({
        title: "Error loading collection",
        description: "Failed to load collection details.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoadingCollection(false);
    }
  };

  const handleRemoveFromCollection = async (wordToRemove: string) => {
    if (!collectionId) return;
    
    try {
      await removeWordFromCollection(collectionId, wordToRemove);
      
      // Refresh collection data
      const data = await getCollection(collectionId);
      setCollectionWords(data.words || []);
      setWordCount(data.word_count);
      
      toast({
        title: "Word removed",
        description: `"${wordToRemove}" has been removed from your collection.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: "Error removing word",
        description: "Failed to remove word from collection.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  // Load collection word count on component mount
  React.useEffect(() => {
    if (collectionId) {
      getCollection(collectionId)
        .then(data => {
          setWordCount(data.word_count);
        })
        .catch(error => {
          console.error('Error loading collection:', error);
        });
    }
  }, [collectionId]);

  return (
    <Box maxW="700px" mx="auto" mt={8}>
      <VStack spacing={6} align="stretch">
        <Heading as="h2" size="lg" textAlign="center" color={titleColor}>
          Japanese Word Lookup
        </Heading>

        <Text textAlign="center">
          Enter a Japanese word to get translations, readings, examples, and more.
        </Text>

        {/* Collection Status Card */}
        {wordCount > 0 && (
          <Card borderWidth="1px" borderRadius="lg" overflow="hidden" boxShadow="sm" bg={useColorModeValue('green.50', 'green.900')}>
            <CardBody>
              <Flex justifyContent="space-between" alignItems="center">
                <HStack>
                  <Text fontSize="lg" color="green.500">📋</Text>
                  <Text fontWeight="bold">
                    Collection: {wordCount} word{wordCount !== 1 ? 's' : ''}
                  </Text>
                </HStack>
                <HStack spacing={2}>
                  <Button
                    colorScheme="blue"
                    size="sm"
                    leftIcon={<ViewIcon />}
                    onClick={handlePreviewCollection}
                    isLoading={isLoadingCollection}
                    loadingText="Loading..."
                  >
                    Preview
                  </Button>
                  <Button
                    colorScheme="green"
                    size="sm"
                    leftIcon={<DownloadIcon />}
                    onClick={handleCreateDeck}
                    isLoading={isCreatingDeck}
                    loadingText="Creating..."
                  >
                    Create Anki Deck
                  </Button>
                </HStack>
              </Flex>
            </CardBody>
          </Card>
        )}

        <Card borderWidth="1px" borderRadius="lg" overflow="hidden" boxShadow="sm">
          <CardBody>
            <FormControl>
              <FormLabel>Japanese Word</FormLabel>
              <HStack>
                <Input
                  placeholder="Enter Japanese word (e.g. 猫)"
                  value={word}
                  onChange={(e) => setWord(e.target.value)}
                  size="lg"
                  fontFamily="'Noto Sans JP', sans-serif"
                  fontSize="xl"
                />
                <Button
                  colorScheme="brand"
                  onClick={handleLookup}
                  isLoading={isLoading}
                  loadingText="Looking up..."
                  size="lg"
                  px={8}
                >
                  Lookup
                </Button>
              </HStack>
            </FormControl>
          </CardBody>
        </Card>

        {error && (
          <Alert status="error" borderRadius="md">
            <AlertIcon />
            {error}
          </Alert>
        )}

        {isLoading && (
          <Box textAlign="center" py={10}>
            <Spinner size="xl" color="brand.500" thickness="4px" speed="0.65s" />
            <Text mt={4}>Looking up word details...</Text>
          </Box>
        )}

        {result && !isLoading && !error && (
          <Card
            borderWidth="1px"
            borderRadius="lg"
            overflow="hidden"
            boxShadow="md"
            bg={cardBg}
          >
            <CardHeader bg={useColorModeValue('brand.50', 'brand.900')} py={4}>
              <HStack spacing={3}>
                <Heading size="lg" fontFamily="'Noto Sans JP', sans-serif">
                  {result.word}
                </Heading>
                {result.reading && (
                  <Text fontSize="lg" color="gray.500" fontStyle="italic">
                    {result.reading}
                  </Text>
                )}
              </HStack>
            </CardHeader>

            <CardBody>
              <VStack spacing={4} align="stretch" divider={<Divider />}>
                {/* Meanings - Show either senses or flat meanings */}
                <Box>
                  <Heading size="sm" mb={2}>
                    Meanings
                  </Heading>
                  {result.senses && result.senses.length > 1 ? (
                    // Multiple senses - show selectable options
                    <VStack spacing={3} align="stretch">
                      <Text fontSize="sm" color="gray.600" mb={2}>
                        Multiple meanings found. Select the ones you want to include:
                      </Text>
                      <CheckboxGroup
                        value={selectedSenseIds.map(String)}
                        onChange={(values) => setSelectedSenseIds(values.map(Number))}
                      >
                        <Stack spacing={3}>
                          {result.senses.map((sense: any, idx: number) => (
                            <Box
                              key={idx}
                              p={3}
                              borderWidth="1px"
                              borderRadius="md"
                              borderColor={selectedSenseIds.includes(idx) ? "blue.300" : borderColor}
                              bg={selectedSenseIds.includes(idx) ? useColorModeValue('blue.50', 'blue.900') : 'transparent'}
                            >
                              <Checkbox value={String(idx)} size="lg">
                                <VStack align="start" spacing={2} ml={2}>
                                  <HStack spacing={2} flexWrap="wrap">
                                    {sense.parts_of_speech && sense.parts_of_speech.map((pos: string, posIdx: number) => (
                                      <Badge key={posIdx} colorScheme="purple" size="sm">
                                        {pos}
                                      </Badge>
                                    ))}
                                  </HStack>
                                  <UnorderedList spacing={1}>
                                    {sense.meanings.map((meaning: string, meaningIdx: number) => (
                                      <ListItem key={meaningIdx} fontSize="sm">
                                        {meaning}
                                      </ListItem>
                                    ))}
                                  </UnorderedList>
                                  {sense.tags && sense.tags.length > 0 && (
                                    <HStack spacing={1} flexWrap="wrap">
                                      {sense.tags.map((tag: string, tagIdx: number) => (
                                        <Badge key={tagIdx} colorScheme="gray" size="sm">
                                          {tag}
                                        </Badge>
                                      ))}
                                    </HStack>
                                  )}
                                </VStack>
                              </Checkbox>
                            </Box>
                          ))}
                        </Stack>
                      </CheckboxGroup>
                    </VStack>
                  ) : (
                    // Single sense or flat meanings - show as before
                    result.meanings && result.meanings.length > 0 ? (
                      <UnorderedList spacing={1}>
                        {result.meanings.map((meaning: string, idx: number) => (
                          <ListItem key={idx}>{meaning}</ListItem>
                        ))}
                      </UnorderedList>
                    ) : (
                      <Text color="gray.500">No meanings found</Text>
                    )
                  )}
                </Box>

                {/* Parts of Speech */}
                {result.parts_of_speech && result.parts_of_speech.length > 0 && (
                  <Box>
                    <Heading size="sm" mb={2}>
                      Parts of Speech
                    </Heading>
                    <HStack spacing={2} flexWrap="wrap">
                      {result.parts_of_speech.map((pos: string, idx: number) => (
                        <Badge key={idx} colorScheme="purple" px={2} py={1}>
                          {pos}
                        </Badge>
                      ))}
                    </HStack>
                  </Box>
                )}

                {/* Examples */}
                {result.examples && result.examples.length > 0 && (
                  <Box>
                    <Heading size="sm" mb={2}>
                      Example Sentences
                    </Heading>
                    <VStack spacing={3} align="stretch">
                      {result.examples.map((ex: any, idx: number) => (
                        <Box
                          key={idx}
                          p={3}
                          borderRadius="md"
                          bg={useColorModeValue('gray.50', 'gray.700')}
                        >
                          <Text fontFamily="'Noto Sans JP', sans-serif" mb={1} fontSize="md">
                            {ex.japanese}
                          </Text>
                          <Text fontSize="sm" color="gray.500">
                            {ex.english}
                          </Text>
                        </Box>
                      ))}
                    </VStack>
                  </Box>
                )}
              </VStack>
              
              {/* Add to Collection Button */}
              <Divider my={4} />
              <Flex justifyContent="center">
                <Button
                  colorScheme="green"
                  leftIcon={<AddIcon />}
                  onClick={handleAddToCollection}
                  isLoading={isAddingToCollection}
                  loadingText="Adding..."
                  size="lg"
                  variant="solid"
                >
                  Add to Collection
                </Button>
              </Flex>
            </CardBody>
          </Card>
        )}
      </VStack>

      {/* Collection Preview Modal */}
      <Modal isOpen={isCollectionOpen} onClose={onCollectionClose} size="xl">
        <ModalOverlay />
        <ModalContent maxW="800px">
          <ModalHeader>
            <HStack>
              <Text>📋</Text>
              <Text>Word Collection ({collectionWords.length} words)</Text>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody maxH="500px" overflowY="auto">
            {collectionWords.length === 0 ? (
              <Text color="gray.500" textAlign="center" py={8}>
                No words in collection yet.
              </Text>
            ) : (
              <VStack spacing={3} align="stretch">
                {collectionWords.map((word: any, idx: number) => (
                  <Card key={idx} size="sm" variant="outline">
                    <CardBody>
                      <Flex justifyContent="space-between" alignItems="start">
                        <VStack align="start" spacing={2} flex={1}>
                          <HStack spacing={3}>
                            <Heading size="md" fontFamily="'Noto Sans JP', sans-serif">
                              {word.word}
                            </Heading>
                            {word.reading && (
                              <Text fontSize="md" color="gray.500" fontStyle="italic">
                                {word.reading}
                              </Text>
                            )}
                          </HStack>
                          
                          {/* Meanings */}
                          {word.meanings && word.meanings.length > 0 && (
                            <Box>
                              <Text fontSize="sm" fontWeight="semibold" mb={1}>
                                Meanings:
                              </Text>
                              <UnorderedList spacing={0} ml={4}>
                                {word.meanings.slice(0, 3).map((meaning: string, meaningIdx: number) => (
                                  <ListItem key={meaningIdx} fontSize="sm" color="gray.600">
                                    {meaning}
                                  </ListItem>
                                ))}
                                {word.meanings.length > 3 && (
                                  <ListItem fontSize="sm" color="gray.500" fontStyle="italic">
                                    +{word.meanings.length - 3} more...
                                  </ListItem>
                                )}
                              </UnorderedList>
                            </Box>
                          )}
                          
                          {/* Parts of Speech */}
                          {word.parts_of_speech && word.parts_of_speech.length > 0 && (
                            <HStack spacing={1} flexWrap="wrap">
                              {word.parts_of_speech.slice(0, 3).map((pos: string, posIdx: number) => (
                                <Badge key={posIdx} colorScheme="purple" size="sm">
                                  {pos}
                                </Badge>
                              ))}
                              {word.parts_of_speech.length > 3 && (
                                <Badge colorScheme="gray" size="sm">
                                  +{word.parts_of_speech.length - 3}
                                </Badge>
                              )}
                            </HStack>
                          )}
                        </VStack>
                        
                        <Tooltip label="Remove from collection">
                          <IconButton
                            aria-label="Remove word"
                            icon={<Text>🗑️</Text>}
                            size="sm"
                            variant="ghost"
                            colorScheme="red"
                            onClick={() => handleRemoveFromCollection(word.word)}
                          />
                        </Tooltip>
                      </Flex>
                    </CardBody>
                  </Card>
                ))}
              </VStack>
            )}
          </ModalBody>
          <ModalFooter>
            <HStack spacing={3}>
              <Button variant="ghost" onClick={onCollectionClose}>
                Close
              </Button>
              {collectionWords.length > 0 && (
                <Button
                  colorScheme="green"
                  leftIcon={<DownloadIcon />}
                  onClick={() => {
                    handleCreateDeck();
                    onCollectionClose();
                  }}
                  isLoading={isCreatingDeck}
                  loadingText="Creating..."
                >
                  Create Anki Deck
                </Button>
              )}
            </HStack>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default JapaneseWordLookup;
