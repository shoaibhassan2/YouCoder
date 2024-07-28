# YouCoder

**YouCoder** is a powerful Python program designed to extract detailed information from YouTube videos, such as author name, description, and more. It also provides the capability to retrieve muxed, audio-only, and video-only formats of YouTube videos.

## Features

- Extract video details:
  - Author name
  - Channel Id
  - Description
  - Video title
  - Publish date
  - View count
  - Video Duration
  - Keywords
  - Thumbnails urls
- Retrieve video formats:
  - Muxed (combined audio and video)
  - Audio-only
  - Video-only

## Installation 
-Directly download and use it directly.

## Usage
```python
from YouCoder import YouTube
import json
# Main function to demonstrate functionality
def main(): # ciphered url https://youtu.be/sZtp-2R4hRo
            # simple url https://youtu.be/5Ga1IXE-hLs
    youtube = YouTube('https://youtu.be/5Ga1IXE-hLs')\

    youtube.parse_player_response()
    if youtube.jsondata:
        print(json.dumps(youtube.jsondata, indent=4))
    else:
        print(f'{EXT_BLUE}[!] : {RED}could not extract data{RESET}')
    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f'{EXT_BLUE}[!] : {RED}Interrupted by user{RESET}')
```
