# installer.py
import os
import shutil
import zipfile
from datetime import datetime

# المجلد المصدر (المشروع الفعلي)
SOURCE_DIR = "buffett_screener"
OUTPUT_ZIP = f"buffett_screener_{datetime.now().strftime('%Y%m%d')}.zip"

def create_zip():
    """ضغط المشروع بالكامل مع استثناء الملفات غير الضرورية"""
    EXCLUDE = {
        'venv', '__pycache__', '.git', '.vscode',
        'logs', 'cache', '*.pyc', '.env'
    }
    
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(SOURCE_DIR):
            # استثناء المجلدات
            dirs[:] = [d for d in dirs if d not in EXCLUDE]
            
            for file in files:
                if file.endswith(('.pyc', '.log')) or file == '.env':
                    continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, SOURCE_DIR)
                zipf.write(file_path, arcname)
    
    print(f"✅ تم إنشاء: {OUTPUT_ZIP}")
    print(f"📦 الحجم: {os.path.getsize(OUTPUT_ZIP) / 1024:.2f} KB")

if __name__ == "__main__":
    create_zip()