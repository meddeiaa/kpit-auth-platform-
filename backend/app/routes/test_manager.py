"""
Routes du Test Manager.

Ce module expose les endpoints pour :
- Lister les suites et test cases
- Exécuter des tests sélectionnés
- Récupérer les rapports
"""
from flask import request, send_file
from flask_restx import Namespace, Resource, fields

from app.services.robot_parser import get_default_parser
from app.services.robot_runner import get_default_runner
from app.services.async_robot_runner import get_async_runner
from app.services.robot_file_manager import get_file_manager



# ============================================
# NAMESPACE
# ============================================
test_ns = Namespace(
    'tests',
    description='Test Management - List, Run and Manage Robot Framework tests'
)


# ============================================
# MODÈLES SWAGGER
# ============================================
run_request_model = test_ns.model('RunTestsRequest', {
    'test_names': fields.List(
        fields.String,
        description='List of test names to run (empty = run all)',
        example=['TC-001 API Health Check Should Return Healthy Status']
    ),
    'suite_file': fields.String(
        description='Specific suite file to run (optional)',
        example='02_auth_tests.robot'
    ),
    'include_tags': fields.List(
        fields.String,
        description='Only run tests with these tags',
        example=['smoke']
    ),
    'exclude_tags': fields.List(
        fields.String,
        description='Exclude tests with these tags',
        example=['ui']
    )
})
test_case_model = test_ns.model('TestCaseRequest', {
    'name': fields.String(required=True, description='Test name'),
    'documentation': fields.String(description='Test description'),
    'tags': fields.List(fields.String, description='List of tags')
})


# ============================================
# ENDPOINTS : LISTER
# ============================================

@test_ns.route('/suites')
class TestSuitesList(Resource):
    """Liste des fichiers de tests (.robot)."""
    
    @test_ns.doc('list_suites')
    def get(self):
        """
        Récupérer la liste de tous les fichiers .robot.
        
        Retourne les suites avec le nombre de tests dans chacune.
        """
        try:
            parser = get_default_parser()
            suites = parser.get_all_suites()
            
            return {
                'success': True,
                'count': len(suites),
                'suites': suites
            }, 200
            
        except FileNotFoundError as e:
            return {
                'success': False,
                'error': f'Suites directory not found: {str(e)}'
            }, 404
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, 500


@test_ns.route('/cases')
class TestCasesList(Resource):
    """Liste de tous les test cases."""
    
    @test_ns.doc('list_test_cases')
    def get(self):
        """
        Récupérer tous les test cases de toutes les suites.
        
        Retourne les détails de chaque test (ID, nom, tags, etc.)
        """
        try:
            parser = get_default_parser()
            test_cases = parser.get_all_test_cases()
            
            # Calculer des statistiques
            total_tags = set()
            for tc in test_cases:
                total_tags.update(tc.get('tags', []))
            
            return {
                'success': True,
                'count': len(test_cases),
                'available_tags': sorted(list(total_tags)),
                'test_cases': test_cases
            }, 200
            
        except FileNotFoundError as e:
            return {
                'success': False,
                'error': str(e)
            }, 404
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, 500


@test_ns.route('/cases/<string:suite_name>')
class TestCasesBySuite(Resource):
    """Test cases d'une suite spécifique."""
    
    @test_ns.doc('list_test_cases_by_suite')
    def get(self, suite_name):
        """
        Récupérer les test cases d'un fichier .robot spécifique.
        
        Args:
            suite_name: Nom du fichier .robot (ex: 02_auth_tests.robot)
        """
        try:
            parser = get_default_parser()
            
            # Construire le chemin du fichier
            import os
            file_path = os.path.join(
                str(parser.suites_directory),
                suite_name
            )
            
            test_cases = parser.parse_file(file_path)
            
            return {
                'success': True,
                'suite': suite_name,
                'count': len(test_cases),
                'test_cases': test_cases
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, 500


# ============================================
# ENDPOINT : EXÉCUTER
# ============================================

@test_ns.route('/run')
class RunTests(Resource):
    """Exécuter des tests Robot Framework."""
    
    @test_ns.expect(run_request_model, validate=False)
    @test_ns.doc('run_tests')
    def post(self):
        """
        Exécuter des tests Robot Framework sélectionnés.
        
        Si aucun paramètre n'est fourni, TOUS les tests sont exécutés.
        
        Options :
        - test_names : Liste des noms de tests spécifiques
        - suite_file : Fichier .robot spécifique
        - include_tags : Tags à inclure
        - exclude_tags : Tags à exclure
        """
        data = request.get_json() or {}
        
        try:
            runner = get_default_runner()
            
            result = runner.run_tests(
                test_names=data.get('test_names'),
                suite_file=data.get('suite_file'),
                include_tags=data.get('include_tags'),
                exclude_tags=data.get('exclude_tags')
            )
            
            status_code = 200 if result['success'] else 207
            
            return result, status_code
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'total': 0,
                'passed': 0,
                'failed': 0,
                'tests': []
            }, 500


# ============================================
# ENDPOINTS ASYNC : POLLING
# ============================================

@test_ns.route('/run/async')
class RunTestsAsync(Resource):
    """Démarre l'exécution des tests en arrière-plan."""
    
    @test_ns.expect(run_request_model, validate=False)
    @test_ns.doc('run_tests_async')
    def post(self):
        """
        Démarre l'exécution asynchrone des tests.
        Retourne immédiatement un job_id pour suivre la progression.
        """
        data = request.get_json() or {}
        
        try:
            runner = get_async_runner()
            
            job_id = runner.start_job(
                test_names=data.get('test_names'),
                suite_file=data.get('suite_file'),
                include_tags=data.get('include_tags'),
                exclude_tags=data.get('exclude_tags')
            )
            
            return {
                'success': True,
                'job_id': job_id,
                'message': 'Test execution started'
            }, 202  # 202 Accepted
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, 500


