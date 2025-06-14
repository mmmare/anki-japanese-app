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
} from '@chakra-ui/react';
import { CheckCircleIcon, InfoIcon, RepeatIcon, WarningIcon } from '@chakra-ui/icons';
import { analyzeCsvFields, applyFieldMapping, validateFieldMapping } from '../services/api';

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
  const [validatingWithServer, setValidatingWithServer] = useState<boolean>(false);
  const [serverValidationComplete, setServerValidationComplete] = useState<boolean>(false);
  
  const toast = useToast();
  
  // Anki field names
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
  
  const handleMappingChange = (ankiField: string, csvHeader: string) => {
    setCurrentMapping({
      ...currentMapping,
      [ankiField]: csvHeader
    });
  };
  
  const handleApplyMapping = async () => {
    try {
      // First client-side validation
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
        // Perform server-side validation
        try {
          const validationResult = await validateFieldMapping(sessionId, currentMapping);
          
          if (!validationResult.valid) {
            // Update validation errors from server
            setValidationErrors(validationResult.errors);
            
            toast({
              title: "Server Validation Failed",
              description: "The server found issues with your field mapping. Please check the highlighted fields.",
              status: "warning",
              duration: 4000,
              isClosable: true,
            });
            return;
          }
        } catch (validationError) {
          console.error("Error validating mapping:", validationError);
          // Continue with applying the mapping if the validation endpoint fails
        }
        
        // Apply the mapping
        await applyFieldMapping(sessionId, currentMapping);
        
        // Save to session storage for persistence
        sessionStorage.setItem('csvFieldMapping', JSON.stringify(currentMapping));
        
        toast({
          title: "Field mapping applied",
          description: "Your custom field mapping has been saved",
          status: "success",
          duration: 3000,
          isClosable: true,
        });
        
        onMappingComplete(currentMapping);
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
  
  const handleUseDefault = async () => {
    setCurrentMapping(suggestedMapping);
    setValidationErrors({});
    
    // Apply the suggested mapping automatically if it passes validation
    if (validateMapping(suggestedMapping)) {
      setApplyingMapping(true);
      
      try {
        if (sessionId) {
          await applyFieldMapping(sessionId, suggestedMapping);
          
          // Save to session storage for persistence
          sessionStorage.setItem('csvFieldMapping', JSON.stringify(suggestedMapping));
          
          toast({
            title: "Default mapping applied",
            description: "The suggested field mapping has been applied",
            status: "success",
            duration: 3000,
            isClosable: true,
          });
          
          onMappingComplete(suggestedMapping);
        }
      } catch (error) {
        console.error("Error applying default mapping:", error);
        
        toast({
          title: "Default mapping failed",
          description: "Failed to apply the suggested mapping",
          status: "error",
          duration: 3000,
          isClosable: true,
        });
      } finally {
        setApplyingMapping(false);
      }
    } else {
      // Just update the UI with the suggested mapping
      toast({
        title: "Default mapping loaded",
        description: "Using the suggested field mapping. Click Apply to save it.",
        status: "info",
        duration: 3000,
        isClosable: true,
      });
    }
  };
  
  const handleResetMapping = () => {
    if (Object.keys(currentMapping).length > 0) {
      // Confirm before clearing all mappings if there are any
      if (window.confirm("Are you sure you want to reset all field mappings?")) {
        setCurrentMapping({});
        setValidationErrors({});
        
        toast({
          title: "Mapping reset",
          description: "All field mappings have been cleared",
          status: "warning",
          duration: 2000,
          isClosable: true,
        });
      }
    } else {
      toast({
        title: "Nothing to reset",
        description: "No mappings are currently set",
        status: "info",
        duration: 2000,
        isClosable: true,
      });
    }
  };
  
  // Validate mapping when it changes
  useEffect(() => {
    if (currentMapping && Object.keys(currentMapping).length > 0) {
      validateMapping(currentMapping);
      
      // Check if mapping has changed from suggested
      const isMappingDifferent = JSON.stringify(currentMapping) !== JSON.stringify(suggestedMapping);
      setIsChanged(isMappingDifferent);
      
      // Perform server-side validation if we have a session ID
      // but only do it when the mapping has meaningful changes
      if (sessionId && isMappingDifferent && hasRequiredFields(currentMapping)) {
        const validateOnServer = async () => {
          try {
            setValidatingWithServer(true);
            const validationResult = await validateFieldMapping(sessionId, currentMapping);
            setServerValidationComplete(true);
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
          } finally {
            setValidatingWithServer(false);
          }
        };
        
        // Debounce the validation to avoid too many requests
        const debounceTimer = setTimeout(() => {
          validateOnServer();
        }, 500);
        
        return () => clearTimeout(debounceTimer);
      }
    }
  }, [currentMapping, suggestedMapping, sessionId]);
  
  // Check if all required fields are mapped (helper function)
  const hasRequiredFields = (mapping: Record<string, string>): boolean => {
    return ankiFields
      .filter(field => field.required)
      .every(field => mapping[field.id] && mapping[field.id] !== '');
  };
  
  // Validate that required fields are mapped correctly
  const validateMapping = (mapping: Record<string, string>): boolean => {
    const errors: Record<string, string> = {};
    let isValid = true;
    
    // Check required fields
    ankiFields.forEach(field => {
      if (field.required && (!mapping[field.id] || mapping[field.id] === '')) {
        errors[field.id] = `${field.label} is required`;
        isValid = false;
      }
    });
    
    // Check for duplicate mappings
    const usedHeaders = Object.values(mapping).filter(Boolean);
    const uniqueHeaders = new Set(usedHeaders);
    if (usedHeaders.length !== uniqueHeaders.size) {
      // Find duplicates
      const seen = new Set();
      const duplicates = usedHeaders.filter(item => {
        if (!item) return false;
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
  
  // Helper function to find CSV column headers that might match Anki field names
  const findPossibleMatches = (ankiField: string): string[] => {
    if (!headers.length) return [];
    
    // Define common synonyms for each field type
    const synonyms: Record<string, string[]> = {
      'japanese': ['japanese', 'word', 'expression', 'kanji', 'vocabulary', '日本語', 'front'],
      'english': ['english', 'meaning', 'translation', 'definition', '英語', 'back'],
      'reading': ['reading', 'pronunciation', 'kana', 'hiragana', 'yomigana', '読み方'],
      'example': ['example', 'sentence', 'usage', 'context', '例文'],
      'tags': ['tags', 'tag', 'category', 'categories', 'group']
    };
    
    const fieldSynonyms = synonyms[ankiField] || [];
    
    // Check for headers that match any of the synonyms (case insensitive)
    return headers.filter(header => 
      fieldSynonyms.some(synonym => 
        header.toLowerCase().includes(synonym.toLowerCase())
      )
    );
  };
  
  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" color="blue.500" />
        <Text mt={4}>Analyzing CSV file...</Text>
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
  
  return (
    <VStack spacing={5} align="stretch" p={4}>
      <HStack justifyContent="space-between" alignItems="center">
        <Heading as="h2" size="md">Map CSV Fields to Anki Fields</Heading>
        <HStack spacing={2}>
          {validatingWithServer && (
            <HStack>
              <Spinner size="xs" />
              <Text fontSize="xs" color="gray.500">Validating...</Text>
            </HStack>
          )}
          {serverValidationComplete && !validatingWithServer && Object.keys(validationErrors).length === 0 && (
            <HStack>
              <CheckCircleIcon color="green.500" />
              <Text fontSize="xs" color="green.500">Validation passed</Text>
            </HStack>
          )}
          {isChanged && (
            <Badge colorScheme="purple">Custom Mapping</Badge>
          )}
        </HStack>
      </HStack>
      
      <HStack>
        <Text>
          Choose which CSV columns should map to each Anki card field.
        </Text>
        <Badge colorScheme="green">Auto-detected</Badge>
        <Tooltip label="The system has automatically suggested mappings based on your CSV content. Required fields are marked with an asterisk (*).">
          <InfoIcon color="blue.500" />
        </Tooltip>
      </HStack>
      
      {Object.keys(validationErrors).length > 0 && (
        <Alert status="warning" borderRadius="md">
          <AlertIcon />
          <Box width="100%">
            <HStack justifyContent="space-between">
              <AlertTitle>Please fix these issues</AlertTitle>
              {validatingWithServer && (
                <Badge colorScheme="blue">Checking with server...</Badge>
              )}
            </HStack>
            <VStack align="start" spacing={1} mt={2}>
              {Object.entries(validationErrors)
                .filter(([field]) => field !== '_general') // Skip general errors for now
                .map(([field, error]) => (
                  <HStack key={field} width="100%" justifyContent="space-between">
                    <Text fontSize="sm">• {error}</Text>
                    <Badge colorScheme={field.startsWith('_server_') ? "red" : "orange"}>
                      {field.startsWith('_server_') ? "Server Validation" : "Client Validation"}
                    </Badge>
                  </HStack>
                ))
              }
              {validationErrors['_general'] && (
                <Alert status="error" size="sm" mt={2} width="100%">
                  <AlertIcon />
                  <AlertDescription fontSize="sm">{validationErrors['_general']}</AlertDescription>
                </Alert>
              )}
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
              <Th width="40px">Status</Th>
            </Tr>
          </Thead>
          <Tbody>
            {ankiFields.map((field) => (
              <Tr key={field.id} bg={field.required ? "gray.50" : undefined}>
                <Td fontWeight="bold">
                  {field.label}
                  {field.required && (
                    <Tooltip label="This field is required for proper Anki card creation">
                      <Text as="span" color="red.500" ml={1}>*</Text>
                    </Tooltip>
                  )}
                </Td>
                <Td>
                  <Select 
                    value={currentMapping[field.id] || ''} 
                    onChange={(e) => handleMappingChange(field.id, e.target.value)}
                    isInvalid={!!validationErrors[field.id]}
                    placeholder="Select column..."
                  >
                    <option value="">Not mapped</option>
                    {headers.map((header) => {
                      // Check if this header is a potential match for the current field
                      const possibleMatches = findPossibleMatches(field.id);
                      const isMatch = possibleMatches.includes(header);
                      const isSuggested = suggestedMapping[field.id] === header;
                      
                      return (
                        <option 
                          key={header} 
                          value={header}
                          style={{
                            fontWeight: isMatch || isSuggested ? 'bold' : 'normal',
                            backgroundColor: isSuggested ? '#E6FFFA' : isMatch ? '#F0FFF4' : undefined
                          }}
                        >
                          {header} {isSuggested ? '(suggested)' : isMatch ? '(possible match)' : ''}
                        </option>
                      );
                    })}
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
                <Td textAlign="center">
                  {validationErrors[field.id] ? (
                    <Tooltip label={validationErrors[field.id]}>
                      <WarningIcon color="orange.500" />
                    </Tooltip>
                  ) : currentMapping[field.id] ? (
                    <Tooltip label="Field is mapped correctly">
                      <CheckCircleIcon color="green.500" />
                    </Tooltip>
                  ) : field.required ? (
                    <Tooltip label="This field is required">
                      <WarningIcon color="red.400" />
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
      
      <HStack spacing={4} justifyContent="space-between">
        <Button onClick={onCancel} variant="outline" leftIcon={<WarningIcon />}>
          Cancel
        </Button>
        
        <HStack spacing={3}>
          <Tooltip label="Clear all current mappings">
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
            isDisabled={Object.keys(suggestedMapping).length === 0}
            leftIcon={<InfoIcon />}
          >
            Use Suggested Mapping
          </Button>
          
          <Button 
            onClick={handleApplyMapping} 
            colorScheme="green" 
            isLoading={applyingMapping}
            isDisabled={Object.keys(validationErrors).length > 0}
            leftIcon={<CheckCircleIcon />}
          >
            Apply Custom Mapping
          </Button>
        </HStack>
      </HStack>
      
      <Alert status="info" size="sm" variant="subtle">
        <AlertIcon />
        <Box>
          <AlertDescription fontSize="sm">
            Your mapping choices will be saved and used when creating the Anki deck. The Japanese Word and English Meaning fields are required.
          </AlertDescription>
          
          <Box mt={2} fontSize="xs" color="gray.600">
            <Text fontWeight="bold">Need help?</Text>
            <Text>• <b>Required fields</b> are marked with an asterisk (*)</Text>
            <Text>• <b>Suggested mappings</b> are highlighted in the dropdowns</Text>
            <Text>• Each CSV column can only be mapped to one Anki field</Text>
            <Text>• Click "Use Suggested Mapping" if you're not sure what to do</Text>
          </Box>
        </Box>
      </Alert>
    </VStack>
  );
};

export default FieldMapperComponent;
