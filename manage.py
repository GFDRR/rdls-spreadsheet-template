import click
import codecs
import csv
import datetime
import json
import os
import requests
import subprocess
import warnings
import xlsxwriter

from ocdskit.mapping_sheet import mapping_sheet
from xlsxwriter.utility import xl_col_to_name

RDLS_SCHEMA_URL = "https://docs.riskdatalibrary.org/en/0__2__0/rdls_schema.json"
RDLS_DOCS_URL = "https://docs.riskdatalibrary.org/"

# https://flatten-tool.readthedocs.io/en/latest/create-template/#all-create-template-options
TRUNCATION_LENGTH = 10
MAIN_SHEET_NAME = "datasets"

COMPONENTS = [
    'hazard',
    'exposure',
    'vulnerability',
    'loss'
]

SHEETS = {
    MAIN_SHEET_NAME: [],
    "attributions": [],
    "sources": [],
    "referenced_by": [],
    "spatial_gazetteer_entries": [],
    "resources": [],
    "hazard_event_sets": [],
    "hazard_event_sets_hazards": [],
    "hazard_event_sets_spatial_gazet": [],
    "hazard_event_sets_events": [],
    "hazard_event_sets_events_disast": [],
    "hazard_event_sets_events_footpr": [],
    "exposure_metrics": [],
    "vulnerabil_cost": [],
    "vulnerabil_spatial_gazetteer_en": [],
    "loss_cost": [],
    "links": []
}

# Colours for related tabs
PALETTE = {
    "hazard": "#148cb4",
    "exposure": "#0ed0a9",
    "vulnerability": "#ffd166",
    "loss": "#ee476f"
}

# https://flatten-tool.readthedocs.io/en/latest/unflatten/#metadata-tab
# https://flatten-tool.readthedocs.io/en/latest/unflatten/#configuration-properties-skip-and-header-rows
META_CONFIG = [
    "#",
    "hashComments"
]

INPUT_ROWS = 1000


def get(url):
    """
    GETs a URL and returns the response. Raises an exception if the status code is not successful.
    """
    response = requests.get(url)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response


