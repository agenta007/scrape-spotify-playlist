#!/bin/bash
curl --request GET \
  --url "https://api.spotify.com/v1/playlists/$4/tracks?offset=$1&limit=100" \
  --header "Authorization: Bearer $2" > $3 
