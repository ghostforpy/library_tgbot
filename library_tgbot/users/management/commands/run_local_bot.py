from django.core.management.base import BaseCommand
from django.utils import timezone
from tgbot.handlers.dispatcher import run_pooling
from django.utils import autoreload


class Command(BaseCommand):
    help = 'Run bot for local development'

    def handle(self, *args, **kwargs):
        autoreload.run_with_reloader(run_pooling)
        # run_pooling()
