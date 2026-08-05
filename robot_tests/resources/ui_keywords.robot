*** Settings ***
Documentation     UI keywords for KPIT Auth Platform frontend tests.
...               These keywords interact with the Angular frontend
...               via Selenium.
Library           SeleniumLibrary
Library           String

Resource          variables.robot


*** Keywords ***

# =============================================================
# BROWSER MANAGEMENT
# =============================================================

Open Application In Browser
    [Documentation]    Open the application in a browser with Chrome options
    ...                to disable password save popups and notifications.
    
    # Créer les options Chrome pour désactiver les popups
    ${chrome_options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    Call Method           ${chrome_options}    add_argument    --disable-notifications
    Call Method           ${chrome_options}    add_argument    --disable-popup-blocking
    Call Method           ${chrome_options}    add_argument    --disable-infobars
    Call Method           ${chrome_options}    add_argument    --disable-save-password-bubble
    
    # Préférences avancées pour désactiver le password manager
    ${prefs}=             Create Dictionary
    ...                   credentials_enable_service=${False}
    ...                   profile.password_manager_enabled=${False}
    ...                   profile.password_manager_leak_detection=${False}
    Call Method           ${chrome_options}    add_experimental_option    prefs    ${prefs}
    
    # Ouvrir le navigateur avec les options
    Create Webdriver      Chrome    options=${chrome_options}
    Go To                 ${LOGIN_URL}
    Maximize Browser Window
    Set Selenium Implicit Wait    ${IMPLICIT_WAIT}
    Set Selenium Speed    0.2s

Close Application Browser
    [Documentation]    Close the browser and cleanup.
    Close All Browsers


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
    Log    ✅ Login form filled with username: ${username}


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
# WELCOME PAGE
# =============================================================

Verify Welcome Page Is Displayed
    [Documentation]    Verify that the welcome page is displayed.
    Wait Until Location Is    ${WELCOME_URL}    timeout=10s
    Wait Until Page Contains Element    ${WELCOME_TITLE}    timeout=5s
    Element Should Be Visible    ${WELCOME_TITLE}
    Log    ✅ Welcome page displayed successfully


Verify Welcome Message Contains
    [Documentation]    Verify that welcome page contains expected user info.
    [Arguments]        ${expected_text}
    Wait Until Page Contains    ${expected_text}    timeout=5s
    Page Should Contain    ${expected_text}
    Log    ✅ Welcome page contains: ${expected_text}


Click Logout Button
    [Documentation]    Click the Logout button.
    Wait Until Element Is Visible    ${LOGOUT_BUTTON}    timeout=10s
    Wait Until Element Is Enabled    ${LOGOUT_BUTTON}    timeout=5s
    Sleep    1s    reason=Wait for any animations
    Click Element                    ${LOGOUT_BUTTON}
    Sleep    1s    reason=Wait for navigation
    Log    ✅ Logout button clicked


Verify Redirected To Login
    [Documentation]    Verify that user is redirected back to login page.
    Wait Until Location Contains    /login    timeout=10s
    Wait Until Page Contains Element    ${USERNAME_FIELD}    timeout=5s
    Log    ✅ Redirected to login page


# =============================================================
# ERROR HANDLING
# =============================================================

Verify Error Message Is Displayed
    [Documentation]    Verify that an error message is shown on the login page.
    [Arguments]        ${expected_error_text}=Invalid
    Wait Until Element Is Visible    ${ERROR_MESSAGE}    timeout=5s
    Element Should Be Visible    ${ERROR_MESSAGE}
    Element Should Contain    ${ERROR_MESSAGE}    ${expected_error_text}
    Log    ✅ Error message displayed: ${expected_error_text}


# =============================================================
# UTILITIES
# =============================================================

Take Screenshot With Name
    [Documentation]    Take a screenshot with a descriptive name.
    [Arguments]        ${name}
    ${timestamp}=      Get Time    epoch
    Capture Page Screenshot    ${name}_${timestamp}.png
    Log    📸 Screenshot saved: ${name}_${timestamp}.png