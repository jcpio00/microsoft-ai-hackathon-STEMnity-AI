import uuid
from typing import Any, List, Tuple, Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages # Use for messages state management
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import Tool
from langchain.agents.format_scratchpad import format_log_to_str # Helper for ReAct scratchpad
from langchain.agents.output_parsers import ReActSingleInputOutputParser # Parser for ReAct output
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate # Use base PromptTemplate for ReAct string
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    SystemMessage as LangChainSystemMessage,
    HumanMessage as LangChainHumanMessage,
    AIMessage as LangChainAIMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnablePassthrough # Useful for LCEL chains
from langchain_core.agents import AgentAction, AgentFinish # Represent agent decisions
from azure.ai.inference.models import (
    SystemMessage as AzureSystemMessage,
    UserMessage as AzureUserMessage,
    AssistantMessage as AzureAssistantMessage,
)
from app.tools import math_solver, science_toolkit
from app.core import config
from app.services.llm_service import client as azure_client
import re

# --- Custom LangChain Chat Model Wrapper ---
class GitHubModelsChatWrapper(BaseChatModel):
    client: Any
    model_id: str

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        # Convert LangChain messages to Azure SDK format
        azure_messages = []
        for msg in messages:
            if isinstance(msg, LangChainSystemMessage):
                azure_messages.append(AzureSystemMessage(content=msg.content))
            elif isinstance(msg, LangChainHumanMessage):
                azure_messages.append(AzureUserMessage(content=msg.content))
            elif isinstance(msg, LangChainAIMessage):
                 azure_messages.append(AzureAssistantMessage(content=msg.content))
            # Note: ToolMessage might need handling if tools provide structured output later
            else:
                 print(f"Warning: Skipping unknown message type: {type(msg)}")

        # Define allowed parameters for the SDK
        allowed_params = {
            "temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty"
        }
        sdk_kwargs = {}
        # --- IMPORTANT: Add ReAct Stop Sequence ---
        # The LLM needs to stop generating before hallucinating an Observation
        react_stop_sequence = "\nObservation:"
        if stop:
            # Combine existing stop sequences with the ReAct one
            if isinstance(stop, list):
                if react_stop_sequence not in stop:
                    stop.append(react_stop_sequence)
                sdk_kwargs["stop"] = stop
            elif isinstance(stop, str) and stop != react_stop_sequence:
                 sdk_kwargs["stop"] = [stop, react_stop_sequence]
            else:
                 sdk_kwargs["stop"] = [react_stop_sequence]
        else:
            sdk_kwargs["stop"] = [react_stop_sequence]


        for key, value in kwargs.items():
            if key in allowed_params:
                sdk_kwargs[key] = value

        print(f"--- Azure Messages being sent (ReAct): ---")
        for i, msg in enumerate(azure_messages):
             print(f"[{i}] Type: {type(msg).__name__}, Content: '{getattr(msg, 'content', 'N/A')[:70]}...'")
        print(f"--- SDK Kwargs being sent (ReAct): {sdk_kwargs} ---")

        try:
            response = self.client.complete(
                model=self.model_id,
                messages=azure_messages,
                **sdk_kwargs
            )
            print(f"--- Raw SDK Response Received: ---")
            print(response)
            print(f"---------------------------------")

            choices = response.get('choices') if isinstance(response, dict) else getattr(response, 'choices', None)
            if choices and len(choices) > 0:
                 message_data = choices[0].get('message') if isinstance(choices[0], dict) else getattr(choices[0], 'message', None)
                 content = message_data.get('content') if isinstance(message_data, dict) else getattr(message_data, 'content', None)
                 if content is not None:
                     print(f"Extracted content: {content[:100]}...")
                     # Return LangChain AIMessage wrapped in ChatResult
                     return ChatResult(generations=[ChatGeneration(message=LangChainAIMessage(content=content))])
                 else:
                     print("Warning: Could not extract content from response message.")
                     return ChatResult(generations=[ChatGeneration(message=LangChainAIMessage(content="[Model response format issue - no content]"))])
            else:
                print("Warning: Model response contained no choices or invalid format.")
                return ChatResult(generations=[ChatGeneration(message=LangChainAIMessage(content="[Model returned no response choices]"))])
        except Exception as e:
            print(f"Error in GitHubModelsChatWrapper during sync client.complete: {e}")
            raise

    @property
    def _llm_type(self) -> str:
        return "github_models_chat_wrapper"

