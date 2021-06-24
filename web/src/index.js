import React from 'react';
import ReactDom from 'react-dom';

import App from './components/App.jsx';


ReactDom.render(<App />, document.getElementById('app'));

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js').then(registration => {
            console.log('[YTDL] service worker registered');
        }).catch(registrationError => {
            console.log('[YTDL] service worker registration failed: ', registrationError);
        });
    });
}