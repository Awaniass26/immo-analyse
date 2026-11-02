"""Exécute le pipeline complet, du module 1 au module 2."""
from MODULE01.src.main import main as executer_module01
from MODULE02.src.run_pipeline import main as executer_module02


def main() -> None:
    executer_module01()
    executer_module02()


if __name__ == "__main__":
    main()
