from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
import argparse

# --- 配置 ---
TARGET_FOLDER_ID = None  # 示例: '1A2b3C4d5E6f7G8h9I0jK1l2M3n4O5p6Q'


def authenticate_drive():
    """加载本地凭证并刷新令牌以进行认证"""
    gauth = GoogleAuth()

    # 尝试加载 settings.yaml 或 token.json 文件中的凭证
    # PyDrive2 会自动寻找并加载已保存的凭证
    try:
        gauth.LoadCredentialsFile("settings.yaml")

    except Exception as e:
        # 如果找不到凭证文件，抛出错误
        raise Exception(
            f"无法加载凭证文件，请检查 settings.yaml 或 token.json 是否存在。错误: {e}"
        )

    # 如果 Access Token 过期，使用 Refresh Token 刷新
    if gauth.access_token_expired or not gauth.credentials:
        print("凭证已过期或需要刷新，正在刷新 Access Token...")
        gauth.Refresh()
    else:
        # 如果 Access Token 有效，直接授权
        gauth.Authorize()

    # 保存新的 Access Token (可选，但推荐)
    gauth.SaveCredentialsFile("settings.yaml")

    print("Google Drive 认证成功！")
    return GoogleDrive(gauth)


def upload_file(drive_service, local_filepath, parent_folder_id=None):
    """
    上传指定文件到 Google Drive
    :param drive_service: GoogleDrive 对象
    :param local_filepath: 本地文件完整路径
    :param parent_folder_id: 目标文件夹 ID
    :return: 上传后的文件 ID
    """
    if not os.path.exists(local_filepath):
        print(f"错误: 本地文件 {local_filepath} 不存在。")
        return None

    file_name = os.path.basename(local_filepath)

    # 1. 创建一个 DriveFile 对象
    file_drive = drive_service.CreateFile({"title": file_name})

    # 2. 指定上传目标文件夹
    if parent_folder_id:
        file_drive["parents"] = [{"id": parent_folder_id}]

    # 3. 关联本地文件内容
    file_drive.SetContentFile(local_filepath)

    # 4. 执行上传操作
    file_drive.Upload()

    print(f"\n--- 上传成功 ---")
    print(f"文件名: {file_name}")
    print(f"文件 ID: {file_drive['id']}")
    print(f"Google Drive 链接: https://drive.google.com/open?id={file_drive['id']}")
    return file_drive["id"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, default="2025-08-09")
    parser.add_argument("--where", default="hk", type=str)
    args = parser.parse_args()
    try:
        # 1. 认证
        drive = authenticate_drive()

        # 2. 上传文件
        local_filepath = os.path.join("dataset", "hsi_stock_data", f"Date={args.date}")
        folder_metadata = {
            'title': local_filepath,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': None
        }
        drive_folder = drive.CreateFile(folder_metadata)
        drive_folder.Upload()
        new_folder_id = drive_folder['id']
        print(f"已创建新文件夹 '{local_filepath}' (ID: {new_folder_id})")
        for filename in os.listdir(local_filepath):
            upload_file(drive, os.path.join(local_filepath, filename), new_folder_id)

    except Exception as e:
        print(f"操作过程中发生致命错误: {e}")
