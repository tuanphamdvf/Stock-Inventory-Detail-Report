from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, AccessDenied, Warning
from datetime import date
from functools import reduce
import random
import datetime


class BaoCaoXuatNhapKho(models.TransientModel):
    _name = "reportinp.bao_cao_xuat_nhap_kho.wizard"
    _description = "STOCK INVENTORY REPORT"
    ngay_ton_start = fields.Date(string="Start", required=True)

    ngay_ton_end = fields.Date(string="End", required=True)
    khohang = fields.Many2one('stock.location', string='Location', tracking=True, required=True, domain=[
        ('active', '=', True), ('usage', '=', 'view'), ('location_id', '!=', False)])

    # def get_location(self):
    #     hienthi = 'view'
    #     list_location = []
    #     list_location_main = self.env['product.product'].search(
    #         [('active', '=', True) and ('location', '!=', False) and ('usage', '=', hienthi)])
    #     keys_to_keep = ['id', 'complete_name']
    #     filtered_dict = {k: v  for k, v in list_location_main.items() if k in keys_to_keep}
    #     if len(filtered_dict):
    #         for i in filtered_dict:
    #             list_location.append(tuple(i.items()))
    #     return list_location

    def print_report(self):
        print(self)
        product = "product"
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
        listkhohang = []

        list_san_pham = []
        danhsachphieu = []
        danhsachphieuchilds = []
        khohang = ''
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
                    tongxuattrongkyall += tongxuattrongky
                    tongnhaptrongkyall += tongnhaptrongky
                    tongphieunhap += sophieunhap
                    tongphieuxuat += sophieuxuat

                    tonggiatridau += tondau * i['standard_price']
                    tonggiatricuoi += toncuoi * i['standard_price']
                    tonggiatrixuatall += tongxuattrongky * i['standard_price']
                    tonggiatrinhapall += tongnhaptrongky * i['standard_price']

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

        data['list_san_pham'] = list_san_pham
        data['ngay_ton_start'] = ngay_ton_start.strftime('%d/%m/%Y')
        data['ngay_ton_end'] = ngay_ton_end.strftime('%d/%m/%Y')
        data['tongtondau'] = tongtondau
        data['tongtoncuoi'] = tongtoncuoi
        data['tongthaydoi'] = tongthaydoi
        data['tonggiatridau'] = tonggiatridau
        data['tonggiatricuoi'] = tonggiatricuoi
        data['tonggiatrithaydoi'] = tonggiatrithaydoi

        data['tongphieuxuat'] = tongphieuxuat
        data['tongphieunhap'] = tongphieunhap

        data['tongxuattrongkyall'] = tongxuattrongkyall
        data['tongnhaptrongkyall'] = tongnhaptrongkyall
        data['tonggiatrixuatall'] = tonggiatrixuatall
        data['tonggiatrinhapall'] = tonggiatrinhapall

        data['khohang'] = diadiem['complete_name']
        print(data)
        return self.env.ref("reportinp.action_bao_cao_xuat_nhap_kho_report").report_action(self, data=data)

        # list_id = []
        # if len(list_product) != 0:
        #     for item in list_product:
        #         print(item)
        # list_unique = list(set(list_id))

        # result = []
        # if len(list_product_main) != 0:
        #     for i in list_product_main:
        #         print(i)
        #         print(i['id'])
        #         quant = self.env['stock.quant'].search([('id', '=', i['id'])])

        #         data = {
        #             'name': i.name,
        #             'giavon': i['standard_price'],
        #             'tondau': quant[0]['quantity'],
        #             'toncuoi': quant[-1]['quantity'],
        #             'thaydoi': quant[0]['quantity'] - quant[-1]['quantity'],

        #         }
        #         result.append(data)
        #         product = []

        # if len(data_list) != 0:
        #     for j in data_list:
        #         print(type(i.id), type(j.product_id))
        #         if j.product_id == int(i.id):
        #             product.append(j)
        #             unit_cost.append(j)
        #             print("danh sách", unit_cost)
        #             if len(product) != 0:
