# Generated migration for payment fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0007_pedido_pedido_grupo'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='estado_pago',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('pagado', 'Pagado'), ('rechazado', 'Rechazado'), ('cancelado', 'Cancelado')], default='pendiente', max_length=20),
        ),
        migrations.AddField(
            model_name='pedido',
            name='wompi_transaction_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='wompi_reference',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
