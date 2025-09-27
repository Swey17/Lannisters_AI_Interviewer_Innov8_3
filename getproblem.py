import json
import random
import textwrap

# This list will hold all our problems in memory
problem_bank = []

def load_problems():
    """
    Loads problems from the JSON file into memory.
    """
    global problem_bank
    try:
        # Make sure your JSON file is named 'leetcode_problems_by_difficulty.json'
        with open('leetcode_problems_by_difficulty.json', 'r', encoding='utf-8') as f:
            problem_bank = json.load(f)
        print(f"✅ Successfully loaded {len(problem_bank)} problems into memory.")
    except FileNotFoundError:
        print("🔥 FATAL ERROR: The JSON file 'leetcode_problems_by_difficulty.json' was not found.")
    except json.JSONDecodeError:
        print("🔥 FATAL ERROR: The JSON file is invalid. Check for syntax errors.")

def get_problem(difficulty):
    """
    Selects and returns a single random problem object of the chosen difficulty.
    """
    if not problem_bank:
        return None

    # Filter the problem bank to get only problems of the selected difficulty
    filtered_problems = [p for p in problem_bank if p.get('difficulty') == difficulty]

    if not filtered_problems:
        return None

    # Choose one random problem from the filtered list and return it
    return random.choice(filtered_problems)


# --- Main Program Execution ---

if __name__ == '__main__':
    load_problems()
    
    if not problem_bank:
        # Exit if problems failed to load
        exit()

    # Loop to continuously ask the user for input
    while True:
        user_input = input("\nEnter a difficulty (Easy, Medium, Hard) or type 'quit' to exit: ")
        normalized_input = user_input.strip().title()

        if normalized_input == 'Quit':
            print("Goodbye!")
            break
        
        if normalized_input in ['Easy', 'Medium', 'Hard']:
            # Call the function to get a problem object
            problem = get_problem(normalized_input)
            
            # Check if a problem was successfully returned
            if problem:
                # --- All printing is now handled here in the main loop ---
                print("\n" + "="*80)
                print(f"Difficulty: {problem.get('difficulty')} | Tags: {', '.join(problem.get('tags', []))}")
                print(f"Problem ID: {problem.get('id')}")
                print("="*80)

                print("\n--- Problem Description ---")
                description = problem.get('problemDescription', 'No description available.')
                print(textwrap.fill(description, width=80))

                print("\n--- Starter Code ---")
                print(problem.get('starterCode', 'No starter code available.'))

                print("\n--- Test Cases ---")
                test_cases = problem.get('testCases', {})
                if isinstance(test_cases, dict) and 'inputs' in test_cases:
                    for i, (inp, outp) in enumerate(zip(test_cases.get('inputs', []), test_cases.get('outputs', []))):
                        print(f"  Test Case {i+1}:")
                        print(f"    Input:  {inp}")
                        print(f"    Output: {outp}")
                else:
                    print(json.dumps(test_cases, indent=2))
                    
                print("\n" + "="*80)
            else:
                print(f"Sorry, no problems were found for difficulty: {normalized_input}")
        else:
            print("Invalid input. Please choose 'Easy', 'Medium', 'Hard', or 'quit'.")

