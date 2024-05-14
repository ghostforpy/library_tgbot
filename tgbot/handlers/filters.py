from telegram.ext import Filters, MessageFilter
FilterPrivateNoCommand = Filters.chat_type.private & (~Filters.command)
FilterGroupNoCommand = Filters.chat_type.groups & (~Filters.command)


class BotAddedToGroupFilter(MessageFilter):
    def __init__(self, bot_id) -> None:
        self.bot_id = bot_id
        super().__init__()

    def filter(self, message):
        return self.bot_id in [i.id for i in message.new_chat_members]

class BotLeftFromGroupFilter(MessageFilter):
    def __init__(self, bot_id) -> None:
        self.bot_id = bot_id
        super().__init__()

    def filter(self, message):
        return self.bot_id == message.left_chat_member.id

class MessageFromAdminsFilter(MessageFilter):
    def __init__(self, admins_ids) -> None:
        self.admins_ids = admins_ids
        super().__init__()

    def filter(self, message):
        return message.from_user.id in self.admins_ids