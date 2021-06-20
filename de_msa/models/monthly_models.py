# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class monthly_power_model(models.Model):
    _name = 'monthly.power.model'
    
    power_model = fields.Many2one('product.product', 'Power Model', required=True)
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement', required=True)
    site_id = fields.Many2one('project.project', string='Site', required=True)
    period = fields.Char('Period', required=True)


class monthly_tower_model(models.Model):
    _name = 'monthly.tower.model'
    
    tower_model = fields.Many2one('product.product', 'Tower Model', required=True)
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement', required=True)
    site_id = fields.Many2one('project.project', string='Site', required=True)
    period = fields.Char('Period', required=True)
    

class monthly_tower_load(models.Model):
    _name = 'monthly.tower.load'
    
    load = fields.Selection([('access_low','Access Low'),('access_high','Access High'),
                             ('dwdm','DWDM'),('standard_hub','Standard Hub')], string='Load', required=True)
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement', required=True)
    site_id = fields.Many2one('project.project', string='Site', required=True)
    period = fields.Char('Period', required=True)


class monthly_sla_factors(models.Model):
    _name = 'monthly.sla.factor'
    
    sla_factor = fields.Many2one('sla.factor.value', 'SLA Factor', required=True)
    msa_id = fields.Many2one('master.service.agreement', 'Master Service Agreement', required=True)
    site_id = fields.Many2one('project.project', string='Site', required=True)
    period = fields.Char('Period', required=True)

