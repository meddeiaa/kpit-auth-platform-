*** Settings ***
Documentation     Common keywords for KPIT Auth Platform tests.
...               Reusable keywords to avoid code duplication.
Library           RequestsLibrary
Library           Collections
Library           String

Resource          variables.robot


*** Keywords ***

# =============================================================
# SESSION MANAGEMENT
# =============================================================

Create API Session
    [Documentation]    Create an HTTP session to the API.
    ...                Uses global BASE_URL and SESSION_NAME variables.
    Create Session     ${SESSION_NAME}    ${BASE_URL}


# =============================================================
# HEALTH CHECK
# =============================================================

Check API Is Healthy
    [Documentation]    Verify that the API health endpoint responds correctly.
    Create API Session
    ${response}=       GET On Session    ${SESSION_NAME}    ${HEALTH_ENDPOINT}
    Should Be Equal As Numbers    ${response.status_code}    ${STATUS_OK}
    Should Be Equal    ${response.json()}[status]    healthy
    RETURN           ${response}


# =============================================================
# USER REGISTRATION
# =============================================================

Register New User
    [Documentation]    Register a new user with the given data.
    ...                Returns the response object.
    [Arguments]        ${first_name}    ${last_name}    ${email}
    ...                ${login}    ${password}    ${role}=viewer
    ...                ${expected_status}=201
    
    Create API Session
    
    ${user_data}=      Create Dictionary
    ...                first_name=${first_name}
    ...                last_name=${last_name}
    ...                email=${email}
    ...                login=${login}
    ...                password=${password}
    ...                role=${role}
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                ${REGISTER_ENDPOINT}
    ...                json=${user_data}
    ...                expected_status=${expected_status}
    
    RETURN           ${response}


Register New User With Random Data
    [Documentation]    Register a new user with random unique data.
    ...                Useful for tests that need to create fresh users.
    [Arguments]        ${role}=viewer
    
    ${unique_id}=      Generate Random String    5    [NUMBERS]
    ${response}=       Register New User
    ...                first_name=Random
    ...                last_name=User
    ...                email=random${unique_id}@kpit.com
    ...                login=random${unique_id}
    ...                password=RandomPass123
    ...                role=${role}
    
    RETURN           ${response}


Register Should Fail With Duplicate Email
    [Documentation]    Attempt to register with an existing email.
    ...                Verifies that the API returns 409 Conflict.
    [Arguments]        ${existing_email}
    
    ${response}=       Register New User
    ...                first_name=Duplicate
    ...                last_name=Email
    ...                email=${existing_email}
    ...                login=uniquelogin_${existing_email}
    ...                password=somepass123
    ...                expected_status=${STATUS_CONFLICT}
    
    Should Be Equal As Numbers    ${response.status_code}    ${STATUS_CONFLICT}
    Should Contain     ${response.json()}[error]    Email already registered
    RETURN           ${response}


# =============================================================
# USER LOGIN
# =============================================================

Login User
    [Documentation]    Login with given credentials.
    ...                Returns the response object.
    [Arguments]        ${login}    ${password}    ${expected_status}=200
    
    Create API Session
    
    ${credentials}=    Create Dictionary
    ...                login=${login}
    ...                password=${password}
    
    ${response}=       POST On Session
    ...                ${SESSION_NAME}
    ...                ${LOGIN_ENDPOINT}
    ...                json=${credentials}
    ...                expected_status=${expected_status}
    
    RETURN           ${response}


Login Should Succeed
    [Documentation]    Login and verify it succeeds (200 OK).
    [Arguments]        ${login}    ${password}
    
    ${response}=       Login User    ${login}    ${password}
    Should Be Equal As Numbers    ${response.status_code}    ${STATUS_OK}
    Should Be Equal    ${response.json()}[success]    ${True}
    Should Contain     ${response.json()}[message]    Welcome
    RETURN           ${response}


Login Should Fail With Unauthorized
    [Documentation]    Login and verify it fails with 401.
    [Arguments]        ${login}    ${password}
    
    ${response}=       Login User    ${login}    ${password}    ${STATUS_UNAUTHORIZED}
    Should Be Equal As Numbers    ${response.status_code}    ${STATUS_UNAUTHORIZED}
    Should Contain     ${response.json()}[error]    Invalid username or password
    RETURN           ${response}


# =============================================================
# RESPONSE VALIDATION
# =============================================================

Verify Response Is Success
    [Documentation]    Verify that a response indicates success.
    [Arguments]        ${response}
    ${json}=           Set Variable    ${response.json()}
    Should Be Equal    ${json}[success]    ${True}
    RETURN           ${json}


Verify Response Is Error
    [Documentation]    Verify that a response indicates an error.
    [Arguments]        ${response}
    ${json}=           Set Variable    ${response.json()}
    Should Be Equal    ${json}[success]    ${False}
    Should Contain     ${json}    error
    RETURN           ${json}


Verify User Data
    [Documentation]    Verify that user data in response matches expected values.
    [Arguments]        ${response}    ${expected_login}    ${expected_email}
    ${json}=           Set Variable    ${response.json()}
    ${user}=           Set Variable    ${json}[user]
    Should Be Equal    ${user}[login]    ${expected_login}
    Should Be Equal    ${user}[email]    ${expected_email}
    RETURN           ${user}