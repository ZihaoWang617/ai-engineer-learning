import reviewer
import os

def get_multiline_input():
    print("Enter your code (type 'END' on a new line to stop):")
    lines = []
    while True:
        line = input()
        if line.lower() == 'q':
            return 'q'
        elif line.lower() == 'end':
            break
        lines.append(line)
    return "\n".join(lines)

def pick_model():
    while True:
        print("\nPlease pick a model:")
        print("1. OpenAI (gpt-4o-mini)")
        print("2. Anthropic (claude-sonnet-4-20250514)")
        choice = input("Enter 1 or 2: ").strip()
        if choice == '1':
            return 'openai'
        elif choice == '2':
            return 'anthropic'
        else:
            print("Invalid choice. Please enter 1 or 2.")

def main():
    print("Welcome to the Code Reviewer!")
    while True:
        user_input = input("Enter a file path or enter code directly (type 'q' to quit): ").strip()
        if not user_input:
            print("Empty input. Please try again.")
            continue
        elif user_input.lower() == 'q':
            print("Exiting the program.")
            break
        is_filepath = False
        if os.path.isfile(user_input):
            print(f"\nReviewing code from file: {user_input}")
            review_target = user_input
            is_filepath = True
        else:
            if input("Invalid file path. Do you want to enter code directly? (y/n): ").lower() == 'y':
                review_target = get_multiline_input()
                if review_target == 'q':
                    print("Exiting the program.")
                    break
                if not review_target.strip():
                    print("No code entered. Please try again.")
                    continue
            else:
                continue
        model_choice = pick_model()
        if model_choice == 'openai':
            reviewer.review_with_openai(review_target, is_filepath=is_filepath)
        else:            
            reviewer.review_with_anthropic(review_target, is_filepath=is_filepath)

if __name__ == "__main__":
    main()
        
