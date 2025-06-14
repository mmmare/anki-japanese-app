import React, { useState, useRef, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, 
  Button, 
  Text, 
  Heading,
  VStack,
  Input,
  Alert,
  AlertIcon,
  AlertTitle,
  useToast,
  Progress,
  Icon,
  useColorModeValue
} from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { SessionContext } from '../context/SessionContext';

const MotionBox = motion(Box);

const CsvUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const toast = useToast();
  const { setSessionId } = useContext(SessionContext);
  
  // Colors for light/dark mode
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
      setError(null);
      
      toast({
        title: "File selected",
        description: `${event.target.files[0].name} is ready to upload`,
        status: "info",
        duration: 3000,
        isClosable: true,
        position: "top"
      });
    }
  };

  const simulateProgress = () => {
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        const nextProgress = prev + 5;
        if (nextProgress >= 100) {
          clearInterval(interval);
          return 100;
        }
        return nextProgress;
      });
    }, 150);
    
    return () => clearInterval(interval);
  };
  
  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first");
      return;
    }
    
    if (!file.name.endsWith('.csv')) {
      setError("Only CSV files are allowed");
      return;
    }
    
    setLoading(true);
    setError(null);
    setUploadProgress(0);
    
    // Start the progress simulation
    const clearProgressSimulation = simulateProgress();
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      // Import the API URL dynamically to ensure we're using the same URL everywhere
      const { uploadCsv } = await import('../services/api');
      const data = await uploadCsv(file);
      
      console.log('Upload successful:', data);
      setUploadProgress(100);
      
      // Clear the progress simulation
      clearProgressSimulation();
      
      // Store the session ID
      if (data.session_id) {
        setSessionId(data.session_id);
      }
      
      toast({
        title: "Upload successful!",
        description: `${data.row_count} rows imported successfully`,
        status: "success",
        duration: 5000,
        isClosable: true,
        position: "top"
      });
      
      // Navigate to field mapping page after a short delay
      setTimeout(() => {
        // Store the uploaded file for the field mapper
        sessionStorage.setItem('uploadedFile', JSON.stringify({
          name: file.name,
          type: file.type,
          size: file.size
        }));
        navigate('/mapping');
      }, 1000);
      
    } catch (error) {
      console.error('Error uploading file:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setError(`Failed to upload file: ${errorMessage}`);
      clearProgressSimulation();
      setUploadProgress(0);
      
      toast({
        title: "Upload failed",
        description: `There was an error uploading your file: ${errorMessage}`,
        status: "error",
        duration: 5000,
        isClosable: true,
        position: "top"
      });
    } finally {
      setLoading(false);
    }
  };

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };
  
  return (
    <MotionBox 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      p={8} 
      m={0}
    >
      <VStack spacing={6} align="stretch">
        <Heading 
          as="h2" 
          size="xl" 
          textAlign="center" 
          color="brand.600"
          fontWeight="bold"
        >
          日本語 単語 CSV アップロード
        </Heading>
        
        <Text textAlign="center" fontSize="lg" mb={2}>
          Upload a CSV file with Japanese vocabulary to create your Anki deck
        </Text>
        <Button 
          size="sm" 
          colorScheme="accent" 
          mb={4}
          alignSelf="center"
          variant="outline"
          onClick={() => {
            // Download and use the sample file
            fetch('/sample-japanese.csv')
              .then(response => response.blob())
              .then(blob => {
                const file = new File([blob], 'sample-japanese.csv', { type: 'text/csv' });
                setFile(file);
                toast({
                  title: "Sample file loaded",
                  description: "A sample Japanese vocabulary file is ready to use",
                  status: "info",
                  duration: 3000,
                  isClosable: true
                });
              });
          }}
        >
          Try with sample data
        </Button>
        
        <Box 
          borderWidth="2px" 
          borderStyle="dashed" 
          borderColor={borderColor}
          borderRadius="lg" 
          p={6} 
          textAlign="center"
          bg={cardBg}
          _hover={{ borderColor: 'brand.500' }}
          cursor="pointer"
          onClick={triggerFileInput}
          transition="all 0.3s"
        >
          <Input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            hidden
            ref={fileInputRef}
          />
          
          <Icon 
            viewBox="0 0 24 24" 
            boxSize="12"
            color="brand.500"
            mb={3}
          >
            <path
              fill="currentColor"
              d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"
            />
          </Icon>
          
          <Heading size="md" mb={2}>
            {file ? file.name : "Drop your CSV file here"}
          </Heading>
          
          <Text color="gray.500">
            {file ? `${(file.size / 1024).toFixed(2)} KB` : "or click to browse"}
          </Text>
        </Box>
        
        {file && (
          <MotionBox
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            mb={4}
          >
            <Alert
              status="success"
              variant="subtle"
              flexDirection="column"
              alignItems="center"
              justifyContent="center"
              textAlign="center"
              borderRadius="md"
            >
              <AlertIcon boxSize="6" mr={0} />
              <AlertTitle mt={2} mb={1} fontSize="lg">
                File ready for upload
              </AlertTitle>
              <Text>
                {file.name} ({(file.size / 1024).toFixed(2)} KB)
              </Text>
            </Alert>
          </MotionBox>
        )}
        
        {error && (
          <Alert status="error" borderRadius="md">
            <AlertIcon />
            <Text fontWeight="medium">{error}</Text>
          </Alert>
        )}
        
        {loading && (
          <Box mt={4}>
            <Text mb={2} textAlign="center">
              {uploadProgress < 100 ? "Uploading..." : "Upload complete!"}
            </Text>
            <Progress 
              value={uploadProgress} 
              size="sm" 
              colorScheme="brand" 
              borderRadius="full"
              hasStripe
              isAnimated
            />
          </Box>
        )}
        
        <Button
          colorScheme="brand"
          size="lg"
          isLoading={loading}
          loadingText="Uploading..."
          onClick={handleUpload}
          isDisabled={!file || loading}
          width="full"
          mt={4}
          fontWeight="bold"
          fontSize="md"
          height="50px"
          _hover={{ transform: 'translateY(-2px)', boxShadow: 'lg' }}
          transition="all 0.2s"
        >
          {loading ? "Uploading..." : "Upload and Create Anki Deck"}
        </Button>
        
        <Text fontSize="sm" textAlign="center" color="gray.500">
          Your CSV should have columns for Japanese words, meanings, and optional tags (use underscores instead of spaces in tags)
        </Text>
      </VStack>
    </MotionBox>
  );
};

export default CsvUpload;