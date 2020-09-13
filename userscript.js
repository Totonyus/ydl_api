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

    const preset_list = [
        {name: 'Download (default)', key : 'd', host : default_host, params : {}},
        {name: 'Download (best)', key : 'b', host : default_host, params : { format: 'bestvideo+bestaudio/best'}},
        {name: 'Download (720p)', key : '7', host : default_host, params : { format: 'best[height=720]/best'}},
        {name: 'Download (audio)', key : 'a', host : default_host, params : { format: 'bestaudio'}},
        {name: 'Download (best, subtitles)', key : 's', host : default_host, params : { format: 'bestvideo+bestaudio/best', subtitles: 'en'}}, // multiple subtitles example :  'fr,en'
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
            onerror: function (response) {
                GM_notification('Host seams unreachable, is the server up ?', 'Download failed');
            },
            onload: function (response) {
                const jsonResponse = JSON.parse(response.response);
                if (response.status === 200) {
                    GM_notification(`'${jsonResponse.url}' is downloading in '${jsonResponse.download_dir}'`, 'Download launched');
                } else {
                    GM_notification(`Impossible to download '${jsonResponse.url}'`, 'Download failed');
                }
            }
        });
    };

    preset_list.forEach((preset)=>{
        GM_registerMenuCommand(preset.name, ()=>{launchRequest(preset)}, preset.key);
    })
})();
