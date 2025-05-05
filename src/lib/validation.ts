// src/lib/validation.ts

/**
 * Validation utility functions for API settings
 */

// Validate URL format
export const isValidUrl = (url: string): { isValid: boolean; errorMessage?: string } => {
  // Check if field is empty
  if (!url || url.trim() === '') {
    return { isValid: false, errorMessage: 'URL is required' };
  }

  try {
    // Check for protocol (http/https)
    if (!url.match(/^https?:\/\//i)) {
      return { 
        isValid: false, 
        errorMessage: 'URL must start with http:// or https://' 
      };
    }

    // Try to create URL object to validate the whole URL
    const urlObj = new URL(url);
    
    // Check if hostname exists
    if (!urlObj.hostname) {
      return { 
        isValid: false, 
        errorMessage: 'URL must include a valid hostname' 
      };
    }
    
    return { isValid: true };
  } catch (error) {
    return { 
      isValid: false, 
      errorMessage: 'URL is not in a valid format' 
    };
  }
};

// Validate API key format with more specific rules
export const isValidApiKey = (apiKey: string, minLength = 8): { isValid: boolean; errorMessage?: string } => {
  // Check if field is empty
  if (!apiKey || apiKey.trim() === '') {
    return { isValid: false, errorMessage: 'API key is required' };
  }
  
  // Check minimum length
  if (apiKey.length < minLength) {
    return { 
      isValid: false, 
      errorMessage: `API key should be at least ${minLength} characters long` 
    };
  }
  
  // Check for valid characters (letters, numbers, and some symbols)
  if (!/^[a-zA-Z0-9._-]+$/.test(apiKey)) {
    return { 
      isValid: false, 
      errorMessage: 'API key can only contain letters, numbers, dots, underscores, and hyphens' 
    };
  }
  
  return { isValid: true };
};

// Validate user ID
export const isValidUserId = (userId: string): { isValid: boolean; errorMessage?: string } => {
  // Check if field is empty
  if (!userId || userId.trim() === '') {
    return { isValid: false, errorMessage: 'User ID is required' };
  }
  
  // Check for valid characters (common for user IDs)
  if (!/^[a-zA-Z0-9._-]+$/.test(userId)) {
    return { 
      isValid: false, 
      errorMessage: 'User ID can only contain letters, numbers, dots, underscores, and hyphens' 
    };
  }
  
  return { isValid: true };
};

// Validate PIN code
export const isValidPin = (pin: string): { isValid: boolean; errorMessage?: string } => {
  // Check if field is empty
  if (!pin || pin.trim() === '') {
    return { isValid: false, errorMessage: 'PIN is required' };
  }
  
  // Check if PIN is all digits
  if (!/^\d+$/.test(pin)) {
    return {
      isValid: false,
      errorMessage: 'PIN must contain only numbers'
    };
  }
  
  return { isValid: true };
};

// Check if a field is empty - utility function for validation
export const isEmptyField = (value: string): boolean => {
  return !value || value.trim() === '';
};

// Validate Jellyfin config
export const validateJellyfinConfig = (
  config: Record<string, string>
): { isValid: boolean; errors: Record<string, string> } => {
  const errors: Record<string, string> = {};
  
  // Validate URL
  const urlValidation = isValidUrl(config.url);
  if (!urlValidation.isValid) {
    errors.url = urlValidation.errorMessage || 'Invalid URL';
  }
  
  // Validate API key - Jellyfin API keys are typically 32+ characters
  const apiKeyValidation = isValidApiKey(config.apiKey, 16);
  if (!apiKeyValidation.isValid) {
    errors.apiKey = apiKeyValidation.errorMessage || 'Invalid API key';
  }
  
  // Validate User ID
  const userIdValidation = isValidUserId(config.userId);
  if (!userIdValidation.isValid) {
    errors.userId = userIdValidation.errorMessage || 'Invalid User ID';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// Validate OMDB config
export const validateOmdbConfig = (
  config: Record<string, string>
): { isValid: boolean; errors: Record<string, string> } => {
  const errors: Record<string, string> = {};
  
  // Validate API key - OMDB uses 8-character alphanumeric API keys
  const apiKeyValidation = isValidApiKey(config.apiKey, 8);
  if (!apiKeyValidation.isValid) {
    errors.apiKey = apiKeyValidation.errorMessage || 'Invalid API key';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// Validate TMDB config
export const validateTmdbConfig = (
  config: Record<string, string>
): { isValid: boolean; errors: Record<string, string> } => {
  const errors: Record<string, string> = {};
  
  // Validate API key - TMDB API keys are typically longer
  const apiKeyValidation = isValidApiKey(config.apiKey, 32);
  if (!apiKeyValidation.isValid) {
    errors.apiKey = apiKeyValidation.errorMessage || 'Invalid API key';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// Validate TVDB config
export const validateTvdbConfig = (
  config: Record<string, string>
): { isValid: boolean; errors: Record<string, string> } => {
  const errors: Record<string, string> = {};
  
  // Validate API key - TVDB API keys are typically JWT-like tokens
  const apiKeyValidation = isValidApiKey(config.apiKey, 16);
  if (!apiKeyValidation.isValid) {
    errors.apiKey = apiKeyValidation.errorMessage || 'Invalid API key';
  }
  
  // Validate PIN
  const pinValidation = isValidPin(config.pin);
  if (!pinValidation.isValid) {
    errors.pin = pinValidation.errorMessage || 'Invalid PIN';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// Map service IDs to their validation functions
export const validationFunctions: Record<
  string,
  (config: Record<string, string>) => { isValid: boolean; errors: Record<string, string> }
> = {
  jellyfin: validateJellyfinConfig,
  omdb: validateOmdbConfig,
  tmdb: validateTmdbConfig,
  tvdb: validateTvdbConfig,
};