# --- Initialize the Chat Model Wrapper ---
if not azure_client:
    raise RuntimeError("Azure client not initialized in llm_service. Cannot proceed.")
llm = GitHubModelsChatWrapper(client=azure_client, model_id=config.GITHUB_MODEL_ID)

# --- Define Tools (Keep as is) ---
tools = [
    Tool(
        name="AlgebraEquationSolver",
        func=math_solver.solve_algebraic_equation,
        description="Useful for solving algebraic equations for a single variable (usually 'x'). Input should be a string representing the equation, like '2*x + 5 = 15' or 'x**2 - 4 = 0'."
    ),
    Tool(
        name="ExpressionFactorizer",
        func=math_solver.factor_expression,
        description="Useful for factoring mathematical expressions. Input should be a string like 'x**2 - 9' or 'a*b + a*c'."
    ),
    Tool(
        name="UnitConverter",
        func=science_toolkit.convert_units,
        description="Useful for converting values between different physical units. Input should be a single string describing the conversion, like '10 meters to feet', '5 kg, pounds', or '25 miles/hour to km/h'."
    ),
    Tool(
        name="PhysicalConstantLookup",
        func=science_toolkit.get_physical_constant,
        description="Useful for finding the value and unit of a known physical constant. Input should be the name of the constant (e.g., 'speed of light in vacuum', 'electron mass')."
    ),
]
tool_map = {tool.name: tool for tool in tools} # Create a map for easy lookup

# --- Define ReAct Prompt Template ---

tool_descriptions = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
react_prompt_string = f"""
Answer the following questions as best you can, acting as a helpful and patient STEM tutor for K-12 students.
Explain your reasoning step-by-step.
When you decide to use a tool, clearly state which tool you are using and what input you are giving it.
After receiving the result from a tool (the Observation), explain what that result means in the context of the problem before continuing.
Format mathematical equations clearly using LaTeX delimiters ($ for inline, $$ for block).
You have access to the following tools:

{tool_descriptions}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do, explaining your reasoning for the student.
Action: the action to take, should be one of [{', '.join([tool.name for tool in tools])}]
Action Input: the input to the action
Observation: the result of the action
Thought: Now I need to explain the observation to the student and decide the next step.
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I have explained all the steps and reached the final answer.
Final Answer: the final answer to the original input question, presented clearly.

Begin!

Previous conversation history:
{{chat_history}}

Question: {{input}}
{{agent_scratchpad}}
"""


# Use PromptTemplate for string-based prompts
prompt = PromptTemplate.from_template(react_prompt_string)

# --- Build ReAct Agent Logic using LCEL ---
# Bind the LLM with the necessary stop sequence for ReAct
llm_with_stop = llm.bind(stop=["\nObservation:"])

# Define the agent core chain
agent_core = (
    RunnablePassthrough.assign(
        # Format the scratchpad from intermediate steps
        agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
        # Format chat history (simple concatenation for string prompt)
        chat_history=lambda x: "\n".join([f"{type(m).__name__}: {m.content}" for m in x["chat_history"]])
    )
    | prompt
    | llm_with_stop
    | ReActSingleInputOutputParser() # Parses the LLM string output into AgentAction or AgentFinish
)

# --- LangGraph State Definition ---
class GraphState(TypedDict):
    input: str                             # The current user query
    messages: Annotated[List[BaseMessage], add_messages] # Full conversation history managed by LangGraph/MemorySaver
    intermediate_steps: List[Tuple[AgentAction, str]] # ReAct scratchpad for the *current* turn
    agent_outcome: AgentAction | AgentFinish | None

