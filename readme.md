# Simple youtube-dl rest API (ydl_api)

### Exhaustive list of the ydl_api features
- Launch youtube-dl download directly on your server
  - Chose your video format
  - Download subtitles
  
### Disclaimer
This is my very first python program. I did my best. If you are an experienced python developer, you may not want to look at the source code. (I'm kidding, you're going to have to configure some things anyway).

### Files
* `readme.md`
* `main.py` the main program
* `params.py` all the default parameters of the application, everything is set up to offer you a working application out of the box
* `launch.sh` a simple sh file to launch the server
* `userscript.js` a javascript file you can import in [Greasemonkey (firefox)](https://addons.mozilla.org/fr/firefox/addon/greasemonkey/) or [Tampermonkey (chrome)](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo?hl=fr) to access the api from yout browser
* `ydl_api.service` a systemd service file to launch this application as a daemon
* An iOS shortcut you can find [here](https://www.icloud.com/shortcuts/055260591bfe4e6a837df90864705739)

### Dependencies
* Installation with distribution package manager (`apt`, `yum`, ...) : `python3`, `python3-pip`, `ffmpeg`
* Installation with pip3 : `fastapi`, `uvicorn`, `youtube-dl`

```
pip3 install fastapi youtube-dl uvicorn
``` 

* Make sure you have the last youtube-dl version installed : `youtube-dl --version` (currently `2020.09.06`). You could have problems with some videos if you use an older version.

### Installation
#### Download this repo
Download the latest release :
```
wget https://github.com/Totonyus/ydl_api/archive/master.zip
```

Then unzip the file and rename the unziped folder : (note you can use `unzîp -d %your_path%` to specify where you want to unzip the file ) 
```
unzip master.zip; mv ydl_api-master.zip ydl_api
```

#### Configuration
The application is setup to work out of th box but you should probably change some settings :

Placeholders looks like this : `---%--- REPLACE ---%---`
* (Optional) `params.py` : you can change destination folder, file name template and a few others options
* (Optional) `userscript.js` : you must set your api route (default : `http://localhost:5011/download`, you can also add format options as you want
* (Optional) `launch.sh` : the default port is set arbitrarily to `5011`. Change it as you want.
* (Optional) `ydl_api.service` : you must set the working directory to the directory you downloaded this application. If you don't want change default user and group, you can delete those lines :

```
# (Optional, default='root') Enter here the user and group you want
User=---%--- REPLACE ---%---
Group=---%--- REPLACE ---%---
```

#### Install as daemon
Just move `ydl_api.service` in `/usr/lib/systemd/system/` for `systemd` linux.

```
mv ydl_api.service /usr/lib/systemd/system/
```

You can change the name of the service by changing the name of the file.

then (you must run this command every time you change the service file) 

```
systemctl daemon-reload
```

To start the daemon : 
```
systemctl start ydl_api
```

To stop the daemon : 
```
systemctl stop ydl_api
```

To start the daemon on boot : 
```
systemctl enable ydl_api
```

To NOT start the daemon on boot : 
```
systemctl disable ydl_api
```

#### Install the userscript
Install [Greasemonkey (firefox)](https://addons.mozilla.org/fr/firefox/addon/greasemonkey/) or [Tampermonkey (chrome)](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo?hl=fr) and add a new userscript. Then copy the content of `userscript.js` in the interface and save.

You now should have access to download options on every site.

![result.jpg](result.jpg)

##### Userscript setup
You probably should change the default host set in the script.

You can modify the `preset_list` as you want. Note : the key parameter of a preset is not mandatory. It's just a shortcut.

### API usage
#### Templates
You can create three types of templates :

* download destinations in `params.download_directory_templates`
* file names in `params.file_name_templates`
* server-side presets in `params.presets_templates` 

In all cases, always keep a template named `default` (you still can modify them).

##### Download destinations and file name templates
In those templates, you can use tags delimited by `%` (example : `%hostname%`).

Provided tags are `hostname`, `location_identifier` and `filename_identifier`

##### Presets
If more than one preset is provided (`&presets=audio,best`), the url will be downloaded one time with each format. For example, you can download both music and clip of a song video.

Some rules :
* If not all provided presets are correct, only the correct presets will be downloaded
* If no correct preset is provided, the default preset is used

#### Query parameters
Parameters :
* `url` : the page to download
* (optional) `format` : the format of the video you want, if not provided, default value = `params.default_format`
* (optional) `subtitles` : the list of subtitles you want to download. Can not download generated subtitles. If not provided, default value = `params.default_subtitles_languages`
* (optional) `location` : the identifier of the location you want to use. Set in `download_directory_templates`. If not provided, default value = `default`
* (optional) `filename` : the identifier of the filename you want to use. Set in `params.file_name_templates`. If not provided, default value = `default`
* (optional) `presets` : the identifier of the presets you want to use. Multiple preset are separated by coma `&presets=audio,best`. The presets are defines in `params.presets_templates`

#### Priority
The priority order of parameters is : Query paramaters > Preset parameters > Default parameters.

This means :
* you can override a preset parameter in your query
* if a parameter is not present in you preset, the parameter of the default preset will be used (unless the parameter is present il query)

#### API usage examples
Only the url is required to use the api.

The simplest request is : (will use the default preset)

```
GET http://localhost:5011/download?url=https://www.youtube.com/watch?v=9Lgc3TxqgHA
```

However, most of the requests defined in the userscript will look like hits

```
GET http://localhost:5011/download?url=https://www.youtube.com/watch?v=Kf1XttuuIiQ&presets=audio
```

You can override presets parameters
```
GET http://localhost:5011/download?url=https://www.youtube.com/watch?v=wV4wepiucf4&presets=audio&location=default
```

#### API response
Responses status :
* 200 : Everything should be downloaded correctly
* 202 : When downloading playlist : not all downloads were checked, some file may not be downloaded by youtube-dl
* 202 : When using multiple presets : one or more presets is invalid, not all files will be downloaded
* 400 : No video can be downloaded