def json_dump(filename, data):
    """
    Writes JSON data to the given filename.
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')


def delete_directory_contents(directory_path):
    """
    Deletes the contents of a directory on disk.
    """
    if os.path.isdir(directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


@click.group()
def cli():
    pass


@cli.command()
@click.option('-c',
              '--component',
              type=click.Choice(COMPONENTS, case_sensitive=True)
              )
@click.option('-s',
              '--schema_url',
              default='https://docs.riskdatalibrary.org/en/0__2__0/rdls_schema.json',
              show_default=True
              )
@click.option('-w',
              '--wkt',
              default=True,
              show_default=True)
def create_template(component, schema_url, wkt):

    """
    Create an XLSX template.
    """

    temp_path = '.temp'
    os.makedirs(temp_path, exist_ok=True)

    schema = get(schema_url).json()

    # Remove unneeded components from schema
    if component:
        for key in [key for key in COMPONENTS if key != component]:
            del (schema['properties'][key])

    # Can be removed once https://github.com/GFDRR/rdl-standard/pull/181 is merged
    schema['$defs']['Classification']['properties']['scheme']['codelist'] = "classification_scheme.csv"

    # Generate a temporary CSV template using Flatten Tool
    json_dump(".temp/schema.json", schema)
    command = f"flatten-tool create-template -s {temp_path}/schema.json -f csv -m {MAIN_SHEET_NAME} -o {temp_path} --truncation-length {TRUNCATION_LENGTH}"
    if wkt:
        command = f"{command} --convert-wkt" 
    subprocess.run(command.split(" "))

    # Generate a mapping sheet to use as a source for field metadata
    schema_table = mapping_sheet(schema, include_codelist=True)
    field_metadata = {field["path"]: field for field in schema_table[1]}

    # Create XLSX template
    workbook = xlsxwriter.Workbook(
        f"templates/rdls_template{f'_{component}' if component else ''}.xlsx")

    # Define order, row heights and cell formats for header rows 
    header_rows = {
        "path": {
            "row_height": None,
            "cell_format": workbook.add_format({
                "bold": True,
                "bg_color": "#efefef"})
            },
        "title": {
            "row_height": None,
            "cell_format": workbook.add_format({
                "bg_color": "#efefef"})
            },
        "description": {
            "row_height": 30,
            "cell_format": workbook.add_format({
                "font_size": 8,
                "text_wrap": True,
                "valign": "top",
                "bg_color": "#efefef"
              })
            },
        "required": {
            "row_height": None,
            "cell_format": workbook.add_format({
                "font_size": 8,
                "bg_color": "#efefef"})
            },
        "type": {
            "row_height": None,
            "cell_format": workbook.add_format({
                "font_size": 8,
                "bg_color": "#efefef"})
            },
        "values": {
            "row_height": 30,
            "cell_format": workbook.add_format({
                "font_size": 8,
                "text_wrap": True,
                "valign": "top",
                "bg_color": "#efefef"
              })
            },
        "codelist": {
            "row_height": None,
            "cell_format": workbook.add_format({
                "font_size": 8,
                "font_color": "blue",
                "underline": True,
                "bg_color": "#efefef"})
            },
        "input guidance": {
            "row_height": 50,
            "cell_format": workbook.add_format({
                "font_size": 8,
                "text_wrap": True,
                "valign": "top",
                "bg_color": "#efefef",
                "bottom": 1
              })          
        }
    }

    # Write readme worksheet
    readme_worksheet = workbook.add_worksheet("# README")

    readme_worksheet.write_row(0, 0, ["Risk Data Library Standard spreadsheet template"], workbook.add_format({
              "bold": True,
              "font_size": 18,
              "valign": "top", 
              }))
    readme_worksheet.set_row(0, 30)
    readme_worksheet.write_url(1, 0, "https://github.com/GFDRR/rdls-spreadsheet-template/blob/main/README.md", string="To learn about the structure of the template and how to enter data, read the documentation at https://github.com/GFDRR/rdls-spreadsheet-template/blob/main/README.md.")
    readme_worksheet.set_column(0, 0, 150)

    META_CONFIG.append(f"HeaderRows {len(header_rows)}"),

    # Add header column cell format
    header_col_format = workbook.add_format({
        "bold": True,
        "font_size": 11,
        "font_color": "black",
        "underline": False,
        "bg_color": "#efefef"
        })

    # Generate sheet color mapping based on palette and sheet names
    sheet_colors = {key[:TRUNCATION_LENGTH]: value for key, value in PALETTE.items()}

    # Add input cell formats
    input_format = workbook.add_format({})
    string_format = workbook.add_format({"num_format": "@"})
    date_format = workbook.add_format({"num_format": "yyyy-mm-dd"})
    number_format = workbook.add_format({"num_format": "#,##0.00"})

    # Add worksheet for enum validation
    enum_worksheet = workbook.add_worksheet("# Enums")
    enum_column = 0

    # Add meta worksheet for Flatten Tool configuration properties
    meta_worksheet = workbook.add_worksheet("Meta")
    meta_worksheet.hide()
    meta_worksheet.write_row(0, 0, META_CONFIG)

    filenames = os.listdir(temp_path)
    sheet_names = [filename.split('.')[0] for filename in filenames if filename.split('.')[-1] == "csv"]
    
    # Drop sheets that are not included in Flatten Tool output
    for sheet in [sheet for sheet in SHEETS if sheet not in sheet_names]:
        del SHEETS[sheet]

    for sheet_name in sheet_names:

      # Add missing sheet names
      if sheet_name not in SHEETS:
          warnings.warn(
              f"Found new sheet: {sheet_name}. It will be added to the end of the workbook. You should update SHEETS in manage.py to set its order.")
          SHEETS[sheet_name] = []

      # Read column headers
      file_path = os.path.join(temp_path, f"{sheet_name}.csv")

      with open(file_path, 'r') as f:
          reader = csv.reader(f)

          SHEETS[sheet_name] = next(reader)

    # Add worksheets, field metadata, formatting and data validation
    for sheet_name in SHEETS:
        worksheet = workbook.add_worksheet(sheet_name)
        worksheet.set_tab_color(sheet_colors.get(
            sheet_name.split('_')[0], "#efefef"))
        worksheet.freeze_panes(1, 1)

        # Set row formats
        row = 0
        for row_format in header_rows.values():
            worksheet.set_row(
                row, row_format["row_height"], row_format["cell_format"])
            row += 1

        # Write header column
        worksheet.write_column(
            0, 0, [f"# {row_name}" for row_name in header_rows])
        worksheet.set_column(0, 0, 11, header_col_format)
        column = 1

        for path in SHEETS[sheet_name]:

            # Array indices are omitted from field paths in mapping sheet
            metadata_path = "/".join([part for part in path.split("/")
                                     if part != '0'])

            # Write field metadata as header rows
            data_type = field_metadata[metadata_path]["type"]
            values = field_metadata[metadata_path]["values"]
            codelist = field_metadata[metadata_path]["codelist"]

            # Generate codelist hyperlink formula
            if codelist:
                codelist_name = codelist.split(".")[0]
                codelist_formula = f"""=HYPERLINK("{RDLS_DOCS_URL}/reference/codelists/#{codelist_name.replace("_", "-")}","{codelist_name}")"""
            else:
                codelist_formula = ""

            metadata = {
                "path": path,
                "title": field_metadata[metadata_path]["title"],
                "description": field_metadata[metadata_path]["description"],
                "required": "Required" if field_metadata[metadata_path]["range"][0] == "1" else "",
                "type": data_type,
                "values": values,
                "codelist": codelist_formula
            }

            # Add data input guidance
            if data_type == "array":
                if values[:4] == 'Enum':
                  metadata["input guidance"] = "Select from list or enter multiple values as a semicolon-separated list, e.g. a;b;c. Each value must be a code from the codelist."
                else:
                  metadata["input guidance"] = "Enter multiple values as a semicolon-separated list, e.g. a;b;c. Values must not contain semicolons or commas."
            elif path.split('/')[-1] == 'geometry':
                metadata["input guidance"] = "Enter a well-known text value, e.g. POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10)). For more information on the well-known text representation of geometry, see https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry."
            else:
                metadata["input guidance"] = ""

            worksheet.write_column(0, column, [metadata[row_name] for row_name in header_rows])

            # Set cell format for input rows
            if sheet_name == "links":
                cell_format = workbook.add_format({})
            elif values == 'date':
                cell_format = date_format
            elif data_type == 'number':
                cell_format = number_format
            elif data_type in ['string', 'array', 'object']:
                cell_format = string_format
            else:
                cell_format = input_format
            
            # Write input cells, use formulae to populate links sheet
            input_row_ref = len(header_rows) + 1
            if sheet_name == "links":
                for i in range(INPUT_ROWS):
                  if path == "id":
                      worksheet.write_formula(len(header_rows) + i, column, f'=IF(ISBLANK({MAIN_SHEET_NAME}!B{i + input_row_ref}),"",{MAIN_SHEET_NAME}!B{i + input_row_ref})', cell_format, "")
                  elif path == "links/0/href":
                      worksheet.write_formula(len(header_rows) + i, column, f'=IF(B{i + input_row_ref}="","","{RDLS_SCHEMA_URL}")', cell_format, "")
                  elif path == "links/0/rel":
                      worksheet.write_formula(len(header_rows) + i, column, f'=IF(B{i + input_row_ref}="","","describedby")', cell_format, "")                      
            else:
              worksheet.write_column(
                  len(header_rows), column, ["" for i in range(INPUT_ROWS)], cell_format)

            # Set column width
            worksheet.set_column(column, column, max(len(path), 16))

            validation_options = None
            
            # Set data validation for identifiers
            for sheet, paths in SHEETS.items():
                if sheet_name == sheet:
                    break
                elif path in paths:
                    column_ref = xl_col_to_name(paths.index(path) + 1)
                    validation_options = {
                        "validate": "list",
                        "source": f"={sheet}!${column_ref}${len(header_rows) + 1}:${column_ref}${INPUT_ROWS}"
                    }
                    break

            # Set data validation for codelists
            if codelist:
                validation_options = {"validate": "list"}

                if values[:4] == 'Enum':
                    codes = values[6:].split(", ")
                    validation_options["error_title"] = "Value not in codelist"
                    if data_type == "array":
                      validation_options["error_type"] = "warning"
                      validation_options["error_message"] = "You must use a code from the codelist.\n\nIf no code is appropriate, please create an issue in the RDLS GitHub repository. If you entered multiple values from the codelist, you can ignore this warning."                        
                    else:
                      validation_options["error_type"] = "stop"
                      validation_options["error_message"] = "You must use a code from the codelist.\n\nIf no code is appropriate, please create an issue in the RDLS GitHub repository."
                else:
                    codelist_csv = get(
                        f"{schema_url.split('/rdls_schema.json')[0]}/codelists/open/{codelist}")
                    codelist_reader = csv.DictReader(
                        codecs.iterdecode(codelist_csv.iter_lines(), 'utf-8'))
                    codes = [row['Code'] for row in codelist_reader]
                    validation_options["error_type"] = "warning"
                    validation_options["error_title"] = "Value not in codelist"
                    if data_type == "array":
                        validation_options["error_message"] = "You must use a code from the codelist, unless no code is appropriate.\n\nIf you use new codes outside those in an open codelist, please create an issue in the RDLS GitHub repository, so that the codes can be considered for inclusion in the codelist. If you entered multiple values from the codelist, you can ignore this warning."
                    else:
                        validation_options["error_message"] = "You must use a code from the codelist, unless no code is appropriate.\n\nIf you use new codes outside those in an open codelist, please create an issue in the RDLS GitHub repository, so that the codes can be considered for inclusion in the codelist."

                enum_worksheet.write_column(0, enum_column, [path] + codes)
                enum_column_ref = xl_col_to_name(enum_column)
                validation_options["source"] = f"='# Enums'!${enum_column_ref}$2:${enum_column_ref}${len(codes)+1}"
                enum_column += 1

            # Set data validation for dates
            elif values == 'date':
                validation_options = {
                    "validate": "date",
                    "criteria": ">=",
                    "value": datetime.datetime(1, 1, 1)
                }
            
            if validation_options:
                worksheet.data_validation(
                    len(header_rows), column, 1007, column, validation_options)

            column += 1

    # Delete temp files
    delete_directory_contents(".temp")

    # Write template to drive
    readme_worksheet.activate()
    enum_worksheet.hide()
    workbook.get_worksheet_by_name("links").hide()
    workbook.close() 


if __name__ == '__main__':
    cli()
