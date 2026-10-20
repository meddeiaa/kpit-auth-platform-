*** Settings ***
Documentation     UI keywords for KPIT Auth Platform frontend tests.
...               Full-Screen Demonstration Mode with Guaranteed Viewport Rendering.
Library           SeleniumLibrary
Library           String
Library           Collections

Resource          variables.robot


*** Keywords ***

# =============================================================
# BROWSER MANAGEMENT (Guaranteed Full-Screen Version)
# =============================================================

Open Application In Browser
    [Documentation]    Opens Chrome in 100% Full-Screen (1920x1080) with explicit
    ...                viewport initialization to guarantee Angular Material rendering.
    
    ${chrome_options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver

    # Force 100% Full Screen Viewport via ChromeOptions
    Call Method    ${chrome_options}    add_argument    --start-maximized
    Call Method    ${chrome_options}    add_argument    --window-position\=0,0
    Call Method    ${chrome_options}    add_argument    --window-size\=1920,1080

    # Clean UI & Anti-Popup flags
    Call Method    ${chrome_options}    add_argument    --disable-notifications
    Call Method    ${chrome_options}    add_argument    --disable-popup-blocking
    Call Method    ${chrome_options}    add_argument    --disable-infobars
    Call Method    ${chrome_options}    add_argument    --disable-save-password-bubble
    Call Method    ${chrome_options}    add_argument    --no-first-run
    Call Method    ${chrome_options}    add_argument    --no-default-browser-check
    Call Method    ${chrome_options}    add_argument    --disable-features\=PasswordLeakDetection,SafeBrowsing,LeakDetection

    # Password Manager Preferences
    ${prefs}=    Create Dictionary
    ...    credentials_enable_service=${False}
    ...    profile.password_manager_enabled=${False}
    ...    profile.password_manager_leak_detection=${False}
    ...    safebrowsing.enabled=${False}
    
    Call Method    ${chrome_options}    add_experimental_option    prefs    ${prefs}

    # Instanciation de Chrome
    Create Webdriver    Chrome    options=${chrome_options}
    
    # Force l'initialisation explicite des dimensions
    Set Window Position    0    0
    Set Window Size        1920    1080
    Maximize Browser Window

    # Navigation
    Go To               ${LOGIN_URL}
    
    Set Selenium Implicit Wait    ${IMPLICIT_WAIT}
    Set Selenium Speed            0.2s
    
    # Attente explicite du rendu de la page de login Angular
    Wait Until Page Contains Element    ${USERNAME_FIELD}    timeout=15s
    Log    ✅ Browser opened successfully in Full-Screen Mode (1920x1080)


Close Application Browser
    [Documentation]    Close all browsers opened by Selenium.
    Close All Browsers
    Log    ✅ Browser closed cleanly


# =============================================================
# LOGIN PAGE
# =============================================================

Verify Login Page Is Loaded
    [Documentation]    Verify that the login page is displayed correctly.
    Wait Until Page Contains Element    ${USERNAME_FIELD}    timeout=10s
    Element Should Be Visible           ${USERNAME_FIELD}
    Element Should Be Visible           ${PASSWORD_FIELD}
    Element Should Be Visible           ${SIGNIN_BUTTON}
    Log    ✅ Login page loaded successfully


Fill Login Form
    [Documentation]    Fill the login form with given credentials.
    [Arguments]        ${username}    ${password}
    Wait Until Element Is Visible    ${USERNAME_FIELD}    timeout=5s
    Clear Element Text               ${USERNAME_FIELD}
    Input Text                       ${USERNAME_FIELD}    ${username}
    Clear Element Text               ${PASSWORD_FIELD}
    Input Text                       ${PASSWORD_FIELD}    ${password}
    Log    ✅ Login form filled for user: ${username}


Click Sign In Button
    [Documentation]    Click the Sign In button.
    Wait Until Element Is Visible    ${SIGNIN_BUTTON}    timeout=5s
    Wait Until Element Is Enabled    ${SIGNIN_BUTTON}    timeout=5s
    Click Element                    ${SIGNIN_BUTTON}
    Log    ✅ Sign In button clicked


Perform Login
    [Documentation]    Perform a complete login action.
    [Arguments]        ${username}    ${password}
    Verify Login Page Is Loaded
    Fill Login Form    ${username}    ${password}
    Click Sign In Button


# =============================================================
# WELCOME PAGE (Dashboard VEX)
# =============================================================

Verify Welcome Page Is Displayed
    [Documentation]    Verify that the welcome/dashboard page is displayed.
    Wait Until Location Contains         /welcome          timeout=15s
    Wait Until Page Contains Element     css=.banner-card  timeout=15s
    Log    ✅ Welcome page displayed successfully


Verify Welcome Message Contains
    [Documentation]    Verify that welcome page contains expected user info.
    [Arguments]        ${expected_text}
    Wait Until Page Contains    ${expected_text}    timeout=15s
    Page Should Contain         ${expected_text}
    Log    ✅ Welcome page contains expected text


Click Logout Button
    [Documentation]    Click the Logout action on the welcome page.
    Wait Until Page Contains Element     css=.action-logout    timeout=10s
    
    Execute JavaScript    document.querySelector('.action-logout').scrollIntoView(true);
    Sleep    0.5s
    Execute JavaScript    document.querySelector('.action-logout').click();
    
    Sleep    1.5s    reason=Wait for navigation after logout
    Log    ✅ Logout clicked successfully


Verify Redirected To Login
    [Documentation]    Verify that user is redirected back to login page.
    Wait Until Location Contains         /login             timeout=15s
    Wait Until Page Contains Element     ${USERNAME_FIELD}  timeout=10s
    Log    ✅ Redirected to login page


# =============================================================
# ERROR HANDLING
# =============================================================

Verify Error Message Is Displayed
    [Documentation]    Verify that an error message is shown on the login page.
    [Arguments]        ${expected_error_text}=Invalid
    Wait Until Page Contains    ${expected_error_text}    timeout=10s
    Log    ✅ Error message displayed as expected: ${expected_error_text}


# =============================================================
# UTILITIES
# =============================================================

Take Screenshot With Name
    [Documentation]    Take a screenshot with a descriptive name.
    [Arguments]        ${name}
    ${timestamp}=      Get Time    epoch
    Capture Page Screenshot    ${name}_${timestamp}.png
    Log    📸 Screenshot saved: ${name}_${timestamp}.png