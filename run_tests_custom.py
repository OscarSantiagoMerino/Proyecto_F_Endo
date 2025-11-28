import importlib
import sys


def main():
    print("Ejecutando tests desde tests/test_validation.py (sin pytest)")
    try:
        mod = importlib.import_module("tests.test_validation")
    except Exception as e:
        print("Error importando el módulo de tests:", e)
        sys.exit(2)

    tests = [getattr(mod, name) for name in dir(mod) if name.startswith("test_")]
    failures = 0

    for t in tests:
        try:
            t()
            print(f"{t.__name__}: OK")
        except AssertionError as e:
            print(f"{t.__name__}: FAIL -> {e}")
            failures += 1
        except Exception as e:
            print(f"{t.__name__}: ERROR -> {e}")
            failures += 1

    if failures:
        print(f"\n{failures} tests fallaron")
        sys.exit(1)
    else:
        print("\nTodos los tests pasaron")
        sys.exit(0)


if __name__ == "__main__":
    main()