# --- LangGraph Node Functions ---

def run_agent_node(state: GraphState) -> dict:
    """Calls the LLM agent logic to decide the next step."""
    print("--- Running Agent Node ---")
    agent_inputs = {
        "input": state["input"],
        "chat_history": state["messages"], # Pass the full history from state
        "intermediate_steps": state["intermediate_steps"]
    }
    # Call the LCEL chain
    try:
        agent_outcome = agent_core.invoke(agent_inputs)
        print(f"Agent Outcome: {agent_outcome}")
        # Return the outcome to be stored in the state
        return {"agent_outcome": agent_outcome}
    except Exception as e:
        print("Output parsing failed. Raw LLM output was:")
        # If possible, print the raw output here for debugging
        # print(e.raw_output)  # Uncomment if your exception provides this
        print(f"Exception: {e}")
        return {"agent_outcome": AgentFinish(return_values={"output": "Sorry, I couldn't understand the model's response. Please try rephrasing your question."},
                                             log="Output parsing error")}

def execute_tool_node(state: GraphState) -> dict:
    """Executes the tool chosen by the agent."""
    print("--- Running Tool Executor Node ---")
    agent_action = state.get("agent_outcome") # Should be an AgentAction if we are here

    if not isinstance(agent_action, AgentAction):
        # This should not happen if routing is correct, but handle defensively
        print("Error: Tool Executor called without valid AgentAction.")
        # Maybe return an error message or raise exception
        observation = "Error: Invalid agent state for tool execution."
        # Need to return intermediate steps update
        error_action = AgentAction(tool="ErrorTool", tool_input="", log="Error state")
        return {"intermediate_steps": state["intermediate_steps"] + [(error_action, observation)]}


    tool_name = agent_action.tool
    tool_input = agent_action.tool_input
    # Sanitize tool input: remove leading/trailing quotes
    if isinstance(tool_input, str):
        tool_input = tool_input.strip().strip('"').strip("'")
    print(f"Executing Tool: {tool_name} with Input: {tool_input}")

    tool = tool_map.get(tool_name)
    if not tool:
        observation = f"Error: Tool '{tool_name}' not found."
    else:
        try:
            if tool_name == "UnitConverter":
                # Accept any of the LLM's formats and join as a single string
                if isinstance(tool_input, tuple):
                    # Join tuple elements with comma
                    input_str = ", ".join(str(x).strip("'\"") for x in tool_input)
                elif isinstance(tool_input, str):
                    input_str = tool_input.strip().strip("'\"")
                else:
                    input_str = str(tool_input)
                observation = tool.run(input_str)
            else:
                observation = tool.run(tool_input)
        except Exception as e:
            observation = f"Error executing tool {tool_name}: {e}"

    print(f"Tool Observation: {observation}")
    return {"intermediate_steps": state["intermediate_steps"] + [(agent_action, observation)]}


def finalize_node(state: GraphState) -> dict:
    """Appends the final answer to the message history if AgentFinish."""
    agent_outcome = state.get("agent_outcome")
    messages = state.get("messages", [])
    intermediate_steps = state.get("intermediate_steps", [])
    if isinstance(agent_outcome, AgentFinish):
        final_answer = agent_outcome.return_values.get("output", "Agent finished without output.")
        messages = messages + [LangChainAIMessage(content=final_answer)]
    # Return intermediate_steps for frontend
    return {"messages": messages, "intermediate_steps": intermediate_steps}

# --- LangGraph Conditional Edge (Router) ---

def should_continue_router(state: GraphState) -> str:
    """Determines whether to continue the ReAct loop or finish."""
    print("--- Running Router ---")
    agent_outcome = state.get("agent_outcome")

    if isinstance(agent_outcome, AgentAction):
        # Agent decided to use a tool
        print("Router Decision: Continue (Use Tool)")
        return "continue"
    elif isinstance(agent_outcome, AgentFinish):
        # Agent decided it has the final answer
        print("Router Decision: End")
        return "end"
    else:
        # Should not happen in theory
        print("Router Decision: End (Error/Unknown Outcome)")
        return "end"


