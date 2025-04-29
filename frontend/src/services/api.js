// Use environment variable for base URL if set, otherwise default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const sendMessageToBackend = async (message, threadId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
         message: message, 
        session_id: threadId,
       }), // Match ChatMessage model
    });

    if (!response.ok) {
      // Try to parse error detail from backend
      let errorDetail = `HTTP error! status: ${response.status}`;
      try {
          const errorData = await response.json();
          errorDetail = errorData.detail || errorDetail; // Use detail if available
      } catch (e) {
          // Ignore if response is not JSON or empty
      }
      console.error("Backend error response:", errorDetail);
      throw new Error(errorDetail); // Throw error with detail
    }

    const data = await response.json(); // Now contains { answer, thoughts }
    return data; // Return the whole object

  } catch (error) {
    console.error('Error sending message to backend:', error);
    // Re-throw the error so the component can handle it
    throw error;
  }
};