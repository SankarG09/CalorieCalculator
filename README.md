# Daily calorie calculator

Responsive Flask + SQLite calorie calculator and food diary. It estimates resting energy with Mifflin–St Jeor, estimates maintenance calories from an activity multiplier, and estimates maintenance needs. It includes sample foods, custom food entries, daily calorie/protein totals, and a daily goal. The diary is local to this installation and is not account-based.

## Run locally (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
$env:SECRET_KEY = 'replace-with-a-long-random-secret'
.\.venv\Scripts\python app.py
```

Open http://127.0.0.1:8000. The database is created at `data/calories.db`.

The result is a general estimate for adults ages 19–78, not an individualized medical recommendation. The Mifflin–St Jeor formula was derived from healthy adults ages 19–78 ([original study](https://pubmed.ncbi.nlm.nih.gov/2305711/)). Needs vary. Consult a qualified clinician or dietitian for personalized advice. Sample food nutrition and servings are approximate.

## Project files

- `app.py`, `catalog.py`: API, calorie calculations and sample foods.
- `templates/`, `static/`: responsive user interface and illustrations.
- `tests/`: calculator, validation and diary API test suite.
- `scripts/`: backup, packaging, smoke-check and cloud setup helpers.
- `infra/`, `pipelines/`, `azure-pipelines.yml`: optional Azure deployment scaffolding.

Azure deployment is opt-in and requires a configured federated service connection and Terraform backend. No cloud resources are created by running the app locally. Review `docs/pipeline.md` and Azure costs before intentionally applying infrastructure. The Terraform sample uses a single App Service instance with SQLite; it is not suitable for horizontal scaling.
