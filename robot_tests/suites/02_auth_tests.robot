*** Settings ***
Documentation     Authentication tests for KPIT Auth Platform API.
...               These tests verify Register and Login functionality
...               including all success cases and error scenarios.
Library           RequestsLibrary
Library           Collections
Library           String


*** Variables ***
${BASE_URL}           http://localhost:5000/api
${SESSION_NAME}       auth_session

# Test user data
${VALID_FIRST_NAME}   Test
${VALID_LAST_NAME}    User
${VALID_EMAIL}        test.user@kpit.com
${VALID_LOGIN}        testuser
${VALID_PASSWORD}     testpass123
${VALID_ROLE}         viewer

# Existing user (created in previous tests)
${AHMED_LOGIN}        ahmed
${AHMED_PASSWORD}     ahmed123
${AHMED_EMAIL}        ahmed@kpit.com


*** Test Cases ***

# =============================================================
# REGISTER - SUCCESS SCENARIOS
# =============================================================

TC-101 Register New User With Valid Data Should Succeed
    [Documentation]    Verify that a new user can be created with all valid fields.
    [Tags]             auth    register    success    smoke
    
    # Créer une session HTTP
    Create Session     ${SESSION_NAME}    ${BASE_URL}
    
    # Préparer les données (avec un email unique)
    ${unique_id}=      Generate Random String    5    [NUMBERS]
    ${user_data}=      Create Dictionary
    ...                first_name=${VALID_FIRST_NAME}
    ...                last_name=${VALID_LAST_NAME}
    ...                email=user${unique_id}@kpit.com
    ...                login=user${unique_id}
    ...                password=${VALID_PASSWORD}
    ...                role=${VALID_ROLE}
    
    # Envoyer la requête POST
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                /auth/register
    ...                json=${user_data}
    ...                expected_status=201
    
    # Vérifier la réponse
    Should Be Equal As Numbers    ${response.status_code}    201
    
    ${json}=           Set Variable    ${response.json()}
    Should Be Equal    ${json}[success]    ${True}
    Should Contain     ${json}[message]    User created successfully
    
    # Vérifier les données du user créé
    ${user}=           Set Variable    ${json}[user]
    Should Be Equal    ${user}[first_name]    ${VALID_FIRST_NAME}
    Should Be Equal    ${user}[last_name]     ${VALID_LAST_NAME}
    Should Be Equal    ${user}[role]          ${VALID_ROLE}
    
    Log    ✅ User created successfully with ID: ${user}[id]


# =============================================================
# REGISTER - ERROR SCENARIOS
# =============================================================

TC-102 Register With Duplicate Email Should Fail
    [Documentation]    Verify that registering with an existing email returns 409.
    [Tags]             auth    register    error    regression
    
    Create Session     ${SESSION_NAME}    ${BASE_URL}
    
    # Tenter de créer un user avec l'email d'Ahmed (déjà existant)
    ${user_data}=      Create Dictionary
    ...                first_name=Duplicate
    ...                last_name=Email
    ...                email=${AHMED_EMAIL}
    ...                login=uniquelogin123
    ...                password=somepass
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                /auth/register
    ...                json=${user_data}
    ...                expected_status=409
    
    Should Be Equal As Numbers    ${response.status_code}    409
    
    ${json}=           Set Variable    ${response.json()}
    Should Be Equal    ${json}[success]    ${False}
    Should Contain     ${json}[error]      Email already registered
    
    Log    ✅ Duplicate email correctly rejected


TC-103 Register With Duplicate Login Should Fail
    [Documentation]    Verify that registering with an existing login returns 409.
    [Tags]             auth    register    error    regression
    
    Create Session     ${SESSION_NAME}    ${BASE_URL}
    
    ${user_data}=      Create Dictionary
    ...                first_name=Duplicate
    ...                last_name=Login
    ...                email=uniqueemail@kpit.com
    ...                login=${AHMED_LOGIN}
    ...                password=somepass
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                /auth/register
    ...                json=${user_data}
    ...                expected_status=409
    
    Should Be Equal As Numbers    ${response.status_code}    409
    
    ${json}=           Set Variable    ${response.json()}
    Should Contain     ${json}[error]    Login already taken
    
    Log    ✅ Duplicate login correctly rejected


TC-104 Register Without Email Should Fail
    [Documentation]    Verify that missing email field returns 400.
    [Tags]             auth    register    error    validation
    
    Create Session     ${SESSION_NAME}    ${BASE_URL}
    
    ${user_data}=      Create Dictionary
    ...                first_name=Missing
    ...                last_name=Email
    ...                login=noemail
    ...                password=somepass
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                /auth/register
    ...                json=${user_data}
    ...                expected_status=400
    
    Should Be Equal As Numbers    ${response.status_code}    400
    
    ${json}=           Set Variable    ${response.json()}
    Should Contain     ${json}[error]    email
    
    Log    ✅ Missing email correctly rejected


TC-105 Register With Empty Body Should Fail
    [Documentation]    Verify that empty JSON body returns 400.
    [Tags]             auth    register    error    validation
    
    Create Session     ${SESSION_NAME}    ${BASE_URL}
    
    ${empty_data}=     Create Dictionary
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                /auth/register
    ...                json=${empty_data}
    ...                expected_status=400
    
    Should Be Equal As Numbers    ${response.status_code}    400
    
    Log    ✅ Empty body correctly rejected


# =============================================================
# LOGIN - SUCCESS SCENARIOS
# =============================================================

