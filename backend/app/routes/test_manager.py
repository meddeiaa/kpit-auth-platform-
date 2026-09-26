"""
Routes du Test Manager.

Layer 1 — SECURITY+ :
- AuthN : @jwt_required()
- AuthZ : @roles_required(...) selon la matrice admin / tester / viewer
"""
import os
from flask import request, send_from_directory
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from app.services.robot_parser import get_default_parser
from app.services.robot_runner import get_default_runner
from app.services.async_robot_runner import get_async_runner
from app.services.robot_file_manager import get_file_manager
from app.utils.decorators import roles_required


test_ns = Namespace(
    'tests',
    description='Test Management - List, Run and Manage Robot Framework tests'
)

run_request_model = test_ns.model('RunTestsRequest', {
    'test_names': fields.List(fields.String, description='Tests to run', example=['TC-001 ...']),
    'suite_file': fields.String(description='Suite file', example='02_auth_tests.robot'),
    'include_tags': fields.List(fields.String, example=['smoke']),
    'exclude_tags': fields.List(fields.String, example=['ui']),
})

test_case_model = test_ns.model('TestCaseRequest', {
    'name': fields.String(required=True, description='Test name'),
    'documentation': fields.String(description='Description'),
    'tags': fields.List(fields.String, description='Tags'),
})


def _results_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
    return os.path.join(project_root, 'robot_tests', 'results')


# ============================================
# LECTURE — admin, tester, viewer
# ============================================

@test_ns.route('/suites')
class TestSuitesList(Resource):
    @test_ns.doc('list_suites')
    @jwt_required()
    @roles_required('admin', 'tester', 'viewer')
    def get(self):
        try:
            suites = get_default_parser().get_all_suites()
            return {'success': True, 'count': len(suites), 'suites': suites}, 200
        except FileNotFoundError as e:
            return {'success': False, 'error': f'Suites directory not found: {str(e)}'}, 404
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500


@test_ns.route('/cases')
class TestCasesList(Resource):
    @test_ns.doc('list_test_cases')
    @jwt_required()
    @roles_required('admin', 'tester', 'viewer')
    def get(self):
        try:
            test_cases = get_default_parser().get_all_test_cases()
            total_tags = set()
            for tc in test_cases:
                total_tags.update(tc.get('tags', []))
            return {
                'success': True,
                'count': len(test_cases),
                'available_tags': sorted(list(total_tags)),
                'test_cases': test_cases,
            }, 200
        except FileNotFoundError as e:
            return {'success': False, 'error': str(e)}, 404
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500


@test_ns.route('/cases/<string:suite_name>')
class TestCasesBySuite(Resource):
    @test_ns.doc('list_test_cases_by_suite')
    @jwt_required()
    @roles_required('admin', 'tester', 'viewer')
    def get(self, suite_name):
        try:
            parser = get_default_parser()
            file_path = os.path.join(str(parser.suites_directory), suite_name)
            test_cases = parser.parse_file(file_path)
            return {
                'success': True,
                'suite': suite_name,
                'count': len(test_cases),
                'test_cases': test_cases,
            }, 200
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500


# ============================================
# EXÉCUTION — admin, tester
# ============================================

@test_ns.route('/run')
class RunTests(Resource):
    @test_ns.expect(run_request_model, validate=False)
    @test_ns.doc('run_tests')
    @jwt_required()
    @roles_required('admin', 'tester')
    def post(self):
        data = request.get_json() or {}
        try:
            result = get_default_runner().run_tests(
                test_names=data.get('test_names'),
                suite_file=data.get('suite_file'),
                include_tags=data.get('include_tags'),
                exclude_tags=data.get('exclude_tags'),
            )
            return result, (200 if result.get('success') else 207)
        except Exception as e:
            return {
                'success': False, 'error': str(e),
                'total': 0, 'passed': 0, 'failed': 0, 'tests': [],
            }, 500


@test_ns.route('/run/async')
class RunTestsAsync(Resource):
    @test_ns.expect(run_request_model, validate=False)
    @test_ns.doc('run_tests_async')
    @jwt_required()
    @roles_required('admin', 'tester')
    def post(self):
        data = request.get_json() or {}
        try:
            job_id = get_async_runner().start_job(
                test_names=data.get('test_names'),
                suite_file=data.get('suite_file'),
                include_tags=data.get('include_tags'),
                exclude_tags=data.get('exclude_tags'),
            )
            return {
                'success': True,
                'job_id': job_id,
                'message': 'Test execution started',
            }, 202
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500


