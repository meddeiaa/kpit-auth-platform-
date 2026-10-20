*** Settings ***
Resource    ${EXECDIR}/tests/resources/ui_keywords.robot
Resource    ${EXECDIR}/tests/resources/variables.robot

*** Variables ***

*** Test Cases ***
TC_AI_1792358912980
    Open Chrome Fullscreen
    Go To    ${BASE_URL}
    Input Text    id=username    sara
    Input Text    id=password    wrongpassword
    Click Button    button[type="submit"]
    Page Should Contain Element    .error-message
    Close Browser Window