(() => {
    var actualCode =  '(' + function() {
        'use strict';
        var navigator = window.navigator;
        var modifiedNavigator;
        if ('userAgent' in Navigator.prototype) {
            // Chrome 43+ moved all properties from navigator to the prototype,
            // so we have to modify the prototype instead of navigator.
            modifiedNavigator = Navigator.prototype;

        } else {
            // Chrome 42- defined the property on navigator.
            modifiedNavigator = Object.create(navigator);
            Object.defineProperty(window, 'navigator', {
                value: modifiedNavigator,
                configurable: false,
                enumerable: false,
                writable: false
            });
        }
        Object.defineProperties(modifiedNavigator, {
            webdriver: {
                value: false,
                configurable: false,
                enumerable: true,
                writable: false
            }
//            userAgent: {
//                value: navigator.userAgent.replace(/\([^)]+\)/, 'Windows NT 5.1'),
//                configurable: false,
//                enumerable: true,
//                writable: false
//            },
//            appVersion: {
//                value: navigator.appVersion.replace(/\([^)]+\)/, 'Windows NT 5.1'),
//                configurable: false,
//                enumerable: true,
//                writable: false
//            },
//            platform: {
//                value: 'Win32',
//                configurable: false,
//                enumerable: true,
//                writable: false
//            },
        });
    } + ')();';

    var s = document.createElement('script');
    s.textContent = actualCode;
    document.documentElement.appendChild(s);
    s.remove();
})();
//    const switch_off_webdriver = () => {
//        console.log(navigator.webdriver);
////        try {
//        Object.defineProperty(navigator, 'webdriver', {
//        get: () => false,
//        });

//    console.log(navigator.webdriver);