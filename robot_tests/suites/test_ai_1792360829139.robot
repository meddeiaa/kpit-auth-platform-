*** Settings ***
Resource    ${EXECDIR}/tests/resources/ui_keywords.robot
Resource    ${EXECDIR}/tests/resources/variables.robot
Library    SeleniumLibrary

*** Variables ***
${BASE_URL}    http://localhost:4200/login
${USERNAME}    ahmed
${PASSWORD}    ahmed123

*** Test Cases ***
TC_AI_1792360817681
    [Documentation]    Vérifier que la tentative de connexion avec l'utilisateur ahmed affiche la carte de vérification 2FA et demande le code OTP à 6 chiffres.
    Open Chrome Fullscreen    ${BASE_URL}
    Input Text    id=username    ${USERNAME}
    Input Text    id=password    ${PASSWORD}
    Click Button    css=button[type="submit"]
    Wait Until Element Is Visible    css=div.2fa-card    timeout=10s
    Element Should Be Visible    css=div.2fa-card
    Wait Until Element Is Visible    css=input[id="otp"]    timeout=10s
    Element Should Be Visible    css=input[id="otp"]
    ${placeholder}=    Get Element Attribute    css=input[id="otp"]    placeholder
    Should Match Regexp    ${placeholder}    \\d{6}
    Close Browser Window