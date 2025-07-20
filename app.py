"""
Main entry point for the unfold.quest Gradio web application.

This script imports the compiled LangGraph agent, creates a user-friendly
web interface with Gradio, and handles the interaction between the user and
the agent.
"""

import gradio as gr
from dotenv import load_dotenv

# We must load environment variables (like API keys) at the very start.
load_dotenv()

# Import the function that builds our compiled agent.
from src.agent.graph import get_agent_runnable

# --- 1. Agent Initialization ---

# Create the compiled LangGraph agent. This is a stateful, runnable object.
# This happens once when the application starts.
try:
    agent_runnable = get_agent_runnable()
    print("✅ Agent runnable compiled successfully.")
except Exception as e:
    print(f"🔥 Failed to compile agent runnable: {e}")
    agent_runnable = None

# --- 2. Core Application Logic ---

def run_unfold_quest(user_request: str):
    """
    This function is the primary interface between the Gradio UI and the agent.
    It takes the user's text input, invokes the agent, and streams the output.
    """
    if not agent_runnable:
        return "❌ **System Error**: The agent failed to initialize. Please check the logs and try again."

    # Validate input
    if not user_request or not user_request.strip():
        return "📝 **Please enter your quest**: Describe where you'd like to go in Riga!"

    # The initial state for the graph is a dictionary with the input key.
    initial_state = {"original_user_request": user_request.strip()}
    
    # We use `stream` instead of `invoke` to get intermediate steps, which is
    # great for showing the "thought process" in a more advanced UI later.
    # For now, we'll just process the stream to get the final state.
    print(f"\n🚀 Invoking agent for request: '{user_request}'")
    final_state = None
    try:
        # The `stream` method yields the state after each node completes.
        # We iterate through them but only care about the very last one.
        for state_update in agent_runnable.stream(initial_state):
            final_state = state_update

        # The final state contains the `final_response` we want to display.
        if final_state and "final_response" in final_state:
            print("✅ Agent invocation complete.")
            response = final_state["final_response"]
            
            # Add any error information if present
            if "errors" in final_state and final_state["errors"]:
                response += "\n\n---\n\n⚠️ **Note**: Some issues occurred during planning:\n"
                for error in final_state["errors"]:
                    response += f"- {error}\n"
            
            return response
        else:
            print("🔥 Agent did not produce a final response.")
            return "❌ **Unexpected Error**: I couldn't generate a response. Please try again with a different quest."

    except Exception as e:
        error_msg = str(e)
        print(f"🔥 An error occurred during agent invocation: {e}")
        
        # Provide user-friendly error messages
        if "API" in error_msg or "key" in error_msg.lower():
            return "🔑 **API Error**: There seems to be an issue with the AI service. Please try again in a moment."
        elif "timeout" in error_msg.lower():
            return "⏰ **Timeout Error**: The request took too long. Please try a simpler quest or try again."
        else:
            return f"❌ **Error**: Something went wrong: {error_msg}\n\nPlease try again or contact support if the issue persists."

# --- 3. Gradio Interface Definition ---

# Define the user interface using Gradio blocks for more layout control.
with gr.Blocks(
    theme=gr.themes.Soft(), 
    title="unfold.quest",
    css="""
    .container {
        max-width: 900px !important;
        margin: auto !important;
    }
    #quest-input {
        border-radius: 8px !important;
    }
    """
) as demo:
    gr.Markdown(
        """
        # 🗺️ unfold.quest
        ### Your Personal AI Adventure Architect
        
        Welcome to the prototype! Enter a journey you'd like to take in Riga, and the agent will
        transform it into a unique micro-quest.
        """,
        elem_classes=["container"]
    )
    
    with gr.Row():
        with gr.Column(scale=4):
            user_input = gr.Textbox(
                label="What is your quest?",
                placeholder="e.g., I want to go from Purvciems to Old Town, arriving around 14:00",
                lines=2,
                max_lines=4,
                elem_id="quest-input"
            )
        with gr.Column(scale=1, min_width=100):
            submit_button = gr.Button(
                "Unfold My Quest", 
                variant="primary",
                size="lg"
            )

    gr.Markdown("---")
    
    output_response = gr.Markdown(
        label="Your Adventure Plan:",
        elem_classes=["container"],
        line_breaks=True
    )

    # Define the interaction logic with better event handling
    submit_button.click(
        fn=run_unfold_quest,
        inputs=user_input,
        outputs=output_response,
        api_name="unfold_quest"  # Enable API access
    )
    
    # Allow Enter key to submit
    user_input.submit(
        fn=run_unfold_quest,
        inputs=user_input,
        outputs=output_response
    )
    
    gr.Examples(
        examples=[
            ["I want to go from Purvciems to Old Town, arriving around 14:00"],
            ["I need the quickest way from Agenskalns to Old Town"],
            ["Show me an interesting journey from Old Town to Purvciems this afternoon"],
            ["Take me from Mezaparks to Vecrīga with some cultural stops"],
            ["Quick route from Ķengarags to Agenskalns for lunch meeting"]
        ],
        inputs=user_input,
        outputs=output_response,
        fn=run_unfold_quest,
        cache_examples=True,  # Cache for faster demo experience
        label="Try these example quests:"
    )
    
    gr.Markdown(
        """
        ---
        
        ### About this Prototype
        
        🏆 **Research Project**: This is a prototype for the European Universities Competition on AI.  
        🚌 **Data Sources**: Uses static GTFS feed and curated POI dataset for Riga.  
        🤖 **AI-Powered**: Responses generated using Google's Gemini 2.5 Flash model.  
        📍 **Coverage**: Currently supports journeys within Riga, Latvia.
        
        *Built with ❤️ using LangGraph + Gradio*
        """,
        elem_classes=["container"]
    )

# --- 4. Application Launch ---

if __name__ == "__main__":
    if agent_runnable is None:
        print("❌ Could not start the application because the agent failed to initialize.")
        print("🔍 Please check your environment variables and dependencies.")
    else:
        print("🚀 Launching Gradio UI...")
        print("🌍 Agent powered by Gemini 2.5 Flash")
        print("📍 Ready to create quests in Riga!")
        
        # Launch with better configuration for development/demo
        demo.launch(
            show_api=True,  # Enable API documentation
            share=False,    # Set to True if you want a public link
            inbrowser=True, # Automatically open in browser
            favicon_path=None,  # Add favicon if available
            app_kwargs={"docs_url": "/docs", "redoc_url": "/redoc"}  # API docs endpoints
        )