# Flask-Builder Experiment

A sandbox for exploring and building web applications with [Flask-AppBuilder (FAB)](https://flask-appbuilder.readthedocs.io/), a rapid application development framework built on Flask and SQLAlchemy that provides automated CRUD views, role-based security (RBAC), REST APIs, and Bootstrap-themed UIs.

This repository serves as a hands-on experimentation ground for FAB patterns, including Domain-Driven Design (DDD) modeling, Master-Detail views, custom dashboards, state-machine workflows, and polymorphic model structures.

---

## Applications

### REQMan — Enterprise Requirements Management System

A full-featured requirements tracking application built with Flask-AppBuilder. REQMan supports multi-project requirement definitions, version lifecycle governance (Draft → In Review → Approved → Baselined), multi-perspective requirement views, satisfaction assertions, release baselines, and a reviewer inbox dashboard.

See the **[REQMan documentation →](./reqman/README.md)** for setup instructions, architecture details, and feature overview.

---

## Repository Structure

```
flaskbuilder-experiment/
├── reqman/            # Requirements Management application (FAB)
│   ├── app/           # App factory, models, views, APIs, templates
│   ├── config.py      # FAB & Flask configuration
│   ├── run.py         # Development entry point
│   └── seed.py        # Sample data seeder
├── docs/              # Architecture & planning documents
├── .github/           # CI workflows & Copilot instructions
└── LICENSE            # MIT License
```

---

## Getting Started

Each application in this repository has its own setup guide. Quick-start for REQMan:

```bash
cd reqman
pip install -r requirements.txt
flask fab create-admin
export SEED_USER=[user name]
python seed.py
flask run
```

Refer to the individual application READMEs for detailed instructions.

---

## License

Distributed under the [MIT License](./LICENSE).