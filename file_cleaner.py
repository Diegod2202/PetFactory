"""
File Cleaner Module
Cleans up temporary pet-related files before processing
"""
import os
import glob


PETEXP_FILE_PATH = r"C:\Godswar Origin\Localization\en_us\Settings\User"  # Default path


def clean_pet_files(folder_path=None):
    """
    Delete all _petexp.txt and _petalert.txt files from the settings directory
    
    Args:
        folder_path (str): Optional custom path. Uses PETEXP_FILE_PATH if not provided.
    
    Returns:
        dict: Information about cleaned files
    """
    target_path = folder_path if folder_path else PETEXP_FILE_PATH
    
    if not os.path.exists(target_path):
        return {
            'success': False,
            'error': 'Settings directory not found',
            'files_deleted': 0
        }
    
    deleted_files = []
    
    try:
        # Find and delete all *_petexp.txt files
        petexp_files = glob.glob(os.path.join(target_path, "*_petexp.txt"))
        for file_path in petexp_files:
            try:
                os.remove(file_path)
                deleted_files.append(os.path.basename(file_path))
            except Exception as e:
                print(f"Could not delete {file_path}: {e}")
        
        # Find and delete all *_petalert.txt files
        petalert_files = glob.glob(os.path.join(target_path, "*_petalert.txt"))
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
