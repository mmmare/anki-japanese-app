import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api'; // Updated to use port 8000

interface EnrichmentOptions {
    enrichCards: boolean;
    includeAudio: boolean;
    includeExamples: boolean;
    includeExampleAudio?: boolean;
    useCore2000?: boolean;
}

export const uploadCsv = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await axios.post(`${API_BASE_URL}/deck/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Error uploading CSV:', error);
        throw error;
    }
};

export const createDeck = async (
    sessionId: string | null, 
    deckName: string = "Japanese Vocabulary",
    options: EnrichmentOptions = { enrichCards: false, includeAudio: false, includeExamples: false, includeExampleAudio: false, useCore2000: false },
    fieldMapping: Record<string, string> | null = null,
    onProgress?: (progress: { processed: number, total: number, status: string }) => void
) => {
    const formData = new FormData();
    
    if (sessionId) {
        formData.append('session_id', sessionId);
    }
    
    formData.append('deck_name', deckName);
    formData.append('enrich_cards', options.enrichCards.toString());
    formData.append('include_audio', options.includeAudio.toString());
    formData.append('include_examples', options.includeExamples.toString());
    formData.append('include_example_audio', options.includeExampleAudio?.toString() || 'false');
    formData.append('use_core2000', options.useCore2000?.toString() || 'false');
    
    // Add field mapping if provided
    if (fieldMapping) {
        formData.append('field_mapping', JSON.stringify(fieldMapping));
        formData.append('use_custom_mapping', 'true');
    } else {
        // Check if we have a saved mapping in session storage
        const savedMapping = sessionStorage.getItem('csvFieldMapping');
        if (savedMapping) {
            try {
                const parsedMapping = JSON.parse(savedMapping);
                if (parsedMapping && Object.keys(parsedMapping).length > 0) {
                    formData.append('field_mapping', savedMapping);
                    formData.append('use_custom_mapping', 'true');
                    console.log("Using field mapping from session storage:", parsedMapping);
                }
            } catch (e) {
                console.error("Error parsing field mapping from session storage:", e);
            }
        }
    }
    
    try {
        let totalWords = 0;
        let progressInterval: NodeJS.Timeout | null = null;
        let currentStep = 0;
        let progressUpdateCount = 20; // Default, will be updated later
        let currentPhase = 'preparing';
        
        if (onProgress) {
            // Starting progress
            onProgress({ processed: 0, total: 100, status: 'Preparing vocabulary data...' });
            
            // Get the session details to find out how many words we'll be processing
            try {
                const sessionDetails = await axios.get(`${API_BASE_URL}/deck/session/${sessionId}`);
                if (sessionDetails.data && sessionDetails.data.row_count) {
                    totalWords = sessionDetails.data.row_count;
                } else {
                    totalWords = 100; // Default estimate
                }
            } catch {
                totalWords = 100; // Default estimate if can't get session details
            }
            
            // Implement a smooth, more realistic simulated progress bar
            let currentProgress = 0;
            const totalSteps = options.enrichCards ? 100 : 50;
            const audioSteps = (options.includeAudio || options.includeExampleAudio) ? 40 : 10;
            const enrichSteps = options.enrichCards ? 50 : 0;
            
            // Calculate progression speeds - more conservative to avoid jumping from 0 to 100
            // Make the initial steps faster to show immediate feedback
            const initialStepTime = 50; // Faster at the beginning
            const midStepTime = 100;    // Medium speed in the middle
            const finalStepTime = 200;  // Slower near the end
            
            const estimatedTotalTime = 10000 + (totalWords * 200); // Base time + words adjustment
            // Update progress count based on word count
            progressUpdateCount = Math.min(100, Math.max(20, totalWords)); 
            
            // Reset step counter
            currentStep = 0;
            
            // Start with immediately showing some progress
            onProgress({ 
                processed: 1,
                total: totalWords,
                status: 'Preparing vocabulary data...'
            });
            
            // Start progress interval with a non-linear progression curve
            progressInterval = setInterval(() => {
                // Determine step time based on progress - faster early, slower near completion
                let stepTime;
                const progressPercent = currentStep / progressUpdateCount;
                
                // Adjust speed based on progress percent - slower as we approach 100%
                if (progressPercent < 0.1) {
                    currentPhase = 'preparing';
                    stepTime = initialStepTime;
                } else if (progressPercent < 0.7) {
                    currentPhase = options.enrichCards ? 'enriching' : 'processing';
                    stepTime = midStepTime;
                } else if (progressPercent < 0.9) {
                    currentPhase = (options.includeAudio || options.includeExampleAudio) ? 'audio' : 'packaging';
                    stepTime = finalStepTime;
                } else {
                    currentPhase = 'packaging';
                    stepTime = finalStepTime * 1.5;
                }
                
                if (currentStep < progressUpdateCount) {
                    currentStep++;
                    
                    // Calculate expected progress based on a sigmoid-like curve to avoid jumps
                    // Slower at start and end, faster in the middle
                    const sigmoidProgress = 1 / (1 + Math.exp(-12 * (progressPercent - 0.5)));
                    const adjustedProgress = Math.floor(sigmoidProgress * totalWords);
                    const processedWords = Math.min(totalWords - 1, Math.max(1, adjustedProgress));
                    
                    // Determine the current phase based on progress
                    let status: string;
                    
                    switch(currentPhase) {
                        case 'preparing':
                            status = 'Preparing vocabulary data...';
                            break;
                        case 'enriching':
                            const enrichedCount = Math.floor(progressPercent * totalWords);
                            status = `Enriching word ${enrichedCount} of ${totalWords}...`;
                            break;
                        case 'audio':
                            status = options.includeExampleAudio 
                                ? 'Generating vocabulary and example audio...'
                                : 'Generating vocabulary audio...';
                            break;
                        case 'packaging':
                            status = 'Packaging Anki deck...';
                            break;
                        default:
                            status = 'Processing deck...';
                    }
                    
                    // Use requestAnimationFrame for smoother UI updates
                    requestAnimationFrame(() => {
                        if (onProgress) {
                            onProgress({ 
                                processed: processedWords,
                                total: totalWords,
                                status
                            });
                        }
                    });
                    
                    // Dynamically adjust interval time based on remaining steps
                    if (progressInterval) {
                        clearInterval(progressInterval);
                    }
                    progressInterval = setInterval(() => {
                        // This is a recursive use of the same callback
                        // The interval timing will be reset on each call
                        if (currentStep < progressUpdateCount) {
                            currentStep++;
                            
                            // Same calculation logic as above
                            const progressPercent = currentStep / progressUpdateCount;
                            const sigmoidProgress = 1 / (1 + Math.exp(-12 * (progressPercent - 0.5)));
                            const adjustedProgress = Math.floor(sigmoidProgress * totalWords);
                            const processedWords = Math.min(totalWords - 1, Math.max(1, adjustedProgress));
                            
                            // Update phase based on progress
                            if (progressPercent < 0.1) {
                                currentPhase = 'preparing';
                            } else if (progressPercent < 0.7) {
                                currentPhase = options.enrichCards ? 'enriching' : 'processing';
                            } else if (progressPercent < 0.9) {
                                currentPhase = (options.includeAudio || options.includeExampleAudio) ? 'audio' : 'packaging';
                            } else {
                                currentPhase = 'packaging';
                            }
                            
                            // Determine the current phase based on progress
                            let status: string;
                            
                            switch(currentPhase) {
                                case 'preparing':
                                    status = 'Preparing vocabulary data...';
                                    break;
                                case 'enriching':
                                    const enrichedCount = Math.floor(progressPercent * totalWords);
                                    status = `Enriching word ${enrichedCount} of ${totalWords}...`;
                                    break;
                                case 'audio':
                                    status = options.includeExampleAudio 
                                        ? 'Generating vocabulary and example audio...'
                                        : 'Generating vocabulary audio...';
                                    break;
                                case 'packaging':
                                    status = 'Packaging Anki deck...';
                                    break;
                                default:
                                    status = 'Processing deck...';
                            }
                            
                            requestAnimationFrame(() => {
                                if (onProgress) {
                                    onProgress({ 
                                        processed: processedWords,
                                        total: totalWords,
                                        status
                                    });
                                }
                            });
                        }
                    }, stepTime);
                }
            }, initialStepTime);
        }
        
        // Make the request to create the deck
        const response = await axios.post(`${API_BASE_URL}/deck/create`, formData);
        
        // Clear the progress interval if it's running
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
        
        // Always ensure we show 100% completion to avoid stuck progress bars
        if (onProgress) {
            // First show "almost done" state if we aren't already at 100%
            if (currentStep < progressUpdateCount - 1) {
                onProgress({ 
                    processed: Math.max(1, totalWords - 5), 
                    total: totalWords,
                    status: 'Finalizing deck...'
                });
                
                // Short delay before showing completion to ensure visual feedback of the final step
                setTimeout(() => {
                    onProgress({ 
                        processed: totalWords, 
                        total: totalWords,
                        status: 'Deck created successfully!'
                    });
                }, 500);
            } else {
                // Already at or near 100%, just show completion
                onProgress({ 
                    processed: totalWords, 
                    total: totalWords,
                    status: 'Deck created successfully!'
                });
            }
        }
        
        // Log information about the created deck
        if (response.data && response.data.deck_id) {
            console.log(`Deck created successfully with ID: ${response.data.deck_id}`);
            console.log(`Deck data:`, response.data);
            
            // Verify the deck exists immediately after creation
            try {
                const checkResponse = await axios.head(`${API_BASE_URL}/deck/${response.data.deck_id}`);
                console.log(`Deck verification check returned status: ${checkResponse.status}`);
            } catch (error) {
                console.error(`Error verifying deck exists:`, error);
            }
        } else {
            console.warn(`No deck_id in response:`, response.data);
        }
        
        return response.data;
    } catch (error) {
        console.error('Error creating deck:', error);
        throw error;
    }
};

export const downloadDeck = async (deckId: string) => {
    try {
        console.log(`Downloading deck with ID: ${deckId}`);
        
        // Using axios to trigger file download
        const response = await axios({
            url: `${API_BASE_URL}/deck/download/${deckId}`,
            method: 'GET',
            responseType: 'blob', // Important for binary files
            timeout: 30000, // 30 seconds timeout for potentially large files
        });
        
        console.log('Download response received', {
            status: response.status,
            headers: response.headers,
            dataType: typeof response.data,
            dataSize: response.data.size
        });
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        
        // Get filename from content disposition if available, or use default
        const contentDisposition = response.headers['content-disposition'];
        let filename = 'japanese_vocabulary.apkg';
        
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+?)"?$/);
            if (filenameMatch && filenameMatch[1]) {
                filename = filenameMatch[1];
                console.log(`Using filename from Content-Disposition: ${filename}`);
            }
        } else {
            console.log(`Using default filename: ${filename}`);
        }
        
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        
        console.log(`Triggering download for ${filename}`);
        link.click();
        
        // Clean up
        setTimeout(() => {
            window.URL.revokeObjectURL(url);
            link.remove();
            console.log('Download link removed');
        }, 100);
        
        return true;
    } catch (error) {
        console.error('Error downloading deck:', error);
        throw error;
    }
};

export const analyzeCsvFields = async (file: File) => {
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await axios.post(`${API_BASE_URL}/mapping/analyze`, formData);
        return response.data;
    } catch (error) {
        console.error('Error analyzing CSV fields:', error);
        throw error;
    }
};

export const applyFieldMapping = async (sessionId: string, mapping: Record<string, string>) => {
    try {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('mapping', JSON.stringify(mapping));
        
        const response = await axios.post(`${API_BASE_URL}/mapping/apply`, formData);
        return response.data;
    } catch (error) {
        console.error('Error applying field mapping:', error);
        throw error;
    }
};

export const validateFieldMapping = async (sessionId: string, mapping: Record<string, string>) => {
    try {
        // Log what we're sending for debugging purposes
        console.debug('Validating mapping with session:', sessionId);
        console.debug('Mapping data:', mapping);
        
        const response = await axios.post(`${API_BASE_URL}/mapping/validate`, {
            session_id: sessionId,
            mapping: mapping
        });
        
        // Log the response for debugging
        console.debug('Validation response:', response.data);
        return response.data;
    } catch (error) {
        console.error('Error validating field mapping:', error);
        
        // Return a default error response instead of throwing
        return {
            valid: false,
            errors: {
                '_general': 'Failed to validate field mapping with server'
            }
        };
    }
};

export const lookupWord = async (word: string) => {
    try {
        const formData = new FormData();
        formData.append('word', word);
        
        const response = await axios.post(`${API_BASE_URL}/enrich/lookup`, formData);
        return response.data;
    } catch (error) {
        console.error('Error looking up word:', error);
        throw error;
    }
};

export const analyzeCsvFromSession = async (sessionId: string) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/mapping/analyze-session`, {
            session_id: sessionId
        });
        return response.data;
    } catch (error) {
        console.error('Error analyzing CSV from session:', error);
        throw error;
    }
};

