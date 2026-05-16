import sys
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_agent
from agent_tools import all_tools

def main():
    print("Initializing OpenClaw Clone Agent with PC Tools...")
    
    # Initialize the ChatOllama model
    try:
        model = ChatOllama(model="qwen2.5:7b")
    except Exception as e:
        print(f"Error initializing model: {e}")
        print("Make sure Ollama is running and the model is pulled.")
        sys.exit(1)

    system_prompt = '''You are OpenClaw, an intelligent desktop assistant running on a Windows PC.

Your job is to help the user perform tasks on their computer using the available tools.

IMPORTANT RULES:

1. If the user asks for ANY real-world action on the computer, you MUST use the appropriate tool.
   Examples of actions:
   - creating folders
   - renaming files
   - searching files
   - opening applications
   - opening websites
   - getting system information
   - interacting with the operating system

2. NEVER pretend to perform an action. Always call a tool when an action is required.

3. If the request is informational (for example: "what is Python?" or "explain AI"),
   respond normally without using tools.

4. Use the BEST matching tool for the task.

5. After a tool executes, explain the result to the user clearly and briefly.

6. If the user's request is unclear, ask a short clarification question before using a tool.

7. Do not make up tool names. Only use tools that exist.

8. Be concise, helpful, and behave like a professional desktop assistant.

Examples:

User: Create a folder called projects on desktop
→ Use the create_folder tool

User: Open YouTube
→ Use the open_browser tool

User: What time is it?
→ Use the system time tool

User: Explain machine learning
→ Respond normally without tools'''

    # Create the modern LangChain agent graph
    agent = create_agent(
        model=model,
        tools=all_tools,
        system_prompt=system_prompt,
        debug=False # Disabled for clean chat interface
    )

    print("\nChatbot started! Type 'quit' or 'exit' to end the conversation.\n")
    
    messages = []
    
    import threading
    import time
    
    def animate_processing(stop_event):
        states = ["Thinking...", "Analyzing...", "Processing..."]
        idx = 0
        while not stop_event.is_set():
            sys.stdout.write('\r' + states[idx] + ' ')
            sys.stdout.flush()
            idx = (idx + 1) % len(states)
            time.sleep(0.5)
        sys.stdout.write('\r' + ' ' * 20 + '\r') # Clear the line when done
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Bot: Goodbye!")
                break
                
            # Append human message to history
            messages.append(HumanMessage(content=user_input))
            
            # Start the animation
            stop_event = threading.Event()
            anim_thread = threading.Thread(target=animate_processing, args=(stop_event,))
            anim_thread.start()
            
            try:
                # Invoke the LangGraph agent
                response_state = agent.invoke({"messages": messages})
            finally:
                # Stop the animation cleanly regardless of success or error
                stop_event.set()
                anim_thread.join()
            
            # The agent updates the history and returns the full list of messages
            # We fetch the new messages and print the last AI message
            messages = response_state["messages"]
            result_text = messages[-1].content
            
            print(f"Bot: {result_text}")
            
        except KeyboardInterrupt:
            print("\nBot: Goodbye!")
            break
        except Exception as e:
            print(f"\nError processing response: {e}")

if __name__ == "__main__":
    main()
