#!/bin/bash

# Infinite loop to generate a random string every second
while true; do
    # Generate a random string of 16 characters (adjust as needed)
    RANDOM_STRING=$(head /dev/urandom | tr -dc A-Za-z0-9)
    
    # Print the random string
    echo "$RANDOM_STRING"
    
    # Wait for 1 second
    sleep 1
done