export const getFieldMappingStatus = async (sessionId: string) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/mapping/status/${sessionId}`);
        return response.data;
    } catch (error) {
        console.error('Error getting field mapping status:', error);
        throw error;
    }
};

export const previewCards = async (
    sessionId: string | null, 
    deckName: string = "Japanese Vocabulary",
    sampleCount: number = 5, // Default to 5 sample cards
    options: EnrichmentOptions = { enrichCards: false, includeAudio: false, includeExamples: false, includeExampleAudio: false, useCore2000: false },
    fieldMapping: Record<string, string> | null = null
) => {
    const formData = new FormData();
    
    if (sessionId) {
        formData.append('session_id', sessionId);
    }
    
    formData.append('deck_name', deckName);
    formData.append('sample_count', sampleCount.toString());
    formData.append('enrich_cards', options.enrichCards.toString());
    formData.append('include_audio', options.includeAudio.toString());
    formData.append('include_examples', options.includeExamples.toString());
    formData.append('include_example_audio', options.includeExampleAudio?.toString() || 'false');
    formData.append('use_core2000', options.useCore2000?.toString() || 'false');
    
    // Add field mapping if provided
    if (fieldMapping) {
        formData.append('field_mapping', JSON.stringify(fieldMapping));
    } else {
        // Check if we have a saved mapping in session storage
        const savedMapping = sessionStorage.getItem('csvFieldMapping');
        if (savedMapping) {
            try {
                const parsedMapping = JSON.parse(savedMapping);
                if (parsedMapping && Object.keys(parsedMapping).length > 0) {
                    formData.append('field_mapping', savedMapping);
                    console.log("Using field mapping from session storage for preview:", parsedMapping);
                }
            } catch (e) {
                console.error("Error parsing field mapping from session storage:", e);
            }
        }
    }
    
    try {
        const response = await axios.post(`${API_BASE_URL}/deck/preview`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        
        return response.data;
    } catch (error) {
        console.error('Error previewing cards:', error);
        throw error;
    }
};

// Word collection API functions
export const addWordToCollection = async (
    word: string,
    reading?: string,
    meanings?: string[],
    partsOfSpeech?: string[],
    examples?: any[],
    collectionId?: string,
    selectedSenseIds?: number[]  // New parameter for selected sense IDs
) => {
    try {
        const formData = new FormData();
        formData.append('word', word);
        
        if (collectionId) {
            formData.append('collection_id', collectionId);
        }
        if (reading) {
            formData.append('reading', reading);
        }
        if (meanings) {
            formData.append('meanings', JSON.stringify(meanings));
        }
        if (partsOfSpeech) {
            formData.append('parts_of_speech', JSON.stringify(partsOfSpeech));
        }
        if (examples) {
            formData.append('examples', JSON.stringify(examples));
        }
        if (selectedSenseIds) {
            formData.append('selected_sense_ids', JSON.stringify(selectedSenseIds));
        }
        
        const response = await axios.post(`${API_BASE_URL}/enrich/collection/add-word`, formData);
        return response.data;
    } catch (error) {
        console.error('Error adding word to collection:', error);
        throw error;
    }
};

export const getCollection = async (collectionId: string) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/enrich/collection/${collectionId}`);
        return response.data;
    } catch (error) {
        console.error('Error getting collection:', error);
        throw error;
    }
};

export const removeWordFromCollection = async (collectionId: string, word: string) => {
    try {
        const formData = new FormData();
        formData.append('word', word);
        
        const response = await axios.delete(`${API_BASE_URL}/enrich/collection/${collectionId}/word`, {
            data: formData
        });
        return response.data;
    } catch (error) {
        console.error('Error removing word from collection:', error);
        throw error;
    }
};

export const createDeckFromCollection = async (
    collectionId: string,
    deckName: string = "Japanese Vocabulary",
    includeAudio: boolean = false,
    includeExamples: boolean = false,
    includeExampleAudio: boolean = false
) => {
    try {
        const formData = new FormData();
        formData.append('deck_name', deckName);
        formData.append('include_audio', includeAudio.toString());
        formData.append('include_examples', includeExamples.toString());
        formData.append('include_example_audio', includeExampleAudio.toString());
        
        const response = await axios.post(`${API_BASE_URL}/enrich/collection/${collectionId}/create-deck`, formData, {
            responseType: 'blob'
        });
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${deckName}.apkg`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        
        return { success: true, message: 'Deck downloaded successfully' };
    } catch (error) {
        console.error('Error creating deck from collection:', error);
        throw error;
    }
};