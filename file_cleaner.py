"""
File Cleaner Module
Cleans up temporary pet-related files before processing
"""
import os
import glob


PETEXP_FILE_PATH = r"C:\Godswar Origin\Localization\en_us\Settings\User"


def clean_pet_files():
    """
    Delete all _petexp.txt and _petalert.txt files from the settings directory
    
    Returns:
        dict: Information about cleaned files
    """
    if not os.path.exists(PETEXP_FILE_PATH):
        return {
            'success': False,
            'error': 'Settings directory not found',
            'files_deleted': 0
        }
    
    deleted_files = []
    
    try:
        # Find and delete all *_petexp.txt files
        petexp_files = glob.glob(os.path.join(PETEXP_FILE_PATH, "*_petexp.txt"))
        for file_path in petexp_files:
            try:
                os.remove(file_path)
                deleted_files.append(os.path.basename(file_path))
            except Exception as e:
                print(f"Could not delete {file_path}: {e}")
        
        # Find and delete all *_petalert.txt files
        petalert_files = glob.glob(os.path.join(PETEXP_FILE_PATH, "*_petalert.txt"))
        for file_path in petalert_files:
            try:
                os.remove(file_path)
                deleted_files.append(os.path.basename(file_path))
            except Exception as e:
                print(f"Could not delete {file_path}: {e}")
        
        return {
            'success': True,
            'files_deleted': len(deleted_files),
            'files': deleted_files
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'files_deleted': len(deleted_files)
        }