@test_ns.route('/run/status/<string:job_id>')
class RunTestsStatus(Resource):
    """Récupère l'état d'un job en cours."""
    
    @test_ns.doc('get_job_status')
    def get(self, job_id):
        """
        Récupère l'état actuel d'un job.
        À appeler en polling toutes les 500ms.
        """
        try:
            runner = get_async_runner()
            job = runner.get_job_status(job_id)
            
            if not job:
                return {
                    'success': False,
                    'error': 'Job not found'
                }, 404
            
            return {
                'success': True,
                'job': job
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }, 500 

# ============================================
# ENDPOINTS : RAPPORTS & LOGS ROBOT
# ============================================

@test_ns.route('/report')
class TestReport(Resource):
    """Servir le rapport synthétique HTML (report.html)."""
    
    @test_ns.doc('get_report')
    def get(self):
        """Retourne le fichier report.html."""
        import os
        from flask import send_from_directory
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
        results_dir = os.path.join(project_root, 'robot_tests', 'results')
        report_path = os.path.join(results_dir, 'report.html')
        
        if os.path.exists(report_path):
            return send_from_directory(results_dir, 'report.html', mimetype='text/html')
        else:
            return {
                'success': False,
                'error': 'No report available. Run tests first.'
            }, 404


# ============================================
# ENDPOINTS : RAPPORTS & LOGS ROBOT (Bi-directionnels)
# ============================================

@test_ns.route('/report')
@test_ns.route('/report.html')
class TestReport(Resource):
    """Servir le rapport synthétique HTML (report.html)."""
    
    @test_ns.doc('get_report')
    def get(self):
        """Retourne le fichier report.html."""
        import os
        from flask import send_from_directory
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
        results_dir = os.path.join(project_root, 'robot_tests', 'results')
        report_path = os.path.join(results_dir, 'report.html')
        
        if os.path.exists(report_path):
            return send_from_directory(results_dir, 'report.html', mimetype='text/html')
        else:
            return {
                'success': False,
                'error': 'No report available. Run tests first.'
            }, 404


@test_ns.route('/log')
@test_ns.route('/log.html')
class TestLogFile(Resource):
    """Servir le journal détaillé pas à pas (log.html)."""
    
    @test_ns.doc('get_log')
    def get(self):
        """Retourne le fichier log.html."""
        import os
        from flask import send_from_directory
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
        results_dir = os.path.join(project_root, 'robot_tests', 'results')
        log_path = os.path.join(results_dir, 'log.html')
        
        if os.path.exists(log_path):
            return send_from_directory(results_dir, 'log.html', mimetype='text/html')
        else:
            return {
                'success': False,
                'error': 'No log file available. Run tests first.'
            }, 404


@test_ns.route('/artifacts/<string:filename>')
@test_ns.route('/<string:filename>.png')
class TestArtifacts(Resource):
    """Servir les fichiers de preuves et screenshots (ex: .png, output.xml)."""
    
    @test_ns.doc('get_artifact')
    def get(self, filename):
        """Retourne un fichier de capture d'écran ou de résultat."""
        import os
        from flask import send_from_directory
        
        # Sécurité : Éviter la traversée de dossiers
        if '..' in filename or filename.startswith('/'):
            return {'success': False, 'error': 'Invalid filename'}, 400
            
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
        results_dir = os.path.join(project_root, 'robot_tests', 'results')
        
        # Ajouter l'extension .png si appelée depuis la route d'extension
        target_file = filename if '.' in filename else f"{filename}.png"
        file_path = os.path.join(results_dir, target_file)
        
        if os.path.exists(file_path):
            return send_from_directory(results_dir, target_file)
        else:
            return {'success': False, 'error': f'File {target_file} not found'}, 404
# ============================================

@test_ns.route('/suites/<string:suite_name>/cases')
class TestCaseAdd(Resource):
    """Ajouter un test case à une suite."""
    
    @test_ns.expect(test_case_model)
    def post(self, suite_name):
        """Ajouter un nouveau test case dans un fichier .robot"""
        data = request.get_json()
        manager = get_file_manager()
        
        success, message, new_test = manager.add_test_case(suite_name, data)
        
        if success:
            return {'success': True, 'message': message, 'test': new_test}, 201
        return {'success': False, 'error': message}, 400


@test_ns.route('/suites/<string:suite_name>/cases/<string:test_id>')
class TestCaseManage(Resource):
    """Modifier ou Supprimer un test case."""
    
    @test_ns.expect(test_case_model)
    def put(self, suite_name, test_id):
        """Modifier (Update) la doc et les tags d'un test case"""
        data = request.get_json()
        manager = get_file_manager()
        
        success, message = manager.update_test_case(suite_name, test_id, data)
        
        if success:
            return {'success': True, 'message': message}, 200
        return {'success': False, 'error': message}, 404

    def delete(self, suite_name, test_id):
        """Supprimer (Delete) un test case du fichier"""
        manager = get_file_manager()
        success, message = manager.delete_test_case(suite_name, test_id)
        
        if success:
            return {'success': True, 'message': message}, 200
        return {'success': False, 'error': message}, 404 

@test_ns.route('/run/cancel/<string:job_id>')
class CancelTestsAsync(Resource):
    """Annuler l'exécution d'un job en cours."""
    
    @test_ns.doc('cancel_job')
    def post(self, job_id):
        try:
            from app.services.async_robot_runner import get_async_runner
            runner = get_async_runner()
            success = runner.cancel_job(job_id)
            
            if success:
                return {'success': True, 'message': 'Job cancelled successfully'}, 200
            
            return {'success': False, 'error': 'Job not found or already finished'}, 404
            
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500