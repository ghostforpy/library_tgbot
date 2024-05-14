from django.db import models
from django.conf import settings
import telegram
from tgbot.utils import _get_file_id
from tgbot.models.config import Config


# Получает из всех записей модели словарь 
# key - имя поля чье значение попадет в ключ, 
# value имя поля чье значение попадет в значение если "NN" то подставится порядковый номер
# parent значение родительской модели для выборки подчиненных элементов 
def get_model_dict(model, key: str, value: str, parent = None, filter = None):
    res = dict()
    if parent:
        model_set = getattr(parent,model._meta.model_name+"_set") # получаем выборку дочерних записей parent
    else:
        model_set = model.objects # получаем выборку записей
    
    if filter:
        model_set = model_set.filter(**filter)
    else:
        model_set = model_set.all()
    fields = value.split(",")
    str_num = 0
    for elem in model_set:
        str_num += 1
        val_list = []
        for field in fields:
            if field == "NN":
                val_list.append(str(str_num))
            else:
                val_list.append(str(getattr(elem, field.strip())))
        res[str(getattr(elem, key))] = ", ".join(val_list)
    return res

# Получает из всех записей текст 
# fields - список полей которые попадут в текст "NN" - спец поле будет подставляться номер строки
# parent значение родительской модели для выборки подчиненных элементов 
def get_model_text(model, fields: list, parent = None, filter = None ):
    res = ""
    if parent:
        model_set = getattr(parent,model._meta.model_name+"_set") # получаем выборку дочерних записей parent
    else:
        model_set = model.objects # получаем выборку записей
    
    if filter:
        model_set = model_set.filter(**filter)
    else:
        model_set = model_set.all()
    
    str_num = 0
    for elem in model_set:
        str_num += 1
        txt_str_lst = []
        for field in fields:
            if field == "NN":
                txt_str_lst.append(str(str_num)) 
            else:
                field_val = getattr(elem, field)
                if isinstance(field_val,models.fields.files.FieldFile): 
                    if field_val:
                        txt_str_lst.append(settings.MEDIA_DOMAIN + field_val.url)
                else:
                    txt_str_lst.append(str(field_val))
        txt_str = ", ".join(txt_str_lst)+"\n"
        res += txt_str

    return res

def wrong_file_id(file_id: str, tg_token=settings.TELEGRAM_TOKEN):
    bot = telegram.Bot(tg_token)
    try:
        file = bot.get_file(file_id)
        return False
    except:
        return True

def get_no_foto_id():
    """
    Получает ИД фотографии заглушки, для тех у кого нет фото
    """
    config_set = Config.objects.filter(param_name = "no_foto_id")
    bot = telegram.Bot(settings.TELEGRAM_TOKEN)
    photo = f"{settings.MEDIA_ROOT}/no_foto.jpg"
    if len(config_set) == 0:
        message = bot.send_photo(settings.TRASH_GROUP, open(photo, 'rb'), caption="no_foto")
        foto_id, _ = _get_file_id(message)
        config_no_foto_id = Config(param_name = "no_foto_id", param_val = foto_id)
        config_no_foto_id.save()
    else:
        config_no_foto_id = config_set[0]

    if wrong_file_id(config_no_foto_id.param_val):
        message = bot.send_photo(settings.TRASH_GROUP, open(photo, 'rb'), caption="no_foto")
        foto_id, _ = _get_file_id(message)
        config_no_foto_id.param_val = foto_id
        config_no_foto_id.save()
    
    return config_no_foto_id.param_val
