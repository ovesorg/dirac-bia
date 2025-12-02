/**
 * Microsoft Authentication for MkDocs Documentation Sites
 * 
 * Features:
 * - CloudFlare deployment with credential checks
 * - Automatic bypass for local development (localhost/127.0.0.1)
 * - No configuration needed for local testing
 * 
 * Local development is automatically detected and authentication is skipped.
 */

(function() {
    'use strict';

    // Detect if running locally - bypass authentication completely
    const isLocalhost = window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1' ||
                       window.location.hostname === '' ||
                       window.location.protocol === 'file:';

    if (isLocalhost) {
        console.log('[Auth] Local development detected - authentication bypassed');
        return;  // Exit completely, no authentication needed
    }

    // Only run authentication for cloud-deployed sites
    console.log('[Auth] Cloud deployment detected - initializing authentication');

    // MSAL Configuration (to be customized per deployment)
    const msalConfig = {
        auth: {
            clientId: 'YOUR_CLIENT_ID_HERE',  // Replace with your Azure AD App Registration Client ID
            authority: 'https://login.microsoftonline.com/YOUR_TENANT_ID_HERE',  // Replace with your tenant ID
            redirectUri: window.location.origin
        },
        cache: {
            cacheLocation: 'sessionStorage',
            storeAuthStateInCookie: false
        }
    };

    // Required scopes for authentication
    const loginRequest = {
        scopes: ['User.Read']
    };

    let msalInstance;

    // Initialize MSAL
    try {
        msalInstance = new msal.PublicClientApplication(msalConfig);
    } catch (error) {
        console.error('[Auth] Failed to initialize MSAL:', error);
        return;
    }

    // Handle authentication
    async function handleAuthentication() {
        try {
            // Check if user is already authenticated
            const accounts = msalInstance.getAllAccounts();
            
            if (accounts.length === 0) {
                // No user signed in, redirect to login
                await msalInstance.loginRedirect(loginRequest);
            } else {
                // User is already signed in
                console.log('[Auth] User authenticated:', accounts[0].username);
            }
        } catch (error) {
            console.error('[Auth] Authentication error:', error);
            // Show error message to user
            document.body.innerHTML = `
                <div style="display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column;">
                    <h1>Authentication Required</h1>
                    <p>Please sign in to access this documentation.</p>
                    <button onclick="location.reload()">Retry</button>
                </div>
            `;
        }
    }

    // Handle redirect response
    msalInstance.handleRedirectPromise()
        .then(response => {
            if (response !== null) {
                console.log('[Auth] Login successful:', response.account.username);
            }
            return handleAuthentication();
        })
        .catch(error => {
            console.error('[Auth] Redirect error:', error);
        });

})();
