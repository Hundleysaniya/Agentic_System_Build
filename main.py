import os
import uuid
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from src.graph import app

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Main function to run the agentic system.
    """
    # Ensure all required environment variables are set
    required_vars = ["TAVILY_API_KEY", "GOOGLE_API_KEY"]
    for var in required_vars:
        if not os.getenv(var):
            print(f"Error: Environment variable {var} not set.")
            print("Please create a .env file and add the required keys.")
            return

    # Define a unique conversation ID for the session
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    # --- Start the conversation ---
    topic = "The future of AI in business operations"
    initial_message = HumanMessage(content=f"Please research the following topic: {topic}")

    print(f"Starting research on topic: '{topic}'")
    print("---")

    # Stream the events from the graph
    for event in app.stream({"messages": [initial_message]}, config, stream_mode="values"):
        # The stream will stop when it hits the interrupt
        # We can inspect the state and decide whether to continue
        if "messages" in event:
            event["messages"][-1].pretty_print()
        print("---")

    # --- Handle the Human-in-the-Loop (HITL) approval ---
    print("\n---[HUMAN REVIEW REQUIRED]---")
    print("The process is paused for 'HAZE' to review the research.")

    # You can inspect the current state of the graph here
    # current_state = app.get_state(config)
    # print("Current state:", current_state)

    user_input = input("Type 'approve' to continue or 'reject' to stop: ").strip().lower()

    if user_input == "approve":
        print("---[Approval Received]---")
        # To resume, we just stream with a blank input
        # The supervisor will see the last message was from the review node
        # and route to the end.
        for event in app.stream(None, config, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()
            print("---")
        print("\nWorkflow finished successfully.")
    else:
        print("---[Process Rejected]---")
        print("\nWorkflow stopped by user.")

if __name__ == "__main__":
    main()