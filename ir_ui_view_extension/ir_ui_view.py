# -*- coding: utf-8 -*-

import logging
import copy

from openerp import models, api
from openerp.osv.orm import setup_modifiers
from lxml import etree
from openerp.osv import orm
from openerp.tools import SKIPPED_ELEMENT_TYPES

_logger = logging.getLogger(__name__)


class meta_model(models.Model):
    _name = None
    _imherit = None
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(meta_model, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        
        modifiers = {}
        start_keyro = 'readonly_'
        start_keyin = 'invisible_'
        start_keyrq = 'required_'
        
        for key in self._context.keys():
            if key.startswith(start_keyro) or key.startswith(start_keyin) or key.startswith(start_keyrq):
                value_key = self.context.get(key)
                field_name = key.split("_",1)[1]
                modifier = key.split("_",1)[0]
                modifiers[modifier] = value_key
                doc = etree.XML(res['arch'])
                node = doc.xpath("//field[@name='"+field_name+"']")[0]
                node.set(modifier, value_key)
                setup_modifiers(node, res['fields']['res_type'])
                res['arch'] = etree.tostring(doc)


        return res                         


class ir_ui_view(models.Model):
    _inherit = 'ir.ui.view'

    
    def postprocess(self, cr, user, model, node, view_id, in_tree_view, model_fields, context=None):
        fields_def = super(ir_ui_view, self).postprocess(cr, user, model, node, view_id, in_tree_view, model_fields, context=context)
        if bool(node.tag) and isinstance(node.tag, basestring) and bool(node.tag in ('field')):
            if node.get('name'):
                Model = self.pool.get(model)

                field = Model._fields.get(node.get('name'))
                if field:

                    modifiers = {}
                    start_keyro = 'readonly_'
                    start_keyin = 'invisible_'
                    start_keyrq = 'required_'
                    
                    for key in context.keys():
                        key_spplited = key.split("_",1)
                        if len(key_spplited) == 2:
                            modifier = key.split("_",1)[0]
                            field_name = key.split("_",1)[1]
                            if (key.startswith(start_keyro) or key.startswith(start_keyin) or key.startswith(start_keyrq)) and field_name == node.get('name'):
                                value_key = context.get(key)
                                modifiers[modifier] = value_key
                                
                                field = model_fields.get(node.get('name'))
        
                                orm.transfer_modifiers_to_node(modifiers,node)

        return fields_def
    

    def apply_inheritance_specs(self, cr, uid, source, specs_tree, inherit_id, context=None):
        """ Apply an inheriting view (a descendant of the base view)

        Apply to a source architecture all the spec nodes (i.e. nodes
        describing where and what changes to apply to some parent
        architecture) given by an inheriting view.

        :param Element source: a parent architecture to modify
        :param Elepect specs_tree: a modifying architecture in an inheriting view
        :param inherit_id: the database id of specs_arch
        :return: a modified source where the specs are applied
        :rtype: Element
        """
        #source = super(ir_ui_view, self).apply_inheritance_specs(cr,uid,source,specs_tree,inherit_id,context)
        
        # Queue of specification nodes (i.e. nodes describing where and
        # changes to apply to some parent architecture).
        specs = [specs_tree]

        while len(specs):
            spec = specs.pop(0)
            if isinstance(spec, SKIPPED_ELEMENT_TYPES):
                continue
            if spec.tag == 'data':
                specs += [c for c in spec]
                continue
            node = self.locate_node(source, spec)
            if node is not None:
                pos = spec.get('position', 'inside')
                if pos == 'replace':
                    if node.getparent() is None:
                        source = copy.deepcopy(spec[0])
                    else:
                        for child in spec:
                            node.addprevious(child)
                        node.getparent().remove(node)
                elif pos == 'attributes':
                    for child in spec.getiterator('attribute'):
                        attribute = child.get('name')
                        value = child.text or ''
                        separator = child.get('separator', ',')
                        if separator == ' ':
                            separator = None    # squash spaces
                        if child.get('add') or child.get('remove'):
                            assert not child.text
                            to_add = filter(bool, map(str.strip, child.get('add', '').split(separator)))
                            to_remove = map(str.strip, child.get('remove', '').split(separator))
                            values = map(str.strip, node.get(attribute, '').split(separator))
                            value = (separator or ' ').join(filter(lambda s: s not in to_remove, values) + to_add)
                        if child.get('merge'):
                            orig_value = node.get(attribute,'').replace("}", ',')
                            to_merge_value = child.get('merge', '').replace("}", '').replace("{", '')
                            value = orig_value + to_merge_value + '}'
                        if value:
                            node.set(attribute, value)
                        elif attribute in node.attrib:
                            del node.attrib[attribute]
                else:
                    sib = node.getnext()
                    for child in spec:
                        if pos == 'inside':
                            node.append(child)
                        elif pos == 'after':
                            if sib is None:
                                node.addnext(child)
                                node = child
                            else:
                                sib.addprevious(child)
                        elif pos == 'before':
                            node.addprevious(child)
                        else:
                            self.raise_view_error(cr, uid, _("Invalid position attribute: '%s'") % pos, inherit_id, context=context)
            else:
                attrs = ''.join([
                    ' %s="%s"' % (attr, spec.get(attr))
                    for attr in spec.attrib
                    if attr != 'position'
                ])
                tag = "<%s%s>" % (spec.tag, attrs)
                self.raise_view_error(cr, uid, _("Element '%s' cannot be located in parent view") % tag, inherit_id, context=context)

        return source

        specs = [specs_tree]

        while len(specs):
            spec = specs.pop(0)
            if isinstance(spec, SKIPPED_ELEMENT_TYPES):
                continue
            if spec.tag == 'data':
                specs += [c for c in spec]
                continue
            node = self.locate_node(source, spec)
            if node is not None:
                pos = spec.get('position', 'inside')
                if pos == 'attributes':
                    for child in spec.getiterator('attribute'):
                        attribute = child.get('name')
                        value = child.text or ''
                        if child.get('merge'):
                            assert not child.text
                            separator = child.get('separator', ',')
                            if separator == ' ':
                                separator = None    # squash spaces
                            to_add = filter(bool, map(str.strip, child.get('merge', '').split(separator)))
                            values = map(str.strip, node.get(attribute, '').split(separator))
                            
                            value = values.append( to_add)
                        if value:
                            node.set(attribute, value)
                        elif attribute in node.attrib:
                            del node.attrib[attribute]

        return source


