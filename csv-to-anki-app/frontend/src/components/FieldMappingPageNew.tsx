import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Heading,
  Text,
  VStack,
  Button,
  useToast,
  Container,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Progress,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Flex,
  Badge,
  Icon,
  Card,
  CardBody,
  CardHeader
} from '@chakra-ui/react';
import { FaFileUpload, FaListAlt, FaDownload, FaArrowLeft, FaArrowRight } from 'react-icons/fa';
import { SessionContext } from '../context/SessionContext';
// Import the improved FieldMapper component
import FieldMapperComponent from './FieldMapperNew';

const FieldMappingPage: React.FC = () => {
  const { sessionId, setSessionId } = useContext(SessionContext);
  const [mapping, setMapping] = useState<Record<string, string> | null>(null);
  const [serverFile, setServerFile] = useState<{name: string, type: string, size: number} | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const navigate = useNavigate();
  const toast = useToast();
  
  // When component mounts, check if we have a session ID
  useEffect(() => {
    if (!sessionId) {
      toast({
        title: "No session",
        description: "Please upload a CSV file first",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      navigate('/');
      return;
    }
    
    // Get uploaded file info from sessionStorage if available
    const fileInfo = sessionStorage.getItem('uploadedFile');
    if (fileInfo) {
      try {
        const parsedInfo = JSON.parse(fileInfo);
        setServerFile(parsedInfo);
        console.log("Using server file info:", parsedInfo);
        setIsLoading(false);
      } catch (e) {
        console.error("Error parsing uploaded file info:", e);
        setIsLoading(false);
      }
    } else {
      toast({
        title: "Missing file info",
        description: "File information is missing. Please upload your CSV again.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      navigate('/');
    }
  }, [sessionId, navigate, toast]);

  const handleMappingComplete = (fieldMapping: Record<string, string>) => {
    setMapping(fieldMapping);
    
    // Store the mapping in session storage for use in deck creation
    sessionStorage.setItem('csvFieldMapping', JSON.stringify(fieldMapping));
    
    toast({
      title: "Mapping completed",
      description: "Your CSV field mapping has been saved",
      status: "success",
      duration: 3000,
      isClosable: true,
    });
    
    // Navigate to controls page to create the deck
    navigate('/controls');
  };

  const handleCancel = () => {
    // Ask for confirmation before cancelling
    if (window.confirm("Are you sure you want to cancel? Default field mapping will be used.")) {
      toast({
        title: "Mapping cancelled",
        description: "Default field mapping will be used",
        status: "info",
        duration: 3000,
        isClosable: true,
      });
      navigate('/controls');
    }
  };

  if (isLoading) {
    return (
      <Container maxW="container.xl" py={8}>
        <VStack spacing={6}>
          <Heading size="lg">Loading field mapping...</Heading>
          <Progress size="xs" isIndeterminate w="100%" />
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={4}>
      <VStack spacing={6} align="stretch">
        {/* Navigation breadcrumbs */}
        <Breadcrumb separator=">" fontSize="sm">
          <BreadcrumbItem>
            <BreadcrumbLink onClick={() => navigate('/')}> 
              <Flex alignItems="center">
                <Icon as={FaFileUpload as React.ElementType} mr={1} />
                 Upload CSV
              </Flex>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbItem isCurrentPage>
            <BreadcrumbLink>
              <Flex alignItems="center">
                <Icon as={FaListAlt as React.ElementType} mr={1} />
                 Map Fields
              </Flex>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbItem>
            <BreadcrumbLink onClick={() => navigate('/controls')}>
              <Flex alignItems="center">
                <Icon as={FaDownload as React.ElementType} mr={1} />
                 Create Deck
              </Flex>
            </BreadcrumbLink>
          </BreadcrumbItem>
        </Breadcrumb>
        
        <Card variant="outline" mb={4}>
          <CardHeader bg="blue.50" py={2}>
            <Heading size="md">Map CSV Fields to Anki Cards</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Text>
                Select which columns from your CSV should map to each Anki card field
              </Text>
              
              {serverFile && (
                <Alert status="info" borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>Processing file: {serverFile.name}</AlertTitle>
                    <AlertDescription>
                      Map the columns in your CSV to appropriate Anki card fields.
                      Required fields are marked with an asterisk (*).
                    </AlertDescription>
                  </Box>
                </Alert>
              )}
            </VStack>
          </CardBody>
        </Card>

        {sessionId && (
          <FieldMapperComponent
            sessionId={sessionId}
            file={null} // We don't need to pass a file since we're using sessionId
            onMappingComplete={handleMappingComplete}
            onCancel={handleCancel}
          />
        )}
        
        <Flex justifyContent="space-between" mt={4}>
          <Button
            onClick={() => navigate('/')}
            variant="outline"
            leftIcon={<Icon as={FaArrowLeft as React.ElementType} />}
          >
            Back to Upload
          </Button>
          <Button 
            variant="outline"
            colorScheme="blue"
            rightIcon={<Icon as={FaArrowRight as React.ElementType} />}
          >
            Skip to Deck Options
          </Button>
        </Flex>
      </VStack>
    </Container>
  );
};

export default FieldMappingPage;
