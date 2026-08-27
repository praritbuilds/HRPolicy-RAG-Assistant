from api_llm_gemini import *

print("Hi, How can I help you?")
while True:
    choice = input("Press 1 to ask question, 2 to exit: ")
    if choice == "2":
        break
    elif choice == "1":
        query = input("Enter your query: ")
        print("\n\n")
        print(execute_query(query))
        print("\n\n")
    else:
        choice = input("Invalid choice")

