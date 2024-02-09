This project utilizes GPT-4V to generate function calls for reading and writing Snapchat messages via Selenium and the Snapchat web interface.
Setup
1. Install the required dependencies by running pip install -r requirements.txt.
2. Set up the necessary environment variables by creating a .env file and adding your OpenAI API and Twilio credentials.
3. Use service like ngrok to expose the server to the internet. (ngrok http 5000)
4. Set up a Twilio phone number and configure it to send incoming SMS messages to the server.
5. Change path in browser_actions.py to the path of your chrome profile. Make sure this profile is logged into Snapchat.
Usage
1. Start the Flask server by running python main.py.
2. Send SMS messages to the server to trigger the GPT-4V assistant.
3. The assistant will analyze the user query and image analysis of their device to determine the next step.
4. The assistant will generate function calls based on the analysis and respond with the recommended action.
Code Structure
- main.py: Contains the Flask server implementation and the main logic for processing SMS messages and interacting with the GPT-4V assistant.
- browser_actions.py: Provides functions for interacting with the Snapchat web interface using Selenium.
- overlay.py: Handles overlaying coordinates on screenshots.
- decision_prompt.txt: Contains instructions for the assistant on how to choose the correct function to call based on user descriptions.
- vision_prompt.txt: Provides guidance for the assistant on how to summarize chat messages and extract useful information.