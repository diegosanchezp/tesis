import argparse

def parse_test_data_args():
    """
    Parse common args for test data files
    """
    # Beging parser setup
    parser = argparse.ArgumentParser(
        description="Reset database script"
    )

    parser.add_argument(
        "--action",
        help="Delete uploaded data or create it",
        choices=["create", "delete"],
        default="create",
    )

    args = parser.parse_args()

    return args
