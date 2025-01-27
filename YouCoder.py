import re
import requests
import json
import dukpy
from urllib.parse import urlparse, parse_qs, urlencode
# Define color codes
RED = '\x1b[0;31m'
YELLOW = '\x1b[0;33m'
EXT_BLUE = '\x1b[38;5;21m'
UNDERLINE = '\x1b[4m'
RESET = '\x1b[0m'
global_cipher = None
def extract_function_definition(js_code, function_name):
    pattern = re.compile(r'%s=function\([^)]*\)\{.*?\};' % re.escape(function_name), re.DOTALL)
    match = pattern.search(js_code)
    if match:
        return match.group(0)
    return None

def match1(text, *patterns):

    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret

class DecipherSignature:
    def __init__(self,purl):
        self.player_url = purl
        self.player_url_data = self.download_player()

    def download_player(self):
        print(f'{EXT_BLUE}[+] : {YELLOW}Downloading base player : {UNDERLINE}{RESET}')
        if self.player_url:
            try:
                response = requests.get(self.player_url)
                response.raise_for_status()  # Raise an error for bad status codes
                return response.text
            except requests.RequestException as e:
                print(f'{EXT_BLUE}[!] : {RED}Error downloading player: {e}{RESET}')
                return None
        else:
            # with open("base.js","r",encoding='utf-8') as file:
            #     a = file.read()
            #     return a
            print(f'{EXT_BLUE}[!] : {RED}URL is not valid{RESET}')
            return None 
    def sigurl_to_url(self,url):
        qs = parse_qs(url)
        sp = qs['sp'][0]
        sig = self.s_to_sig( qs['s'][0])
        url = qs['url'][0] + '&{}={}'.format(sp, sig)
        url = self.dethrottle(url)
        return url
    def dethrottle(self, url):
        def n_to_n(js, n):
            f1 = match1(js, r',[$\w]+\.length\|\|([$\w]+)\(""\)\)}};')
            f1def = extract_function_definition(js, f1)
            n = dukpy.evaljs('%s\n%s("%s")' % (f1def,f1, n))
            return n

        u = urlparse(url)
        qs = parse_qs(u.query)
        n = n_to_n(self.player_url_data, qs['n'][0])
        qs['n'] = [n]
        return u._replace(query=urlencode(qs, doseq=True)).geturl()
    def s_to_sig(self, s):
        js_code = ''
        f1 = match1(self.player_url_data, r'=([$\w]+)\(decodeURIComponent\(')
        f1def = match1(self.player_url_data, r'\W%s=function(\(\w+\)\{[^\{]+\})' % re.escape(f1))
        f1def = re.sub(r'([$\w]+\.)([$\w]+\(\w+,\d+\))', r'\2', f1def)  # remove . prefix
        f1def = 'function %s%s' % (f1, f1def)
        f2s = set(re.findall(r'([$\w]+)\(\w+,\d+\)', f1def))  # find all invoked function names
        for f2 in f2s:
            f2e = re.escape(f2)
            f2def = re.search(r'[^$\w]%s:function\((\w+,\w+)\)(\{[^\{\}]+\})' % f2e, self.player_url_data)
            if f2def:
                f2def = 'function {}({}){}'.format(f2e, f2def.group(1), f2def.group(2))
            else:
                f2def = re.search(r'[^$\w]%s:function\((\w+)\)(\{[^\{\}]+\})' % f2e, self.player_url_data)
                f2def = 'function {}({},b){}'.format(f2e, f2def.group(1), f2def.group(2))
            js_code += f2def + ';'
        js_code += f1def + ';%s("%s")' % (f1, s)
        sig = dukpy.evaljs(js_code)
        return sig