# --- Build the LangGraph Workflow ---
workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("agent", run_agent_node)
workflow.add_node("tool_executor", execute_tool_node)
workflow.add_node("finalize", finalize_node)

# Define edges
workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent", # Starting node
    should_continue_router, # Function to decide the next path
    {
        "continue": "tool_executor", # If router returns "continue", go to tool_executor
        "end": "finalize"                # Go to finalize node before END
    }
)
workflow.add_edge("finalize", END)
workflow.add_edge("tool_executor", "agent") # Always go back to the agent after executing a tool

# --- Compile the Graph with Memory ---
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# --- Run Agent Function ---
async def run_agent(query: str, thread_id=None) -> dict:
    """Runs the ReAct agent graph with memory."""
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    print(f"\n--- Running Agent for Thread ID: {thread_id} ---")
    print(f"User Query: {query}")

    config = {"configurable": {"thread_id": thread_id}}

    # Define the initial input for this specific run
    # 'messages' will be loaded by the checkpointer
    # 'intermediate_steps' should start empty for each new user query
    graph_input = {
        "input": query,
        "intermediate_steps": []
    }

    final_state = None
    try:
        # Use invoke to run until the END state is reached
        final_state = app.invoke(graph_input, config=config)
    except Exception as e:
        print(f"Error during graph invocation for thread {thread_id}: {e}")
        return {"answer": "Sorry, an error occurred while processing your request.", "thoughts": ""}

    # Extract the final answer
    if final_state:
        agent_outcome = final_state.get("agent_outcome")
        intermediate_steps = final_state.get("intermediate_steps", [])
        if isinstance(agent_outcome, AgentFinish):
            final_answer = agent_outcome.return_values.get("output", "Agent finished without output.")
            # Format thoughts for frontend (as a string or structured list)
            thoughts = "\n".join([f"Thought: {step[0].log}\nAction: {step[0].tool}\nAction Input: {step[0].tool_input}\nObservation: {step[1]}" for step in intermediate_steps])
            return {"answer": final_answer, "thoughts": thoughts}
        else:
            # Agent ended unexpectedly 
            print("Agent ended without AgentFinish.")
            # Check the last message in history as a fallback 
            last_message = final_state.get('messages', [])[-1] if final_state.get('messages') else None
            if last_message and isinstance(last_message, LangChainAIMessage):
                return {"answer": last_message.content + " [Warning: Agent may not have finished correctly]", "thoughts": ""}
            return {"answer": "Agent finished unexpectedly.", "thoughts": ""}
    else:
        return {"answer": "Graph invocation failed to return a final state.", "thoughts": ""}

def parse_tool_args(tool_input):
    """
    Parses tool input for multi-argument tools like UnitConverter.
    Handles formats like:
      - ('5 miles', 'kilometers')
      - '5 miles', 'kilometers'
      - "5 miles", "kilometers"
      - 5 miles, kilometers
    Returns a tuple (arg1, arg2) or (None, None) if parsing fails.
    """
    if isinstance(tool_input, tuple) and len(tool_input) == 2:
        return tool_input[0], tool_input[1]
    if isinstance(tool_input, str):
        # Remove surrounding parentheses if present
        s = tool_input.strip()
        if s.startswith("(") and s.endswith(")"):
            s = s[1:-1].strip()
        # Use regex to extract quoted or unquoted arguments
        matches = re.findall(r"""(['"])(.*?)\1|([^,]+)""", s)
        args = []
        for match in matches:
            if match[1]:  # Quoted
                args.append(match[1].strip())
            elif match[2]:  # Unquoted
                args.append(match[2].strip())
        if len(args) == 2:
            return args[0], args[1]
        # Fallback: split by comma
        parts = [p.strip().strip('"').strip("'") for p in s.split(",")]
        if len(parts) == 2:
            return parts[0], parts[1]
    return None, None