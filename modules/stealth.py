#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Stealth Module
------------
Implements anti-detection measures to avoid bot detection.
"""

import os
import json
import random
import logging
import string
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def apply_stealth_settings(driver):
    """
    Apply stealth settings to WebDriver.
    
    Args:
        driver: Selenium WebDriver instance
    """
    try:
        # Execute JavaScript to override navigator properties
        driver.execute_script("""
            // Override navigator properties
            const originalNavigator = window.navigator;
            const navigatorProxy = new Proxy(originalNavigator, {
                has: (target, key) => (key === 'webdriver' ? false : key in target),
                get: (target, key) => {
                    if (key === 'webdriver') {
                        return false;
                    }
                    
                    const value = target[key];
                    return typeof value === 'function' ? value.bind(target) : value;
                }
            });
            
            // Define navigator
            Object.defineProperty(window, 'navigator', {
                value: navigatorProxy,
                configurable: false,
                writable: false
            });
            
            // Override permissions
            const originalPermissions = window.Permissions;
            if (originalPermissions) {
                window.Permissions.prototype.query = async function() {
                    return { state: 'granted', onchange: null };
                };
            }
            
            // Override plugins
            Object.defineProperty(navigatorProxy, 'plugins', {
                get: () => {
                    const plugins = [];
                    for (let i = 0; i < 3; i++) {
                        plugins.push({
                            name: ['PDF Viewer', 'Chrome PDF Viewer', 'Chromium PDF Viewer'][i],
                            description: ['Portable Document Format', 'Portable Document Format', 'Portable Document Format'][i],
                            filename: ['internal-pdf-viewer', 'mhjfbmdgcfjbbpaeojofohoefgiehjai', 'internal-pdf-viewer'][i],
                            length: 1,
                            item: () => null
                        });
                    }
                    return plugins;
                }
            });
            
            // Override languages
            Object.defineProperty(navigatorProxy, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Override connection
            if (navigator.connection) {
                Object.defineProperty(navigatorProxy, 'connection', {
                    get: () => ({
                        effectiveType: ['4g', '3g'][Math.floor(Math.random() * 2)],
                        rtt: Math.floor(Math.random() * 100),
                        downlink: Math.floor(Math.random() * 10) + 5,
                        saveData: false
                    })
                });
            }
            
            // Override hardware concurrency
            Object.defineProperty(navigatorProxy, 'hardwareConcurrency', {
                get: () => Math.floor(Math.random() * 8) + 2
            });
            
            // Override device memory
            if ('deviceMemory' in navigator) {
                Object.defineProperty(navigatorProxy, 'deviceMemory', {
                    get: () => Math.pow(2, Math.floor(Math.random() * 4) + 1)
                });
            }
            
            // Override automation detection
            window.chrome = {
                app: {
                    isInstalled: false,
                    InstallState: {
                        DISABLED: 'disabled',
                        INSTALLED: 'installed',
                        NOT_INSTALLED: 'not_installed'
                    },
                    RunningState: {
                        CANNOT_RUN: 'cannot_run',
                        READY_TO_RUN: 'ready_to_run',
                        RUNNING: 'running'
                    }
                },
                runtime: {
                    OnInstalledReason: {
                        CHROME_UPDATE: 'chrome_update',
                        INSTALL: 'install',
                        SHARED_MODULE_UPDATE: 'shared_module_update',
                        UPDATE: 'update'
                    },
                    OnRestartRequiredReason: {
                        APP_UPDATE: 'app_update',
                        OS_UPDATE: 'os_update',
                        PERIODIC: 'periodic'
                    },
                    PlatformArch: {
                        ARM: 'arm',
                        ARM64: 'arm64',
                        MIPS: 'mips',
                        MIPS64: 'mips64',
                        X86_32: 'x86-32',
                        X86_64: 'x86-64'
                    },
                    PlatformNaclArch: {
                        ARM: 'arm',
                        MIPS: 'mips',
                        MIPS64: 'mips64',
                        X86_32: 'x86-32',
                        X86_64: 'x86-64'
                    },
                    PlatformOs: {
                        ANDROID: 'android',
                        CROS: 'cros',
                        LINUX: 'linux',
                        MAC: 'mac',
                        OPENBSD: 'openbsd',
                        WIN: 'win'
                    },
                    RequestUpdateCheckStatus: {
                        NO_UPDATE: 'no_update',
                        THROTTLED: 'throttled',
                        UPDATE_AVAILABLE: 'update_available'
                    }
                }
            };
            
            // Override WebGL
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // UNMASKED_VENDOR_WEBGL
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                // UNMASKED_RENDERER_WEBGL
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.apply(this, arguments);
            };
            
            // Override canvas fingerprinting
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                if (this.width > 16 && this.height > 16) {
                    const context = this.getContext('2d');
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    const pixels = imageData.data;
                    
                    // Add subtle noise to canvas
                    for (let i = 0; i < pixels.length; i += 4) {
                        // Only modify non-transparent pixels
                        if (pixels[i + 3] > 0) {
                            pixels[i] = Math.max(0, Math.min(255, pixels[i] + (Math.random() * 2 - 1)));
                            pixels[i + 1] = Math.max(0, Math.min(255, pixels[i + 1] + (Math.random() * 2 - 1)));
                            pixels[i + 2] = Math.max(0, Math.min(255, pixels[i + 2] + (Math.random() * 2 - 1)));
                        }
                    }
                    
                    context.putImageData(imageData, 0, 0);
                }
                return originalToDataURL.apply(this, arguments);
            };
            
            // Override audio context fingerprinting
            const originalGetChannelData = AudioBuffer.prototype.getChannelData;
            if (originalGetChannelData) {
                AudioBuffer.prototype.getChannelData = function() {
                    const channelData = originalGetChannelData.apply(this, arguments);
                    // Add subtle noise to audio data
                    const noise = 0.0001;
                    for (let i = 0; i < channelData.length; i++) {
                        channelData[i] += (Math.random() * 2 - 1) * noise;
                    }
                    return channelData;
                };
            }
            
            // Override font fingerprinting
            const originalMeasureText = CanvasRenderingContext2D.prototype.measureText;
            CanvasRenderingContext2D.prototype.measureText = function(text) {
                const result = originalMeasureText.apply(this, arguments);
                const noise = 0.0001;
                
                // Add subtle noise to text metrics
                Object.defineProperties(result, {
                    width: {
                        get: () => originalMeasureText.apply(this, arguments).width * (1 + (Math.random() * 2 - 1) * noise)
                    },
                    actualBoundingBoxAscent: {
                        get: () => originalMeasureText.apply(this, arguments).actualBoundingBoxAscent * (1 + (Math.random() * 2 - 1) * noise)
                    },
                    actualBoundingBoxDescent: {
                        get: () => originalMeasureText.apply(this, arguments).actualBoundingBoxDescent * (1 + (Math.random() * 2 - 1) * noise)
                    },
                    actualBoundingBoxLeft: {
                        get: () => originalMeasureText.apply(this, arguments).actualBoundingBoxLeft * (1 + (Math.random() * 2 - 1) * noise)
                    },
                    actualBoundingBoxRight: {
                        get: () => originalMeasureText.apply(this, arguments).actualBoundingBoxRight * (1 + (Math.random() * 2 - 1) * noise)
                    }
                });
                
                return result;
            };
        """)
        
        logger.debug("Applied stealth settings to WebDriver")
    
    except Exception as e:
        logger.error(f"Error applying stealth settings: {str(e)}")

def generate_fingerprint_overrides() -> str:
    """
    Generate JavaScript code for fingerprint overrides.
    
    Returns:
        str: JavaScript code for fingerprint overrides
    """
    try:
        # Generate random values for fingerprinting
        fingerprint = {
            "userAgent": _generate_user_agent(),
            "screenWidth": random.randint(1024, 1920),
            "screenHeight": random.randint(768, 1080),
            "colorDepth": random.choice([24, 32]),
            "deviceMemory": random.choice([2, 4, 8, 16]),
            "hardwareConcurrency": random.randint(2, 8),
            "timezone": _generate_timezone(),
            "language": _generate_language(),
            "platform": _generate_platform(),
            "vendor": _generate_vendor(),
            "webglVendor": _generate_webgl_vendor(),
            "webglRenderer": _generate_webgl_renderer(),
            "audioFingerprint": _generate_audio_fingerprint()
        }
        
        # Generate JavaScript code
        js_code = f"""
            // Fingerprint overrides
            (function() {{
                // Override navigator properties
                Object.defineProperties(Navigator.prototype, {{
                    userAgent: {{ get: function() {{ return "{fingerprint['userAgent']}"; }} }},
                    appVersion: {{ get: function() {{ return "{fingerprint['userAgent'].split('Mozilla/')[1]}"; }} }},
                    platform: {{ get: function() {{ return "{fingerprint['platform']}"; }} }},
                    vendor: {{ get: function() {{ return "{fingerprint['vendor']}"; }} }},
                    language: {{ get: function() {{ return "{fingerprint['language']}"; }} }},
                    languages: {{ get: function() {{ return ["{fingerprint['language']}", "en-US", "en"]; }} }},
                    deviceMemory: {{ get: function() {{ return {fingerprint['deviceMemory']}; }} }},
                    hardwareConcurrency: {{ get: function() {{ return {fingerprint['hardwareConcurrency']}; }} }}
                }});
                
                // Override screen properties
                Object.defineProperties(Screen.prototype, {{
                    width: {{ get: function() {{ return {fingerprint['screenWidth']}; }} }},
                    height: {{ get: function() {{ return {fingerprint['screenHeight']}; }} }},
                    availWidth: {{ get: function() {{ return {fingerprint['screenWidth']}; }} }},
                    availHeight: {{ get: function() {{ return {fingerprint['screenHeight']} - 40; }} }},
                    colorDepth: {{ get: function() {{ return {fingerprint['colorDepth']}; }} }},
                    pixelDepth: {{ get: function() {{ return {fingerprint['colorDepth']}; }} }}
                }});
                
                // Override WebGL fingerprinting
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    // UNMASKED_VENDOR_WEBGL
                    if (parameter === 37445) {{
                        return "{fingerprint['webglVendor']}";
                    }}
                    // UNMASKED_RENDERER_WEBGL
                    if (parameter === 37446) {{
                        return "{fingerprint['webglRenderer']}";
                    }}
                    return getParameter.apply(this, arguments);
                }};
                
                // Override timezone
                Date.prototype.getTimezoneOffset = function() {{
                    return {fingerprint['timezone']};
                }};
                
                // Override audio fingerprinting
                const audioFp = {json.dumps(fingerprint['audioFingerprint'])};
                const originalGetChannelData = AudioBuffer.prototype.getChannelData;
                if (originalGetChannelData) {{
                    AudioBuffer.prototype.getChannelData = function(channel) {{
                        const channelData = originalGetChannelData.call(this, channel);
                        if (channel === 0 && this.length === 44100 && audioFp.length === 126) {{
                            for (let i = 0; i < audioFp.length; i++) {{
                                channelData[i] = audioFp[i];
                            }}
                        }}
                        return channelData;
                    }};
                }}
                
                // Override canvas fingerprinting
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type) {{
                    if (this.width === 16 && this.height === 16) {{
                        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABmklEQVQ4jY2TP2hTURTGf+e+vPdIaRND0sZUaRBD/5hODkVEcHRwEMHJyUUQRNBBJwcR3QQnwVkEQXBwcHAQOhUHIUMGCUW0rUMiGpLw8u69x+G9QIgpfcOFw+F83+9+9zsiQr/Ml0HkAMjDlcWI6YQJgPVt+XR7W5rJpABE9HYs4vJE/8PGaBgPiYsIy1vJIQB9sLr9LBndBLCxU+iUDECTCYDrc5P7AIZvLh+JRhcBdg7aNDuZAJhMJgCuTRUBuDJZBODT7gHNTqbpZALg6uQBgMsTYwC83j2k1ck0nUwAXJnIAzA7PgrAq91DWt1M08kEwMxYDoBL43kAXu4e0e5mmk4mAC6O5QC4OJ4H4MXuEe1upulkAmB6LAvA9FgOgO2ve3QyTScTAFO5DABTuSwAW1/26GSaTiYAJrNpACazGQA2P+/TzTSdTABMjKQBmBhJA/Ds0z7dTNPJBMD4cAqA8eEUAE8/HtDLNJ1MAIwNpQAYG0oBsPHhgF6m6WQCYDQTAxjNxABsNI7oZZpOJgB+A0DBzlBHh8LaAAAAAElFTkSuQmCC";
                    }}
                    return originalToDataURL.apply(this, arguments);
                }};
                
                // Override font fingerprinting
                const originalMeasureText = CanvasRenderingContext2D.prototype.measureText;
                CanvasRenderingContext2D.prototype.measureText = function(text) {{
                    const result = originalMeasureText.apply(this, arguments);
                    if (text === "mmmmmmmmmmlli") {{
                        Object.defineProperty(result, "width", {{ value: 72.2578125 }});
                    }}
                    return result;
                }};
                
                // Override webdriver flag
                Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});
                
                // Override Chrome
                window.chrome = {{
                    app: {{
                        isInstalled: false,
                        InstallState: {{
                            DISABLED: 'disabled',
                            INSTALLED: 'installed',
                            NOT_INSTALLED: 'not_installed'
                        }},
                        RunningState: {{
                            CANNOT_RUN: 'cannot_run',
                            READY_TO_RUN: 'ready_to_run',
                            RUNNING: 'running'
                        }}
                    }},
                    runtime: {{
                        OnInstalledReason: {{
                            CHROME_UPDATE: 'chrome_update',
                            INSTALL: 'install',
                            SHARED_MODULE_UPDATE: 'shared_module_update',
                            UPDATE: 'update'
                        }},
                        OnRestartRequiredReason: {{
                            APP_UPDATE: 'app_update',
                            OS_UPDATE: 'os_update',
                            PERIODIC: 'periodic'
                        }},
                        PlatformArch: {{
                            ARM: 'arm',
                            ARM64: 'arm64',
                            MIPS: 'mips',
                            MIPS64: 'mips64',
                            X86_32: 'x86-32',
                            X86_64: 'x86-64'
                        }},
                        PlatformNaclArch: {{
                            ARM: 'arm',
                            MIPS: 'mips',
                            MIPS64: 'mips64',
                            X86_32: 'x86-32',
                            X86_64: 'x86-64'
                        }},
                        PlatformOs: {{
                            ANDROID: 'android',
                            CROS: 'cros',
                            LINUX: 'linux',
                            MAC: 'mac',
                            OPENBSD: 'openbsd',
                            WIN: 'win'
                        }},
                        RequestUpdateCheckStatus: {{
                            NO_UPDATE: 'no_update',
                            THROTTLED: 'throttled',
                            UPDATE_AVAILABLE: 'update_available'
                        }}
                    }}
                }};
                
                // Override permissions
                if (navigator.permissions) {{
                    navigator.permissions.query = function(parameters) {{
                        return Promise.resolve({{ state: 'granted', onchange: null }});
                    }};
                }}
                
                console.log("Fingerprint overrides applied");
            }})();
        """
        
        return js_code
    
    except Exception as e:
        logger.error(f"Error generating fingerprint overrides: {str(e)}")
        return ""

def _generate_user_agent() -> str:
    """
    Generate a random user agent.
    
    Returns:
        str: Random user agent
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:92.0) Gecko/20100101 Firefox/92.0"
    ]
    
    return random.choice(user_agents)

