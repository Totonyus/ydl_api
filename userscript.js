// ==UserScript==
// @name        youtube-dl-rest-api
// @include     *
// @grant       GM_registerMenuCommand
// @grant       GM_xmlhttpRequest
// @grant       GM_notification
// ==/UserScript==

(function() {
    'use strict';

    const launchRequest = function(format){
        GM_xmlhttpRequest ( {
            method:     'GET',
            url:        `http://---%--- REPLACE ---%---/download?url=${window.location.href}&${format}`,
            onerror:    function (){
                GM_notification('Host seams unreachable, is the server up ?', 'Download failed');
            },
            onload:     function (response) {
                const jsonResponse = JSON.parse(response.response);

                if(response.status === 200){
                    GM_notification(`'${jsonResponse.url}' is downloading in '${jsonResponse.download_dir}'`, 'Download launched');
                }else{
                    GM_notification(`Impossible to download '${jsonResponse.url}'`, 'Download failed');
                }
            }
        });
    };

    // Add every format you want !
    GM_registerMenuCommand("Download (default)", ()=>{launchRequest("")}, "d");
    GM_registerMenuCommand("Download (best)", ()=>{launchRequest("format=bestvideo%2Bbestaudio/best")}, "b"); //replace + with %2B
    GM_registerMenuCommand("Download (720p)", ()=>{launchRequest("format=best[height=720]/best")}, "7");
})();
