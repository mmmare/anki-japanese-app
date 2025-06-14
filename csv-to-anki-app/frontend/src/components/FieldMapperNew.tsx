import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Select,
  Button,
  Text,
  useToast,
  VStack,
  HStack,
  Badge,
  Divider,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Tooltip,
  IconButton,
  Progress,
  Icon,
} from '@chakra-ui/react';
import { analyzeCsvFields, applyFieldMapping, validateFieldMapping } from '../services/api';
import { RepeatIcon, InfoIcon, CheckCircleIcon, WarningIcon } from '@chakra-ui/icons';
import { FaFileUpload, FaListAlt, FaDownload, FaArrowLeft, FaArrowRight } from 'react-icons/fa';

interface FieldMappingProps {
  sessionId: string | null;
  file: File | null;
  onMappingComplete: (mapping: Record<string, string>) => void;
  onCancel: () => void;
}

interface SampleData {
  [key: string]: string;
}

const FieldMapperComponent: React.FC<FieldMappingProps> = ({ 
  sessionId, 
  file, 
  onMappingComplete, 
  onCancel 
}) => {
  const [headers, setHeaders] = useState<string[]>([]);
  const [sampleData, setSampleData] = useState<SampleData[]>([]);
  const [suggestedMapping, setSuggestedMapping] = useState<Record<string, string>>({});
  const [currentMapping, setCurrentMapping] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [applyingMapping, setApplyingMapping] = useState<boolean>(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [isChanged, setIsChanged] = useState<boolean>(false);
  const [mapCompleted, setMapCompleted] = useState<boolean>(false);
  
  const toast = useToast();
  
  // Anki field names with validation requirements
  const ankiFields = [
    { id: 'japanese', label: 'Japanese Word', required: true },
    { id: 'english', label: 'English Meaning', required: false },
    { id: 'reading', label: 'Reading/Pronunciation', required: false },
    { id: 'example', label: 'Example Sentence', required: false },
    { id: 'tags', label: 'Tags', required: false }
  ];
  
  useEffect(() => {
    // Analyze the CSV file when component mounts
    const analyzeCSV = async () => {
      setLoading(true);
      setError(null);
      try {
        // First check if we have a sessionId (server-side file)
        if (sessionId) {
          // We need a function to analyze the CSV from the session
          try {
            const result = await fetch(`http://localhost:8000/api/mapping/analyze-session`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ session_id: sessionId }),
            });
            
            if (!result.ok) {
              throw new Error(`Server error: ${result.status}`);
            }
            
            const data = await result.json();
            setHeaders(data.headers);
            setSampleData(data.sample_data);
            setSuggestedMapping(data.suggested_mapping);
            setCurrentMapping(data.suggested_mapping);
            
            // Check validation right away
            validateMapping(data.suggested_mapping);
          } catch (error) {
            console.error("Error analyzing from session:", error);
            setError("Failed to analyze the uploaded CSV file");
          }
        } 
        // If no sessionId but we have a file (direct upload)
        else if (file) {
          const result = await analyzeCsvFields(file);
          setHeaders(result.headers);
          setSampleData(result.sample_data);
          setSuggestedMapping(result.suggested_mapping);
          setCurrentMapping(result.suggested_mapping);
          
          // Check validation right away
          validateMapping(result.suggested_mapping);
        } else {
          setError("No CSV file available to analyze");
        }
      } catch (err) {
        console.error("Error analyzing CSV:", err);
        setError("Failed to analyze CSV file");
      } finally {
        setLoading(false);
      }
    };
    
    analyzeCSV();
  }, [file, sessionId]);
  
  // Validate that required fields are mapped
  const validateMapping = (mapping: Record<string, string>): boolean => {
    const errors: Record<string, string> = {};
    let isValid = true;
    
    // Check if required fields are mapped
    ankiFields.forEach(field => {
      if (field.required && (!mapping[field.id] || mapping[field.id] === '')) {
        errors[field.id] = `${field.label} is required`;
        isValid = false;
      }
    });
    
    // Check if there are duplicate mappings
    const usedHeaders = Object.values(mapping).filter(Boolean);
    const uniqueHeaders = new Set(usedHeaders);
    if (usedHeaders.length !== uniqueHeaders.size) {
      // Find duplicates
      const seen = new Set();
      const duplicates = usedHeaders.filter(item => {
        if (seen.has(item)) return true;
        seen.add(item);
        return false;
      });
      
      // Add errors for fields with duplicate mappings
      Object.entries(mapping).forEach(([field, header]) => {
        if (duplicates.includes(header)) {
          errors[field] = `This column is used in multiple fields`;
        }
      });
      isValid = false;
    }
    
    setValidationErrors(errors);
    return isValid;
  };
  
  // Compare if the current mapping is different from suggested
  useEffect(() => {
    const isMappingDifferent = JSON.stringify(currentMapping) !== JSON.stringify(suggestedMapping);
    setIsChanged(isMappingDifferent);
    
    // Validate whenever the mapping changes
    validateMapping(currentMapping);
    
    // Perform server-side validation if we have a session ID
    // but only do it when the mapping has meaningful changes
    if (sessionId && isMappingDifferent && Object.keys(currentMapping).some(k => !!currentMapping[k])) {
      const validateOnServer = async () => {
        try {
          const validationResult = await validateFieldMapping(sessionId, currentMapping);
          if (!validationResult.valid) {
            // Merge server validation errors with client-side errors
            setValidationErrors(prev => ({
              ...prev,
              ...validationResult.errors
            }));
          }
        } catch (error) {
          console.error("Background validation error:", error);
          // Don't show errors during background validation
        }
      };
      
      // Debounce the validation to avoid too many requests
      const debounceTimer = setTimeout(() => {
        validateOnServer();
      }, 500);
      
      return () => clearTimeout(debounceTimer);
    }
  }, [currentMapping, suggestedMapping, sessionId]);
  
  const handleMappingChange = (ankiField: string, csvHeader: string) => {
    const newMapping = {
      ...currentMapping,
      [ankiField]: csvHeader
    };
    
    setCurrentMapping(newMapping);
  };
  
  const handleApplyMapping = async () => {
    try {
      // First validate mapping
      if (!validateMapping(currentMapping)) {
        toast({
          title: "Validation Error",
          description: "Please fix the errors in your field mapping",
          status: "error",
          duration: 3000,
          isClosable: true,
        });
        return;
      }
      
      setApplyingMapping(true);
      if (sessionId) {
        await applyFieldMapping(sessionId, currentMapping);
        
        // Save to session storage
        sessionStorage.setItem('csvFieldMapping', JSON.stringify(currentMapping));
        
        toast({
          title: "Field mapping applied",
          description: "Your custom field mapping has been saved",
          status: "success",
          duration: 3000,
          isClosable: true,
        });
        
        setMapCompleted(true);
        setTimeout(() => {
          onMappingComplete(currentMapping);
        }, 1000); // Give time for completion animation
      } else {
        throw new Error("No session ID available");
      }
    } catch (err) {
      console.error("Error applying field mapping:", err);
      
      toast({
        title: "Mapping failed",
        description: "Failed to apply field mapping",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setApplyingMapping(false);
    }
  };
  
  const handleUseDefault = () => {
    setCurrentMapping(suggestedMapping);
    
    toast({
      title: "Default mapping applied",
      description: "Using the suggested field mapping",
      status: "info",
      duration: 2000,
      isClosable: true,
    });
    
    // Save to session storage
    sessionStorage.setItem('csvFieldMapping', JSON.stringify(suggestedMapping));
    
    setMapCompleted(true);
    setTimeout(() => {
      onMappingComplete(suggestedMapping);
    }, 1000); // Give time for completion animation
  };
  
  const handleResetMapping = () => {
    setCurrentMapping({});
    setValidationErrors({});
    
    toast({
      title: "Mapping reset",
      description: "Field mapping has been reset",
      status: "warning",
      duration: 2000,
      isClosable: true,
    });
  };
  
  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" color="blue.500" />
        <Text mt={4}>Analyzing CSV file...</Text>
        <Progress size="xs" isIndeterminate colorScheme="blue" mt={4} />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Alert status="error" borderRadius="md">
        <AlertIcon />
        <Box>
          <AlertTitle>Error analyzing CSV</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
          <Button mt={3} onClick={onCancel}>Go back</Button>
        </Box>
      </Alert>
    );
  }
  
  if (mapCompleted) {
    return (
      <Box textAlign="center" py={10}>
        <CheckCircleIcon boxSize="50px" color="green.500" />
        <Heading as="h3" size="md" mt={4}>Mapping Complete!</Heading>
        <Text mt={2}>Redirecting to deck creation...</Text>
        <Progress size="xs" isIndeterminate colorScheme="green" mt={4} />
      </Box>
    );
  }
  
  return (
    <VStack spacing={5} align="stretch" p={4}>
      <Heading as="h2" size="md">Map CSV Fields to Anki Fields</Heading>
      
      <Text>
        Choose which CSV columns should map to each Anki card field.
        <Badge ml={2} colorScheme="green">Auto-detected</Badge>
      </Text>
      
      {Object.keys(validationErrors).length > 0 && (
        <Alert status="warning" borderRadius="md">
          <AlertIcon />
          <Box>
            <AlertTitle>Please fix these issues</AlertTitle>
            <VStack align="start" spacing={1} mt={2}>
              {Object.entries(validationErrors).map(([field, error]) => (
                <Text key={field} fontSize="sm">• {error}</Text>
              ))}
            </VStack>
          </Box>
        </Alert>
      )}
      
      <Box overflowX="auto">
        <Table variant="simple" size="sm">
          <Thead>
            <Tr>
              <Th>Anki Field</Th>
              <Th>CSV Column</Th>
              <Th>Sample Data</Th>
              <Th width="40px"></Th>
            </Tr>
          </Thead>
          <Tbody>
            {ankiFields.map((field) => (
              <Tr key={field.id}>
                <Td fontWeight="bold">
                  {field.label}
                  {field.required && <Text as="span" color="red.500" ml={1}>*</Text>}
                </Td>
                <Td>
                  <Select 
                    value={currentMapping[field.id] || ''} 
                    onChange={(e) => handleMappingChange(field.id, e.target.value)}
                    isInvalid={!!validationErrors[field.id]}
                    placeholder="Select column..."
                  >
                    <option value="">Not mapped</option>
                    {headers.map((header) => (
                      <option key={header} value={header}>
                        {header}
                      </option>
                    ))}
                  </Select>
                </Td>
                <Td>
                  {currentMapping[field.id] && sampleData.length > 0 ? (
                    <Box maxW="200px" overflow="hidden" textOverflow="ellipsis" whiteSpace="nowrap">
                      {sampleData[0][currentMapping[field.id]]}
                    </Box>
                  ) : (
                    <Text color="gray.500" fontStyle="italic">No mapping</Text>
                  )}
                </Td>
                <Td>
                  {validationErrors[field.id] ? (
                    <Tooltip label={validationErrors[field.id]}>
                      <WarningIcon color="orange.500" />
                    </Tooltip>
                  ) : currentMapping[field.id] ? (
                    <Tooltip label="Field is mapped correctly">
                      <CheckCircleIcon color="green.500" />
                    </Tooltip>
                  ) : null}
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>
      
      <Box>
        <Heading as="h3" size="sm" mb={2}>Sample Data Preview</Heading>
        <Box overflowX="auto" maxHeight="200px" overflowY="auto" borderWidth="1px" borderRadius="md">
          <Table variant="simple" size="sm">
            <Thead>
              <Tr>
                {headers.map((header) => (
                  <Th key={header}>{header}</Th>
                ))}
              </Tr>
            </Thead>
            <Tbody>
              {sampleData.map((row, idx) => (
                <Tr key={idx}>
                  {headers.map((header) => (
                    <Td key={`${idx}-${header}`}>{row[header]}</Td>
                  ))}
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      </Box>
      
      <Divider />
      
      <HStack spacing={4} justifyContent="flex-end">
        <Button onClick={onCancel} variant="outline" leftIcon={<Icon as={FaArrowLeft as React.ElementType} />}>
          Back to Upload
        </Button>
        <Tooltip label="Reset all mappings">
          <IconButton 
            aria-label="Reset mapping" 
            icon={<RepeatIcon />} 
            onClick={handleResetMapping} 
            colorScheme="red"
            variant="outline"
            isDisabled={Object.keys(currentMapping).length === 0}
          />
        </Tooltip>
        <Button 
          onClick={handleUseDefault} 
          colorScheme="blue" 
          variant="outline"
          isDisabled={!Object.keys(suggestedMapping).length}
          leftIcon={<Icon as={FaListAlt as React.ElementType} />}
        >
          Use Suggested Mapping
        </Button>
        <Button 
          onClick={handleApplyMapping} 
          colorScheme="green" 
          isLoading={applyingMapping}
          isDisabled={Object.keys(validationErrors).length > 0}
          leftIcon={<Icon as={FaDownload as React.ElementType} />}
        >
          Apply Custom Mapping
        </Button>
        <Button rightIcon={<Icon as={FaArrowRight as React.ElementType} />} colorScheme="teal" variant="solid" onClick={() => onMappingComplete(currentMapping)}>
          Skip to Deck Options
        </Button>
      </HStack>
    </VStack>
  );
};

export default FieldMapperComponent;
