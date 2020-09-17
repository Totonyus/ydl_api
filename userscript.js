// ==UserScript==
// @name        ydl_api
// @include     *
// @grant       GM_registerMenuCommand
// @grant       GM_xmlhttpRequest
// @grant       GM_notification
// ==/UserScript==

(function() {
    'use strict';

    // ---%--- REPLACE ---%--- your host here
    const default_host = 'http://127.0.0.1:5011/download';

    // possible parameters : 'format', 'subtitles', 'location'
    const preset_list = [
        {name: 'Download (default)', key : 'd', host : default_host, params : {}},
        {name: 'Download (best)', key : 'b', host : default_host, params : { presets: 'best'}},
        {name: 'Download (720p)', key : '7', host : default_host, params : { presets: 'hd'}},
        {name: 'Download (audio)', key : 'a', host : default_host, params : { presets: 'audio'}},
        {name: 'Download (audio + video)', key : 'v', host : default_host, params : { presets: 'best,audio'}},
        {name: 'Download (best, subtitles)', key : 's', host : default_host, params : { presets: 'best', subtitles: 'en'}}, // multiple subtitles example :  'fr,en'
    ];

    const buildURL = function (preset) {
        const url = new URL(preset.host);

        url.searchParams.append('url', window.location.href);

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
                const jsonResponse = JSON.parse(response.response);
                if (response.status === 200) {
                    GM_notification(`Downloading`, 'Download launched');
                } else if(response.status === 202){
                    GM_notification(`The download have not been checked. Some files may be not downloaded`, 'Download launched');
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
