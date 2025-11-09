#!/usr/bin/env python3
"""
Comprehensive Test Runner for Stardew Valley Dashboard Advanced Filtering System

Runs Python unit tests and Playwright integration tests, generates a detailed report.
"""

import sys
import time
import subprocess
from pathlib import Path
from collections import defaultdict

class TestRunner:
    def __init__(self):
        self.results = {
            'python': {'passed': [], 'failed': [], 'errors': []},
            'playwright': {'passed': [], 'failed': [], 'errors': []}
        }
        self.start_time = None
        self.end_time = None

    def run_python_tests(self):
        """Run Python unit tests using pytest"""
        print("\n" + "="*70)
        print("PHASE 1: PYTHON UNIT TESTS")
        print("="*70 + "\n")

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short',
                 '-k', 'not playwright', '--color=yes'],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )

            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            # Parse pytest output
            self._parse_pytest_output(result.stdout, 'python')

            return result.returncode == 0

        except FileNotFoundError:
            print("❌ pytest not found. Install with: pip install pytest")
            return False
        except Exception as e:
            print(f"❌ Error running Python tests: {e}")
            self.results['python']['errors'].append(str(e))
            return False

    def run_playwright_tests(self):
        """Run Playwright integration tests"""
        print("\n" + "="*70)
        print("PHASE 2: PLAYWRIGHT INTEGRATION TESTS")
        print("="*70 + "\n")

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', 'tests/test_integration_playwright.py',
                 '-v', '--tb=short', '--color=yes'],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )

            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            # Parse pytest output
            self._parse_pytest_output(result.stdout, 'playwright')

            return result.returncode == 0

        except Exception as e:
            print(f"❌ Error running Playwright tests: {e}")
            self.results['playwright']['errors'].append(str(e))
            return False

    def _parse_pytest_output(self, output, category):
        """Parse pytest output to extract test results"""
        lines = output.split('\n')
        for line in lines:
            if 'PASSED' in line:
                test_name = line.split('::')[1].split(' ')[0] if '::' in line else 'unknown'
                self.results[category]['passed'].append(test_name)
            elif 'FAILED' in line:
                test_name = line.split('::')[1].split(' ')[0] if '::' in line else 'unknown'
                self.results[category]['failed'].append(test_name)

    def generate_report(self):
        """Generate comprehensive test report"""
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time

        print("\n" + "="*70)
        print("TEST EXECUTION SUMMARY")
        print("="*70 + "\n")

        total_passed = len(self.results['python']['passed']) + len(self.results['playwright']['passed'])
        total_failed = len(self.results['python']['failed']) + len(self.results['playwright']['failed'])
        total_errors = len(self.results['python']['errors']) + len(self.results['playwright']['errors'])
        total_tests = total_passed + total_failed + total_errors

        # Python Tests Summary
        print("PYTHON UNIT TESTS")
        print(f"   [PASS] {len(self.results['python']['passed'])}")
        print(f"   [FAIL] {len(self.results['python']['failed'])}")
        print(f"   [ERROR] {len(self.results['python']['errors'])}")

        # Playwright Tests Summary
        print(f"\nPLAYWRIGHT INTEGRATION TESTS")
        print(f"   [PASS] {len(self.results['playwright']['passed'])}")
        print(f"   [FAIL] {len(self.results['playwright']['failed'])}")
        print(f"   [ERROR] {len(self.results['playwright']['errors'])}")

        # Overall Summary
        print(f"\n{'='*70}")
        print(f"TOTAL: {total_passed}/{total_tests} tests passed")
        print(f"Execution Time: {execution_time:.2f} seconds")
        print(f"{'='*70}\n")

        # Failed Tests Detail
        if total_failed > 0:
            print("\n[FAILED TESTS]:\n")
            if self.results['python']['failed']:
                print("  Python Unit Tests:")
                for test in self.results['python']['failed']:
                    print(f"    - {test}")
            if self.results['playwright']['failed']:
                print("  Playwright Integration Tests:")
                for test in self.results['playwright']['failed']:
                    print(f"    - {test}")

        # Errors Detail
        if total_errors > 0:
            print("\n[ERRORS]:\n")
            for error in self.results['python']['errors'] + self.results['playwright']['errors']:
                print(f"    - {error}")

        # Success/Failure Status
        if total_failed == 0 and total_errors == 0:
            print("\n[SUCCESS] ALL TESTS PASSED!\n")
            return 0
        else:
            print("\n[FAILURE] SOME TESTS FAILED\n")
            return 1

    def run(self):
        """Run all tests and generate report"""
        print("\n" + "="*70)
        print("STARDEW VALLEY DASHBOARD - ADVANCED FILTERING TEST SUITE")
        print("="*70)

        self.start_time = time.time()

        # Run Python tests
        python_success = self.run_python_tests()

        # Run Playwright tests
        playwright_success = self.run_playwright_tests()

        # Generate report
        exit_code = self.generate_report()

        return exit_code


if __name__ == '__main__':
    runner = TestRunner()
    exit_code = runner.run()
    sys.exit(exit_code)
