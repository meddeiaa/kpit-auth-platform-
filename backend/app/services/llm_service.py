import os
import re
import urllib.request
import urllib.error
import json
import logging

logger = logging.getLogger(__name__)

# =====================================================================
# OFFICIAL PROMPTS & DICTIONARIES
# =====================================================================

SYSTEM_PROMPT_UI = """Vous êtes un expert Robot Framework pour l'application Web KPIT Auth Platform (suite '03_ui_tests.robot').

CHAQUE CAS DE TEST DOIT OBLIGATOIREMENT CONTENIR LES EN-TÊTES :
- [Documentation]    Description claire du test
- [Tags]             ai-generated    ui    <tag_spécifique>

INSTRUCTIONS STRICTES SELON LE TYPE DE TEST :

1. TEST D'ÉCHEC / ERREUR DE CONNEXION (si la demande contient: "échec", "fail", "mauvais", "wrong", "invalide", "erreur") :
   - Utilisez Perform Login avec un mauvais mot de passe (ex: WrongPass123).
   - Vérifiez le message d'erreur : Verify Error Message Is Displayed    Invalid username or password
   - Tags : [Tags]    ai-generated    ui    security    error
   - Ne JAMAIS inclure "Verify Welcome Page Is Displayed" dans un test d'échec !

2. TEST DE CONNEXION RÉUSSIE :
   - Perform Login    <username>    <password>
   - Verify Welcome Page Is Displayed
   - Verify Welcome Message Contains    Welcome back, <FIRST_NAME>
   - Tags : [Tags]    ai-generated    ui    smoke

3. TEST DE DÉCONNEXION (logout) :
   - Click Logout Button
   - Verify Redirected To Login
   - Tags : [Tags]    ai-generated    ui    logout

MOTS-CLÉS UI VALIDES (UTILISER EXCLUSIVEMENT CEUX-CI) :
- Perform Login    <username>    <password>    (EXACTEMENT 2 ARGUMENTS)
- Verify Welcome Page Is Displayed
- Verify Welcome Message Contains    Welcome back, <FIRST_NAME>
- Verify Error Message Is Displayed    Invalid username or password
- Click Logout Button
- Verify Redirected To Login

COMPTES UTILISATEURS :
- Sara  : ${SARA_LOGIN} / ${SARA_PASSWORD} / ${SARA_FIRST_NAME}
- Ahmed : ${AHMED_LOGIN} / ${AHMED_PASSWORD} / ${AHMED_FIRST_NAME}
- Ali   : ${ALI_LOGIN} / ${ALI_PASSWORD} / ${ALI_FIRST_NAME}

STRUCTURE STRICTE D'UN CAS DE TEST :
<Test_Case_Name>
    [Documentation]    <description>
    [Tags]             ai-generated    ui
    <Keywords>
"""

SYSTEM_PROMPT_API = """Vous êtes un expert Robot Framework pour l'API REST KPIT Auth Platform.

CHAQUE CAS DE TEST DOIT OBLIGATOIREMENT CONTENIR :
- [Documentation]    Description du test API
- [Tags]             ai-generated    api    <tag_spécifique>

MOTS-CLÉS API OFFICIELS :
- Create API Session
- Register New User With Random Data
- Login Should Succeed    <login>    <password>
- Login Should Fail With Unauthorized    <login>    <password>
- Verify Response Is Success    ${response}
- Verify User Data    ${response}    <expected_login>    <expected_email>

VARIABLES COMPTES :
- ${AHMED_LOGIN}, ${AHMED_PASSWORD}, ${AHMED_EMAIL}
- ${SARA_LOGIN}, ${SARA_PASSWORD}, ${SARA_EMAIL}
- ${ALI_LOGIN}, ${ALI_PASSWORD}, ${ALI_EMAIL}

STRUCTURE STRICTE D'UN CAS DE TEST :
<Test_Case_Name>
    [Documentation]    <description>
    [Tags]             ai-generated    api
    <Keywords>
"""


