*** Settings ***
Documentation     Global variables for KPIT Auth Platform tests.
...               These variables can be imported in any test suite.


*** Variables ***

# =============================================================
# API CONFIGURATION
# =============================================================
${BASE_URL}                http://localhost:5000/api
${SESSION_NAME}            kpit_api_session


# =============================================================
# ENDPOINTS
# =============================================================
${HEALTH_ENDPOINT}         /health
${REGISTER_ENDPOINT}       /auth/register
${LOGIN_ENDPOINT}          /auth/login


# =============================================================
# TEST USER : AHMED (Admin)
# =============================================================
${AHMED_FIRST_NAME}        Ahmed
${AHMED_LAST_NAME}         Ben Ali
${AHMED_EMAIL}             ahmed@kpit.com
${AHMED_LOGIN}             ahmed
${AHMED_PASSWORD}          ahmed123
${AHMED_ROLE}              admin


# =============================================================
# TEST USER : SARA (Tester)
# =============================================================
${SARA_FIRST_NAME}         Sara
${SARA_LAST_NAME}          Trabelsi
${SARA_EMAIL}              sara@kpit.com
${SARA_LOGIN}              sara
${SARA_PASSWORD}           sara2026
${SARA_ROLE}               tester


# =============================================================
# TEST USER : ALI (Viewer)
# =============================================================
${ALI_FIRST_NAME}          Ali
${ALI_LAST_NAME}           Jarraya
${ALI_EMAIL}               ali@kpit.com
${ALI_LOGIN}               ali
${ALI_PASSWORD}            ali_secure_pwd
${ALI_ROLE}                viewer


# =============================================================
# EXPECTED STATUS CODES
# =============================================================
${STATUS_OK}               200
${STATUS_CREATED}          201
${STATUS_BAD_REQUEST}      400
${STATUS_UNAUTHORIZED}     401
${STATUS_FORBIDDEN}        403
${STATUS_NOT_FOUND}        404
${STATUS_CONFLICT}         409
${STATUS_SERVER_ERROR}     500

# =============================================================
# UI CONFIGURATION (Frontend)
# =============================================================
${FRONTEND_URL}            http://localhost:4200
${BROWSER}                 chrome
${IMPLICIT_WAIT}           10s

# =============================================================
# UI SELECTORS (Frontend Elements) - AMÉLIORÉS
# =============================================================

# Login Page URLs
${LOGIN_URL}               ${FRONTEND_URL}/login
${WELCOME_URL}             ${FRONTEND_URL}/welcome

# Login Page Elements
${USERNAME_FIELD}          css=input[formcontrolname="login"]
${PASSWORD_FIELD}          css=input[formcontrolname="password"]
${SIGNIN_BUTTON}           css=button[type="submit"]
${ERROR_MESSAGE}           css=.error-message
${SHOW_PASSWORD_BUTTON}    css=button[mat-icon-button][matSuffix]

# Welcome Page Elements
${WELCOME_TITLE}           css=.welcome-title
${WELCOME_MESSAGE}         css=.welcome-message
${LOGOUT_BUTTON}           xpath=//strong[text()='Logout']/ancestor::div[contains(@class,'action-item')]