# Define the YouTube class
class YouTube:
    def __init__(self, url):

        self.url = url
        self.video_id = self.get_video_id(url)

        if self.video_id:
            print(f'{EXT_BLUE}[+] : {YELLOW}video_id : {UNDERLINE}{self.video_id}{RESET}')
        else:
            print(f'{EXT_BLUE}[!] : {RED}Not a youtube URL{RESET}')
            exit(1)
        self.watch_url = self.get_watch_url(url)
        self.html = self.download_html()
        self.player_url = self.get_player_url()
        self.player_response = self.get_player_response()
        if self.player_response:
            print(f'{EXT_BLUE}[+] : {YELLOW}Extracted player response data from HTML : {UNDERLINE}{self.video_id}{RESET}')
        self.jsondata = {}
        
        if self.player_url:
        	print(f'{EXT_BLUE}[+] : {YELLOW}Extracted player url from HTML : {UNDERLINE}{self.video_id}{RESET}')



    def get_video_id(self, url):
        # Regex pattern to match YouTube video ID
        pattern = r'(?:youtu\.be\/|youtube\.com\/(?:[^\"&\?\/]+\/)?(?:embed\/|v\/|watch\?v=|shorts\/)?)([a-zA-Z0-9_-]+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def get_watch_url(self, url):
        video_id = self.get_video_id(url)
        if video_id:
            # Construct the new URL
            return f"https://www.youtube.com/watch?v={video_id}"
        return None

    def download_html(self):
        print(f'{EXT_BLUE}[+] : {YELLOW}Downloading HTML : {UNDERLINE}{self.video_id}{RESET}')
        if self.watch_url:
            try:
                response = requests.get(self.watch_url)
                response.raise_for_status()  # Raise an error for bad status codes
                return response.text
            except requests.RequestException as e:
                print(f'{EXT_BLUE}[!] : {RED}Error downloading HTML: {e}{RESET}')
                return None
        else:
            # with open("youtube.html","r",encoding='utf-8') as file:
            #     a = file.read()
            #     return a
            print(f'{EXT_BLUE}[!] : {RED}Watch URL is not valid{RESET}')
            return None

    def get_player_response(self):
        if self.html:
            # Regex pattern to match ytInitialPlayerResponse data
            pattern = r'ytInitialPlayerResponse\s*=\s*({.*?});'
            match = re.search(pattern, self.html, re.DOTALL)
            if match:
                return match.group(1)
            else:
                print(f'{EXT_BLUE}[!] : {RED}Player response not found in HTML{RESET}')
                return None
        else:
            print(f'{EXT_BLUE}[!] : {RED}HTML content is not available{RESET}')
            return None

    def parse_player_response(self):
        try:
            player_response_obj = json.loads(self.player_response)
            microformat = player_response_obj.get('microformat', {}).get('playerMicroformatRenderer', {})
            self.jsondata['uploadDate'] = microformat.get('uploadDate')

            playability_status = player_response_obj.get('playabilityStatus', {})
            status = playability_status.get('status')
            reason = playability_status.get('reason')
            if reason:
                self.jsondata['PlayabilityError'] = reason
            if status and status.lower() != "error":
                self.jsondata["IsAvailable"] = True
            if status and status.lower() == "ok":
                self.jsondata["IsPlayable"] = True

            video_details = player_response_obj.get('videoDetails', {})
            self.jsondata['Title'] = video_details.get('title')
            self.jsondata['ChannelId'] = video_details.get('channelId')
            self.jsondata['Author'] = video_details.get('author')
            self.jsondata['Duration'] = video_details.get('lengthSeconds')
            self.jsondata['keywords'] = video_details.get('keywords')
            self.jsondata['Description'] = video_details.get('shortDescription')
            self.jsondata['ViewCount'] = video_details.get('viewCount')
            
            thumbnails = video_details.get('thumbnail', {}).get('thumbnails', [])
            thumbnails_array = []
            for thumbnail in thumbnails:
                thumbnails_array.append({
                    "url": thumbnail.get("url"),
                    "width": thumbnail.get("width"),
                    "height": thumbnail.get("height")
                })
            self.jsondata['thumbnails'] = thumbnails_array
            
            # Extract stream data
            self.extract_stream_data(player_response_obj.get('streamingData', {}))
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f'{EXT_BLUE}[!] : {RED}Error parsing player response: {e}{RESET}')

    def extract_stream_data(self, streaming_data):
        formats = {}
        # Extract Muxed formats
        muxed_formats = streaming_data.get('formats', [])

        muxed_array = []


        global global_cipher
        global_cipher = DecipherSignature(self.player_url)
        
        for format in muxed_formats:
            muxed_array.append(self.extract_stream_info(format, "MUXED"))
        
        formats['Muxed'] = muxed_array

        
        # Extract OnlyAudio formats
        adaptive_formats = streaming_data.get('adaptiveFormats', [])
        audio_array = []
        video_array = []
        for format in adaptive_formats:
            mime_type = format.get('mimeType', '')
            if 'audio' in mime_type:
                audio_array.append(self.extract_stream_info(format, "AUDIO"))
            elif 'video' in mime_type:
                video_array.append(self.extract_stream_info(format, "VIDEO"))
        formats['OnlyAudio'] = audio_array
        formats['OnlyVideo'] = video_array

        self.jsondata['Formats'] = formats

    def extract_stream_info(self, stream, stream_type):
        # Extract relevant stream info for both audio and video
        info = {
            'itag': stream.get('itag'),
            'mimeType': stream.get('mimeType'),
            'bitrate': stream.get('bitrate'),
            'initRange': stream.get('initRange'),
            'indexRange': stream.get('indexRange'),
            'lastModified': stream.get('lastModified'),
            'contentLength': stream.get('contentLength'),
            'quality': stream.get('quality'),
            'projectionType': stream.get('projectionType'),
            'averageBitrate': stream.get('averageBitrate'),
            'approxDurationMs': stream.get('approxDurationMs'),
            'url': stream.get('url')
        }
        global global_cipher
        if info.get('url') is not None:  
            info['url'] = global_cipher.dethrottle(info['url'])
         # If the URL is None, delete it from the dictionary
        if info.get('url') is None:
            info['signatureCipher'] = stream.get('signatureCipher')         
            info['url'] = global_cipher.sigurl_to_url(info['signatureCipher'])
            del info['signatureCipher']    

        # Add additional fields for video streams
        if stream_type == "VIDEO" or stream_type == "MUXED":
            info.update({
                'width': stream.get('width'),
                'height': stream.get('height'),
                'fps': stream.get('fps'),
                'qualityLabel': stream.get('qualityLabel')
            })

        # Add additional fields for audio streams
        if stream_type == "AUDIO":
            info.update({
                'audioQuality': stream.get('audioQuality'),
                'audioSampleRate': stream.get('audioSampleRate'),
                'audioChannels': stream.get('audioChannels'),
                'loudnessDb': stream.get('loudnessDb')
            })

        return info
    def get_player_url(self):
	    # if HTML is None return error
	    if self.html is None:
	    	print(f'{EXT_BLUE}[!] : {RED}HTML not downloaded yet {RESET}')
	    	return None


	    # Searching player URL data using regex
	    match = re.search(r'/s/player/[\w\d]+/[\w\d_/.]+/base\.js', self.html)
	    if not match:
	        print(f'{EXT_BLUE}[!] : {RED}Player url not found in HTML{RESET}')
	        return None
	    
	    player_last_url = match.group(0)
	    
	    # Adding the YouTube address to create a valid player URL
	    youtube_url = "https://www.youtube.com"
	    PlayerUrl = youtube_url + player_last_url
	    
	    return PlayerUrl
