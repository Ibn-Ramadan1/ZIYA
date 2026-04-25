import pandas as pd

files = ["data/diseases.csv", "data/drugs.csv", "data/disease_drug_links.csv"]

for file in files:
    # قراءة الملف
    df = pd.read_csv(file)
    # تنظيف أسماء الأعمدة
    df.columns = df.columns.str.strip()
    # تنظيف كل القيم داخل الجدول من المسافات
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    # حفظ الملف مرة تانية وهو نظيف
    df.to_csv(file, index=False)

print("تم تنظيف كل الملفات بنجاح! جرب تشغل الـ main.py دلوقتي.")