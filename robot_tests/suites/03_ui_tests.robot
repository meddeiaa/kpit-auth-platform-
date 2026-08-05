*** Settings ***
Documentation     UI tests for KPIT Auth Platform frontend.
...               These tests interact with the Angular application
...               via a real browser (Selenium).

Resource          ../resources/variables.robot
Resource          ../resources/ui_keywords.robot

# Setup et Teardown appliqués à chaque test
Test Setup        Open Application In Browser
Test Teardown     Close Application Browser


*** Test Cases ***

# =============================================================
# LOGIN PAGE - UI ELEMENTS
# =============================================================

TC-501 Login Page Should Display All Required Elements
    [Documentation]    Verify that the login page has all necessary elements.
    [Tags]             ui    login    smoke
    
    Verify Login Page Is Loaded
    
    # Vérifier tous les éléments visuels
    Page Should Contain     KPIT Auth Platform
    Page Should Contain     Sign in to your account
    Page Should Contain     Username
    Page Should Contain     Password
    
    Log    ✅ All login page elements are visible


# =============================================================
# LOGIN - SUCCESS SCENARIO
# =============================================================

TC-502 User Can Login With Valid Credentials
    [Documentation]    Verify that a user can login successfully with valid credentials.
    [Tags]             ui    login    success    smoke    critical
    
    # Étape 1 : Login
    Perform Login    ${AHMED_LOGIN}    ${AHMED_PASSWORD}
    
    # Étape 2 : Vérifier la redirection vers Welcome
    Verify Welcome Page Is Displayed
    
    # Étape 3 : Vérifier les informations utilisateur
    Verify Welcome Message Contains    Welcome, ${AHMED_FIRST_NAME} ${AHMED_LAST_NAME}
    Verify Welcome Message Contains    ${AHMED_EMAIL}
    Verify Welcome Message Contains    ${AHMED_LOGIN}


# =============================================================
# LOGIN - ERROR SCENARIOS
# =============================================================

TC-503 Login Should Fail With Wrong Password
    [Documentation]    Verify that login fails when password is incorrect.
    [Tags]             ui    login    error    security
    
    Perform Login    ${AHMED_LOGIN}    WrongPassword123
    
    # Vérifier qu'on reste sur la page login
    Location Should Be    ${LOGIN_URL}
    
    # Vérifier le message d'erreur
    Verify Error Message Is Displayed    Invalid username or password


TC-504 Login Should Fail With Unknown User
    [Documentation]    Verify that login fails when username doesn't exist.
    [Tags]             ui    login    error    security
    
    Perform Login    nonexistent_user    anyPassword123
    
    Location Should Be    ${LOGIN_URL}
    Verify Error Message Is Displayed    Invalid username or password


# =============================================================
# LOGOUT
# =============================================================

TC-601 User Can Logout Successfully
    [Documentation]    Verify that a logged-in user can logout.
    [Tags]             ui    logout    smoke
    
    # Étape 1 : Login
    Perform Login    ${AHMED_LOGIN}    ${AHMED_PASSWORD}
    Verify Welcome Page Is Displayed
    
    # Étape 2 : Logout
    Click Logout Button
    
    # Étape 3 : Vérifier la redirection
    Verify Redirected To Login


# =============================================================
# COMPLETE E2E JOURNEY
# =============================================================

TC-701 Complete User Journey Login-Welcome-Logout
    [Documentation]    Test the complete user journey from login to logout.
    [Tags]             ui    e2e    smoke    critical
    
    # ÉTAPE 1 : Vérifier la page login
    Verify Login Page Is Loaded
    
    # ÉTAPE 2 : Se connecter
    Fill Login Form    ${AHMED_LOGIN}    ${AHMED_PASSWORD}
    Click Sign In Button
    
    # ÉTAPE 3 : Vérifier Welcome
    Verify Welcome Page Is Displayed
    Verify Welcome Message Contains    Welcome, ${AHMED_FIRST_NAME}
    
    # ÉTAPE 4 : Se déconnecter
    Click Logout Button
    
    # ÉTAPE 5 : Vérifier retour à Login
    Verify Redirected To Login
    Verify Login Page Is Loaded
    
    Log    🎉 Complete E2E journey successful!


# =============================================================
# DIFFERENT USERS
# =============================================================

TC-801 Sara (Tester Role) Can Login
    [Documentation]    Verify that Sara (with tester role) can login.
    [Tags]             ui    login    roles    regression
    
    Perform Login    ${SARA_LOGIN}    ${SARA_PASSWORD}
    Verify Welcome Page Is Displayed
    Verify Welcome Message Contains    Welcome, ${SARA_FIRST_NAME}
    Verify Welcome Message Contains    TESTER


TC-802 Ali (Viewer Role) Can Login
    [Documentation]    Verify that Ali (with viewer role) can login.
    [Tags]             ui    login    roles    regression
    
    Perform Login    ${ALI_LOGIN}    ${ALI_PASSWORD}
    Verify Welcome Page Is Displayed
    Verify Welcome Message Contains    Welcome, ${ALI_FIRST_NAME}
    Verify Welcome Message Contains    VIEWER