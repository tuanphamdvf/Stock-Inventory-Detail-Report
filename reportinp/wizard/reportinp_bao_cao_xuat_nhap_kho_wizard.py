from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, AccessDenied, Warning
from datetime import date
from functools import reduce
import random
import datetime
from odoo.http import request


class BaoCaoXuatNhapKho(models.TransientModel):
    _name = "reportinp.bao_cao_xuat_nhap_kho.wizard"
    _description = "STOCK INVENTORY REPORT"
    ngay_ton_start = fields.Date(string="Start", required=True)

    ngay_ton_end = fields.Date(string="End", required=True)
    khohang = fields.Many2one('stock.location', string='Location', tracking=True, required=True, domain=[
        ('active', '=', True), ('usage', '=', 'view'), ('location_id', '!=', False)])

    def print_report(self):
        print(self)
        product = "product"
        user_id = request.session.uid
        user = request.env['res.users'].browse(user_id)
        # danh sách sản phẩm và giá trị vốn
        list_product = self.env['product.template'].search(
            [('detailed_type', '=', product) and ('active', '=', True)])
        list_product_main = self.env['product.product'].search(
            [('active', '=', True) and ('detailed_type', '=', product)])
        list_kho_hang_main = self.env['stock.location'].search(
            [('active', '=', True)])
        # giá trị vốn
        # list_unit_cost = self.env['stock.valuation.layer'].search([])
        # today = date.today().strftime("%d/%m/%Y")
        todayDate = datetime.date.today()
        if todayDate.day > 25:
            todayDate += datetime.timedelta(7)
        data = {
            'model': 'reportinp.bao_cao_xuat_nhap_kho.wizard',
            'form_data': self.read()[0]
        }
        ngay_ton_start = data['form_data']['ngay_ton_start']
        ngay_ton_end = data['form_data']['ngay_ton_end']
        diadiem = self.khohang
        danhsachphieuxuat = diadiem['child_ids']['outgoing_move_line_ids']
        danhsachphieunhap = diadiem['child_ids']['incoming_move_line_ids']
        if len(danhsachphieunhap) != 0:
            for i in danhsachphieunhap:
                print(i['qty_done'])

        list_san_pham = []
        tongtondau = 0
        tongtoncuoi = 0
        tongthaydoi = 0
        tongxuattrongkyall = 0
        tongnhaptrongkyall = 0
        tonggiatrixuatall = 0
        tonggiatrinhapall = 0
        tongphieunhap = 0
        tongphieuxuat = 0

        tonggiatridau = 0
        tonggiatricuoi = 0
        tonggiatrithaydoi = 0

        tongxuatdauky = 0
        tongnhapdauky = 0
        tongxuattrongky = 0
        tongnhaptrongky = 0
        sophieunhap = 0
        sophieuxuat = 0

        tondau = 0
        toncuoi = 0
        tontrongky = 0
        if len(list_product_main) != 0:
            for i in list_product_main:
                vals = {
                    'name': i.name,
                    'masp': i.default_code,
                    'giavon': i['standard_price'],
                    'barcode': i['barcode'],
                    'tongnhap': 0,
                    'tongxuat': 0,
                    'giatrinhap': 0,
                    'giatrixuat': 0,
                    'sophieunhap': 0,
                    'sophieuxuat': 0,
                    'tondau': 0,
                    'toncuoi': 0,
                    'thaydoi': 0,
                    'giatridau': 0,
                    'giatricuoi': 0,
                    'giatrithaydoi': 0
                }

                if len(danhsachphieuxuat) != 0:
                    for j in danhsachphieuxuat:
                        print(j['qty_done'])
                        if j['date'].date() < ngay_ton_start and j['product_id']['id'] == i.id:
                            tongxuatdauky += j['qty_done']
                        if j['date'].date() >= ngay_ton_start and j['product_id']['id'] == i.id and j[
                                'date'].date() <= ngay_ton_end:
                            tongxuattrongky += j['qty_done']
                            sophieuxuat = sophieuxuat + 1
                if len(danhsachphieunhap) != 0:
                    for j in danhsachphieunhap:
                        if j['date'].date() < ngay_ton_start and j['product_id']['id'] == i.id:
                            tongnhapdauky += j['qty_done']
                        if j['date'].date() >= ngay_ton_start and j['product_id']['id'] == i.id and j[
                                'date'].date() <= ngay_ton_end:
                            tongnhaptrongky += j['qty_done']
                            sophieunhap = sophieunhap + 1

                    tondau = tongnhapdauky - tongxuatdauky
                    tontrongky = tongnhaptrongky - tongxuattrongky
                    toncuoi = tondau + tontrongky

                    tongtondau += tondau
                    tongtoncuoi += toncuoi
                    tongthaydoi += tontrongky
                    tonggiatrithaydoi += (tonggiatricuoi - tonggiatridau)
                    vals = {
                        'name': i.name,
                        'masp': i.default_code,
                        'giavon': i['standard_price'],
                        'barcode': i['barcode'],
                        'tongnhap': tongnhaptrongky,
                        'tongxuat': tongxuattrongky,
                        'giatrinhap': tongnhaptrongky * i['standard_price'],
                        'giatrixuat': tongxuattrongky * i['standard_price'],
                        'sophieunhap': sophieunhap,
                        'sophieuxuat': sophieuxuat,
                        'tondau': tondau,
                        'toncuoi': toncuoi,
                        'thaydoi': tontrongky,
                        'giatridau': tondau * i['standard_price'],
                        'giatricuoi': toncuoi * i['standard_price'],
                        'giatrithaydoi': tontrongky * i['standard_price']

                    }

                    tondau = 0
                    toncuoi = 0
                    tontrongky = 0
                    tongxuatdauky = 0
                    tongnhapdauky = 0
                    tongxuattrongky = 0
                    tongnhaptrongky = 0
                    sophieunhap = 0
                    sophieuxuat = 0

                list_san_pham.append(vals)

        # if len(list_san_pham) != 0:
        #     for i in list_san_pham:
        #         print(i['name'])
        totaltondau = 0
        totalgiatridau = 0
        totaltoncuoi = 0
        totalgiatricuoi = 0
        totalthaydoi = 0
        totalgiatrithaydoi = 0

        if len(list_san_pham) != 0:
            for i in list_san_pham:
                totaltondau += i['tondau']
                totalgiatridau += i['giatridau']
                totaltoncuoi += i['toncuoi']
                totalgiatricuoi += i['giatricuoi']
                totalthaydoi += i['thaydoi']
                totalgiatrithaydoi += i['giatrithaydoi']
                tongxuattrongkyall += i['tongxuat']
                tongnhaptrongkyall += i['tongnhap']
                tonggiatrixuatall += i['giatrixuat']
                tonggiatrinhapall += i['giatrinhap']
                tongphieunhap += i['sophieunhap']
                tongphieuxuat += i['sophieuxuat']

        data['list_san_pham'] = list_san_pham
        data['ngay_ton_start'] = ngay_ton_start.strftime('%d/%m/%Y')
        data['ngay_ton_end'] = ngay_ton_end.strftime('%d/%m/%Y')

        data['name_user'] = user.name

        data['list_san_pham'] = list_san_pham
        data['ngay_ton_start'] = ngay_ton_start.strftime('%d/%m/%Y')
        data['ngay_ton_end'] = ngay_ton_end.strftime('%d/%m/%Y')
        data['tongtondau'] = totaltondau
        data['tongtoncuoi'] = totaltoncuoi
        data['tongthaydoi'] = totalthaydoi
        data['tonggiatridau'] = totalgiatridau
        data['tonggiatricuoi'] = totalgiatricuoi
        data['tonggiatrithaydoi'] = totalgiatrithaydoi

        data['tongphieuxuat'] = tongphieuxuat
        data['tongphieunhap'] = tongphieunhap

        data['tongxuattrongkyall'] = tongxuattrongkyall
        data['tongnhaptrongkyall'] = tongnhaptrongkyall
        data['tonggiatrixuatall'] = tonggiatrixuatall
        data['tonggiatrinhapall'] = tonggiatrinhapall

        data['khohang'] = diadiem['complete_name']
        print(data)
        return self.env.ref("reportinp.action_bao_cao_xuat_nhap_kho_report").report_action(self, data=data)
