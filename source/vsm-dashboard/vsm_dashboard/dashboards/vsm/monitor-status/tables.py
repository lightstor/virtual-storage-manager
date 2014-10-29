# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2014 Intel Corporation, All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict
from django import forms

from django.utils.safestring import mark_safe

from horizon import tables
from horizon.utils import html
from horizon import exceptions
from vsm_dashboard.api import vsm as vsmapi
from .utils import checkbox_transform

STRING_SEPARATOR = "__"

class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, id):
        # todo update zone info in apiclient CEPH_LOG
        try:
            _zones = vsmapi.get_zone_list(request,)
        except:
            exceptions.handle(request,
                              _('Unable to retrieve sever list. '))
        zones = {}
        for _zone in _zones:
            zones.setdefault(_zone.id, _zone.name)

        _server = vsmapi.get_server(request, id)
        server = {"id": _server.id,
                  "name": _server.host,
                  "primary_public_ip": _server.primary_public_ip,
                  "secondary_public_ip": _server.secondary_public_ip,
                  "cluster_ip": _server.cluster_ip,
                  "zone_id": _server.zone_id,
                  "zone": "",
                  "osds": _server.osds,
                  "type": _server.type,
                  "status": _server.status}
        if "monitor" in _server.type:
                server['is_monitor'] = "yes"
        else:
                server['is_monitor'] = "no"
        if _server.zone_id in zones:
            server['zone'] = zones[_server.zone_id]

        return server

STATUS_DISPLAY_CHOICES = (
    ("resize", "Resize/Migrate"),
    ("verify_resize", "Confirm or Revert Resize/Migrate"),
    ("revert_resize", "Revert Resize/Migrate"),
)

class ListMonitorStatusTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ("available", True),
        ("Active", True),
    )

    #server_id = tables.Column("id", verbose_name=_("ID"))
    ordinal = tables.Column("id", verbose_name=_("ordinal"))
    name = tables.Column("name", verbose_name=_("Name"))
    address = tables.Column("address", verbose_name=_("Address"))
    health = tables.Column("health", verbose_name=_("Health"))
    details = tables.Column("details", verbose_name=_("Detail"))
    skew = tables.Column("skew", verbose_name=_("Skew"))
    latency = tables.Column("latency", verbose_name=_("Latency"))
    kb_total = tables.Column("mb_total", verbose_name=_("MB Total (disk)"))
    kb_used = tables.Column("mb_used", verbose_name=_("MB Used (disk)"))
    kb_avail = tables.Column("mb_avail", verbose_name=_("MB Available (disk)"))
    percent_avail = tables.Column("percent_avail", verbose_name=_("Percent Available"))
    updated_at = tables.Column("updated_at", verbose_name=_("Updated at"), classes=("span2",))

    class Meta:
        name = "monitor_list"
        verbose_name = _("Monitor List")
        #status_columns = ['status']
        row_class = UpdateRow
        multi_select = False

    def get_object_id(self, datum):
        if hasattr(datum, "id"):
            return datum.id
        else:
            return datum["id"]

    def get_object_display(self, datum):
        if hasattr(datum, "name"):
            return datum.id
        else:
            return datum["name"]

def empty_value_maker(type, name, value, attrs=None):
    def _empty_value_caller(datum):
        if type == "text":
            widget = forms.TextInput()
        elif type == "choice":
            widget = forms.ChoiceField().widget
        elif type == "checkbox":
            widget = forms.CheckboxInput()
        data = dict(name=name, value=value)
        if name in datum.keys():
            data.update(datum[name])
        if attrs:
            data.update(dict(attrs=attrs))
        data = widget.render(**data)
        return data
    return _empty_value_caller

