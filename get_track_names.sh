#!/bin/bash

# Specify the text file containing the URLs
input_file="tracklistlinks.txt"

# Check if the file exists
if [ ! -f "$input_file" ]; then
  echo "Input file not found: $input_file"
  exit 1
fi

# Iterate through each line in the file
while IFS= read -r line; do
  # Use curl to make a request for each URL
  echo $line
  curl --request GET --url https://api.spotify.com/v1/tracks/$line --header 'Authorization: Bearer BQBskB3MaYKVaxdnHXOgsGtj5vIU9bwgyLMvR9PxGBE5wWgIDSOweeNUKBhAWGUr5ZnMFs0xzlYquXGGEm7ZGF2Y1dwtN_MxidVCnV7rghJQNcj7MOM' >> responses.json
done < "$input_file"

