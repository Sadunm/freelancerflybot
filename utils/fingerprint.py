#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fingerprint Module
---------------
Generates fingerprint overrides for browser instances.
"""

import os
import json
import random
import logging
import string
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def generate_fingerprint_overrides() -> str:
    """
    Generate JavaScript code for fingerprint overrides.
    
    Returns:
        str: JavaScript code for fingerprint overrides
    """
    # Generate random fingerprint values
    fingerprint = {
        "userAgent": _generate_user_agent(),
        "appVersion": _generate_app_version(),
        "platform": _generate_platform(),
        "vendor": _generate_vendor(),
        "language": _generate_language(),
        "languages": _generate_languages(),
        "deviceMemory": _generate_device_memory(),
        "hardwareConcurrency": _generate_hardware_concurrency(),
        "screenWidth": _generate_screen_width(),
        "screenHeight": _generate_screen_height(),
        "colorDepth": _generate_color_depth(),
        "timezone": _generate_timezone(),
        "webglVendor": _generate_webgl_vendor(),
        "webglRenderer": _generate_webgl_renderer(),
        "fonts": _generate_fonts(),
        "audioFingerprint": _generate_audio_fingerprint()
    }
    
    # Generate JavaScript code
    js_code = f"""
        // Fingerprint overrides
        (function() {{
            // Override navigator properties
            Object.defineProperties(Navigator.prototype, {{
                userAgent: {{ get: function() {{ return "{fingerprint['userAgent']}"; }} }},
                appVersion: {{ get: function() {{ return "{fingerprint['appVersion']}"; }} }},
                platform: {{ get: function() {{ return "{fingerprint['platform']}"; }} }},
                vendor: {{ get: function() {{ return "{fingerprint['vendor']}"; }} }},
                language: {{ get: function() {{ return "{fingerprint['language']}"; }} }},
                languages: {{ get: function() {{ return {json.dumps(fingerprint['languages'])}; }} }},
                deviceMemory: {{ get: function() {{ return {fingerprint['deviceMemory']}; }} }},
                hardwareConcurrency: {{ get: function() {{ return {fingerprint['hardwareConcurrency']}; }} }},
                webdriver: {{ get: function() {{ return false; }} }}
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
            
            // Override canvas fingerprinting
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {{
                if (this.width > 16 && this.height > 16) {{
                    const context = this.getContext('2d');
                    if (context) {{
                        const imageData = context.getImageData(0, 0, this.width, this.height);
                        const pixels = imageData.data;
                        
                        // Add subtle noise to canvas
                        for (let i = 0; i < pixels.length; i += 4) {{
                            // Only modify non-transparent pixels
                            if (pixels[i + 3] > 0) {{
                                pixels[i] = Math.max(0, Math.min(255, pixels[i] + (Math.random() * 2 - 1)));
                                pixels[i + 1] = Math.max(0, Math.min(255, pixels[i + 1] + (Math.random() * 2 - 1)));
                                pixels[i + 2] = Math.max(0, Math.min(255, pixels[i + 2] + (Math.random() * 2 - 1)));
                            }}
                        }}
                        
                        context.putImageData(imageData, 0, 0);
                    }}
                }}
                return originalToDataURL.apply(this, arguments);
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
                    }} else {{
                        // Add subtle noise to audio data
                        const noise = 0.0001;
                        for (let i = 0; i < channelData.length; i++) {{
                            channelData[i] += (Math.random() * 2 - 1) * noise;
                        }}
                    }}
                    return channelData;
                }};
            }}
            
            // Override font fingerprinting
            const originalMeasureText = CanvasRenderingContext2D.prototype.measureText;
            CanvasRenderingContext2D.prototype.measureText = function(text) {{
                const result = originalMeasureText.apply(this, arguments);
                const noise = 0.0001;
                
                // Add subtle noise to text metrics
                Object.defineProperties(result, {{
                    width: {{
                        get: () => originalMeasureText.apply(this, arguments).width * (1 + (Math.random() * 2 - 1) * noise)
                    }},
                    actualBoundingBoxAscent: {{
                        get: () => originalMeasureText.apply(this, arguments).actualBoundingBoxAscent * (1 + (Math.random() * 2 - 1) * noise)
                    }},
                    actualBoundingBoxDescent: {{
                        get: () => originalMeasureText.apply(this, arguments).actualBoundingBoxDescent * (1 + (Math.random() * 2 - 1) * noise)
                    }},
                    actualBoundingBoxLeft: {{
                        get: () => originalMeasureText.apply(this, arguments).actualBoundingBoxLeft * (1 + (Math.random() * 2 - 1) * noise)
                    }},
                    actualBoundingBoxRight: {{
                        get: () => originalMeasureText.apply(this, arguments).actualBoundingBoxRight * (1 + (Math.random() * 2 - 1) * noise)
                    }}
                }});
                
                return result;
            }};
            
            // Override font availability
            const originalFontFace = window.FontFace;
            const availableFonts = {json.dumps(fingerprint['fonts'])};
            
            if (window.queryLocalFonts) {{
                window.queryLocalFonts = async function() {{
                    return availableFonts.map(font => ({{
                        family: font,
                        fullName: font,
                        postscriptName: font.replace(/\\s+/g, ''),
                        style: 'normal'
                    }}));
                }};
            }}
            
            // Override permissions
            if (navigator.permissions) {{
                navigator.permissions.query = function(parameters) {{
                    return Promise.resolve({{ state: 'granted', onchange: null }});
                }};
            }}
            
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
            
            console.log("Fingerprint overrides applied");
        }})();
    """
    
    return js_code

def _generate_user_agent() -> str:
    """
    Generate a random user agent.
    
    Returns:
        str: Random user agent
    """
    from freelancerfly_bot.utils.user_agents import get_random_user_agent
    return get_random_user_agent()

def _generate_app_version() -> str:
    """
    Generate a random app version.
    
    Returns:
        str: Random app version
    """
    # Extract app version from user agent
    user_agent = _generate_user_agent()
    app_version = user_agent.split('Mozilla/')[1] if 'Mozilla/' in user_agent else "5.0"
    return app_version

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

def _generate_language() -> str:
    """
    Generate a random language.
    
    Returns:
        str: Random language
    """
    languages = ["en-US", "en-GB", "fr-FR", "de-DE", "es-ES", "it-IT", "pt-BR", "nl-NL", "pl-PL", "ru-RU"]
    return random.choice(languages)

def _generate_languages() -> List[str]:
    """
    Generate a random list of languages.
    
    Returns:
        List[str]: Random list of languages
    """
    primary_language = _generate_language()
    languages = [primary_language, "en-US", "en"]
    return languages

def _generate_device_memory() -> int:
    """
    Generate a random device memory.
    
    Returns:
        int: Random device memory
    """
    return random.choice([2, 4, 8, 16])

def _generate_hardware_concurrency() -> int:
    """
    Generate a random hardware concurrency.
    
    Returns:
        int: Random hardware concurrency
    """
    return random.randint(2, 16)

def _generate_screen_width() -> int:
    """
    Generate a random screen width.
    
    Returns:
        int: Random screen width
    """
    return random.choice([1366, 1440, 1536, 1600, 1680, 1920, 2048, 2560])

def _generate_screen_height() -> int:
    """
    Generate a random screen height.
    
    Returns:
        int: Random screen height
    """
    return random.choice([768, 900, 1024, 1050, 1080, 1200, 1440, 1600])

def _generate_color_depth() -> int:
    """
    Generate a random color depth.
    
    Returns:
        int: Random color depth
    """
    return random.choice([24, 32])

def _generate_timezone() -> int:
    """
    Generate a random timezone offset.
    
    Returns:
        int: Random timezone offset in minutes
    """
    timezones = [-480, -420, -360, -300, -240, -180, -120, -60, 0, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600]
    return random.choice(timezones)

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

def _generate_fonts() -> List[str]:
    """
    Generate a random list of fonts.
    
    Returns:
        List[str]: Random list of fonts
    """
    common_fonts = [
        "Arial", "Arial Black", "Arial Narrow", "Calibri", "Cambria", "Cambria Math",
        "Candara", "Comic Sans MS", "Consolas", "Constantia", "Corbel", "Courier New",
        "Georgia", "Helvetica", "Impact", "Lucida Console", "Lucida Sans Unicode",
        "Microsoft Sans Serif", "Palatino Linotype", "Segoe UI", "Tahoma", "Times New Roman",
        "Trebuchet MS", "Verdana"
    ]
    
    # Select a random subset of fonts
    num_fonts = random.randint(10, 20)
    return random.sample(common_fonts, min(num_fonts, len(common_fonts)))

def _generate_audio_fingerprint() -> List[float]:
    """
    Generate a random audio fingerprint.
    
    Returns:
        List[float]: Random audio fingerprint
    """
    # Generate 126 random values between -0.2 and 0.2
    return [random.uniform(-0.2, 0.2) for _ in range(126)]

def generate_fingerprint_profile() -> Dict[str, Any]:
    """
    Generate a complete fingerprint profile.
    
    Returns:
        Dict[str, Any]: Fingerprint profile
    """
    return {
        "userAgent": _generate_user_agent(),
        "appVersion": _generate_app_version(),
        "platform": _generate_platform(),
        "vendor": _generate_vendor(),
        "language": _generate_language(),
        "languages": _generate_languages(),
        "deviceMemory": _generate_device_memory(),
        "hardwareConcurrency": _generate_hardware_concurrency(),
        "screenWidth": _generate_screen_width(),
        "screenHeight": _generate_screen_height(),
        "colorDepth": _generate_color_depth(),
        "timezone": _generate_timezone(),
        "webglVendor": _generate_webgl_vendor(),
        "webglRenderer": _generate_webgl_renderer(),
        "fonts": _generate_fonts(),
        "audioFingerprint": _generate_audio_fingerprint()
    }

def save_fingerprint_profile(profile: Dict[str, Any], profile_file: str) -> bool:
    """
    Save fingerprint profile to file.
    
    Args:
        profile: Fingerprint profile
        profile_file: Path to profile file
    
    Returns:
        bool: True if profile was saved, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(profile_file), exist_ok=True)
        
        # Save profile
        with open(profile_file, 'w') as f:
            json.dump(profile, f, indent=2)
        
        logger.debug(f"Saved fingerprint profile to {profile_file}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error saving fingerprint profile: {str(e)}")
        return False

def load_fingerprint_profile(profile_file: str) -> Optional[Dict[str, Any]]:
    """
    Load fingerprint profile from file.
    
    Args:
        profile_file: Path to profile file
    
    Returns:
        Optional[Dict[str, Any]]: Fingerprint profile, or None if file not found
    """
    try:
        # Check if file exists
        if not os.path.exists(profile_file):
            logger.warning(f"Fingerprint profile file {profile_file} not found")
            return None
        
        # Load profile
        with open(profile_file, 'r') as f:
            profile = json.load(f)
        
        logger.debug(f"Loaded fingerprint profile from {profile_file}")
        
        return profile
    
    except Exception as e:
        logger.error(f"Error loading fingerprint profile: {str(e)}")
        return None