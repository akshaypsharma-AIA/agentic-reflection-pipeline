import os
import json
import time
import matplotlib.pyplot as plt
from IPython import display
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# 1. API Client Initialization (Secure Environment Variable Configuration)
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "CRITICAL ERROR: GEMINI_API_KEY is not set in your environment variables. "
        "Please run 'export GEMINI_API_KEY=\"your_key\"' in your terminal before running this script."
    )

# Initialize the official Google GenAI Client
client = genai.Client(api_key=GEMINI_API_KEY)

# Use the free-tier friendly model
MODEL_NAME = 'gemini-2.5-flash'


# ---------------------------------------------------------------------------
# 2. Strategic Rulesets and Evaluation Metrics
# ---------------------------------------------------------------------------
UM_USER_GOAL = """
Translate this clinical denial note into a letter to the member:
'Prior authorization for Humira 40mg injection is denied. Patient has moderate-to-severe plaque psoriasis but documentation fails to confirm trial and failure of Tier 1 alternatives: methotrexate or adalimumab biosimilars. Letter must notify member of appeal rights within 60 days.'
"""

UM_RUBRIC = """
Score the member letter from 1 to 5 on these three critical dimensions (Max 15):
1. Readability (Is the text free of clinical jargon? Is it written at an accessible 6th-8th grade reading level?)
2. Empathy (Does it sound supportive and human, acknowledging that health news can be stressful?)
3. Compliance (Does it clearly and explicitly instruct the member that they have exactly 60 days to file an appeal?)

Determine if further adjustment is necessary. If the total score >= 14, or if further changes 
would be trivial, set "continue_optimization" to false.

Output your evaluation strictly as a JSON object matching this schema:
{"readability": int, "empathy": int, "compliance": int, "total": int, "continue_optimization": bool}
"""


# ---------------------------------------------------------------------------
# 3. Observability Component (Real-Time Visualization Engine)
# ---------------------------------------------------------------------------
def stream_improvement_graph(iterations, scores):
    """Clears the previous plot and draws an updated line graph in real-time."""
    display.clear_output(wait=True)
    plt.figure(figsize=(8, 4.5))
    
    # Plot the optimization trajectory
    plt.plot(iterations, scores, marker='o', color='#008080', linewidth=2.5, markersize=8)
    
    # Chart Styling
    plt.title('Real-Time Agentic Optimization (Gemini Pipeline)', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Successful Optimization Rounds', fontsize=10, labelpad=10)
    plt.ylabel('Evaluator Metric Score (Max 15)', fontsize=10, labelpad=10)
    plt.xlim(-0.5, max(5, len(iterations)))
    plt.ylim(5, 16)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Add data point labels above the graph markers
    for i, score in enumerate(scores):
        plt.annotate(f'{score}/15', (iterations[i], scores[i]), textcoords="offset points", 
                     xytext=(0,10), ha='center', fontweight='bold', color='#2c3e50')
    
    plt.show()


# ---------------------------------------------------------------------------
# 4. Core LLM Multi-Agent Network Functions
# ---------------------------------------------------------------------------
def generate_initial_draft(goal):
    """The Generator Agent: Constructs the base draft candidate."""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=f"Goal: {goal}\nWrite an initial draft letter to the health plan member."
    )
    return response.text

def evaluate_draft(draft, rubric):
    """The Inspector Agent: Executes strict evaluation and enforces schema compliance."""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            f"You are a healthcare compliance auditor and communication expert. {rubric}",
            f"Evaluate this member notification text:\n\n{draft}"
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    return json.loads(response.text)

def refine_draft(original_draft, feedback, goal):
    """The Optimization Agent: Incorporates granular metrics to rebuild the text."""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=f"Goal: {goal}\nOriginal Version: {original_draft}\nFeedback to fix: {feedback}\nRewrite the letter to improve it based on feedback."
    )
    return response.text


# ---------------------------------------------------------------------------
# 5. Core Orchestration State Machine
# ---------------------------------------------------------------------------
def run_visual_optimization_pipeline(goal, max_attempts=5):
    """Orchestrates the reflection state loop and controls algorithmic halting."""
    attempts = 0
    
    # Run structural baseline generation
    current_draft = generate_initial_draft(goal)
    current_eval = evaluate_draft(current_draft, UM_RUBRIC)
    
    # Setup historical arrays for observability plotting
    graph_iterations = [0]
    graph_scores = [current_eval["total"]]
    
    # Render the initial system canvas
    stream_improvement_graph(graph_iterations, graph_scores)
    print(f" Baseline score calculated: {current_eval['total']}/15")
    time.sleep(1) 

    # Begin State Optimization Loop
    while attempts < max_attempts and current_eval["continue_optimization"]:
        attempts += 1
        
        feedback_str = f"Current Metrics: {current_eval}. Please optimize the draft."
        proposed_draft = refine_draft(current_draft, feedback_str, goal)
        proposed_eval = evaluate_draft(proposed_draft, UM_RUBRIC)
        
        # Calculate mathematical utility delta
        gain = proposed_eval["total"] - current_eval["total"]
        
        # Programmatic Guardrail: Only accept positive improvements
        if gain > 0:
            current_draft = proposed_draft
            current_eval = proposed_eval
            
            # Record state advancement metrics and draw new canvas frame
            graph_iterations.append(len(graph_iterations))
            graph_scores.append(current_eval["total"])
            stream_improvement_graph(graph_iterations, graph_scores)
            print(f" Round {attempts}: Optimization accepted! Score rose by +{gain}.")
            time.sleep(1.5) 
        else:
            print(f" Round {attempts}: Alternate variant rejected (No metric gain).")
            
        # Break execution block early if model determines convergence
        if not current_eval["continue_optimization"]:
            print("\n Final optimization goals achieved. Pipeline completed.")
            break
            
    return current_draft


# ---------------------------------------------------------------------------
# 6. Main Script Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Initializing Agentic Optimization Pipeline...")
    final_letter = run_visual_optimization_pipeline(UM_USER_GOAL)
    
    print("\n" + "="*50)
    print("🏆 FINAL CONSUMER-OPTIMIZED MEMBER LETTER")
    print("="*50)
    print(final_letter)
