// Stability Test Utility - Check for potential issues
export const stabilityTest = {
  // Test API responses
  validateApiResponse: (data: any, expectedKeys: string[]): boolean => {
    if (!data || typeof data !== 'object') {
      console.warn('Invalid API response: data is not an object')
      return false
    }

    for (const key of expectedKeys) {
      if (!(key in data)) {
        console.warn(`Invalid API response: missing key '${key}'`)
        return false
      }
    }

    return true
  },

  // Test array safety
  validateArray: (arr: any, itemValidator?: (item: any) => boolean): boolean => {
    if (!Array.isArray(arr)) {
      console.warn('Expected array but got:', typeof arr)
      return false
    }

    if (itemValidator) {
      for (let i = 0; i < arr.length; i++) {
        if (!itemValidator(arr[i])) {
          console.warn(`Invalid array item at index ${i}:`, arr[i])
          return false
        }
      }
    }

    return true
  },

  // Test object safety
  validateObject: (obj: any, requiredKeys: string[] = []): boolean => {
    if (!obj || typeof obj !== 'object') {
      console.warn('Invalid object:', obj)
      return false
    }

    for (const key of requiredKeys) {
      if (!(key in obj)) {
        console.warn(`Missing required object key: ${key}`)
        return false
      }
    }

    return true
  },

  // Test string safety
  validateString: (str: any, minLength: number = 0): boolean => {
    if (typeof str !== 'string') {
      console.warn('Expected string but got:', typeof str)
      return false
    }

    if (str.length < minLength) {
      console.warn(`String too short: ${str.length} < ${minLength}`)
      return false
    }

    return true
  }
} 