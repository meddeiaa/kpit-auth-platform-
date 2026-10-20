*** Settings ***
Resource    ${EXECDIR}/tests/resources/ui_keywords.robot
Resource    ${EXECDIR}/tests/resources/variables.robot

*** Variables ***
${BASE_URL}    http://localhost:4200/login
${INVALID_PASSWORD}    WrongPass123
${ERROR_SELECTOR}    css=.error-message
${EXPECTED_ERROR}    Invalid username or password.

*** Test Cases ***
TC_AI_1792359295893
    [Documentation]    Vérifier que si l'utilisateur entre le login sara et un mauvais mot de passe, un message d'erreur est affiché.
    Open Chrome Fullscreen    ${BASE_URL}
    Input Text    id=username    sara
    Input Text    id=password    ${INVALID_PASSWORD}
    Click Button    button[type="submit"]
    Wait Until Element Is Visible    ${ERROR_SELECTOR}    timeout=5s
    Element Text Should Be    ${ERROR_SELECTOR}    ${EXPECTED_ERROR}
    Close Browser Window