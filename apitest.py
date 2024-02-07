from browser_actions import BrowserActions
import sys

def main():
    browser_actions = BrowserActions()

    while True:
        print("Choose an action:")
        print("0 - Exit")
        print("1 - Take a screenshot")
        print("2 - Open a chat")
        print("3 - Reply to a chat")

        
        choice = input("Enter your choice (0-3): ")

        if choice == "0":
            print("Exiting...")
            sys.exit(0)
        elif choice == "1":
            browser_actions.take_screenshot("screen.png")
        elif choice == "2":
            chat_num = input("Enter chat number (0-9): ")
            browser_actions.open_chat(chat_num)
        elif choice == "3":
            message = input("Enter your message: ")
            browser_actions.reply_to_chat(message)
        else:
            print("Invalid choice. Please enter a number between 0 and 3.")

if __name__ == "__main__": 
    main()
