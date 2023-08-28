#  Risk Data Library Standard Spreadsheet Template

A template for entering [Risk Data Library Standard (RDLS)](https://rdl-standard.readthedocs.io) metadata in spreadsheet format. For more information on the Risk Data Library project, see [https://riskdatalibrary.org/](https://riskdatalibrary.org/). For guidance on how to publish RDLS metadata using the spreadsheet template, refer to the [implementation guidance](https://rdl-standard.readthedocs.io/en/dev/guides/).

**[Download the template](https://github.com/GFDRR/rdls-spreadsheet-template/raw/main/templates/full.xlsx)**

## Template structure

The template consists of several worksheets, reflecting the structure of the RDLS schema. The `datasets` worksheet is the main worksheet and each row in the `datasets` worksheet represents a risk dataset. The other worksheets in the template represent arrays in the RDLS schema, with rows representing items in the arrays. For example, each row in the the `resources` worksheet represents a [resource](https://rdl-standard.readthedocs.io/en/dev/reference/schema/#resource). For more information on the RDLS schema, refer to the [schema reference](https://rdl-standard.readthedocs.io/en/dev/reference/).

## Relationships using identifiers

Identifiers are used to relate data entered across multiple worksheets, allowing the possibility of one-to-many relationships, such as one dataset made up of many resources. Rows in child worksheets are related to rows in parent worksheets using the parent object’s `id` field. For example, the `id` column in the `resources` is used to reference the `id` of the dataset to which the resource belongs. Similarly, each row in the `hazard_event_sets_events` represents an event in an event set. The `hazard/event_sets/0/id` column references the event set to which the event belongs and the `id` column references the dataset to which the event set and event belong."

## Fields

Each column in the template represents a field in the RDLS schema. The following information is provided for each field:

* `path`: A JSON pointer that identifies the RDLS field represented by the column. This information is used to convert data from spreadsheet format to JSON format. For more information, refer to the [Flatten Tool JSON pointer documentation](https://flatten-tool.readthedocs.io/en/latest/unflatten/#understanding-json-pointer-and-how-flatten-tool-uses-it).
* `title`: The title of the field, from the RDLS schema.
* `description`: The description of the field, from the RDLS schema. You must ensure that the data you enter into each column conforms to the field's description.
* `required`: Whether the field is required (mandatory). You must populate required fields unless no other fields in the sheet are populated.
* `type`: The data type of the field, from the RDLS schema. The possible types are:
  * string (text)
  * number (decimal)
  * integer (whole number)
  * boolean (true/false)
  * array (list of values).
* `values`: If the field references a closed [codelist](https://rdl-standard.readthedocs.io/en/dev/reference/codelists/), the permitted values. If the value of the field must conform to a particular [string format](https://json-schema.org/understanding-json-schema/reference/string.html#built-in-formats), the name of the format. The possible formats are:
  * date (YYYY-MM-DD)
  * email
  * iri (web address)
* `codelist`: If the field references a codelist, the name of the codelist. To view the title and description of each code, open the link.
* `input guidance`: Guidance on how to enter data in spreadsheet format.
