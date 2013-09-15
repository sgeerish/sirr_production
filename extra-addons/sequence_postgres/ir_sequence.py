"""
    Postgres Sequences

    :copyright: (c) 2011 by Openlabs Technologies & Consulting (P) Ltd..
    :copyright: (c) 2011 by Multibase WebAustralis Pty Ltd.
    :license: GPLv3, see LICENSE for more details.
"""
from osv import fields, osv

class IrSequence(osv.osv):
    "Postgres Sequence"
    _inherit = 'ir.sequence'

    _columns = dict(
        type = fields.selection([
            ('default', 'Default OpenERP'),
            ('postgres', 'Postgres')
            ], 'Sequence', required=True),
        )
        
    _defaults = dict(
        type = 'default'
        )

    def create(self, cursor, user, values, context=None):
        """Create the postgres sequence after creation of ir.sequence if the
        type is postrges"""
        id = super(IrSequence, self).create(cursor, user, values, context)
        if values.get('type') == 'postgres':
            self.create_sequence(cursor, user, id, context)
        return id

    def write(self, cursor, user, ids, values, context=None):
        """Write to the postgres sequence after the editing
        """
        ids = [ids] if isinstance(ids, (long, int)) else ids
        for id in ids:
            type_before_write = self.browse(cursor, user, id, context).type
            rv = super(IrSequence, self).write(cursor, user, ids, 
                values, context)
            if type_before_write == 'default':
                if values.get('type') in [None, 'default']:
                    return rv
                self.create_sequence(cursor, user, id, context)
                return rv
            else:
                if values.get('type') == 'default':
                    self.drop_sequence(cursor, user, id, context)
                    return rv
                self.alter_sequence(cursor, user, id, context)
        return rv

    def unlink(self, cursor, user, ids, context=None):
        """Delete the sequence if there is one in postgres"""
        # TODO: DROP the sequence if it exists
        return super(IrSequence, self).unlink(cursor, user, ids, context)

    def create_sequence(self, cursor, user, id, context):
        """CREATE the sequence in database

        :param id: Id of the ir.sequence for which a postgres sequence is to 
            be created
        :type id: int, long
        """
        # The name of the sequence in the database
        sequence = self.browse(cursor, user, id, context)

        cursor.execute("""CREATE SEQUENCE ir_sequence_%s INCREMENT BY %s 
            START WITH %s""", (id, sequence.number_increment, 
                sequence.number_next,))

        return True

    def alter_sequence(self, cursor, user, id, context):
        """ALTER the current sequence"""
        sequence = self.browse(cursor, user, id, context)
        cursor.execute("""ALTER SEQUENCE ir_sequence_%s INCREMENT BY %s 
            RESTART WITH %s""", (id, sequence.number_increment, 
                sequence.number_next))

        return True

    def drop_sequence(self, cursor, user, id, context):
        """DROP the current sequence"""
        sequence = self.browse(cursor, user, id, context)
        cursor.execute("""DROP SEQUENCE ir_sequence_%s""", (id,))

        return True

    def get_id(self, cursor, user, sequence_id, test='id', context=None):
        """If the sequence type is default pass it on to super function else
        call the select sequence.

        :param sequence_id: This may be the id or codee of the sequence. Just
            another silly variable naming in openerp. (This is copied into
            variable `identifier` below)
        :param test: This is a disastrous misnomer which indicates if the 
            :attr: sequence_id is an id or a code. We are not renaming any of
            these vars to avoid issues when keywords args are specified 
            elsewhere. This is copied to variable `identifier_type` below.
        """
        user_obj = self.pool.get('res.users')
        # Fix the misnomers first to make code readable
        identifier_type, identifier = test, sequence_id

        if identifier_type == 'code':
            user_rec = user_obj.browse(cursor, user, user, context)
            # Convert identifier to id if code is the type
            identifier, = self.search(cursor, user, [
                ('code', '=', identifier),
                ('company_id', 'in', [False, user_rec.company_id.id]),
                ], limit=1, context=context)

        sequence = self.browse(cursor, user, identifier, context)
        if sequence.type == 'postgres':
            cursor.execute("SELECT nextval('ir_sequence_%s')", (sequence.id,))
            next_id = cursor.fetchone()
            return ''.join([
                self._process(sequence.prefix),
                '%%0%sd' % sequence.padding % next_id,
                self._process(sequence.suffix)])

        elif sequence.type == 'default':
            return super(IrSequence, self).get_id(cursor, user, sequence_id, 
                test, context)

    def get(self, cr, uid, code, context=None):
        # How funny that get_id() need context and get() doesn't
        # Silly programmers forgot their own guidelines
        return self.get_id(cr, uid, code, test='code', context=context)

IrSequence()