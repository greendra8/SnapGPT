## SMSGPT

This project takes incoming SMS messages and uses GPT-4V to generate a series of function calls to perform the action. The main actions we will perform are reading and writing snapchat messages via the snapchat web interface. It then sends the requested information back to the user.

In the initial setup, we will ignore the SMS part and instead interact with the project through the command line.

We will need to implement functions to open a selenium instance, take screenshots, overlay coordinates, and to click on the screen. GPT-4V will handle reading the messages via its vision API. 
