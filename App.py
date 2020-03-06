from bs4 import BeautifulSoup
from time import sleep
import requests as req
import argparse
import wget
import os
import re

BASE_URL = "https://www.aparat.com"
HEADERS = {'user-agent': 'Mozilla/6.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Chrome/66'}

PLAYLIST_CODE = ""
PLAYLIST_URL = ""
OUT_PATH_DIR = ""
OFFLINE_HTML_FILE = ""
LOG_FILE_FOR_LINKS = "download_links.txt"
LOG_FILE_FOR_NAME = "download_file_names.txt"
# for separate saving name and link in txt file
LINE_SEP = "<@@@>"


def usage():
    return """
        use example :>
        for online mode :
        app.exe -code="117849" or
        app.exe -code="117849" -out="d:\\117849" 
        for offline mode :
        App.exe -code="110553"  -file="ss.html -online=n"
        App.exe -code="110553"  -file="ss.html" -out="d:\\110553" 
        out dir is optional parm and also The default quality is 720.
    """


def get_all_links_online(url):
    """
    get all a tag by request playlist url
    :param url: play list link such as https://www.aparat.com/playlist/288572
    :return: request result form url
    """
    res = req.get(url).content
    links = BeautifulSoup(res, 'html.parser')
    ls = links.find_all('a')
    lst_res = []
    for item in ls:
        link = (item.get('href'))
        if '/v/' in link and 'playlist={0}'.format(PLAYLIST_CODE) in link:
            lst_res.append(link)
    return lst_res


def generate_final_link_and_name(episode_link):
    """
    generate final download file link and name
    :param episode_link:
    :return: simple_name and file_name and also download_link contain dict
    """
    episode_url = BASE_URL + episode_link
    download_link = generate_episode_download_link(episode_url)
    file_name = str(os.path.basename(download_link['link']))
    simple_name = file_name.split('-')[0]
    return simple_name, download_link


def get_episode_links_online(lst_web_content):
    """
    generate base link for each episode in playlist  as list links form lst_web_content
    :param lst_web_content:request result
    :return: list of item contain dict name and txt links of episodes
    """
    if not len(lst_web_content) > 0:
        print('not found any links !!!')
        return
    lst_duplicate_link = []
    lst_download_links = []
    lst_file_names = []
    counter = 0
    for episode_link in lst_web_content:
        try:
            if episode_link is None:
                continue
            file_name, download_link = generate_final_link_and_name(episode_link)
            if lst_duplicate_link.count(file_name) > 0:
                continue
            lst_download_links.append(download_link)
            lst_duplicate_link.append(file_name)
            lst_file_names.append(file_name + LINE_SEP + download_link['filename'])
            counter += 1
            print("{0} :> add to download list :> {1}".format(counter, download_link['link']))
        except Exception as e:
            print(e)
    lst_pure_links = [link['link'] for link in lst_download_links]
    log_content_to_txt_file(lst_pure_links, LOG_FILE_FOR_LINKS)
    log_content_to_txt_file(lst_file_names, LOG_FILE_FOR_NAME)
    return lst_download_links


def generate_episode_download_link(url):
    """
    generate episode mp4 file link form apart site by quality
    start form 720p and end with 1080p (1080p is end because for large size)
    :param url: episode url link
    :return: list contain dict for files with name and url of file
    """
    request_res = req.get(url, headers=HEADERS)
    final_links = BeautifulSoup(request_res.content, "html.parser")
    file_name = str(final_links.title.text).strip().replace('  ', '')
    all_links = final_links.find_all('a')
    quality_range = ('720p', '480p', '360p', '240p', '1080p')
    for file_quality in quality_range:
        for my_link in all_links:
            result_link_end = str(my_link.get('href'))
            if result_link_end.endswith('.mp4') and file_quality in result_link_end:
                return {"filename": file_name, "link": result_link_end}
    return None


def get_all_links_from_html_file(html_file):
    link_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    with open(html_file, 'r', encoding="utf-8")as f:
        html_content = f.read()
        lst_links = re.findall(link_pattern, html_content)
        lst_final_links = [link for link in lst_links if PLAYLIST_CODE in link]
    return lst_final_links


def generate_episode_links_from_html_file(playlist_links):
    """
    generate list of episode playlist links form apart site
    :return: list txt links of episode playlist
    """
    lst_duplicate_link = []
    lst_download_links = []
    lst_file_names = []
    counter = 0
    for episode_link in playlist_links:
        try:
            if episode_link.startswith("http") and "playlist" in episode_link:
                download_link = generate_episode_download_link(episode_link)
                if download_link is None:
                    continue
                farsi_name = download_link['filename']
                file_name = str(os.path.basename(download_link['link']))
                fix_file_name = file_name.split('-')[0]
                if fix_file_name is None or lst_duplicate_link.count(fix_file_name) > 0:
                    continue
                lst_duplicate_link.append(fix_file_name)
                lst_download_links.append(download_link)
                lst_file_names.append(fix_file_name + LINE_SEP + farsi_name)
                counter += 1
                print(counter, " file found :> ", download_link['link'])
        except Exception as e:
            print(e, episode_link)
    lst_pure_links = [link['link'] for link in lst_download_links]
    log_content_to_txt_file(lst_pure_links, LOG_FILE_FOR_LINKS)
    log_content_to_txt_file(lst_file_names, LOG_FILE_FOR_NAME)
    return lst_download_links