class LLMService:

    @classmethod
    def _get_available_models(cls, api_key: str) -> list:
        """Découvre dynamiquement les modèles textuels d'I.A. actifs sur Groq API."""
        default_active_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ]
        try:
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/models",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                discovered = []
                for m in data.get('data', []):
                    m_id = m.get('id', '')
                    if any(name in m_id.lower() for name in ['llama', 'mixtral', 'gemma', 'qwen']):
                        if not any(bad in m_id.lower() for bad in ['guard', 'whisper', 'safetensors', 'embed']):
                            discovered.append(m_id)

                if discovered:
                    logger.info(f"Groq active text models discovered: {discovered}")
                    return discovered
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode('utf-8', errors='ignore')
            logger.warning(f"Groq GET /models HTTP {e.code}: {err_msg}")
        except Exception as e:
            logger.warning(f"Could not fetch Groq models dynamically: {e}")

        return default_active_models

    @classmethod
    def _sanitize_and_fix_robot_code(cls, code: str, target_suite: str, requirement: str = "") -> str:
        """
        POST-PROCESSEUR AUTOMATIQUE (GUARDRAIL) :
        1. Nettoie le Markdown.
        2. Assure la présence de [Documentation] et [Tags].
        3. Corrige la syntaxe et les mots-clés.
        """
        code = re.sub(r'```robotframework|```robot|```', '', code).strip()
        is_ui_suite = '03_ui' in target_suite or 'ui' in target_suite.lower()

        lines = code.splitlines()
        cleaned_lines = []
        has_tags = False
        has_doc = False

        for line in lines:
            stripped = line.strip()

            if '[Tags]' in line:
                has_tags = True
            if '[Documentation]' in line:
                has_doc = True

            if is_ui_suite:
                # Supprimer ouvertures/fermetures manuelles de navigateur
                if any(stripped.startswith(cmd) for cmd in ["Open Browser", "Close Browser", "Maximize Browser Window", "[Teardown]  Close Browser", "[Teardown]    Close Browser"]):
                    continue

                line = re.sub(r'\bPerform Logout\b', 'Click Logout Button', line)
                line = re.sub(r'\bVerify Home Page Is Displayed\b', 'Verify Welcome Page Is Displayed', line)
                line = re.sub(r'\bVerify Dashboard Is Displayed\b', 'Verify Welcome Page Is Displayed', line)

                if 'Perform Login' in line:
                    parts = [p for p in re.split(r'\s{2,}', line.strip()) if p]
                    if len(parts) > 3:
                        line = f"    Perform Login    {parts[1]}    {parts[2]}"

            cleaned_lines.append(line)

        # INJECTION AUTOMATIQUE DE TAGS ET DOCUMENTATION SI MANQUANTS
        final_lines = []
        default_tag = "ui" if is_ui_suite else "api"

        for line in cleaned_lines:
            final_lines.append(line)
            # Détection du titre du test (ligne non indentée après *** Test Cases ***)
            if line.strip() and not line.startswith(' ') and not line.startswith('\t') and not line.startswith('*') and not line.startswith('#'):
                if not has_doc:
                    doc_desc = requirement if requirement else "Test généré par IA"
                    final_lines.append(f"    [Documentation]    {doc_desc}")
                    has_doc = True
                if not has_tags:
                    final_lines.append(f"    [Tags]             ai-generated    {default_tag}    auto")
                    has_tags = True

        final_code = "\n".join(final_lines)

        if is_ui_suite:
            final_code = re.sub(
                r'(Click Logout Button\n\s*Verify Redirected To Login)\n\s*Verify Welcome Page Is Displayed',
                r'\1',
                final_code
            )
            if 'Verify Error Message Is Displayed' in final_code:
                res_lines = []
                for l in final_code.splitlines():
                    if 'Verify Welcome Page Is Displayed' in l or 'Verify Welcome Message Contains' in l:
                        continue
                    res_lines.append(l)
                final_code = "\n".join(res_lines)

        return final_code

    @classmethod
    def generate_robot_test(cls, requirement: str, test_name: str = "TC-AI Generated Test", target_suite: str = "03_ui_tests.robot") -> dict:
        groq_key = os.getenv('GROQ_API_KEY', '').strip()
        provider_used = "fallback_engine"

        if '03_ui' in target_suite or 'ui' in target_suite.lower():
            sys_prompt = SYSTEM_PROMPT_UI
        else:
            sys_prompt = SYSTEM_PROMPT_API

        user_prompt = f"Besoin utilisateur : {requirement}\n"
        if test_name:
            user_prompt += f"Nom exact du cas de test (Test Case Title) : {test_name}\n"

        raw_code = None

        if groq_key:
            available_models = cls._get_available_models(groq_key)
            
            for model in available_models:
                try:
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    payload = json.dumps({
                        "model": model,
                        "messages": [
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.1
                    }).encode('utf-8')

                    req = urllib.request.Request(
                        url,
                        data=payload,
                        headers={
                            "Authorization": f"Bearer {groq_key}",
                            "Content-Type": "application/json",
                            "User-Agent": "Mozilla/5.0"
                        },
                        method="POST"
                    )

                    with urllib.request.urlopen(req, timeout=12) as resp:
                        res_data = json.loads(resp.read().decode('utf-8'))
                        raw_code = res_data['choices'][0]['message']['content']
                        provider_used = f"groq ({model})"
                        logger.info(f"Successfully generated script via Groq model: {model}")
                        break

                except urllib.error.HTTPError as e:
                    err_body = e.read().decode('utf-8', errors='ignore')
                    logger.warning(f"Groq API call failed for model {model} (HTTP {e.code}): {err_body}")
                except Exception as e:
                    logger.warning(f"Groq API call failed for model {model}: {e}")

        if not raw_code:
            raw_code = cls._generate_fallback(requirement, test_name, target_suite)
            provider_used = "fallback_engine"

        # Pass through Post-Processor with requirement context for tags injection
        fixed_code = cls._sanitize_and_fix_robot_code(raw_code, target_suite, requirement)

        return {
            "generated_code": fixed_code,
            "code": fixed_code,
            "provider": provider_used
        }

    @classmethod
    def _generate_fallback(cls, requirement: str, test_name: str, target_suite: str) -> str:
        tc_title = test_name if test_name else "TC-AI Generated Test Case"
        req_lower = requirement.lower()

        if "sara" in req_lower:
            user_var, pass_var, name_var = "${SARA_LOGIN}", "${SARA_PASSWORD}", "${SARA_FIRST_NAME}"
        elif "ali" in req_lower:
            user_var, pass_var, name_var = "${ALI_LOGIN}", "${ALI_PASSWORD}", "${ALI_FIRST_NAME}"
        else:
            user_var, pass_var, name_var = "${AHMED_LOGIN}", "${AHMED_PASSWORD}", "${AHMED_FIRST_NAME}"

        is_error = any(w in req_lower for w in ["échec", "echec", "fail", "wrong", "mauvais", "erreur", "invalid", "invalide"])

        if is_error:
            wrong_pass = "WrongPass123"
            return f"""*** Test Cases ***
{tc_title}
    [Documentation]    Test généré automatiquement pour : {requirement}
    [Tags]             ai-generated    ui    security    error
    Perform Login    {user_var}    {wrong_pass}
    Verify Error Message Is Displayed    Invalid username or password
"""
        else:
            return f"""*** Test Cases ***
{tc_title}
    [Documentation]    Test généré automatiquement pour : {requirement}
    [Tags]             ai-generated    ui    smoke
    Perform Login    {user_var}    {pass_var}
    Verify Welcome Page Is Displayed
    Verify Welcome Message Contains    Welcome back, {name_var}
"""