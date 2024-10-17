# -*- coding: utf-8 -*-
# Este es el primer modelo en Odoo

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime

# --proyect--
class ManageProyect(models.Model):
    _name = 'manage.proyect'
    _description = 'Manage Proyect' 

    name = fields.Char()
    description = fields.Text() 
    history_ids = fields.One2many(comodel_name='manage.history', inverse_name='proyect_id', string='History')


# --history--
class ManageHistory(models.Model):
    _name = 'manage.history'
    _description = 'Manage History' 

    name = fields.Char()
    description = fields.Text()
    proyect_id = fields.Many2one('manage.proyect', ondelete='set null', string='Proyect')
    task_ids = fields.One2many(comodel_name='manage.task', inverse_name='history_id', string='Tareas')
    used_technologies = fields.Many2many("manage.technology", compute="_get_used_technologies")

    # Recorrer las tareas asociadas y ver qué tecnologías están en uso
    @api.depends('task_ids.technologies_ids')
    def _get_used_technologies(self):
        for history in self:
            technologies = set()
            for task in history.task_ids:
                technologies.update(task.technologies_ids)
            history.used_technologies = list(technologies)


# --task--
class ManageTask(models.Model):
    _name = 'manage.task'
    _description = 'Manage Task'

    definition_date = fields.Datetime(default=lambda d: datetime.datetime.now())
    proyect_id = fields.Many2one('manage.proyect', related='history_id.proyect_id', readonly=True)
    code = fields.Char(compute="_get_code", string="Code")
    name = fields.Char(string="Nombre", required=True, help="Introduzca el nombre")
    history_id = fields.Many2one('manage.history', ondelete='set null', help='Historia relacionada')
    description = fields.Text()
    start_date = fields.Datetime()
    end_date = fields.Datetime()
    is_paused = fields.Boolean()
    sprint_id = fields.Many2one("manage.sprint", compute="_get_sprint", store=True)
    technologies_ids = fields.Many2many(comodel_name="manage.technology", relation="technologies_tasks", column1="task_id", column2="technology_id", string="Technologies")

    @api.depends('sprint_id')
    def _get_code(self):
        for task in self:
            if not task.sprint_id:
                task.code = f"TSK_{task.id}"
            else:
                task.code = f"TSK_{task.sprint_id.name.upper()}_{task.id}"

    @api.depends('history_id.proyect_id')
    def _get_sprint(self):
        for task in self:
            sprints = self.env['manage.sprint'].search([('proyect_id', '=', task.proyect_id.id)])
            task.sprint_id = next((sprint for sprint in sprints if sprint.end_date > fields.Datetime.now()), False)


# --sprint--
class ManageSprint(models.Model):
    _name = 'manage.sprint'
    _description = 'Manage Sprint'

    proyect_id = fields.Many2one('manage.proyect')
    name = fields.Char()
    description = fields.Text()
    duration = fields.Integer(default=15)
    start_date = fields.Datetime()
    end_date = fields.Datetime(compute="_get_end_date", store=True)
    task_ids = fields.One2many("manage.task", "sprint_id", string="Tasks")

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for sprint in self:
            sprint.end_date = sprint.start_date + datetime.timedelta(days=sprint.duration) if sprint.start_date else False


# --technology--
class ManageTechnology(models.Model):
    _name = 'manage.technology'
    _description = 'Manage Technology'

    name = fields.Char()
    description = fields.Text()
    photo = fields.Image(max_width=200, max_height=200)
    tasks_ids = fields.Many2many(comodel_name="manage.task", relation="technologies_tasks", column1="technology_id", column2="task_id", string="Tasks")