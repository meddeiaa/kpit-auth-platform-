"""
Robot Framework Parser.

Ce module parse les fichiers .robot pour extraire les Test Cases
et leurs métadonnées (nom, documentation, tags, etc.).

Utilisé par les endpoints API pour lister les tests disponibles.
"""
import os
import re
from typing import List, Dict, Optional
from pathlib import Path


class RobotFrameworkParser:
    """
    Parser pour les fichiers Robot Framework (.robot).
    
    Cette classe lit les fichiers .robot d'un dossier et extrait
    les informations des Test Cases.
    """
    
    def __init__(self, suites_directory: str):
        """
        Initialise le parser avec le chemin du dossier des suites.
        
        Args:
            suites_directory (str): Chemin absolu vers le dossier
                                    contenant les fichiers .robot
        """
        self.suites_directory = Path(suites_directory)
        
        if not self.suites_directory.exists():
            raise FileNotFoundError(
                f"Directory not found: {suites_directory}"
            )
    
    def get_all_suites(self) -> List[Dict]:
        """
        Récupère la liste de tous les fichiers .robot dans le dossier.
        
        Returns:
            List[Dict]: Liste des suites avec leurs informations
                       [
                         {
                           "file_name": "01_health_tests.robot",
                           "file_path": "/path/to/file",
                           "test_cases_count": 2
                         },
                         ...
                       ]
        """
        suites = []
        
        # Parcourir tous les fichiers .robot du dossier
        for robot_file in sorted(self.suites_directory.glob("*.robot")):
            
            # Parser le fichier pour compter les test cases
            test_cases = self.parse_file(str(robot_file))
            
            suite_info = {
                "file_name": robot_file.name,
                "file_path": str(robot_file),
                "test_cases_count": len(test_cases)
            }
            
            suites.append(suite_info)
        
        return suites
    
    def get_all_test_cases(self) -> List[Dict]:
        """
        Récupère TOUS les test cases de TOUS les fichiers.
        
        Returns:
            List[Dict]: Liste complète des test cases
        """
        all_test_cases = []
        
        for robot_file in sorted(self.suites_directory.glob("*.robot")):
            test_cases = self.parse_file(str(robot_file))
            all_test_cases.extend(test_cases)
        
        return all_test_cases
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """
        Parse un fichier .robot et extrait ses test cases.
        
        Args:
            file_path (str): Chemin vers le fichier .robot
        
        Returns:
            List[Dict]: Liste des test cases avec leurs métadonnées
        """
        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            return []
        
        # Lire le contenu du fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraire le nom du fichier (sans le chemin)
        file_name = os.path.basename(file_path)
        
        # Parser le contenu
        test_cases = self._extract_test_cases(content, file_name)
        
        return test_cases
    
    def _extract_test_cases(self, content: str, file_name: str) -> List[Dict]:
        """
        Extrait les test cases du contenu d'un fichier.
        
        Args:
            content (str): Contenu du fichier .robot
            file_name (str): Nom du fichier (pour référence)
        
        Returns:
            List[Dict]: Liste des test cases parsés
        """
        test_cases = []
        
        # Trouver la section *** Test Cases ***
        test_cases_section = self._get_test_cases_section(content)
        
        if not test_cases_section:
            return []
        
        # Séparer les test cases individuels
        # Un test case commence par un nom qui n'est PAS indenté
        # (les étapes du test SONT indentées)
        
        # Regex : trouve les blocs qui commencent en début de ligne
        # (pas d'espace au début) et NE sont PAS des commentaires
        test_blocks = re.split(r'\n(?=\S)', test_cases_section)
        
        for block in test_blocks:
            # Ignorer les blocs vides ou les commentaires
            block = block.strip()
            if not block or block.startswith('#') or block.startswith('*'):
                continue
            
            # Parser le test case
            test_case = self._parse_single_test_case(block, file_name)
            
            if test_case:
                test_cases.append(test_case)
        
        return test_cases
    
    def _get_test_cases_section(self, content: str) -> str:
        """
        Extrait la section *** Test Cases *** du contenu.
        
        Args:
            content (str): Contenu complet du fichier
        
        Returns:
            str: Contenu de la section Test Cases, ou "" si absente
        """
        # Regex pour trouver la section *** Test Cases ***
        pattern = r'\*\*\*\s*Test\s*Cases\s*\*\*\*(.*?)(?=\*\*\*|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _parse_single_test_case(self, block: str, file_name: str) -> Optional[Dict]:
        """
        Parse un seul test case et extrait ses informations.
        
        Args:
            block (str): Bloc de texte contenant un test case
            file_name (str): Nom du fichier (pour référence)
        
        Returns:
            Optional[Dict]: Dictionnaire avec les infos du test case,
                          ou None si le parsing échoue
        """
        lines = block.split('\n')
        
        if not lines:
            return None
        
        # La première ligne est le nom du test case
        test_name_line = lines[0].strip()
        
        if not test_name_line:
            return None
        
        # Extraire l'ID (ex: "TC-201") s'il existe
        test_id = self._extract_test_id(test_name_line)
        
        # Extraire le nom complet du test
        test_name = test_name_line
        
        # Initialiser les autres champs
        documentation = ""
        tags = []
        steps_count = 0
        
        # Parcourir les lignes suivantes
        i = 1
        while i < len(lines):
            line = lines[i].strip()
            
            # Ignorer les lignes vides
            if not line:
                i += 1
                continue
            
            # Extraire la documentation
            if line.startswith('[Documentation]'):
                doc_content = line.replace('[Documentation]', '').strip()
                documentation = doc_content
                
                # Gérer les documentations multi-lignes (avec ...)
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith('...'):
                    continuation = lines[j].strip().replace('...', '').strip()
                    documentation += " " + continuation
                    j += 1
                i = j
                continue
            
            # Extraire les tags
            if line.startswith('[Tags]'):
                tags_content = line.replace('[Tags]', '').strip()
                # Séparer par les espaces multiples ou tabulations
                tags = [t.strip() for t in re.split(r'\s{2,}|\t', tags_content) if t.strip()]
                i += 1
                continue
            
            # Ignorer les autres directives entre crochets
            if line.startswith('['):
                i += 1
                continue
            
            # Compter les étapes (lignes qui ne sont ni des directives, ni des commentaires)
            if line and not line.startswith('#'):
                steps_count += 1
            
            i += 1
        
        # Construire le dictionnaire du test case
        return {
            "id": test_id,
            "name": test_name,
            "documentation": documentation,
            "tags": tags,
            "steps_count": steps_count,
            "file_name": file_name
        }
    
    def _extract_test_id(self, test_name_line: str) -> str:
        """
        Extrait l'ID du test s'il existe (format : TC-XXX).
        
        Args:
            test_name_line (str): Première ligne du test case
        
        Returns:
            str: ID du test (ex: "TC-201") ou "" si absent
        """
        # Regex pour trouver TC-XXX au début
        match = re.match(r'^(TC-\d+)', test_name_line)
        
        if match:
            return match.group(1)
        
        return ""


# ============================================
# FONCTION UTILITAIRE
# ============================================

def get_default_parser() -> RobotFrameworkParser:
    """
    Retourne un parser configuré avec le chemin par défaut.
    
    Le chemin par défaut est : robot_tests/suites/
    (relatif à la racine du projet)
    
    Returns:
        RobotFrameworkParser: Parser initialisé
    """
    # Chemin vers robot_tests/suites/
    # backend/ → ../../robot_tests/suites/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
    suites_path = os.path.join(project_root, 'robot_tests', 'suites')
    
    return RobotFrameworkParser(suites_path)