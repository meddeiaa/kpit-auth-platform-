"""
Script de test pour le RobotFrameworkParser.

Exécute ce script pour vérifier que le parser fonctionne :
    python test_parser.py
"""
from app.services.robot_parser import get_default_parser
import json


def main():
    """Test le parser Robot Framework."""
    
    print("=" * 60)
    print("🤖 TEST DU ROBOT FRAMEWORK PARSER")
    print("=" * 60)
    print()
    
    # Créer le parser
    print("📁 Initialisation du parser...")
    parser = get_default_parser()
    print(f"   Dossier : {parser.suites_directory}")
    print()
    
    # ==========================================
    # TEST 1 : Lister les suites
    # ==========================================
    print("=" * 60)
    print("📊 TEST 1 : Liste des Suites")
    print("=" * 60)
    suites = parser.get_all_suites()
    print(f"Nombre de suites trouvées : {len(suites)}")
    print()
    for suite in suites:
        print(f"   📄 {suite['file_name']}")
        print(f"      Test Cases : {suite['test_cases_count']}")
    print()
    
    # ==========================================
    # TEST 2 : Lister tous les Test Cases
    # ==========================================
    print("=" * 60)
    print("📋 TEST 2 : Tous les Test Cases")
    print("=" * 60)
    all_tests = parser.get_all_test_cases()
    print(f"Nombre total de Test Cases : {len(all_tests)}")
    print()
    
    # Afficher les 3 premiers pour vérifier
    print("Aperçu (3 premiers) :")
    print()
    for i, test in enumerate(all_tests[:3], 1):
        print(f"   Test #{i} :")
        print(f"   ├── ID       : {test['id']}")
        print(f"   ├── Name     : {test['name']}")
        print(f"   ├── Doc      : {test['documentation'][:60]}...")
        print(f"   ├── Tags     : {test['tags']}")
        print(f"   ├── Steps    : {test['steps_count']}")
        print(f"   └── File     : {test['file_name']}")
        print()
    
    # ==========================================
    # TEST 3 : Export JSON (pour visualiser)
    # ==========================================
    print("=" * 60)
    print("💾 TEST 3 : Export JSON")
    print("=" * 60)
    print("Sauvegarde dans 'parsed_tests.json'...")
    
    with open('parsed_tests.json', 'w', encoding='utf-8') as f:
        json.dump(all_tests, f, indent=2, ensure_ascii=False)
    
    print("✅ Fichier créé !")
    print()
    
    # ==========================================
    # RÉSUMÉ
    # ==========================================
    print("=" * 60)
    print("✅ TESTS TERMINÉS AVEC SUCCÈS !")
    print("=" * 60)
    print(f"   Total suites  : {len(suites)}")
    print(f"   Total tests   : {len(all_tests)}")
    print()


if __name__ == "__main__":
    main()