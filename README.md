#  Risk Data Library Standard Spreadsheet Template

A template for entering [Risk Data Library Standard (RDLS)](https://docs.riskdatalibrary.org) metadata in spreadsheet format. For more information on the Risk Data Library project, see [https://riskdatalibrary.org/](https://riskdatalibrary.org/).

**[:arrow_down: Download the full template](https://github.com/GFDRR/rdls-spreadsheet-template/raw/main/templates/rlds_template.xlsx)** (Hazard, exposure, vulnerability and loss metadata)

* **[:arrow_down: Download the hazard metadata template](https://github.com/GFDRR/rdls-spreadsheet-template/raw/main/templates/rlds_template_hazard.xlsx)**
* **[:arrow_down: Download the exposure metadata template](https://github.com/GFDRR/rdls-spreadsheet-template/raw/main/templates/rlds_template_exposure.xlsx)**
* **[:arrow_down: Download the vulnerability metadata template](https://github.com/GFDRR/rdls-spreadsheet-template/raw/main/templates/rlds_template_vulnerability.xlsx)**
* **[:arrow_down: Download the loss metadata template](https://github.com/GFDRR/rdls-spreadsheet-template/raw/main/templates/rlds_template_loss.xlsx)**

## How to use the template

1. Read the [RDLS documentation](https://docs.riskdatalibrary.org) to learn about the structure of RDLS metadata.
1. Download the template and enter your data in your preferred spreadsheet software:
   1. Start by entering data in the first row in the `datasets` worksheet and then complete any other [worksheets](#worksheets) that are relevant to your dataset.
   1. Use the [field information](#field-information) to understand what data to enter into each column and how to format it.
   1. Use [identifiers](#identifiers) to relate data entered across multiple worksheets.
   1. Make sure that you complete all of the required fields for each worksheet that you add data to.
1. Check that your data conforms to the schema using the [RDLS metadata toolkit]() and correct any errors.

 For more guidance on how to publish RDLS metadata, refer to the [implementation guidance](https://docs.riskdatalibrary.org/en/dev/guides/).

## How to customise the template

You can hide worksheets and columns that are not relevant to your datasets. However, you must ensure that you complete all of the required fields for each worksheet to which you add data.

## Frequently asked questions

### What does the '0' refer to in the field names?

It indicates that each row under that field path should be interpreted as an item in an array, e.g. under `attributions/0/id` the first row will be interpreted as the `id` of the first item in the `attributions` array and the second row will be interpreted as the `id` of the second item.

## Reference
### Worksheets

The template consists of several worksheets, reflecting the structure of the RDLS schema. The `datasets` worksheet is the main worksheet and each row in the `datasets` worksheet represents a risk dataset. The other worksheets in the template represent arrays in the RDLS schema, with rows representing items in the arrays. For example, each row in the the `resources` worksheet represents a [resource](https://docs.riskdatalibrary.org/en/dev/reference/schema/#resource). For more information on the RDLS schema, refer to the [schema reference](https://docs.riskdatalibrary.org/en/dev/reference/).

### Identifiers

Identifiers are used to relate data entered across multiple worksheets, allowing the possibility of one-to-many relationships, such as one dataset made up of many resources. Rows in child worksheets are related to rows in parent worksheets using the parent object’s `id` field. For example, the `id` column in the `resources` is used to reference the `id` of the dataset to which the resource belongs. Similarly, each row in the `hazard_event_sets_events` represents an event in an event set. The `hazard/event_sets/0/id` column references the event set to which the event belongs and the `id` column references the dataset to which the event set and event belong."

### Field information

Each column in the template represents a field in the RDLS schema. The following information is provided for each field:

* `path`: A JSON pointer that identifies the RDLS field represented by the column. This information is used to convert data from spreadsheet format to JSON format. For more information, refer to the [Flatten Tool JSON pointer documentation](https://flatten-tool.readthedocs.io/en/latest/unflatten/#understanding-json-pointer-and-how-flatten-tool-uses-it).
* `title`: The title of the field, from the RDLS schema.
* `description`: The description of the field, from the RDLS schema. You must ensure that the data you enter into each column conforms to the field's description.
* `required`: Whether the field is required (mandatory). You must populate required fields unless no other fields in the worksheet are populated.
* `type`: The data type of the field, from the RDLS schema. The possible types are:
  * string (text)
  * number (decimal)
  * integer (whole number)
  * boolean (true/false)
  * array (list of values).
* `values`: If the field references a closed [codelist](https://docs.riskdatalibrary.org/en/dev/reference/codelists/), the permitted values. If the value of the field must conform to a particular [string format](https://json-schema.org/understanding-json-schema/reference/string.html#built-in-formats), the name of the format. The possible formats are:
  * date (YYYY-MM-DD)
  * email
  * iri (web address)
* `codelist`: If the field references a codelist, the name of the codelist. To view the title and description of each code, open the link.
* `input guidance`: Guidance on how to enter data in spreadsheet format.

## Developer documentation

The spreadsheet template is generated from the RDLS schema using the script in `manage.py`.

### How to update the template

Run the following command:

```bash
python manage.py create-template
```

To see all options, pass the --help flag:

```bash
python manage.py create-template --help
```
