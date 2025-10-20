from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
import argparse


# --- 认证和路径解析函数 (假设它们已修复并正常工作) ---

def authenticate_drive():
    """加载本地凭证并刷新令牌以进行认证"""
    gauth = GoogleAuth()
    
    try:
        gauth.LoadCredentialsFile("settings.yaml")
    except Exception as e:
        raise Exception(f"无法加载凭证文件，请检查 settings.yaml 是否存在。错误: {e}")
    
    if gauth.access_token_expired or not gauth.credentials:
        print("凭证已过期或需要刷新，正在刷新 Access Token...")
        gauth.Refresh()
    else:
        gauth.Authorize()
        
    gauth.SaveCredentialsFile("settings.yaml")
    print("Google Drive 认证成功！")
    return GoogleDrive(gauth)

def get_folder_id_by_path(drive_service, path):
    """通过路径查找文件夹 ID (代码省略，使用之前修复后的版本)"""
    # 假设这里的实现是正确的，它返回目标文件夹的 ID 或 None
    # ... [请确保你之前修复好的 get_folder_id_by_path 函数在这里] ...
    
    # 示例简化版 (需要你插入之前修复好的代码)
    path_components = [p.strip() for p in path.split('/') if p.strip()]
    current_parent_id = 'root'
    
    for folder_name in path_components:
        query = (
            f"title = '{folder_name}' and "
            f"'{current_parent_id}' in parents and "
            "trashed = false and "
            "mimeType = 'application/vnd.google-apps.folder'"
        )
        file_list = drive_service.ListFile({'q': query}).GetList()
        
        if not file_list:
            print(f"!!! 错误: 路径解析失败，找不到文件夹 '{folder_name}'。")
            return None
        
        current_parent_id = file_list[0]['id']
    return current_parent_id


# --- 核心上传函数 ---

def upload_directory_recursive(drive_service, local_path, parent_drive_id):
    """
    递归上传本地文件夹及其内容到 Google Drive。
    :param drive_service: GoogleDrive 对象
    :param local_path: 本地文件夹路径
    :param parent_drive_id: 云端目标父文件夹 ID
    :return: 云端新创建的文件夹 ID
    """
    folder_name = os.path.basename(local_path)
    print(f"\n--- 开始上传文件夹: {folder_name} ---")

    # 1. 在云端创建新文件夹
    folder_metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [{'id': parent_drive_id}]
    }
    drive_folder = drive_service.CreateFile(folder_metadata)
    drive_folder.Upload()
    new_folder_id = drive_folder['id']
    print(f"已创建云端文件夹 '{folder_name}' (ID: {new_folder_id})")

    # 2. 遍历本地文件夹内容
    for item_name in os.listdir(local_path):
        local_item_path = os.path.join(local_path, item_name)
        
        if os.path.isfile(local_item_path):
            # 是文件，直接上传到新创建的文件夹中
            file_drive = drive_service.CreateFile({
                'title': item_name,
                'parents': [{'id': new_folder_id}]
            })
            file_drive.SetContentFile(local_item_path)
            file_drive.Upload()
            print(f"  - 上传文件: {item_name}")

        elif os.path.isdir(local_item_path):
            # 是子文件夹，递归调用自身
            print(f"  - 进入子文件夹: {item_name}")
            upload_directory_recursive(drive_service, local_item_path, new_folder_id)
            
    return new_folder_id


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, default="2025-08-09")
    parser.add_argument("--where", default="hk", type=str)
    args = parser.parse_args()
    # --- 配置 ---
    # 本地要上传的完整文件夹路径
    LOCAL_UPLOAD_PATH = f'./dataset/hsi_stock_data/Date={args.date}' 
    # 云端目标父目录路径 (上传后，新文件夹将位于此路径下)
    DRIVE_PARENT_PATH = 'stock_dataset/hsi_stock_data'
    # 确保本地文件夹存在
    if not os.path.isdir(LOCAL_UPLOAD_PATH):
        print(f"错误: 本地文件夹路径不存在或不是目录: {LOCAL_UPLOAD_PATH}")
    else:
        try:
            # 1. 认证
            drive = authenticate_drive()
            
            # 2. 查找云端父目录 ID
            print(f"开始查找云端父目录 ID: {DRIVE_PARENT_PATH}")
            parent_id = get_folder_id_by_path(drive, DRIVE_PARENT_PATH)
            
            if parent_id is None:
                print("操作终止：无法找到云端目标父目录。")
            else:
                # 3. 递归上传本地文件夹
                upload_directory_recursive(drive, LOCAL_UPLOAD_PATH, parent_id)
                print("\n--- 文件夹上传操作完成 ---")
            
        except Exception as e:
            print(f"操作过程中发生致命错误: {e}")