from fastapi import APIRouter, HTTPException, status, Body
from app.models.chat_models import ChatMessage, ChatResponse
from app.utils.moderation import is_content_safe, MODERATION_REJECTION_MESSAGE
from app.agent.tutor_agent import run_agent

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def handle_chat(request_body: ChatMessage): # Use the new request body model
    """
    Receives a user message and session ID, performs moderation,
    processes it using the LangChain agent with memory context,
    and returns the final reply.
    """
    user_message = request_body.message
    session_id = request_body.session_id

    print(f"Received message for session '{session_id}': {user_message[:100]}...") # Log session ID

    # --- 1. Input Validation ---
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )

    # --- 2. Moderation Check ---
    # Use is_content_safe (or your function name like is_content_appropriate)
    if not is_content_safe(user_message):
        print(f"Moderation failed for session '{session_id}'.")
        # Return the standard rejection message without calling the agent
        # Ensure MODERATION_REJECTION_MESSAGE is defined in your moderation utils
        return ChatResponse(reply=MODERATION_REJECTION_MESSAGE)
    print(f"Moderation passed for session '{session_id}'.")

    # --- 3. Session ID Handling (Optional but Recommended) ---
    if not session_id:
        
        print(f"Warning: No session_id provided for message: {user_message[:50]}... Memory will not persist across requests.")
        # Let run_agent handle None session_id if it's designed to

    # --- 4. Call the Agent ---
    try:
        # Pass both message and session_id to the agent runner
        agent_reply = await run_agent(user_message, session_id) # Pass session_id
        print(f"Sending agent reply for session '{session_id}': {agent_reply.get('answer', '')[:100]}...")
        return ChatResponse(answer=agent_reply.get('answer', ''), thoughts=agent_reply.get('thoughts', ''))

    # --- 5. Error Handling ---
    except HTTPException as http_exc:
        # Re-raise specific HTTPExceptions if needed (e.g., from deeper layers)
        print(f"HTTPException caught in /chat for session '{session_id}': {http_exc.detail}")
        raise http_exc
    except Exception as e:
        # Catch any other unexpected errors during agent processing
        # Log the full error for debugging
        import traceback
        print(f"Unexpected error in /chat endpoint for session '{session_id}': {e}\n{traceback.format_exc()}")
        # Return a generic server error to the client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred while processing your request."
            # Avoid sending detailed internal errors like the exception 'e' back to the client
        )