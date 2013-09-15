from osv import fields, osv
import time
class notebook(osv.osv):
_name = "notebook"
_description = "Simple Notebook"
_columns = {
‘title’ : fields.char(‘Title’, size=30, required=True),
‘note’ : fields.text(‘Note’),
‘note_date’ : fields.date(‘Date’),
}
notebook()