def _generate_timezone() -> int:
    """
    Generate a random timezone offset.
    
    Returns:
        int: Random timezone offset in minutes
    """
    timezones = [-480, -420, -360, -300, -240, -180, -120, -60, 0, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600]
    return random.choice(timezones)

def _generate_language() -> str:
    """
    Generate a random language.
    
    Returns:
        str: Random language
    """
    languages = ["en-US", "en-GB", "fr-FR", "de-DE", "es-ES", "it-IT", "pt-BR", "nl-NL", "pl-PL", "ru-RU"]
    return random.choice(languages)

def _generate_platform() -> str:
    """
    Generate a random platform.
    
    Returns:
        str: Random platform
    """
    platforms = ["Win32", "MacIntel", "Linux x86_64"]
    return random.choice(platforms)

def _generate_vendor() -> str:
    """
    Generate a random vendor.
    
    Returns:
        str: Random vendor
    """
    vendors = ["Google Inc.", "Apple Computer, Inc.", ""]
    return random.choice(vendors)

def _generate_webgl_vendor() -> str:
    """
    Generate a random WebGL vendor.
    
    Returns:
        str: Random WebGL vendor
    """
    vendors = [
        "Google Inc. (Intel)",
        "Google Inc. (NVIDIA)",
        "Google Inc. (AMD)",
        "Google Inc.",
        "Intel Inc.",
        "NVIDIA Corporation",
        "AMD Corporation"
    ]
    return random.choice(vendors)

def _generate_webgl_renderer() -> str:
    """
    Generate a random WebGL renderer.
    
    Returns:
        str: Random WebGL renderer
    """
    renderers = [
        "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (NVIDIA, NVIDIA GeForce GTX 1050 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (Intel HD Graphics 620 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (AMD Radeon RX 550 Direct3D11 vs_5_0 ps_5_0)",
        "Intel Iris OpenGL Engine",
        "NVIDIA GeForce GT 750M OpenGL Engine",
        "AMD Radeon Pro 560 OpenGL Engine"
    ]
    return random.choice(renderers)

def _generate_audio_fingerprint() -> List[float]:
    """
    Generate a random audio fingerprint.
    
    Returns:
        List[float]: Random audio fingerprint
    """
    # Generate 126 random values between -1 and 1
    return [random.uniform(-0.2, 0.2) for _ in range(126)]