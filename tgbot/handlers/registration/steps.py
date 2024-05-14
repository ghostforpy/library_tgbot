from .prepares import (
    prepare_ask_phone,
    prepare_ask_lastname,
    prepare_ask_role,
    prepare_ask_photo,
    prepare_ask_first_name,
)
from .utils import counter
from .saveuser import end_registration

step_iterator = counter(1)
STEPS = {
    "FIRSTNAME": {
        "step": step_iterator.current,
        "prepare": prepare_ask_lastname,
        "self_prepare": prepare_ask_first_name,
        "next": next(step_iterator)
    },
    "LASTNAME": {
        "step": step_iterator.current,
        "prepare": prepare_ask_phone,
        "self_prepare": prepare_ask_lastname,
        "next": next(step_iterator)
    },
    "PHONE": {
        "step": step_iterator.current,
        "prepare": prepare_ask_photo,
        "self_prepare": prepare_ask_phone,
        "next": next(step_iterator)
    },
    "PHOTO": {
        "step": step_iterator.current,
        "prepare": prepare_ask_role,
        "self_prepare": prepare_ask_photo,
        "next": next(step_iterator)
    },
    # "PATRONYMIC": { # отчество
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_lastname,
    #     "next": next(step_iterator)
    # },
    # "CITY": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_business_branch,
    #     "self_prepare": prepare_ask_city,
    #     "next": next(step_iterator)
    # },
    # "BUSINESS_BRANCH": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_company,
    #     "self_prepare": prepare_ask_business_branch,
    #     "next": next(step_iterator)
    # },
    # "COMPANY": {
    #     "step": step_iterator.current,
    #     "self_prepare": prepare_ask_company,
    #     "prepare": prepare_ask_job,
    #     "next": next(step_iterator)
    # },
    # "JOB": {
    #     "step": step_iterator.current,
    #     "self_prepare": prepare_ask_job,
    #     "prepare": prepare_company_number_of_employees,
    #     "next": next(step_iterator)
    # },
    # "SITE": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_company_number_of_employees,
    #     "next": next(step_iterator)
    # },
    "ROLE": {
        "step": step_iterator.current,
        "prepare": "",
        "self_prepare": prepare_ask_role,
        "next": end_registration
    },
    # "SHOP": {
    #     "step": step_iterator.current,
    #     "prepare": "",
    #     "self_prepare": prepare_ask_shop,
    #     "next": end_registration
    # },
    # "COMPANY_NUMBER_OF_EMPLOYESS": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_business_problems,
    #     "self_prepare": prepare_company_number_of_employees,
    #     "next": next(step_iterator)
    # },
    # "BUSINESS_PROBLEMS": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_completion_of_training,
    #     "self_prepare": prepare_ask_business_problems,
    #     "next": next(step_iterator)
    # },
    # "COMPLETION_OF_TRAINING": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_course,
    #     "self_prepare": prepare_ask_completion_of_training,
    #     "next": next(step_iterator),
    # },
    # "COURSE": {
    #     "step": step_iterator.current,
    #     "prepare": "",
    #     "self_prepare": prepare_ask_course,
    #     "next": end_registration,
    #     "_": next(step_iterator)
    # },
    # "COURSE_EXPECTATIONS": {
    #     "step": step_iterator.current,
    #     "prepare": "",
    #     "self_prepare": prepare_ask_course_expectations,
    #     "next": end_registration
    # },
    # "DEEP_LINK": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_approval,
    #     "self_prepare": prepare_deep_link,
    #     "next": next(step_iterator)
    # },
    # "APROVAL": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_phone,
    #     "next": next(step_iterator)
    # },



    # "FIO": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_birthday,
    #     "next": next(step_iterator)
    # },
    # "BIRTHDAY": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_about,
    #     "next": next(step_iterator)
    # },
    # "ABOUT": {
    #     "step": step_iterator.current,
    #     "prepare": ,
    #     "next": next(step_iterator)
    # },





    # "HOBBY": {
    #     "step": step_iterator.current,
    #     "prepare": prepare_ask_find_out,
    #     "next": next(step_iterator)
    # },
}