def download_play_list_files(lst_download_links_dict, out_path_dir):
    """
    download file form list contain dict
    :param lst_download_links_dict:
    :param out_path_dir: save download files
    :return: no this !!!
    """
    if not os.path.exists(out_path_dir):
        os.mkdir(out_path_dir)
    for download_item in lst_download_links_dict:
        try:
            if download_item is not None:
                url_link = download_item["link"]
                file_final_path = os.path.join(out_path_dir, os.path.basename(url_link).split('-')[0] + '.mp4')
                if not os.path.exists(file_final_path):
                    print("download start : " + url_link)
                    wget.download(url_link, file_final_path)
                    sleep(2)
                else:
                    print(download_item[" filename "] + 'is exists')
            else:
                print('bad file ', download_item)
        except Exception as e:
            print(e, download_item["filename"])


def remove_extra_char_in_persian_name(farsi_name):
    """
    remove extra char for farsi name
    :param farsi_name:
    :return: clean str of farsi file name
    """
    if farsi_name is not None:
        clean_extra_char_farsi_name = re.sub(r"[^\w.  ]+", '', farsi_name)
        final_farsi_name = str(clean_extra_char_farsi_name).strip() + '.mp4'
        return final_farsi_name
    else:
        print('invalid name !!!')


def rename_download_files_to_persian_name(txt_file, dir_path):
    file = open(txt_file, 'r', encoding='utf-8')
    lst_file_names = file.readlines()
    for item in lst_file_names:
        english_name, farsi_name = item.split(LINE_SEP)
        final_farsi_name = remove_extra_char_in_persian_name(farsi_name)
        current_file_name = os.path.join(dir_path, english_name + '.mp4')
        if os.path.exists(current_file_name):
            os.rename(current_file_name, os.path.join(dir_path, final_farsi_name))
        else:
            print(english_name + "  not find  !!!!!!!!!! ")


def log_content_to_txt_file(lst_links_text, my_file):
    """
    log all content to txt file
    :param lst_links_text: list of item to save in txt file
    :param my_file:file name
    :return: none
    """
    ls = list(lst_links_text)
    with open(my_file, 'w', encoding="utf-8")as f:
        for item in ls:
            if item is not None:
                f.write(item + "\n")


def start_online_mode():
    print("start generate download links online")
    web_req_result = get_all_links_online(PLAYLIST_URL)
    lst_links = get_episode_links_online(web_req_result)
    if lst_links:
        print("start download files !!! \n")
        download_play_list_files(lst_links, OUT_PATH_DIR)
        rename_download_files_to_persian_name(LOG_FILE_FOR_NAME, OUT_PATH_DIR)
        print("end downloads !!!")


def start_offline_mode():
    print("start generate download links form file")
    lst_links = get_all_links_from_html_file(OFFLINE_HTML_FILE)
    lst_download_link = generate_episode_links_from_html_file(lst_links)
    if lst_download_link:
        print("start download files !!! \n")
        download_play_list_files(lst_download_link, OUT_PATH_DIR)
        rename_download_files_to_persian_name(LOG_FILE_FOR_NAME, OUT_PATH_DIR)
        print("end downloads !!!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Aparat PlayList Downloader", usage=usage())
    parser.add_argument("-online", metavar='online', type=str, default="y", help="online or offline mode")
    parser.add_argument("-file", metavar='file', type=str, help="input html file")
    parser.add_argument("-code", metavar='code', type=str, help="playlist code")
    parser.add_argument("-out", metavar='out', type=str, help=" output folder to save files")
    args = parser.parse_args()
    if args.code is None and args.file is None:
        usage()
    if args.out is None:
        args.out = os.getcwd()
    OUT_PATH_DIR = os.path.join(args.out, "{0}_Aparat_Files".format(args.code))
    if args.online == "y":
        PLAYLIST_CODE = args.code
        PLAYLIST_URL = BASE_URL + "/playlist/" + PLAYLIST_CODE
        start_online_mode()
    else:
        PLAYLIST_CODE = args.code
        PLAYLIST_URL = BASE_URL + "/playlist/" + PLAYLIST_CODE
        OFFLINE_HTML_FILE = args.file
        start_offline_mode()
