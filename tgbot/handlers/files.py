import telegram
from tgbot.models import User
from tgbot.utils import _get_file_id

def show_file_id(update, context):
    """ Returns file_id of the attached file/media  """
    u = User.get_user(update, context)

    if u.is_admin:
        update_json = update.to_dict()
        file_id = _get_file_id(update_json["message"])
        message_id = update_json["message"]["message_id"]
        update.message.reply_text(text=f"`{file_id}`", parse_mode=telegram.ParseMode.MARKDOWN, reply_to_message_id=message_id)
