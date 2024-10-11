# -*- coding: utf-8 -*-
# este es el primer modelo en odoo

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _
import datetime

#--project--
class ManageProyect(models.Model):
    _name = 'manage.proyect'
    _description = 'Manage Proyect' 

    name = fields.Char()
    description = fields.Text() 
    history_ids = fields.One2many(comodel_name='manage.history', inverse_name='proyect_id', string='History')


#--history--
class ManageHistory(models.Model):
    _name = 'manage.history'
    _description = 'Manage History' 

    name = fields.Char()
    description = fields.Text()
    proyect_id = fields.Many2one('manage.proyect', ondelete='set null', string='Proyect')
    task_ids = fields.One2many(string='tareas', comodel_name='manage.task', inverse_name='history_id')
    used_technologies = fields.Many2many("manage.technology", compute="_get_used_technologies")

    #recorrer la tareas que están asociadad a esta historia, ver que tecnologias se estan utilizando en las tareas
    def _get_used_technologies(self):
        for history in self:
            technologies = None
            for task in history.tasks:
                if not technologies:
                    technologies = task.technologies
                else:
                    technologies = technologies + task.technologies
            history.used_technologies  = technologies     
            



#--task----------
class ManageTask(models.Model):
    _name = 'manage.task'
    _description = 'Manage Task'

    project = fields.Many2one('manage.project', related='history.project', readonly=True)

    code = fields.Char(compute="_get_code", string="Code")

    name = fields.Char(string="Nombre", readonly=False, required=True, help="Introduzca el nombre")
    history_id = fields.Many2one('manage.history', ondelete='set null', help='historia relacionada')
    description = fields.Text()
    start_date = fields.Datetime()
    end_date = fields.Datetime()
    is_paused = fields.Boolean()
    #sprint_id = fields.Many2one("manage.sprint", string="Sprint")
    sprint_id = fields.Many2one("manage.sprint", compute="_get_sprint", store=True)
    technologies_ids = fields.Many2many(comodel_name="manage.technology",
                                        relation="technologies_tasks",
                                        column1="task_id",
                                        column2="technology_id",
                                        string="Technologies")

    @api.depends('sprint_id')
    def _get_code(self):
        for task in self:
            try:
                if not task.sprint_id:
                    task.code = "TSK_" + str(task.id)
                else:
                    task.code = "TSK_" + str(task.sprint_id.name).upper() + "_" + str(task.id)
            except Exception as e:
                raise ValidationError(f"Error al generar el código: {str(e)}")

    @api.depends('code')
    def _get_sprint(self):
        for task in self:
            sprints = self.env['manage.sprint'].search([('project.id' '=', task.history.proyect.id)])  #un sprint por proyecto
            found = False
            for sprint in sprints:
                if isinstance(sprint.end_date, datetime.datetime) and sprint.end_date > datetime.datetime.now():
                    task.sprint = sprint.id
                    found = True
            if not found:
                task.sprint = False


#sprint
class ManageSprint(models.Model):
    _name = 'manage.sprint'
    _description = 'Manage Sprint'

    proyect_ids = fields.Many2one('manage.proyect')
    name = fields.Char()
    description = fields.Text()
    duration = fields.Integer()
    start_date = fields.Datetime()
    end_date = fields.Datetime(compute="_get_end_date", store=True)
    task_ids = fields.One2many("manage.task", "sprint_id", string="Tasks")

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for sprint in self:
            if isinstance(sprint.start_date, datetime.datetime) and sprint.duration > 0:
                sprint.end_date = sprint.start_date + datetime.timedelta(days=sprint.duration)
            else:
                sprint.end_date = sprint.start_date


class ManageTechnology(models.Model):
    _name = 'manage.technology'
    _description = 'Manage Technology'

    name = fields.Char()
    description = fields.Text()
    photo = fields.Image(max_width=200, max_height=200)
    tasks_ids = fields.Many2many(comodel_name="manage.task",
                                relation="technologies_tasks",
                                column1="technology_id",
                                column2="task_id",
                                string="Tasks")