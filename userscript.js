// ==UserScript==
// @name        ydl_api
// @include     *
// @grant       GM_registerMenuCommand
// @grant       GM_xmlhttpRequest
// @grant       GM_notification
// ==/UserScript==

(function() {
    'use strict';

    // ---%--- REPLACE ---%--- your host and token here
    const default_host = 'http://127.0.0.1:5011/download';
    const userToken = null;

    // possible parameters : 'format', 'subtitles', 'location', 'filename', 'presets'
    const preset_list = [
        {name: 'Download (default)', key : '1', host : default_host, params : {}},
        {name: 'Download (best)', key : '2', host : default_host, params : { presets: 'best'}},
        {name: 'Download (720p)', key : '3', host : default_host, params : { presets: 'hd'}},
        {name: 'Download (audio)', key : '4', host : default_host, params : { presets: 'audio'}},
        {name: 'Download (audio + video)', key : '5', host : default_host, params : { presets: 'best,audio'}},
        {name: 'Download (best, subtitles)', key : '6', host : default_host, params : { presets: 'best', subtitles: 'en'}}, // multiple subtitles example :  'fr,en'
    ];

    const buildURL = function (preset) {
        const url = new URL(preset.host);

        url.searchParams.append('url', window.location.href);

        if(userToken !== null){
            url.searchParams.append('token', userToken);
        }

        Object.entries(preset.params).forEach(([key, value]) => {
            url.searchParams.append(key, value);
        });

        return url.href;
    };

    const launchRequest = function (preset) {
        GM_xmlhttpRequest({
            method: 'GET',
            url: buildURL(preset),
            onerror: function () {
                GM_notification('Host seams unreachable, is the server up ?', 'Download failed');
            },
            onload: function (response) {
                if (response.status === 200) {
                    GM_notification(`Downloading`, 'Download launched');
                } else if(response.status === 202){
                    GM_notification(`The download have not been checked. Some files may be not downloaded`, 'Download launched');
                } else if(response.status === 401){
                    GM_notification(`The server require a user token or the provided token is wrong`, 'Authentication failed');
                } else {
                    GM_notification(`The format may be wrong or not available or there is no video to download`, 'Download failed');
                }
            }
        });
    };

    preset_list.forEach((preset)=>{
        GM_registerMenuCommand(preset.name, ()=>{launchRequest(preset)}, preset.key);
    })
})();
