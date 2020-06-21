# -*- coding: utf-8 -*-
from django3_apps.settings import BASE_DIR
import csv
import datetime
from django.db.models import Sum, F, Q
from django.http import HttpResponse
from canteen.models import OrderItems


def run():
    day = str(datetime.date.today())
    dishes = OrderItems.objects.filter(Q(order__date__exact=day), ~Q(quantity__isnull=True), Q(product__isnull=False),
                                       ~Q(quantity=0)).distinct().values('product__product__name')
    lista = dishes.distinct().annotate(ile=Sum(F('quantity')))
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response, delimiter=';')
    writer.writerow(["orders for the day: ", day])
    writer.writerow(["dish", "quantity"])
    for n in lista:
        writer.writerow([n.values()[1].encode('utf-8').strip(), n.values()[0]])
    file_save = open(BASE_DIR + '/canteen/reports/' + day + '.csv', 'w')
    file_save.write(str(response))
    file_save.close()
