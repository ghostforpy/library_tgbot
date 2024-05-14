from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram import ReplyKeyboardRemove

from tgbot.models import (
    # Status,
    # UserReferrers, 
    User
)
from tgbot.utils import send_message

from .messages import *
from .answers import *

def prepare_go_start_conversation(update: Update, context: CallbackContext):
    reply_markup = make_keyboard_start_menu()
    if update.message is not None:
        update.message.reply_text(PROF_HELLO, reply_markup=reply_markup)
    elif update.callback_query is not None:
        send_message(
            user_id=update.callback_query.from_user.id,
            text=PROF_HELLO,
            reply_markup=reply_markup
        )

def prepare_company_business_branches(update: Update, user: User):
    company_business_branches = dict()
    for n in BusinessBranches.objects.all():
        company_business_branches[str(n.id)] = n.title
        if n in user.business_branches.all():
            company_business_branches[str(n.id)] = CHECK_ICON + company_business_branches[str(n.id)]
    footer_buttons = NEXT if user.business_branches.count() > 0 else []
    kwargs = {
        "text":ASK_COMPANY_COMPANY_BUSINESS_BRANCHES,
        "reply_markup": make_keyboard(
                company_business_branches,
                "inline",
                1,
                footer_buttons=footer_buttons
            )
    }
    if update.message is not None:
        update.message.reply_text(
            "Начало работы с сегментом бизнеса",
            reply_markup=make_keyboard(EMPTY,"usual",2)
        )
        send_message(
            user_id=update.message.from_user.id,
            **kwargs
        )
    elif update.callback_query is not None:
        update.callback_query.edit_message_text(**kwargs)

def prepare_company_business_needs(update: Update, user: User):
    company_business_needs = dict()
    for n in BusinessNeeds.get_needs_by_user(user):
    # for n in BusinessNeeds.objects.all():
        company_business_needs[str(n.id)] = n.title
        if n in user.business_needs.all():
            company_business_needs[str(n.id)] = CHECK_ICON + company_business_needs[str(n.id)]
    footer_buttons = CREATE.copy()
    if user.business_needs.count() > 0:
        footer_buttons.update(NEXT)
    kwargs = {
        "text": ASK_COMPANY_BUSINESS_NEEDS,
        "reply_markup": make_keyboard(
                company_business_needs,
                "inline",
                1,
                footer_buttons=footer_buttons
            )
    }
    if update.message is not None:
        update.message.reply_text(
            "Начало работы с потребностями бизнеса",
            reply_markup=make_keyboard(EMPTY,"usual",2)
        )
        send_message(
            user_id=update.message.from_user.id,
            **kwargs
        )
    elif update.callback_query is not None:
        update.callback_query.edit_message_text(**kwargs)

def prepare_create_business_needs(update:Update):
    kwargs = {
        "text": ASK_CREATE_COMPANY_BUSINESS_NEEDS,
        "reply_markup": make_keyboard(
                CANCEL_CREATE,
                "inline",
                1,
            )
    }
    if update.message is not None:
        update.message.reply_text(**kwargs)
    elif update.callback_query is not None:
        update.callback_query.edit_message_text(**kwargs)

def prepare_manage_personal_info(update: Update, context: CallbackContext):
    kwargs ={
        "text":PERSONAL_START_MESSS,
        "reply_markup": make_keyboard_pers_menu()
    }
    if update.message is not None:
        update.message.reply_text(**kwargs)
    elif update.callback_query is not None:
        send_message(
            user_id=update.callback_query.from_user.id,
            **kwargs
    )
        # update.callback_query.edit_message_text(**kwargs)

def prepare_manage_busines_info(update: Update, context: CallbackContext):
    kwargs ={
        "text":BUSINES_START_MESSS,
        "reply_markup": make_keyboard_busines_menu()
    }
    if update.message is not None:
        update.message.reply_text(**kwargs)
    elif update.callback_query is not None:
        send_message(
            user_id=update.callback_query.from_user.id,
            **kwargs
        )


def prepare_company_business_benefits(update: Update, user: User):
    company_business_benefits = dict()
    # for n in BusinessBenefits.objects.all():
    for n in BusinessBenefits.get_benefits_by_user(user):
        company_business_benefits[str(n.id)] = n.title
        if n in user.business_benefits.all():
            company_business_benefits[str(n.id)] = CHECK_ICON + company_business_benefits[str(n.id)]
    footer_buttons = CREATE.copy()
    if user.business_benefits.count() > 0:
        footer_buttons.update(NEXT)
    kwargs = {
        "text": ASK_COMPANY_COMPANY_BUSINESS_BENEFITS,
        "reply_markup": make_keyboard(
                company_business_benefits,
                "inline",
                1,
                footer_buttons=footer_buttons
            )
    }
    if update.message is not None:
        # ечли нужно будет удаление нижней клавиатуры
        #         update.message.reply_text(
        #     "Начало работы с потребностями бизнеса",
        #     reply_markup=make_keyboard(EMPTY,"usual",2)
        # )
        # send_message(
        #     user_id=update.message.from_user.id,
        #     **kwargs
        # )
        update.message.reply_text(**kwargs)
    elif update.callback_query is not None:
        update.callback_query.edit_message_text(**kwargs)

def prepare_create_business_benefits(update:Update):
    kwargs = {
        "text": ASK_CREATE_COMPANY_BUSINESS_BENEFITS,
        "reply_markup": make_keyboard(
                CANCEL_CREATE,
                "inline",
                1,
            )
    }
    if update.message is not None:
        update.message.reply_text(**kwargs)
    elif update.callback_query is not None:
        update.callback_query.edit_message_text(**kwargs)