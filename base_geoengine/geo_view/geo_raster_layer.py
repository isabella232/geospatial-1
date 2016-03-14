# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2011-2012 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import api, fields, models


class GeoRasterLayerType(models.Model):
    _name = 'geoengine.raster.layer.type'

    name = fields.Char(
        translate=True, required=True
    )
    code = fields.Char(
        required=True,
    )
    service = fields.Char(
        required=True,
    )


class GeoRasterLayer(models.Model):
    _name = 'geoengine.raster.layer'

    raster_type = fields.Selection(
        [('osm', 'OpenStreetMap'),
         ('mapbox', 'MapBox'),
         ('wmts', 'WMTS'),
         # FIXME ('google', 'Google'), see OCA/geospatial#63
         ('d_wms', 'Distant WMS'),
         ('swisstopo', 'swisstopo'),
         ('map.lausanne.ch', 'map.lausanne.ch'),
         ('odoo', 'Odoo field')],
        string="Raster layer type",
        default='osm',
        required=True)
    name = fields.Char(
        'Layer Name', size=256, translate=True, required=True)
    url = fields.Char('Service URL', size=1024)

    # technical field to display or not wmts options
    is_wmts = fields.Boolean(compute='_get_is_wmts')
    # wmts options
    matrix_set = fields.Char("matrixSet")
    format_suffix = fields.Char("formatSuffix", help="eg. png")
    request_encoding = fields.Char("requestEncoding", help="eg. REST")
    projection = fields.Char("projection", help="eg. EPSG:21781")
    units = fields.Char(help="eg. m")
    resolutions = fields.Char("resolutions")
    max_extent = fields.Char("max_extent")
    server_resolutions = fields.Char(
        "resolutions",
        help="List of dimensions separated by ',' eg. 50, 20, 10")
    dimensions = fields.Char(
        "dimensions",
        help="List of dimensions separated by ','")
    params = fields.Char(
        "params",
        help="Dictiorary of values for dimensions as JSON"
    )

    # technical field to display or not layer type
    has_type = fields.Boolean(compute='_get_has_type')
    type_id = fields.Many2one('geoengine.raster.layer.type', "Layer", domain="[('service', '=', raster_type)]")
    type = fields.Char(related='type_id.code')
    mapbox_id = fields.Char("Mapbox ID", size=256)
    swisstopo_time = fields.Char('Release date', size=256)
    sequence = fields.Integer('layer priority lower on top', default=6)
    overlay = fields.Boolean('Is overlay layer?')
    field_id = fields.Many2one(
        'ir.model.fields', 'Odoo layer field to use',
        domain=[('ttype', 'ilike', 'geo_'),
                ('model', '=', 'view_id.model')])
    view_id = fields.Many2one(
        'ir.ui.view', 'Related View', domain=[('type', '=', 'geoengine')],
        required=True)
    use_to_edit = fields.Boolean('Use to edit')

    @api.one
    @api.depends('raster_type', 'is_wmts')
    def _get_has_type(self):
        self.has_type = self.raster_type in ('google', 'mapbox', 'is_wmts')
        if self.raster_type == 'map.lausanne.ch':
            self.has_type = True

    @api.one
    @api.depends('raster_type')
    def _get_is_wmts(self):
        self.is_wmts = self.raster_type in ('swisstopo', 'wmts',
                'map.lausanne.ch')

    @api.one
    @api.onchange('raster_type')
    def onchange_set_wmts_options(self):
        # XXX move in swisstopo module
        if self.raster_type == 'swisstopo':
            self.url = ('https://wmts0.geo.admin.ch/,'
                        'https://wmts1.geo.admin.ch/,'
                        'https://wmts2.geo.admin.ch/')
            self.format_suffix = 'jpeg'
            self.projection = 'EPSG:21781'
            self.units = 'm'
            self.resolutions = (
                '4000, 3750, 3500, 3250, 3000, 2750, 2500, 2250, 2000, 1750, '
                '1500, 1250, 1000, 750, 650, 500, 250, 100, 50, 20, 10, 5, 2.5'
            )
            self.max_extent = '420000, 30000, 900000, 350000'
            self.request_encoding = 'REST'
            self.matrix_set = '21781'
            self.dimensions = 'TIME'
            self.params = '{"time": 2015}'
        # XXX move in lausanne module
        if self.raster_type == 'map.lausanne.ch':
            self.url = 'http://map.lausanne.ch/main/tiles/'
            self.format_suffix = 'png'
            self.projection = 'EPSG:21781'
            self.units = 'm'
            self.resolutions = (
                '20, 10, 5, 2.5, 2, 1.5, 1, 0.5, 0.25, 0.1, 0.05'
            )
            self.max_extent = '420000, 30000, 900000, 350000'
            self.server_resolutions = (
                '50, 20, 10, 5, 2.5, 2, 1.5, 1, 0.5, 0.25, 0.1, 0.05'
            )
            self.request_encoding = 'REST'
            self.matrix_set = 'swissgrid_05'
            self.dimensions = 'DATE'
            self.params = '{"date": 2015}'
