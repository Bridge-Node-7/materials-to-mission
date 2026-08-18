.PHONY: install test coverage evidence check demo release clean

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements-dev.txt
	python -m pip install --no-deps --no-build-isolation -e .

test:
	python -m pytest

coverage:
	python -m coverage run -m pytest
	python -m coverage report

evidence:
	python scripts/check_repo.py --update-evidence

check:
	python scripts/check_repo.py

demo:
	python -m materials_to_mission validate examples/synthetic-critical-material-pathway/case.json --public
	python -m materials_to_mission render examples/synthetic-critical-material-pathway/case.json --output build/decision-passport.md

release:
	python scripts/build_release.py

clean:
	rm -rf build dist .pytest_cache .coverage htmlcov
