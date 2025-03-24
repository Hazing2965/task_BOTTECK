import os
import nats
from django.contrib import admin
from .models import Cart, Categories, DistributionUser, Payments, SubCategories, Product, UsersBot, Orders
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)



class CreateDistribution(admin.ModelAdmin):
    exclude = ('photo_id',)  # Исключаем поле photo_id из формы

    async def send_nats_message(self, obj):
        user_id_list = [user.user_id async for user in UsersBot.objects.all()]
        
        nc = await nats.connect(os.getenv('NATS_URL'))
        js = nc.jetstream()
        for user_id in user_id_list:
            try:
                headers = {
                    'id': str(obj.id)
                }
                await js.publish(subject=os.getenv('SUBJECT_DISTRIBUT'),
                        stream=os.getenv('STREAM_NAME'),
                        payload=str(user_id).encode(encoding='utf-8'),
                        headers=headers)
            except Exception as e:
                print(e)
        await nc.close()

    def save_model(self, request, obj, form, change):

        super().save_model(request, obj, form, change)
        if not change:
            async_to_sync(self.send_nats_message)(obj)

admin.site.register(DistributionUser, CreateDistribution)

admin.site.register(Categories)
admin.site.register(SubCategories)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Orders)
admin.site.register(Payments)
admin.site.register(UsersBot)