TC-201 Login With Valid Credentials Should Succeed
    [Documentation]    Verify that a user can login with correct credentials.
    [Tags]             auth    login    success    smoke
    
    Create Session     ${SESSION_NAME}    ${BASE_URL}
    
    ${credentials}=    Create Dictionary
    ...                login=${AHMED_LOGIN}
    ...                password=${AHMED_PASSWORD}
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                /auth/login
    ...                json=${credentials}
    ...                expected_status=200
    
    Should Be Equal As Numbers    ${response.status_code}    200
    
    ${json}=           Set Variable    ${response.json()}
    Should Be Equal    ${json}[success]    ${True}
    Should Contain     ${json}[message]    Welcome
    Should Contain     ${json}[message]    Ahmed
    
    # Vérifier les infos du user
    ${user}=           Set Variable    ${json}[user]
    Should Be Equal    ${user}[login]    ${AHMED_LOGIN}
    Should Be Equal    ${user}[email]    ${AHMED_EMAIL}
    
    Log    ✅ Login successful for user: ${user}[login]


# =============================================================
# LOGIN - ERROR SCENARIOS
# =============================================================

TC-202 Login With Wrong Password Should Fail
    [Documentation]    Verify that wrong password returns 401.
    [Tags]             auth    login    error    security
    
    Create Session     ${SESSION_NAME}    ${BASE_URL}
    
    ${credentials}=    Create Dictionary
    ...                login=${AHMED_LOGIN}
    ...                password=WrongPassword123
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                /auth/login
    ...                json=${credentials}
    ...                expected_status=401
    
    Should Be Equal As Numbers    ${response.status_code}    401
    
    ${json}=           Set Variable    ${response.json()}
    Should Be Equal    ${json}[success]    ${False}
    Should Contain     ${json}[error]      Invalid username or password
    
    Log    ✅ Wrong password correctly rejected


TC-203 Login With Unknown User Should Fail
    [Documentation]    Verify that unknown username returns 401.
    [Tags]             auth    login    error    security
    
    Create Session     ${SESSION_NAME}    ${BASE_URL}
    
    ${credentials}=    Create Dictionary
    ...                login=nonexistent_user_xyz
    ...                password=anypassword
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                /auth/login
    ...                json=${credentials}
    ...                expected_status=401
    
    Should Be Equal As Numbers    ${response.status_code}    401
    
    ${json}=           Set Variable    ${response.json()}
    Should Contain     ${json}[error]    Invalid username or password
    
    Log    ✅ Unknown user correctly rejected


TC-204 Login Without Password Should Fail
    [Documentation]    Verify that missing password returns 400.
    [Tags]             auth    login    error    validation
    
    Create Session     ${SESSION_NAME}    ${BASE_URL}
    
    ${credentials}=    Create Dictionary
    ...                login=${AHMED_LOGIN}
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                /auth/login
    ...                json=${credentials}
    ...                expected_status=400
    
    Should Be Equal As Numbers    ${response.status_code}    400
    
    ${json}=           Set Variable    ${response.json()}
    Should Contain     ${json}[error]    required
    
    Log    ✅ Missing password correctly rejected


# =============================================================
# CASE SENSITIVITY TESTS (Demandé par l'encadrant)
# =============================================================

TC-301 Login With Uppercase Username Should Fail
    [Documentation]    Verify that usernames are case-sensitive.
    ...                Login "AHMED" should fail even if "ahmed" exists.
    [Tags]             auth    login    case-sensitive    supervisor-request
    
    Create Session     ${SESSION_NAME}    ${BASE_URL}
    
    ${credentials}=    Create Dictionary
    ...                login=AHMED
    ...                password=${AHMED_PASSWORD}
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                /auth/login
    ...                json=${credentials}
    ...                expected_status=401
    
    Should Be Equal As Numbers    ${response.status_code}    401
    Log    ✅ Uppercase username correctly rejected (case-sensitive)


TC-302 Login With Uppercase Password Should Fail
    [Documentation]    Verify that passwords are case-sensitive.
    [Tags]             auth    login    case-sensitive    supervisor-request
    
    Create Session     ${SESSION_NAME}    ${BASE_URL}
    
    ${credentials}=    Create Dictionary
    ...                login=${AHMED_LOGIN}
    ...                password=AHMED123
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                /auth/login
    ...                json=${credentials}
    ...                expected_status=401
    
    Should Be Equal As Numbers    ${response.status_code}    401
    Log    ✅ Uppercase password correctly rejected (case-sensitive)


# =============================================================
# INPUT ORDER TESTS (Demandé par l'encadrant)
# =============================================================

TC-401 Login With Login First Then Password Should Succeed
    [Documentation]    Verify that JSON order doesn't matter (login first).
    [Tags]             auth    login    input-order    supervisor-request
    
    Create Session     ${SESSION_NAME}    ${BASE_URL}
    
    # Ordre : login PUIS password
    ${credentials}=    Create Dictionary
    ...                login=${AHMED_LOGIN}
    ...                password=${AHMED_PASSWORD}
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                /auth/login
    ...                json=${credentials}
    ...                expected_status=200
    
    Should Be Equal As Numbers    ${response.status_code}    200
    Log    ✅ Login OK with order: login then password


TC-402 Login With Password First Then Login Should Succeed
    [Documentation]    Verify that JSON order doesn't matter (password first).
    [Tags]             auth    login    input-order    supervisor-request
    
    Create Session     ${SESSION_NAME}    ${BASE_URL}
    
    # Ordre : password PUIS login
    ${credentials}=    Create Dictionary
    ...                password=${AHMED_PASSWORD}
    ...                login=${AHMED_LOGIN}
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                /auth/login
    ...                json=${credentials}
    ...                expected_status=200
    
    Should Be Equal As Numbers    ${response.status_code}    200
    Log    ✅ Login OK with order: password then login