@test_ns.route('/run/status/<string:job_id>')
class RunTestsStatus(Resource):
    @test_ns.doc('get_job_status')
    @jwt_required()
    @roles_required('admin', 'tester', 'viewer')
    def get(self, job_id):
        try:
            job = get_async_runner().get_job_status(job_id)
            if not job:
                return {'success': False, 'error': 'Job not found'}, 404
            return {'success': True, 'job': job}, 200
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500


@test_ns.route('/run/cancel/<string:job_id>')
class CancelTestsAsync(Resource):
    @test_ns.doc('cancel_job')
    @jwt_required()
    @roles_required('admin', 'tester')
    def post(self, job_id):
        try:
            success = get_async_runner().cancel_job(job_id)
            if success:
                return {'success': True, 'message': 'Job cancelled successfully'}, 200
            return {'success': False, 'error': 'Job not found or already finished'}, 404
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500


# ============================================
# RAPPORTS — admin, tester, viewer
# (UNE seule classe report — évite l'écrasement)
# ============================================

@test_ns.route('/report')
@test_ns.route('/report.html')
class TestReport(Resource):
    @test_ns.doc('get_report')
    @jwt_required()
    @roles_required('admin', 'tester', 'viewer')
    def get(self):
        results_dir = _results_dir()
        path = os.path.join(results_dir, 'report.html')
        if os.path.exists(path):
            return send_from_directory(results_dir, 'report.html', mimetype='text/html')
        return {'success': False, 'error': 'No report available. Run tests first.'}, 404


@test_ns.route('/log')
@test_ns.route('/log.html')
class TestLogFile(Resource):
    @test_ns.doc('get_log')
    @jwt_required()
    @roles_required('admin', 'tester', 'viewer')
    def get(self):
        results_dir = _results_dir()
        path = os.path.join(results_dir, 'log.html')
        if os.path.exists(path):
            return send_from_directory(results_dir, 'log.html', mimetype='text/html')
        return {'success': False, 'error': 'No log file available. Run tests first.'}, 404


@test_ns.route('/artifacts/<string:filename>')
class TestArtifacts(Resource):
    @test_ns.doc('get_artifact')
    @jwt_required()
    @roles_required('admin', 'tester', 'viewer')
    def get(self, filename):
        if '..' in filename or filename.startswith('/'):
            return {'success': False, 'error': 'Invalid filename'}, 400
        results_dir = _results_dir()
        target = filename if '.' in filename else f'{filename}.png'
        if os.path.exists(os.path.join(results_dir, target)):
            return send_from_directory(results_dir, target)
        return {'success': False, 'error': f'File {target} not found'}, 404


# ============================================
# CRUD .robot — admin only
# ============================================

@test_ns.route('/suites/<string:suite_name>/cases')
class TestCaseAdd(Resource):
    @test_ns.expect(test_case_model)
    @test_ns.doc('add_test_case')
    @jwt_required()
    @roles_required('admin')
    def post(self, suite_name):
        data = request.get_json() or {}
        success, message, new_test = get_file_manager().add_test_case(suite_name, data)
        if success:
            return {'success': True, 'message': message, 'test': new_test}, 201
        return {'success': False, 'error': message}, 400


@test_ns.route('/suites/<string:suite_name>/cases/<string:test_id>')
class TestCaseManage(Resource):
    @test_ns.expect(test_case_model)
    @test_ns.doc('update_test_case')
    @jwt_required()
    @roles_required('admin')
    def put(self, suite_name, test_id):
        data = request.get_json() or {}
        success, message = get_file_manager().update_test_case(suite_name, test_id, data)
        if success:
            return {'success': True, 'message': message}, 200
        return {'success': False, 'error': message}, 404

    @test_ns.doc('delete_test_case')
    @jwt_required()
    @roles_required('admin')
    def delete(self, suite_name, test_id):
        success, message = get_file_manager().delete_test_case(suite_name, test_id)
        if success:
            return {'success': True, 'message': message}, 200
        return {'success': False, 'error': message}, 404