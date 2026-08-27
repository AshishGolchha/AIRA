import sys
from app import create_app
from app.services.monitoring_runner import MonitoringRunner


def main():
    """CLI entry point for executing one scheduled monitoring cycle."""
    app = create_app()
    with app.app_context():
        runner = MonitoringRunner()
        result = runner.run()
        status = result.get("status")
        print(f"AIRA Monitoring Cycle Completed. Status: {status}")
        print(f"Result Summary: {result}")

        # Exit 0 on completed, partial_failure, or skipped; exit 1 on total failure
        if status in ("completed", "partial_failure", "skipped"):
            sys.exit(0)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
