import os
import zipfile
import shutil
from datetime import datetime
from config import EXTRACTED_DIR, VIDEO_EXTENSIONS, IMAGE_EXTENSIONS

MAX_FILES = 100
MAX_TOTAL_SIZE = 100 * 1024 * 1024
MAX_SINGLE_FILE_SIZE = 50 * 1024 * 1024

def check_zip_safety(file_path):
    try:
        total_size = 0
        file_count = 0
        
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.is_dir():
                    continue
                
                file_count += 1
                total_size += file_info.file_size
                
                if file_count > MAX_FILES:
                    return False, f"Too many files in archive (max: {MAX_FILES})"
                
                if file_info.file_size > MAX_SINGLE_FILE_SIZE:
                    return False, f"File too large: {file_info.filename} (max: 50MB per file)"
                
                if total_size > MAX_TOTAL_SIZE:
                    return False, f"Total uncompressed size too large (max: 100MB)"
        
        return True, None
    except zipfile.BadZipFile:
        return False, "Invalid or corrupted ZIP file"
    except Exception as e:
        return False, str(e)

def extract_zip(file_path, user_id):
    is_safe, error = check_zip_safety(file_path)
    if not is_safe:
        return {"success": False, "error": error}
    
    user_extract_dir = os.path.join(EXTRACTED_DIR, str(user_id), datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(user_extract_dir, exist_ok=True)
    
    extracted_files = []
    video_files = []
    image_files = []
    
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.is_dir():
                    continue
                    
                file_name = os.path.basename(file_info.filename)
                if not file_name:
                    continue
                
                safe_name = "".join(c for c in file_name if c.isalnum() or c in "._- ")
                if not safe_name:
                    safe_name = f"file_{len(extracted_files)}"
                
                target_path = os.path.join(user_extract_dir, safe_name)
                
                counter = 1
                base_name, ext = os.path.splitext(safe_name)
                while os.path.exists(target_path):
                    target_path = os.path.join(user_extract_dir, f"{base_name}_{counter}{ext}")
                    counter += 1
                
                with zip_ref.open(file_info) as source:
                    with open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                
                extracted_files.append(target_path)
                
                ext_lower = os.path.splitext(safe_name)[1].lower()
                if ext_lower in VIDEO_EXTENSIONS:
                    video_files.append(target_path)
                elif ext_lower in IMAGE_EXTENSIONS:
                    image_files.append(target_path)
        
        return {
            "success": True,
            "extract_dir": user_extract_dir,
            "total_files": len(extracted_files),
            "extracted_files": extracted_files,
            "video_files": video_files,
            "image_files": image_files
        }
        
    except zipfile.BadZipFile:
        return {"success": False, "error": "Invalid or corrupted ZIP file"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_backup_zip(items, output_path, base_dir=None):
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for item in items:
                if not os.path.exists(item):
                    continue
                
                if os.path.isfile(item):
                    if base_dir:
                        arcname = os.path.relpath(item, base_dir)
                    else:
                        arcname = os.path.basename(item)
                    zipf.write(item, arcname)
                elif os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        dirs[:] = [d for d in dirs if d != '__pycache__' and not d.startswith('.')]
                        for file in files:
                            if file.endswith('.pyc') or file.startswith('.'):
                                continue
                            file_path = os.path.join(root, file)
                            if base_dir:
                                arcname = os.path.relpath(file_path, base_dir)
                            else:
                                arcname = os.path.relpath(file_path, os.path.dirname(item))
                            zipf.write(file_path, arcname)
        return True, output_path
    except Exception as e:
        return False, str(e)
