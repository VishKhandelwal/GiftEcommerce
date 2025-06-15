import pandas as pd
from django.core.management.base import BaseCommand
from accounts.models import UniqueCode

class Command(BaseCommand):
    help = 'Import unique codes from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str)

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        df = pd.read_excel("C:/Users/khand/Gift_ecommerce/unique_codes.xlsx")


        count = 0
        for code in df['code']:
            code = str(code).strip()
            if not UniqueCode.objects.filter(code=code).exists():
                UniqueCode.objects.create(code=code)
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} unique codes.'))
