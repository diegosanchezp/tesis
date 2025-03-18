"""
Just a little script to get the column names from an Excel file for the django ORM, which are a bunch (53)
"""

import pandas as pd
import argparse


def main(file_path):
    # Specify the name of the sheet you want to read
    sheet_name = "Hoja1"

    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # List the columns of the sheet
    columns = df.columns.tolist()

    print(f"number of columns = {len(columns)}")

    for column in columns:
        # lowercase and substitute whitespaces with underscore "_"
        colum_lowercase_name = column.lower().replace(" ", "_")
        col_model = f"""
            {colum_lowercase_name} = models.CharField(
                max_length=255,
                verbose_name=_("{column}"),
                help_text=_(""),
            )
        """
        # col_model = f"{colum_lowercase_name} = \"\","
        print(col_model)


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Extract column names from an Excel file."
    )
    parser.add_argument("file_path", type=str, help="Path to the Excel file")

    # Parse arguments
    args = parser.parse_args()

    # Call main with the provided file path
    main(args.file_path)
