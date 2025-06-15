import pandas as pd
from accounts.models import UniqueCode

df = pd.read_excel("C:\Users\khand\Gift_ecommerce\unique_codes.xlsx") 
for code in df['code']:
    UniqueCode.objects.get_or_create(code=code.strip())