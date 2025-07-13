from celery import shared_task
from Store.models import Orders


@shared_task
def mark_order_status_true(order_id):
    try:
        order = Orders.objects.get(id=order_id)
        order.status = True
        order.order_state = 'confirm'
        order.save()
    except Orders.DoesNotExist:
        pass

