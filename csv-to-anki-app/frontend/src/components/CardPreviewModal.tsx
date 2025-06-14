import React from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  Box,
  VStack,
  Text,
  Badge,
  Flex,
  Divider,
  useColorModeValue,
  Spinner,
  Center,
  Alert,
  AlertIcon,
  HStack,
  IconButton,
  Tooltip,
  Icon
} from '@chakra-ui/react';
import { ChevronLeftIcon, ChevronRightIcon, RepeatIcon, TriangleUpIcon, MinusIcon } from '@chakra-ui/icons';

interface AnkiCard {
  front: string;
  back: string;
  reading?: string;
  example?: string;
  audio?: string;
  example_audio?: string;
  tags?: string[];
}

interface CardPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  deckName: string;
  cards: AnkiCard[];
  isLoading: boolean;
  error: string | null;
  onRefresh: () => void;
}

const CardPreviewModal: React.FC<CardPreviewModalProps> = ({
  isOpen,
  onClose,
  deckName,
  cards,
  isLoading,
  error,
  onRefresh
}) => {
  const [currentCardIndex, setCurrentCardIndex] = React.useState(0);
  const [showFront, setShowFront] = React.useState(true);
  const [isPlayingAudio, setIsPlayingAudio] = React.useState(false);
  const [isPlayingExampleAudio, setIsPlayingExampleAudio] = React.useState(false);
  const audioRef = React.useRef<HTMLAudioElement>(null);
  const exampleAudioRef = React.useRef<HTMLAudioElement>(null);
  
  // Colors for light/dark mode
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const accentColor = useColorModeValue('accent.500', 'accent.400');

  // Reset state when modal opens
  React.useEffect(() => {
    if (isOpen) {
      setCurrentCardIndex(0);
      setShowFront(true);
    }
  }, [isOpen]);

  const handleNextCard = () => {
    if (currentCardIndex < cards.length - 1) {
      stopAudio();
      stopAudio(true);
      setCurrentCardIndex(currentCardIndex + 1);
      setShowFront(true);
    }
  };

  const handlePrevCard = () => {
    if (currentCardIndex > 0) {
      stopAudio();
      stopAudio(true);
      setCurrentCardIndex(currentCardIndex - 1);
      setShowFront(true);
    }
  };

  const flipCard = () => {
    setShowFront(!showFront);
  };

  const playAudio = async (audioUrl: string, isExample: boolean = false) => {
    try {
      const audioElement = isExample ? exampleAudioRef.current : audioRef.current;
      const setPlayingState = isExample ? setIsPlayingExampleAudio : setIsPlayingAudio;
      
      if (!audioElement) return;
      
      // Stop any currently playing audio
      if (!audioElement.paused) {
        audioElement.pause();
        audioElement.currentTime = 0;
      }
      
      setPlayingState(true);
      audioElement.src = audioUrl;
      await audioElement.play();
      
      audioElement.onended = () => {
        setPlayingState(false);
      };
      
      audioElement.onerror = () => {
        setPlayingState(false);
        console.error('Error playing audio:', audioUrl);
      };
    } catch (error) {
      console.error('Error playing audio:', error);
      if (isExample) {
        setIsPlayingExampleAudio(false);
      } else {
        setIsPlayingAudio(false);
      }
    }
  };

  const stopAudio = (isExample: boolean = false) => {
    const audioElement = isExample ? exampleAudioRef.current : audioRef.current;
    const setPlayingState = isExample ? setIsPlayingExampleAudio : setIsPlayingAudio;
    
    if (audioElement) {
      audioElement.pause();
      audioElement.currentTime = 0;
      setPlayingState(false);
    }
  };

  // Safety check for currentCard
  const currentCard = cards && cards.length > 0 ? cards[currentCardIndex] : { front: "", back: "" };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          Preview Cards - {deckName}
          <Text fontSize="sm" color="gray.500" mt={1}>
            Sample {currentCardIndex + 1} of {cards.length}
          </Text>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          {isLoading ? (
            <Center py={10}>
              <VStack spacing={4}>
                <Spinner
                  thickness="4px"
                  speed="0.65s"
                  emptyColor="gray.200"
                  color={accentColor}
                  size="xl"
                />
                <Text color="gray.500">Loading preview cards...</Text>
              </VStack>
            </Center>
          ) : error ? (
            <Alert status="error" mb={4}>
              <AlertIcon />
              <Box flex="1">
                <Text fontWeight="bold">Error loading preview</Text>
                <Text fontSize="sm">{error}</Text>
              </Box>
              <Button onClick={onRefresh} leftIcon={<RepeatIcon />} size="sm">
                Retry
              </Button>
            </Alert>
          ) : cards.length === 0 ? (
            <Alert status="info">
              <AlertIcon />
              No cards available for preview.
            </Alert>
          ) : (
            <VStack spacing={4} align="stretch">
              {/* Card display */}
              <Box
                borderWidth="1px"
                borderRadius="lg"
                borderColor={borderColor}
                p={6}
                bg={cardBg}
                minH="200px"
                position="relative"
                onClick={flipCard}
                cursor="pointer"
                _hover={{ boxShadow: 'md' }}
                transition="all 0.2s ease-in-out"
              >
                {/* Card content */}
                <VStack spacing={4} align="stretch">
                  {showFront ? (
                    // Front of card
                    <>
                      <Flex align="center" justify="space-between">
                        <VStack align="start" flex="1">
                          <Text fontSize="xl" fontWeight="bold">
                            {currentCard.front}
                          </Text>
                          {currentCard.reading && (
                            <Text fontSize="md" color="gray.500">
                              {currentCard.reading}
                            </Text>
                          )}
                        </VStack>
                        {currentCard.audio && (
                          <IconButton
                            aria-label="Play pronunciation"
                            icon={<Icon as={isPlayingAudio ? MinusIcon : TriangleUpIcon} />}
                            colorScheme="blue"
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              if (isPlayingAudio) {
                                stopAudio();
                              } else {
                                playAudio(currentCard.audio!);
                              }
                            }}
                            isLoading={isPlayingAudio}
                          />
                        )}
                      </Flex>
                      <Text
                        fontSize="sm"
                        fontStyle="italic"
                        color="gray.500"
                        position="absolute"
                        bottom={2}
                        right={4}
                      >
                        Click to flip
                      </Text>
                    </>
                  ) : (
                    // Back of card
                    <>
                      <Text fontSize="lg">{currentCard.back}</Text>
                      {currentCard.example && (
                        <Box mt={2}>
                          <Flex align="center" justify="space-between">
                            <VStack align="start" flex="1">
                              <Text fontWeight="bold" fontSize="sm" color="gray.500">
                                Example:
                              </Text>
                              <Text fontSize="md">{currentCard.example}</Text>
                            </VStack>
                            {currentCard.example_audio && (
                              <IconButton
                                aria-label="Play example audio"
                                icon={<Icon as={isPlayingExampleAudio ? MinusIcon : TriangleUpIcon} />}
                                colorScheme="green"
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  if (isPlayingExampleAudio) {
                                    stopAudio(true);
                                  } else {
                                    playAudio(currentCard.example_audio!, true);
                                  }
                                }}
                                isLoading={isPlayingExampleAudio}
                              />
                            )}
                          </Flex>
                        </Box>
                      )}
                      {currentCard.tags && currentCard.tags.length > 0 && (
                        <Flex wrap="wrap" gap={2} mt={2}>
                          {currentCard.tags.map((tag, i) => (
                            <Badge key={i} colorScheme="accent" variant="subtle">
                              {tag}
                            </Badge>
                          ))}
                        </Flex>
                      )}
                      <Text
                        fontSize="sm"
                        fontStyle="italic"
                        color="gray.500"
                        position="absolute"
                        bottom={2}
                        right={4}
                      >
                        Click to flip
                      </Text>
                    </>
                  )}
                </VStack>
              </Box>

              {/* Navigation controls */}
              <Flex justify="space-between" align="center">
                <Tooltip label="Previous card">
                  <IconButton
                    icon={<ChevronLeftIcon />}
                    aria-label="Previous card"
                    onClick={handlePrevCard}
                    isDisabled={currentCardIndex === 0}
                  />
                </Tooltip>
                <HStack spacing={2}>
                  <Text fontSize="sm" color="gray.500">
                    {currentCardIndex + 1} of {cards.length}
                  </Text>
                </HStack>
                <Tooltip label="Next card">
                  <IconButton
                    icon={<ChevronRightIcon />}
                    aria-label="Next card"
                    onClick={handleNextCard}
                    isDisabled={currentCardIndex === cards.length - 1}
                  />
                </Tooltip>
              </Flex>
            </VStack>
          )}
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Close
          </Button>
        </ModalFooter>
        
        {/* Hidden audio elements for playback */}
        <audio ref={audioRef} style={{ display: 'none' }} />
        <audio ref={exampleAudioRef} style={{ display: 'none' }} />
      </ModalContent>
    </Modal>
  );
};

export default CardPreviewModal;
