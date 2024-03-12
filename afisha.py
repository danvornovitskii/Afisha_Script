import subprocess
import os
import tempfile
import pyperclip
import requests
import datetime

def generate_unique_id():
    # Create a string containing uppercase letters, lowercase letters, and digits
    characters = string.ascii_letters + string.digits
    # Randomly select one character
    unique_id = random.choice(characters)
    return unique_id

################### Yandex Disk Integrations
URL = 'https://cloud-api.yandex.net/v1/disk/resources'
public_URL = 'https://cloud-api.yandex.net/v1/disk/public/resources'
TOKEN = 'y0_AgAAAAA3Qp8VAADLWwAAAAD8hU8WAADxbbacRWBGKaIKYIHn8795va9d2g'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}

def create_folder(path):
    # Создание папки. \n path: Путь к создаваемой папке
    requests.put(f'{URL}?path=/Mercury%20WORK/Afisha/{path}', headers=headers)

    return f'/Mercury%20WORK/Afisha/{path}'


def upload_file(loadfile, savefile, replace=False):
    #Загрузка файла.
    #savefile: Путь к файлу на Диске
    #loadfile: Путь к загружаемому файлу
    #replace: true or false Замена файла на Диск
    res = requests.get(f'{URL}/upload?path={savefile}&overwrite={replace}', headers=headers).json()
    with open(loadfile, 'rb') as f:
        try:
            requests.put(res['href'], files={'file':f})
        except KeyError:
            print(res)

# Publishes file and copies public link into a clipboard
def publish_file(path):
    res = requests.put(f'{URL}/publish?path={path}', headers=headers)
    meta = requests.get(f'{URL}/?path={path}', headers=headers).json()
    pyperclip.copy(meta['public_url'])
    print('Public URL copied to the clipboard.')

########################################

def create_video_with_transitions():

    output_dir = os.path.dirname(os.path.abspath(__file__))
    overlay_image_path = os.path.join(output_dir, "top_img.jpg")
    # Prompt the user to input image paths, separated by commas
    image_paths_input = input("Enter image paths, separated by space: ")
    
    # Split the input string into a list of paths and strip whitespace
    images = [path.strip() for path in filter(None, image_paths_input.split(' '))]

    with tempfile.TemporaryDirectory() as temp_dir:
        video_files = []

        # Step 1: Create individual videos
        for idx, image_path in enumerate(images):
            # Define the output video path for the current image
            video_path = os.path.join(temp_dir, f"video_{idx+1}.mp4")
            video_files.append(video_path)

            # Construct and run the FFmpeg command
            ffmpeg_cmd = [
                'ffmpeg',
                '-loop', '1',  # Loop the input image
                '-framerate', '25',  # Set framerate
                '-i', image_path,  # Input image path
                '-vf', 'fade=t=in:st=0:d=0.5,fade=t=out:st=4.5:d=0.5',  # Apply fade in and out
                '-t', '5',  # Set the duration of the output video
                '-pix_fmt', 'yuv420p',  # Specify pixel format
                video_path  # Output video path
            ]

            # Execute the FFmpeg command
            try:
                subprocess.run(ffmpeg_cmd, check=True)
                print(f"Video created at {video_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error creating video for {image_path}: {e}")

        for image_path in images:
            try:
                os.remove(image_path)
                print(f"Deleted image: {image_path}")
            except Exception as e:
                print(f"Error deleting image {image_path}: {e}")

        # Step 2: Generate FFmpeg file list for concatenation
        list_file_path = os.path.join(temp_dir, "file_list.txt")
        with open(list_file_path, "w") as list_file:
            for video_file in video_files:
                list_file.write(f"file '{video_file}'\n")

        # Step 3: Concatenate videos
        output_video_path = os.path.join(temp_dir, "final_output.mp4")
        ffmpeg_concat_cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file_path,
            '-c', 'copy',
            output_video_path
        ]
        
        subprocess.run(ffmpeg_concat_cmd, check=True)

        # Overlay the image on top of the concatenated video
        final_video_path = os.path.join(temp_dir, "final_video.mp4")
        ffmpeg_overlay_cmd = [
            'ffmpeg',
            '-i', output_video_path,
            '-i', overlay_image_path,
            '-filter_complex', 'overlay=0:0',  # Adjust '0:0' as needed to change overlay position
            '-codec:a', 'copy',
            final_video_path
        ]
        
        subprocess.run(ffmpeg_overlay_cmd, check=True)

        suffix = input("Add suffix to file name: ")
        today = datetime.date.today().isoformat()
        today2 = datetime.date.today()
        formatted_today = today2.strftime("%Y_%m_%d")
        yandex_folder_path = create_folder(today)
        upload_file(final_video_path, f'{yandex_folder_path}/Afisha_{formatted_today}_{suffix}.mp4')
        publish_file(yandex_folder_path)

create_video_with_transitions()