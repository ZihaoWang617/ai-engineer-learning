import reviewer
import file_tools
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

def main():
    print("Welcome to the Code Reviewer!")
    while True:
        user_input = input("Enter a file path or type 'input' to enter code directly (type 'q' to quit): ")
        if user_input.lower() == 'q':
            print("Exiting the program.")
            break

        if os.path.isfile(user_input):
            code = file_tools.read_file(user_input)
            print(f"\nReviewing code from file: {user_input}")
        else:
            code = get_multiline_input()
            if code.lower() == 'q':
                print("Exiting the program.")
                break
        print("\nPlease pick a model for code review:")
        print("1. OpenAI (gpt-4o-mini)")
        print("2. Anthropic (claude-sonnet-4-20250514)")
        model_choice = input("Enter the number corresponding to your choice: ")
        if model_choice == '1':
            print("\nReviewing code with OpenAI...")
            reviewer.review_with_openai(code)
        elif model_choice == '2':
            print("\nReviewing code with Anthropic...")
            reviewer.review_with_anthropic(code)
        else:
            print("Invalid choice. Please try again.")
        
if __name__ == "__main__":
    main()
        