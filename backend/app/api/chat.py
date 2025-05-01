"""
Chat API Router

This module handles the chat endpoint for the STEMnity AI tutor.
It processes incoming messages through:
1. Input validation
2. Content moderation
3. LangGraph agent processing
4. Error handling and response formatting
"""

from fastapi import APIRouter, HTTPException, status, Body
from app.models.chat_models import ChatMessage, ChatResponse
from app.utils.moderation import is_content_safe, MODERATION_REJECTION_MESSAGE
from app.agent.tutor_agent import run_agent

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def handle_chat(request_body: ChatMessage):
    """
    Process a chat message and return the AI tutor's response.

    Args:
        request_body (ChatMessage): Contains the user's message and optional session ID

    Returns:
        ChatResponse: The AI tutor's response and reasoning process

    Raises:
        HTTPException: For empty messages, moderation failures, or processing errors
    """
    user_message = request_body.message
    session_id = request_body.session_id

    # Log incoming request for debugging
    print(f"Processing message for session '{session_id}': {user_message[:100]}...")

    # --- 1. Input Validation ---
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )

    # --- 2. Content Moderation ---
    if not is_content_safe(user_message):
        print(f"Moderation failed for session '{session_id}' - Inappropriate content detected")
        return ChatResponse(
            answer=MODERATION_REJECTION_MESSAGE,
            thoughts="Message rejected by content moderation"
        )
    print(f"Moderation passed for session '{session_id}'")

    # --- 3. Session Management ---
    if not session_id:
        print(f"Warning: No session_id provided - Memory persistence disabled")
        # Agent will handle None session_id with default memory

    # --- 4. Agent Processing ---
    try:
        # Process message through LangGraph agent
        agent_reply = await run_agent(user_message, session_id)
        
        # Log successful response
        print(f"Generated response for session '{session_id}': {agent_reply.get('answer', '')[:100]}...")
        
        return ChatResponse(
            answer=agent_reply.get('answer', ''),
            thoughts=agent_reply.get('thoughts', '')
        )

    except HTTPException as http_exc:
        # Re-raise API-specific exceptions with details
        print(f"HTTP error in chat handler: {http_exc.detail}")
        raise http_exc
        
    except Exception as e:
        # Log unexpected errors and return safe error message
        import traceback
        print(f"Unexpected error processing message:")
        print(f"Session: {session_id}")
        print(f"Error: {str(e)}")
        print(f"Trace:\n{traceback.format_exc()}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request."
        )