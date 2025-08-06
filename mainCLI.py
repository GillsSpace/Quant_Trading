#Project Imports
from utility.lib_apiManagment import create_client

#Python Imports
import os
import sys
import schwabdev as sd
import numpy as np
import pandas as pd

def main():
    option = ""
    print("Welcome to the Quant Trading CLI by Wills Erda!")
    print("Type 'exit' or 'e' to exit the program.")
    print("Type 'help' or 'h' for help.")

    while option.lower() not in ["exit", "quit","e"]:
        option = input("Please enter a command: ").strip()
        
        if option.lower() in ["help", "h"]:
            print("Available commands:")
            print("   - 'gen-keys': Generate API keys for Schwab via Schwabdev script.")
        elif option.lower() == "gen-keys":
            client = create_client()
            client.tokens.update_tokens(True,True)

        elif option.lower() in ["exit", "quit", "e"]:
            print("Exiting the program. Goodbye!")
        else:
            print(f"Unknown command: {option}. Type 'help' for available commands.")

if __name__ == "__main__":
    main()
    sys.exit(0)
